/* =====================================================================
   Open Air Gallery — WASH

   The graffiti-removal mechanic: drag across a tagged brick wall and the
   tag comes off under the stroke. Markup from wall.py, staging in
   css/wash.css; nothing in this file is load-bearing.

   It returns before touching the DOM unless html.motion is present and the
   visitor has not asked for reduced motion, so the reduced-motion render is
   the same document as the no-script one: the finished clean wall with the
   tagged version beside it as a "before" thumbnail.

   How it works. A 256x144 offscreen canvas starts opaque and the stroke
   punches soft radial holes in it with destination-out; the canvas goes to
   .wall-tag as a PNG data URL in --wash-mask, so the clean layer shows
   through the stroke. Every 6th frame an alpha-sum of the same buffer says
   how much of the wall is clean; at 78% the remainder wipes itself, one
   glint sweeps the bricks, a few sparks fire, and the wall rests clean.
   No counter, no percentage, no label — ever.

   API (window.oagWash):
     .instances   the bound walls, in document order
     .refresh()   re-scan the document for [data-wash] (idempotent)
     .sound.get() / .sound.set(on)   the persisted mute state
   ===================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  if (!root.classList.contains('motion')) return;
  var reduced = false;
  try { reduced = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (reduced) return;

  var W = 256, H = 144;             // the mask, at every display size
  var DONE_AT = 0.78;               // cleaned fraction that finishes it
  var WIPE_MS = 500;                // how long the remainder takes
  var FPS_FRAMES = 20, FPS_FLOOR = 25, WORK_FLOOR = 8;   // 25ms a frame is 40fps

  var fine = false, coarse = false;
  try {
    fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
    coarse = matchMedia('(pointer:coarse)').matches;
  } catch (e) {}

  /* ---------------------------------------------------------------- sound
     One AudioContext for the page, and it is not built here: site.js's kit
     owns it (window.oagKit.sound), because /about and /404 needed the same
     module for the Wall brush and a second AudioContext in a second file was
     the wrong answer. Same voices, same persisted key, same rule — muted by
     default, nothing ever runs on load. site.js is written into the document
     ahead of this file and both are deferred, so the kit is there by the
     time this line runs; the stub is for the case where site.js never
     arrived at all, in which case the wall still washes, in silence. */
  var Sound = (window.oagKit && window.oagKit.sound) || {
    get: function () { return false; }, set: function () {},
    sprayOn: function () {}, spraySpeed: function () {}, sprayOff: function () {},
    squeak: function () {}
  };

  /* ----------------------------------------------------------------- one wall */
  function Wash(fig) {
    this.fig = fig;
    this.mode = fig.getAttribute('data-wash') === 'auto' ? 'auto' : 'interactive';
    this.stage = fig.querySelector('[data-wash-stage]');
    this.tag = fig.querySelector('[data-wash-tag]');
    this.sparkbox = fig.querySelector('[data-wash-sparks]');
    this.head = fig.querySelector('[data-wash-head]');
    this.btn = fig.querySelector('[data-wash-snd]');
    this.armed = false; this.inview = false; this.done = false;
    this.dragging = false; this.raf = 0; this.frames = 0;
    this.queue = []; this.last = null; this.travel = 0; this.speed = 0;
    this.cleaned = 0; this.rect = null; this.hx = -999; this.hy = -999;
    this.fps = []; this.workT = []; this.work = 0; this.degraded = false;
    this.tilt = { bound: false, base: null, y: 0, t: 0 };
    this.r = coarse ? 19 : 15;                 // brush radius, x1.3 on a finger
    this.sparkCount = coarse ? 4 : 8;
    var self = this;

    if (this.btn) {
      this.btn.setAttribute('aria-pressed', String(Sound.get()));
      this.btn.addEventListener('click', function () {
        var next = self.btn.getAttribute('aria-pressed') !== 'true';
        self.btn.setAttribute('aria-pressed', String(next));
        Sound.set(next);                        // this click is the gesture
      });
    }
  }

  /* Once, when the wall first comes into view: the CSS hooks go live and the
     2.8s self-reveal that would have undone them is cancelled. */
  Wash.prototype.arm = function () {
    if (this.armed) return;
    this.armed = true;
    this.fig.classList.add('is-live');
    if (this.mode === 'interactive') this.bind();
  };

  Wash.prototype.bind = function () {
    if (this.bound || this.done || this.degraded) return;
    this.bound = true;
    var self = this;
    this.on = {
      down: function (e) { self.down(e); },
      move: function (e) { self.move(e); },
      up: function (e) { self.up(e); },
      enter: function () { self.fig.classList.add('is-hover'); },
      leave: function () { self.fig.classList.remove('is-hover'); self.up(); }
    };
    this.stage.addEventListener('pointerdown', this.on.down);
    this.stage.addEventListener('pointermove', this.on.move);
    this.stage.addEventListener('pointerup', this.on.up);
    this.stage.addEventListener('pointercancel', this.on.up);
    this.stage.addEventListener('pointerenter', this.on.enter);
    this.stage.addEventListener('pointerleave', this.on.leave);
  };

  Wash.prototype.unbind = function () {
    if (!this.bound) return;
    this.bound = false;
    this.stage.removeEventListener('pointerdown', this.on.down);
    this.stage.removeEventListener('pointermove', this.on.move);
    this.stage.removeEventListener('pointerup', this.on.up);
    this.stage.removeEventListener('pointercancel', this.on.up);
    this.stage.removeEventListener('pointerenter', this.on.enter);
    this.stage.removeEventListener('pointerleave', this.on.leave);
    this.fig.classList.remove('is-hover');
    this.untilt();
  };

  /* The mask buffer and the brush, both made once and only if a pointer
     actually arrives: a wall nobody touches costs nothing. */
  Wash.prototype.canvas = function () {
    if (this.cv) return this.cv;
    var cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    var g = cv.getContext('2d', { willReadFrequently: true });
    g.fillStyle = '#fff';
    g.fillRect(0, 0, W, H);            // opaque: the tag is all still up
    // Every mark from here on subtracts alpha, so the stroke is a hole in
    // the mask and the clean layer shows through it.
    g.globalCompositeOperation = 'destination-out';
    this.cv = cv; this.g = g;

    var b = document.createElement('canvas'), rr = 48;
    b.width = b.height = rr * 2;
    var bg = b.getContext('2d');
    var rad = bg.createRadialGradient(rr, rr, 0, rr, rr, rr);
    rad.addColorStop(0, 'rgba(255,255,255,1)');
    rad.addColorStop(0.55, 'rgba(255,255,255,.92)');
    rad.addColorStop(0.82, 'rgba(255,255,255,.42)');
    rad.addColorStop(1, 'rgba(255,255,255,0)');
    bg.fillStyle = rad; bg.fillRect(0, 0, rr * 2, rr * 2);
    this.brush = b;
    return cv;
  };

  Wash.prototype.stamp = function (x, y, r) {
    this.g.drawImage(this.brush, x - r, y - r, r * 2, r * 2);
  };

  /* Water runs: three fading dabs straight down from the stroke. */
  Wash.prototype.drip = function (x, y) {
    var r = this.r, j = (Math.random() - 0.5) * r * 0.5;
    this.stamp(x + j, y + r * 0.85, r * 0.55);
    this.stamp(x + j * 1.4, y + r * 1.55, r * 0.40);
    this.stamp(x + j * 1.8, y + r * 2.15, r * 0.26);
  };

  Wash.prototype.push = function () {
    this.tag.style.setProperty('--wash-mask', 'url("' + this.cv.toDataURL() + '")');
  };

  Wash.prototype.at = function (e) {
    var r = this.rect;
    return {
      x: (e.clientX - r.left) / r.width * W,
      y: (e.clientY - r.top) / r.height * H,
      cx: e.clientX - r.left, cy: e.clientY - r.top, t: e.timeStamp || performance.now()
    };
  };

  Wash.prototype.down = function (e) {
    if (this.done || this.degraded) return;
    this.canvas();
    this.rect = this.stage.getBoundingClientRect();
    try { this.stage.setPointerCapture(e.pointerId); } catch (err) {}
    this.dragging = true;
    this.fig.classList.add('is-dragging');
    this.last = this.at(e);
    this.hx = this.last.cx; this.hy = this.last.cy;
    if (Sound.get()) Sound.sprayOn();
    this.schedule();
  };

  Wash.prototype.move = function (e) {
    if (this.done || this.degraded) return;
    if (!this.rect) this.rect = this.stage.getBoundingClientRect();
    var evs = (this.dragging && e.getCoalescedEvents) ? e.getCoalescedEvents() : null;
    if (evs && evs.length) {
      for (var i = 0; i < evs.length; i++) this.queue.push(this.at(evs[i]));
    } else if (this.dragging) {
      this.queue.push(this.at(e));
    }
    var p = this.at(e);
    this.hx = p.cx; this.hy = p.cy;
    this.schedule();
  };

  Wash.prototype.up = function (e) {
    if (e && e.pointerId != null) {
      try { this.stage.releasePointerCapture(e.pointerId); } catch (err) {}
    }
    if (!this.dragging) return;
    this.dragging = false;
    this.fig.classList.remove('is-dragging');
    Sound.sprayOff();
    this.hadDrag = true;
    this.maybeTilt();
  };

  Wash.prototype.schedule = function () {
    if (this.raf) return;
    var self = this;
    this.raf = requestAnimationFrame(function (t) { self.frame(t); });
  };

  /* One rAF handler for the whole wall: read the box, paint the queue, write
     the mask and the follower. Reads before writes, once a frame. */
  Wash.prototype.frame = function (t) {
    this.raf = 0;
    if (this.done || this.degraded) return;
    var painted = false, w0 = performance.now();

    if (this.queue.length) {
      this.rect = this.stage.getBoundingClientRect();     // read first
      var r = this.r, q = this.queue, moved = 0;
      for (var i = 0; i < q.length; i++) {
        var p = q[i], a = this.last || p;
        var dx = p.x - a.x, dy = p.y - a.y, d = Math.sqrt(dx * dx + dy * dy);
        var steps = Math.max(1, Math.ceil(d / (r / 3)));
        for (var s = 1; s <= steps; s++) {
          this.stamp(a.x + dx * s / steps, a.y + dy * s / steps, r);
        }
        this.travel += d; moved += d;
        if (this.travel > 13) {          // ~60 display px between drips
          this.travel = 0;
          this.drip(p.x, p.y);
        }
        this.last = p;
      }
      this.queue.length = 0;
      this.speed = this.speed * 0.6 + Math.min(1, moved / 26) * 0.4;
      if (Sound.get()) Sound.spraySpeed(this.speed);
      this.push();                                        // then write
      painted = true;
    }

    if (this.head) {
      this.head.style.setProperty('--hx', this.hx + 'px');
      this.head.style.setProperty('--hy', this.hy + 'px');
    }

    if (painted) {
      this.frames++;
      if (this.frames % 6 === 0) this.coverage();
    }
    this.work = performance.now() - w0;
    if (this.dragging) { this.measure(t); this.schedule(); }
  };

  /* Hardware check. The frame loop runs every frame while the pointer is
     down, so the gap between frames is the real frame rate rather than how
     fast the pointer happens to be sending events. Twenty frames that cannot
     hold 40fps means this device should not be doing this, and it gets the
     crossfade instead. The single worst frame is thrown away: one hitch — a
     font landing, a tab waking — is not a slow device.

     The second half of the test matters as much as the first. A tab can be
     stalled for reasons that are nothing to do with us — a remote-driven
     browser, a background throttle, another tab eating the compositor — and
     on a bare rAF loop with no work at all this machine measures 12fps under
     Playwright. Dropping the mechanic there helps nobody, so we also require
     our own per-frame work (stamping, the coverage read, the data URL) to be
     a real share of the frame. If we are cheap and the frame is still slow,
     we are not what is making it slow. */
  Wash.prototype.measure = function (t) {
    if (this.fpsDone) return;
    this.tick = (this.tick || 0) + 1;
    if (this.lastT && this.tick > 4) {
      this.fps.push(t - this.lastT);
      this.workT.push(this.work);
    }
    this.lastT = t;
    if (this.fps.length < FPS_FRAMES) return;
    this.fpsDone = true;
    var gap = 0, worst = 0, work = 0, i;
    for (i = 0; i < this.fps.length; i++) {
      gap += this.fps[i]; work += this.workT[i];
      if (this.fps[i] > worst) worst = this.fps[i];
    }
    this.meanGap = (gap - worst) / (this.fps.length - 1);
    this.meanWork = work / this.workT.length;
    if (this.meanGap > FPS_FLOOR && this.meanWork > WORK_FLOOR) this.degrade();
  };

  /* Cheap coverage: alpha-sum of every 8th pixel of the mask buffer. It
     never becomes a number the visitor can see. */
  Wash.prototype.coverage = function () {
    var d;
    try { d = this.g.getImageData(0, 0, W, H).data; } catch (e) { return; }
    var clean = 0, n = 0;
    for (var y = 0; y < H; y += 2) {
      for (var x = 0; x < W; x += 4) {
        if (d[(y * W + x) * 4 + 3] < 128) clean++;
        n++;
      }
    }
    this.cleaned = clean / n;
    if (this.cleaned >= DONE_AT) this.finish();
  };

  /* The payoff: the remainder wipes itself, one glint crosses the bricks,
     a handful of sparks pop, and that is the end of it. */
  Wash.prototype.finish = function () {
    if (this.done) return;
    this.done = true;
    this.dragging = false;
    this.fig.classList.remove('is-dragging');
    this.unbind();
    Sound.sprayOff();

    var self = this, t0 = performance.now();
    (function wipe(now) {
      var p = Math.min(1, (now - t0) / WIPE_MS);
      var e = 1 - Math.pow(1 - p, 3);              // ease out
      var front = e * (W + 40);
      var g = self.g;
      var grad = g.createLinearGradient(front - 34, 0, front + 6, 0);
      grad.addColorStop(0, 'rgba(255,255,255,1)');
      grad.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = grad;
      g.fillRect(0, 0, front + 6, H);
      self.push();
      if (p < 1) requestAnimationFrame(wipe);
      else self.rest();
    })(t0);
  };

  Wash.prototype.rest = function () {
    this.fig.classList.add('is-clean', 'is-done');
    this.tag.style.removeProperty('--wash-mask');
    this.sparkle();
    if (Sound.get()) Sound.squeak();
    this.cv = this.g = this.brush = null;            // let the buffers go
  };

  Wash.prototype.sparkle = function () {
    if (!this.sparkbox) return;
    var n = this.sparkCount, made = [];
    for (var i = 0; i < n; i++) {
      var s = document.createElement('span');
      s.className = 'wall-spark';
      s.style.setProperty('--x', (10 + Math.random() * 80).toFixed(1) + '%');
      s.style.setProperty('--y', (14 + Math.random() * 68).toFixed(1) + '%');
      s.style.setProperty('--s', (12 + Math.random() * 16).toFixed(0) + 'px');
      s.style.setProperty('--d', (i * 70 + Math.random() * 60).toFixed(0) + 'ms');
      this.sparkbox.appendChild(s);
      made.push(s);
    }
    setTimeout(function () {
      made.forEach(function (s) { if (s.parentNode) s.parentNode.removeChild(s); });
    }, 2200);
  };

  /* Too slow, or asked for less: no canvas, no particles, no sound — the tag
     simply dissolves and the before goes back to being a thumbnail. */
  Wash.prototype.degrade = function () {
    if (this.degraded || this.done) return;
    this.degraded = true;
    this.dragging = false;
    this.unbind();
    Sound.sprayOff();
    this.fig.classList.remove('is-dragging');
    this.fig.classList.add('is-crossfade');
    var self = this;
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { self.fig.classList.add('is-faded'); });
    });
  };

  /* ------------------------------------------------------- tilt rinse (mobile)
     Offered only after a first drag, only on a coarse pointer, and only where
     the reading needs no permission prompt: on iOS DeviceOrientationEvent
     carries requestPermission, so this silently never happens there. */
  Wash.prototype.maybeTilt = function () {
    if (this.tilt.bound || !coarse || this.done || this.degraded) return;
    var DOE = window.DeviceOrientationEvent;
    if (!DOE || typeof DOE.requestPermission === 'function') return;
    var self = this;
    this.tilt.bound = true;
    this.tilt.fn = function (e) { self.onTilt(e); };
    addEventListener('deviceorientation', this.tilt.fn, { passive: true });
  };

  Wash.prototype.untilt = function () {
    if (!this.tilt.bound) return;
    removeEventListener('deviceorientation', this.tilt.fn);
    this.tilt.bound = false;
    this.fig.classList.remove('is-rinsing');
  };

  Wash.prototype.onTilt = function (e) {
    var now = performance.now();
    if (now - this.tilt.t < 33) return;                  // 30Hz is plenty
    this.tilt.t = now;
    var b = e.beta;
    if (b == null || this.done || this.degraded) return;
    if (this.tilt.base == null) { this.tilt.base = b; return; }
    var lean = Math.max(-1, Math.min(1, (b - this.tilt.base) / 30));
    if (lean < 0.35) { this.fig.classList.remove('is-rinsing'); return; }
    this.canvas();
    this.fig.classList.add('is-rinsing');
    this.tilt.y = Math.min(H + this.r, this.tilt.y + lean * 5);
    this.fig.style.setProperty('--rinse', (this.tilt.y / H * 100).toFixed(1) + '%');
    for (var x = 0; x <= W; x += this.r) this.stamp(x, this.tilt.y, this.r);
    this.push();
    this.frames++;
    if (this.frames % 6 === 0) this.coverage();
  };

  /* ------------------------------------------------------------- the observer
     One for every wall on the page. Listeners exist only while the figure is
     on screen; the home band's loop is paused the moment it leaves. */
  var instances = [];

  function bindAll() {
    var figs = document.querySelectorAll('[data-wash]');
    for (var i = 0; i < figs.length; i++) {
      if (figs[i].__wash) continue;
      var w = new Wash(figs[i]);
      figs[i].__wash = w;
      instances.push(w);
      if (!('IntersectionObserver' in window)) { w.arm(); continue; }
      io.observe(figs[i]);
    }
  }

  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      var w = e.target.__wash;
      if (!w) return;
      w.inview = e.isIntersecting;
      if (e.isIntersecting) {
        w.arm();
        w.fig.classList.remove('is-paused');
        if (w.mode === 'interactive') w.bind();
      } else {
        w.fig.classList.add('is-paused');
        w.unbind();
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -4% 0px' }) : null;

  bindAll();

  window.oagWash = {
    instances: instances,
    refresh: bindAll,
    sound: { get: function () { return Sound.get(); }, set: function (v) { Sound.set(v); } }
  };
})();
