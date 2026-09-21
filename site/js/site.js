/* =====================================================================
   Open Air Gallery — site scripts.

   Nothing in here is load-bearing. The pages render complete without it;
   this only adds the mobile menu, the scrolled state on the nav, the
   current-page marker and the copyright year.
   ===================================================================== */

/* =====================================================================
   The kit — the two things more than one mechanic needs.

   A seeded random and a sound module, on window.oagKit, because they were
   each about to exist twice. The generator was written for Splat's bristles
   and is what Wall's bristles are stamped from; the sound module was written
   inside wash.js and is what /about and /404 now ask for, and wash.js asks
   the same module rather than building a second AudioContext.

   Nothing here is gated on motion and nothing here starts anything: the
   generator is pure and the sound module is a closure that has not touched
   the audio API until the visitor has turned sound on and then done
   something. Muted is the default, the choice persists under the key wash
   has always used, and no page ever makes a noise on load.

   This block runs before the mechanics below it and, because both files are
   deferred and site.js is written into the document ahead of wash.js, before
   wash.js — which is the whole reason the script tag moved out of the head.
   ===================================================================== */
(function () {
  'use strict';

  /* mulberry32. Seeded on purpose: the same fingers every run, so a brush
     built in the browser is the same brush every time it is built. */
  const rng = (seed) => {
    let t = seed >>> 0;
    return () => {
      t = (t + 0x6D2B79F5) >>> 0;
      let r = Math.imul(t ^ (t >>> 15), 1 | t);
      r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
      return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    };
  };

  /* --- sound ---------------------------------------------------------
     One AudioContext for the page, built on a real user gesture and only
     once the visitor has asked for sound. Two kinds of voice:

       a loop     filtered white noise held open while something is being
                  dragged, its gain following how fast it is moving — the
                  pressure washer's spray, and the brush's hiss on brick.
                  Each voice has a name so two mechanics can never fight
                  over one gain node.
       a chirp    the squeak of a finger on clean glass, fired once.

     The noise buffer is two seconds long and every voice shares it. */
  const SND_KEY = 'oag:wash:snd';
  const sound = (function () {
    let ctx = null, buf = null, on = false;
    const voices = Object.create(null);
    try { on = localStorage.getItem(SND_KEY) === '1'; } catch (e) {}

    function ensure() {
      if (!on) return null;
      if (!ctx) {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return null;
        try { ctx = new AC(); } catch (e) { return null; }
        buf = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
        const d = buf.getChannelData(0);
        for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
      }
      if (ctx.state === 'suspended') ctx.resume();
      return ctx;
    }

    // floor/span are this voice's gain range: its faintest and how much
    // louder the fastest stroke makes it. Both are small on purpose.
    function voiceOn(name, freq, q, floor, span) {
      const c = ensure();
      if (!c || voices[name]) return;
      const src = c.createBufferSource(), bp = c.createBiquadFilter(), g = c.createGain();
      src.buffer = buf; src.loop = true;
      bp.type = 'bandpass'; bp.frequency.value = freq; bp.Q.value = q;
      g.gain.value = 0;
      src.connect(bp); bp.connect(g); g.connect(c.destination);
      src.start();
      voices[name] = { src, g, floor, span };
    }

    function voiceAt(name, v) {
      const o = voices[name];
      if (!o || !ctx) return;
      const t = Math.max(0, Math.min(1, v));
      o.g.gain.setTargetAtTime(o.floor + t * o.span, ctx.currentTime, 0.06);
    }

    function voiceOff(name) {
      const o = voices[name];
      if (!o) return;
      delete voices[name];
      if (!ctx) return;
      o.g.gain.setTargetAtTime(0, ctx.currentTime, 0.05);
      try { o.src.stop(ctx.currentTime + 0.4); } catch (e) {}
    }

    function allOff() { for (const k in voices) voiceOff(k); }

    return {
      get: () => on,
      set: (v) => {
        on = !!v;
        try { localStorage.setItem(SND_KEY, on ? '1' : '0'); } catch (e) {}
        if (!on) allOff(); else ensure();
      },
      // Wash: the pressure washer's spray.
      sprayOn: () => voiceOn('spray', 2600, 0.7, 0.015, 0.10),
      spraySpeed: (v) => voiceAt('spray', v),
      sprayOff: () => voiceOff('spray'),
      // Wall: a brush dragged over brick — lower, broader, and fainter.
      hissOn: () => voiceOn('brush', 1250, 0.55, 0.006, 0.042),
      hissSpeed: (v) => voiceAt('brush', v),
      hissOff: () => voiceOff('brush'),
      // Spray: the can writing on a wall. Its own named voice, tighter and
      // higher than the washer's jet, so a Home page that carries both can
      // never have one of them reaching for the other's gain node.
      canOn: () => voiceOn('can', 3400, 1.2, 0.006, 0.045),
      canAt: (v) => voiceAt('can', v),
      canOff: () => voiceOff('can'),
      // Spray: the ball bearing in a rattle can, shaken as it comes in.
      // Four knocks out of the same noise buffer every other voice uses,
      // each one a few milliseconds of band-passed noise and gone.
      rattle: () => {
        const c = ensure();
        if (!c) return;
        [0, 0.105, 0.2, 0.315].forEach((at, i) => {
          const t = c.currentTime + at;
          const src = c.createBufferSource(), bp = c.createBiquadFilter(), g = c.createGain();
          src.buffer = buf; src.loop = true;
          bp.type = 'bandpass';
          bp.frequency.value = 1700 + i * 260;
          bp.Q.value = 2.4;
          g.gain.setValueAtTime(0.0001, t);
          g.gain.exponentialRampToValueAtTime(0.05, t + 0.006);
          g.gain.exponentialRampToValueAtTime(0.0001, t + 0.055);
          src.connect(bp); bp.connect(g); g.connect(c.destination);
          src.start(t); src.stop(t + 0.07);
        });
      },
      // Tip: a tin of paint going over. Two sounds in one: the slosh, a
      // band of noise swept downward as the body of paint leans over and
      // leaves, and behind it three glugs — the air going back into the
      // tin, each one lower than the last as it empties.
      glug: () => {
        const c = ensure();
        if (!c) return;
        const t0 = c.currentTime;
        const src = c.createBufferSource(), bp = c.createBiquadFilter(), g = c.createGain();
        src.buffer = buf; src.loop = true;
        bp.type = 'bandpass'; bp.Q.value = 1.1;
        bp.frequency.setValueAtTime(900, t0);
        bp.frequency.exponentialRampToValueAtTime(330, t0 + 0.34);
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.exponentialRampToValueAtTime(0.042, t0 + 0.06);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.4);
        src.connect(bp); bp.connect(g); g.connect(c.destination);
        src.start(t0); src.stop(t0 + 0.44);
        [[0.21, 210], [0.34, 172], [0.46, 142]].forEach((s) => {
          const t = t0 + s[0];
          const o = c.createOscillator(), og = c.createGain();
          o.type = 'sine';
          o.frequency.setValueAtTime(s[1], t);
          o.frequency.exponentialRampToValueAtTime(s[1] * 0.55, t + 0.09);
          og.gain.setValueAtTime(0.0001, t);
          og.gain.exponentialRampToValueAtTime(0.055, t + 0.015);
          og.gain.exponentialRampToValueAtTime(0.0001, t + 0.12);
          o.connect(og); og.connect(c.destination);
          o.start(t); o.stop(t + 0.14);
        });
      },
      // Wash: two rising chirps, the squeak of a finger on clean glass.
      squeak: () => {
        const c = ensure();
        if (!c) return;
        [[0, 1500, 2700, 0.11], [0.085, 1900, 3300, 0.08]].forEach((s) => {
          const t = c.currentTime + s[0];
          const o = c.createOscillator(), g = c.createGain();
          o.type = 'sine';
          o.frequency.setValueAtTime(s[1], t);
          o.frequency.exponentialRampToValueAtTime(s[2], t + 0.09);
          g.gain.setValueAtTime(0.0001, t);
          g.gain.exponentialRampToValueAtTime(s[3], t + 0.02);
          g.gain.exponentialRampToValueAtTime(0.0001, t + 0.13);
          o.connect(g); g.connect(c.destination);
          o.start(t); o.stop(t + 0.15);
        });
      },
    };
  })();

  /* --- the sound toggle ------------------------------------------------
     The button a mechanic puts in the corner of its hero to ask for sound.
     It was the wall's; the tin on /services wanted the same one, and the
     second time something is about to be written twice is exactly what
     this kit is for — so it lives here and both call it.

     Muted is the default and the state is the one key every mechanic on
     the site shares, so turning sound on for the wall turns it on for the
     tin. The click is also the gesture the audio API wants: nothing here
     builds an AudioContext until a visitor has pressed this. It is only
     ever built under html.motion, by the mechanic that wants it, so the
     no-script and reduced-motion documents have no toggle in them at all.
     .paint-snd in site.css is absolutely positioned, so it costs the hero
     it is dropped into no height.                                        */
  const SND_ON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/>' +
    '<path d="M18.5 5.5a9 9 0 0 1 0 13"/></svg>';
  const SND_OFF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M16 9.5 21 15"/><path d="M21 9.5 16 15"/></svg>';

  const sndToggle = (label) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'paint-snd';
    b.setAttribute('aria-pressed', String(sound.get()));
    b.setAttribute('aria-label', label || 'Sound');
    b.innerHTML = '<span class="paint-snd-on" aria-hidden="true">' + SND_ON + '</span>' +
      '<span class="paint-snd-off" aria-hidden="true">' + SND_OFF + '</span>' +
      '<span class="paint-snd-t">Sound</span>';
    b.addEventListener('click', () => {
      const next = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', String(next));
      sound.set(next);                      // this click is the gesture
    });
    return b;
  };

  window.oagKit = { rng, sound, sndToggle };
})();

(function () {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];

  const nav = $('.nav');
  const toggle = $('.nav-toggle');
  if (!nav) return;

  const onScroll = () => nav.classList.toggle('scrolled', scrollY > 24);
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  if (toggle) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
    });
    // A link tap closes the panel; so does Escape.
    $$('.nav-links a').forEach(a => a.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }));
    addEventListener('keydown', e => {
      if (e.key !== 'Escape' || !nav.classList.contains('open')) return;
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      toggle.focus();
    });
  }

  // Current page. Hrefs carry the PREFIX the build was run with, and so does
  // location.pathname, so the two compare directly.
  const here = location.pathname.replace(/index\.html$/, '').replace(/\/$/, '') || '/';
  $$('.nav-links a').forEach(a => {
    const p = (a.getAttribute('href') || '').replace(/\/$/, '') || '/';
    if (p === here || (p !== '/' && here.startsWith(p + '/'))) a.classList.add('active');
  });

  const y = $('#year');
  if (y) y.textContent = new Date().getFullYear();
})();

/* =====================================================================
   The motion layer — Roll · Scale · Cure · Live · Brush · Stencil.

   One IntersectionObserver, one class. Nothing in here is load-bearing:
   without it html.motion is absent, nothing is hidden, and the page is the
   page. It returns before touching the DOM unless motion is genuinely on,
   so the reduced-motion render is the same document as the no-script one.
   ===================================================================== */
(function () {
  const root = document.documentElement;
  const motion = root.classList.contains('motion');
  let reduced = false;
  try { reduced = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (!motion || reduced) return;

  /* The whole film, behind a button.
     The <video> is already in the server HTML with its controls, its poster
     and preload="none", so with no script — and under reduced motion, where
     this block never runs — it is a film a visitor can play with the browser's
     own control, and nothing is fetched until they do. What is added here is
     the one thing that control cannot be: a button the width of the picture,
     in the site's own type, so a still reads as an invitation. It is built
     here rather than in the server HTML because a button that cannot do
     anything is worse than no button — the same reason the paint tin gets its
     role from this file — and that is also why the play glyph lives here and
     not in build.py's ICONS: the element it goes in is built here.
     Splat never sees it. The click mechanic acts on a[href] and on a form's
     submit button, and this is neither. */
  const PLAY = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" '
             + 'focusable="false"><path d="M8 5.2v13.6c0 .9 1 1.5 1.8 1l11-6.8c.7-.5.7-1.5 '
             + '0-1.9l-11-6.8C9 3.7 8 4.3 8 5.2z"/></svg>';
  document.querySelectorAll('[data-film]').forEach(fig => {
    const v = fig.querySelector('video');
    if (!v) return;
    v.controls = false;
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'btn film-play';
    b.innerHTML = PLAY + 'Watch the film';
    b.addEventListener('click', () => {
      // Pressed by a person, so the sound is allowed — which is the point of
      // this and not of the muted loop at the top of the page.
      v.controls = true;
      v.preload = 'auto';
      v.play().catch(() => { v.controls = true; });
      b.remove();
    });
    fig.appendChild(b);
  });

  /* The hero clip. It has the autoplay attribute, so it starts on its own
     where the browser allows; this is the nudge for the ones that wait for
     a script, and the one place data-saver is honoured: on a metered
     connection the still stays and the clip never loads.
     Which file it is playing was settled before this ran: the rendition is
     picked by the one-line script the page writes after each element, while
     the parser is still standing there (build.py, clip_sources()). Doing it
     here would be too late — the 1080 file would already be on the wire. */
  document.querySelectorAll('video[data-autoplay]').forEach(v => {
    const c = navigator.connection;
    if (c && c.saveData) { v.removeAttribute('autoplay'); v.preload = 'none'; return; }
    v.muted = true;
    v.play().catch(() => {});
  });

  /* --- Live: the figures as mechanical counters ----------------------
     Owner: "Try to animate the numbers on his site ... I'd like him to see
     motion as he scrolls up and down from them."

     Every figure on the site — the stats band and every .dims — is real
     text in the server HTML and stays real text: this walks the text nodes
     that carry digits and lays a column of 0-9 over each digit, keeping the
     original characters in place underneath as the thing that sizes the
     box. Nothing moves the mint prime marks or the times sign; they are
     their own spans and are never touched.

     The box is the ghost's box, so there is no layout shift whatever the
     column does: the columns are absolutely positioned over it, each one a
     grid of ten cells exactly one window tall, and the roll is one
     translateY of a whole number of windows. Speed scales with the figure
     (five digits ~1.1s, one digit ~.4s) and the digits start right to left,
     the way a counter's wheels turn.                                      */
  const STAG = 0.04;                 // between one wheel and the next
  // How long a figure's wheels take, which is also when Stencil sprays it.
  const stRoll = new Map();
  const rollUp = (host) => {
    [...host.childNodes].forEach(node => {
      if (node.nodeType !== 3 || !/[0-9]/.test(node.nodeValue)) return;
      const text = node.nodeValue;
      let n = 0;
      for (const ch of text) if (ch >= '0' && ch <= '9') n++;
      const span = (cls) => {
        const s = document.createElement('span');
        s.className = cls;
        return s;
      };

      const wrap = span('roll');
      wrap.setAttribute('data-live', '');
      const ghost = span('roll-g');
      ghost.textContent = text;      // the real figure, and the real box
      const cols = span('roll-w');
      cols.setAttribute('aria-hidden', 'true');

      // The whole roll lands in `all`, and the wheel on the right sets off
      // first, so each wheel's own turn is shortened by the stagger ahead
      // of it rather than the figure taking longer the wider it is.
      const all = Math.min(1.2, 0.4 + 0.175 * (n - 1));
      const each = Math.max(0.28, all - STAG * (n - 1));
      // A figure is as slow as its slowest half: 81' x 80' rolls two wheels
      // twice and lands once.
      const fig = host.closest('.dims') || host;
      stRoll.set(fig, Math.max(stRoll.get(fig) || 0, Math.round(all * 1000)));
      let right = n;                 // wheels still to this one's right
      for (const ch of text) {
        if (ch < '0' || ch > '9') { const s = span('roll-x'); s.textContent = ch; cols.appendChild(s); continue; }
        right--;
        const win = span('roll-d'), col = span('roll-c');
        col.setAttribute('style',
          `--v:${ch};--rt:${each.toFixed(3)}s;--rd:${(right * STAG).toFixed(3)}s`);
        for (let d = 0; d < 10; d++) {
          const cell = document.createElement('span');
          cell.textContent = String(d);
          col.appendChild(cell);
        }
        win.appendChild(col);
        cols.appendChild(win);
      }
      wrap.appendChild(ghost);
      wrap.appendChild(cols);
      node.parentNode.replaceChild(wrap, node);
    });
  };
  document.querySelectorAll('.stat-n,.dims .n').forEach(rollUp);

  /* --- Live: the cards -----------------------------------------------
     Owner: "add more motion to the cards".

     Three things, all composed on top of the hover the card already has
     (mint hairline, photograph to 1.04) rather than replacing any of it:
     the photograph drifts inside its frame with where the card is on the
     screen, the card rises into place coming up and settles back going
     out, and on a desktop it tilts a few degrees toward the pointer.

     One passive scroll listener and one rAF for the whole of it, and the
     only cards measured are the ones the observer says are on screen. The
     frame reads every box first and writes every property after, so a
     hundred feet of scrolling is still one layout pass.                  */
  const cards = new Set(), glows = new Set(), rules = new Map();
  let frame = 0, tiltEl = null, tiltX = 0, tiltY = 0;

  // Where a box sits on the screen: -1 at the top, 0 dead centre, +1 at
  // the bottom. Both the drift and the glow are this one number.
  const place = (r, H) => (r.top + r.height / 2 - H / 2) / ((H + r.height) / 2);

  /* --- Brush: the rule his three stages sit on -----------------------
     Owner: "Add an animated paintbrush in more places on his site."

     One number, --paint, from 0 to 1: how much of the mint rule has been
     painted. The stylesheet scales the rule by it and carries the brush
     along the leading edge by it, so there is nothing to keep in step.

     0 is the rule crossing the bottom of the window — 94% of it, which is
     where the observer below starts calling, so the first frame is 0 and
     not a jump — and 1 is a rule finished while the last stage is still on
     screen: the travel is the list's own height plus a fifth of a window,
     held between .45 and .8 of a window so that a long list on a phone
     still finishes with the brush in front of the visitor rather than
     somewhere above the top of the screen.

     Scrolling back up runs the same sum backwards, which is the whole of
     the un-painting: this is Live behaviour, not a one-shot reveal.

     Each stage takes the Cure sheen as the brush goes over it — the middle
     of its share of the rule, which on the Home row is the middle of its
     column and in the About column is simply its turn. .cured is the
     state, .curing is the pass: taking it off, reading a box to force the
     style through, and putting it back is what makes the sheen run again
     on the way back past. It happens three times a pass at most.       */
  const brushTo = (el, beats, r, H) => {
    const travel = Math.max(H * 0.45, Math.min(H * 0.8, r.height + H * 0.2));
    const p = Math.max(0, Math.min(1, (H * 0.94 - r.top) / travel));
    el.style.setProperty('--paint', p.toFixed(4));
    beats.forEach((b, i) => {
      const past = p >= (i + 0.5) / beats.length;
      if (past === b.classList.contains('cured')) return;
      b.classList.toggle('cured', past);
      b.classList.remove('curing');
      void b.offsetWidth;
      b.classList.add('curing');
    });
  };

  const paint = () => {
    frame = 0;
    const H = innerHeight || 1;
    // Every box is read before anything is written: one layout pass, no
    // matter how many cards and glows are on screen.
    const read = [], lit = [], painting = [];
    cards.forEach(c => read.push([c, place(c.getBoundingClientRect(), H)]));
    glows.forEach(g => lit.push([g, place(g.getBoundingClientRect(), H)]));
    rules.forEach((beats, el) => painting.push([el, beats, el.getBoundingClientRect()]));

    read.forEach(([c, p]) => {
      // The photograph lags the frame: as the card rides up the screen the
      // picture slides down inside it. That is the whole of the depth.
      c.style.setProperty('--drift', (-Math.max(-1, Math.min(1, p))).toFixed(3));
    });
    /* One glow at a time, and it is the rule rather than an accident of
       where the sections fell: the one nearest the middle of the screen is
       lit and every other one on screen is put out. It is brightest as its
       section centres and gone by the time it is half a screen away. */
    let near = null, best = Infinity;
    lit.forEach(([g, p]) => { if (Math.abs(p) < best) { best = Math.abs(p); near = g; } });
    lit.forEach(([g, p]) => {
      const v = g === near ? Math.max(0, 1 - Math.abs(p) * 1.3) : 0;
      g.style.setProperty('--g', v.toFixed(3));
    });

    painting.forEach(([el, beats, r]) => brushTo(el, beats, r, H));

    if (tiltEl) {
      tiltEl.style.setProperty('--ry', tiltX.toFixed(2) + 'deg');
      tiltEl.style.setProperty('--rx', tiltY.toFixed(2) + 'deg');
      tiltEl = null;
    }
  };
  const pump = () => { if (!frame) frame = requestAnimationFrame(paint); };
  addEventListener('scroll', pump, { passive: true });
  addEventListener('resize', pump, { passive: true });

  /* The tilt is a desktop thing only: a finger is already on the card it
     is tilting, and a phone has the drift. Four degrees is the cap. */
  let fine = false;
  try { fine = matchMedia('(hover:hover) and (pointer:fine)').matches; } catch (e) {}
  if (fine) document.querySelectorAll('.pcard[data-live]').forEach(c => {
    const aim = (e) => {
      const r = c.getBoundingClientRect();
      if (!r.width || !r.height) return;
      tiltEl = c;
      tiltX = ((e.clientX - r.left) / r.width - 0.5) * 8;      // toward the pointer
      tiltY = -((e.clientY - r.top) / r.height - 0.5) * 8;
      pump();
    };
    c.addEventListener('pointerenter', e => {
      if (e.pointerType === 'touch') return;
      c.classList.add('is-tilt');
      aim(e);
    });
    c.addEventListener('pointermove', e => { if (c.classList.contains('is-tilt')) aim(e); });
    c.addEventListener('pointerleave', () => {
      c.classList.remove('is-tilt');
      if (tiltEl === c) tiltEl = null;
      c.style.removeProperty('--rx');
      c.style.removeProperty('--ry');
    });
  });

  /* --- Roll it in: the pointer over a grid is a roller ----------------
     Concept 2. Over the project grids the pointer stops being a pointer
     and becomes the roller itself — not a second drawing of one: the
     <symbol> build.py put in the page (roller_sprite()) is serialised at
     40 px into a data URI, so the roller the pointer wears and the roller
     that will ride the card are one drawing. The hotspot is the nap —
     69.8% across and 66.9% down its box, which is art.py's contact point
     — so the paint lands under the nap rather than under the handle.

     Desktop only, and only while there is something left to paint: a
     finger has no cursor to change, and a wall that is painted does not
     want a roller held over it. `pointer` is the fallback, so a browser
     that will not take an SVG cursor still says the card is a link.   */
  const RCUR = 40;                     // how big the cursor is drawn, in px
  const sprite = document.getElementById('oa-roller');
  const grids = [...document.querySelectorAll('.pgrid')];
  let rollerCursor = '';
  if (fine && sprite && grids.length) {
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="'
      + RCUR + '" height="' + RCUR + '">' + sprite.innerHTML + '</svg>';
    rollerCursor = 'url("data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg)
      + '") ' + Math.round(RCUR * 0.698) + ' ' + Math.round(RCUR * 0.669) + ', pointer';
  }
  const wearRoller = (on) => grids.forEach(g => {
    if (on && rollerCursor) g.style.cursor = rollerCursor;
    else g.style.removeProperty('cursor');
  });
  wearRoller(true);

  /* --- Roll it in: the primer, and the pass that takes it off --------
     The stylesheet primes every photograph on a card from the first
     paint. This is the pass that takes the primer off, and the first
     thing it does is say so: .rollin on <html> calls off the 2.8s
     bail-out the primer carries, so a page whose script never arrives
     lifts the primer by itself instead of stranding the murals under it.

     The wipe wants two layers and the page has one, so the unprimed copy
     is cloned here rather than sent twice down the wire: a crawler is
     never handed the same mural with two alts, and the document without
     a script is the document it was before this existed. The clone is
     masked from nothing to the full card; the photograph underneath it
     loses the primer the moment the pass is over and the clone goes in
     the same frame, which is the same pixels either side of the swap.

     Every card rolls itself in as it arrives, on a desktop as much as on
     a phone: a portfolio can never sit whitewashed waiting for a hover
     that may never come, so the stagger is what paints the wall and the
     hover is only ever a shortcut. The cards enter the queue as the
     observer sees them and go 120ms apart, the first of a run after a
     350ms grace — long enough that a pointer already resting on a card
     when the grid arrives paints that one first, under the roller
     cursor, which is the beat worth having.

     Hover and focus therefore call roll() straight out, ahead of the
     queue; the card's own timer finds it already claimed and returns.
     Once a card is claimed it is never claimed again: this is Roll,
     which runs once, and not Live, which runs both ways. And because
     everything is painted in the end, the roller cursor is a passing
     thing — the pointer is handed back the moment the last card lands. */
  const ROLL = 600, STAGGER = 120, GRACE = 350;
  const pcards = [...document.querySelectorAll('.pcard')];
  let unpainted = pcards.length, nextAt = 0;
  if (pcards.length) {
    root.classList.add('rollin');
    pcards.forEach(card => {
      const base = card.querySelector('.pcard-img picture');
      if (!base) return;
      const paint = base.cloneNode(true);
      paint.classList.add('pcard-paint');
      paint.setAttribute('aria-hidden', 'true');
      paint.querySelectorAll('img').forEach(im => { im.alt = ''; });
      base.after(paint);
    });
  }

  // roll() is the only door, and it is one-way: hover, focus and the
  // card's own place in the queue all come through it, and whichever
  // arrives first is the one that paints.
  const roll = (card) => {
    if (card.dataset.rollin) return;
    card.dataset.rollin = '1';
    card.classList.add('rolling');
    setTimeout(() => {
      card.classList.add('painted');        // the primer comes off
      card.classList.remove('rolling');
      const paint = card.querySelector('.pcard-paint');
      if (paint) paint.remove();
      // A wall with nothing left to paint hands the pointer back.
      if (--unpainted <= 0) wearRoller(false);
    }, ROLL + 60);
  };
  const queue = (card) => {
    if (card.dataset.rollq) return;       // already waiting its turn
    card.dataset.rollq = '1';
    const now = performance.now();
    const at = Math.max(now + GRACE, nextAt);
    nextAt = at + STAGGER;
    setTimeout(() => roll(card), at - now);
  };
  pcards.forEach(card => {
    if (fine) card.addEventListener('pointerenter', (e) => {
      if (e.pointerType !== 'touch') roll(card);
    });
    card.addEventListener('focus', () => roll(card));
  });

  /* --- Stencil: the feet are sprayed on ------------------------------
     The site's hook is 81' x 80', and a figure that big should arrive the
     way it arrives on a wall: a stencil card comes down over it, the paint
     goes through the cut, the card lifts off, and the overspray stays.

     The cut is the figure's own glyphs and never a drawing of digits.
     Every run of text on the line — the ghost inside each rolling column,
     the mint prime marks, the times sign — is measured where it actually
     sits and laid into an SVG <mask> in the same font at the same size and
     the same width axis, cut a hair wide the way a stencil is cut so that
     nothing of the figure ever catches on its edge. The baseline comes
     from a probe: a zero-height inline-block stands its bottom edge on the
     baseline it is in, and it is out again before the next frame.

     The order is what makes it compose. .st goes on first, which snaps
     Scale's width axis to its end value (under the card, where it was
     going anyway) and takes the rolling columns out of sight; the card is
     measured against that, so the cut is true. Then the wheels are started
     and the card comes down over them — the roll happens under the
     stencil, and the spray is the moment the columns land. Cure is timed
     by --st-cure rather than by hand, so the sheen sets off as the card is
     lifted, and a figure that never gets a stencil still cures at the .4s
     it always did.

     What it leaves is a text-shadow and nothing else. The tags' own spray
     filter is on the halo for the moment the can is open and off it again
     when the paint is dry, so no live feTurbulence is ever left on a
     settled page.                                                       */
  const ST_HOLD = 120, ST_LIFT = 220, ST_SETTLE = 60, ST_AGAIN = 200;
  const figures = [...document.querySelectorAll('.dims,.stat-n')];
  // Spray's halo wears the same aerosol, so the band asks for it here
  // rather than defining a second copy of the same filter further down.
  const spBands = [...document.querySelectorAll('.spray-band[data-spray]')];
  if (figures.length || spBands.length) {
    // wall.py's aerosol, in the one place off the wall that needs it:
    // turbulence displaces the halo by a few units and a hair of blur takes
    // the vector edge off it, which is the difference between a can and a
    // shape tool. It is a definition, not a filter on anything — what wears
    // it wears it for 380ms and hands it back.
    const defs = document.createElement('div');
    defs.innerHTML =
      '<svg class="st-defs" aria-hidden="true" focusable="false">' +
      '<filter id="oa-spray" x="-30%" y="-30%" width="160%" height="160%" ' +
      'color-interpolation-filters="sRGB">' +
      '<feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="2" seed="5" result="t"/>' +
      '<feDisplacementMap in="SourceGraphic" in2="t" scale="6" ' +
      'xChannelSelector="R" yChannelSelector="G"/>' +
      '<feGaussianBlur stdDeviation="1.1"/></filter></svg>';
    document.body.appendChild(defs.firstElementChild);
  }

  const esc = (t) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  let stN = 0;

  // Every run of glyphs on the figure's line: what it says, where it starts
  // and the baseline it stands on.
  const stRuns = (fig) => {
    const out = [];
    const probe = document.createElement('i');
    probe.className = 'st-probe';
    fig.querySelectorAll('.roll-g,.f,.x').forEach(el => {
      const t = el.textContent;
      if (!t) return;
      el.appendChild(probe);
      const base = probe.getBoundingClientRect().top;
      probe.remove();
      const r = el.getBoundingClientRect();
      out.push({ t, x: r.left, y: base, s: getComputedStyle(el) });
    });
    return out;
  };

  // The card and the halo, cut and hung for the figure as it is right now.
  // Both are built fresh every time, so a figure resprayed at another size
  // is cut again at that size rather than wearing the old cut.
  const stBuild = (fig) => {
    [...fig.children].forEach(n => {
      if (n.classList.contains('st-card') || n.classList.contains('st-halo')) n.remove();
    });
    const runs = stRuns(fig);
    if (!runs.length) return false;
    const r = fig.getBoundingClientRect();
    const fs = parseFloat(getComputedStyle(fig).fontSize) || 16;
    const px = Math.max(16, fs * 0.22), py = Math.max(14, fs * 0.34);
    const w = Math.round(r.width + px * 2), h = Math.round(r.height + py * 2);
    if (!w || !h) return false;
    const id = 'oa-st-' + (++stN);
    const dil = (fs * 0.045).toFixed(2);        // the cut, a hair wide
    const cut = runs.map(g =>
      '<text x="' + (g.x - r.left + px).toFixed(2) + '" y="' + (g.y - r.top + py).toFixed(2) +
      '">' + esc(g.t) + '</text>').join('');

    const card = document.createElement('span');
    card.className = 'st-card';
    card.setAttribute('aria-hidden', 'true');
    card.style.cssText = 'left:' + (-px).toFixed(1) + 'px;top:' + (-py).toFixed(1) +
                         'px;width:' + w + 'px;height:' + h + 'px';
    card.innerHTML =
      '<svg viewBox="0 0 ' + w + ' ' + h + '" focusable="false">' +
        '<defs>' +
          '<linearGradient id="' + id + '-g" x1="0" y1="0" x2="0" y2="1">' +
            '<stop offset="0" class="st-s0"/><stop offset="1" class="st-s1"/>' +
          '</linearGradient>' +
          '<mask id="' + id + '" maskUnits="userSpaceOnUse" x="0" y="0" ' +
                'width="' + w + '" height="' + h + '">' +
            '<rect width="' + w + '" height="' + h + '" fill="white"/>' +
            '<g fill="black" stroke="black" stroke-width="' + dil +
               '" stroke-linejoin="round">' + cut + '</g>' +
          '</mask>' +
          // and the cut on its own, which is where the card's own shadow
          // falls: a stencil is held a little off the wall, so what shows
          // through it is always darker than the wall beside it.
          '<mask id="' + id + '-c" maskUnits="userSpaceOnUse" x="0" y="0" ' +
                'width="' + w + '" height="' + h + '">' +
            '<g fill="white" stroke="white" stroke-width="' + dil +
               '" stroke-linejoin="round">' + cut + '</g>' +
          '</mask>' +
        '</defs>' +
        '<rect class="st-cut" width="' + w + '" height="' + h + '" mask="url(#' + id + '-c)"/>' +
        '<g mask="url(#' + id + ')">' +
          '<rect width="' + w + '" height="' + h + '" rx="2" fill="url(#' + id + '-g)"/>' +
          '<rect class="st-edge" x=".5" y=".5" width="' + (w - 1) + '" height="' + (h - 1) + '" rx="1.6"/>' +
        '</g>' +
      '</svg>';
    // The type is set on the nodes rather than written into the string: a
    // font stack carries quotation marks of its own, and a style attribute
    // built out of them is a style attribute that ends early.
    card.querySelectorAll('mask text').forEach((t, i) => {
      const s = runs[i % runs.length].s;
      t.style.fontFamily = s.fontFamily;
      t.style.fontSize = s.fontSize;
      t.style.fontWeight = s.fontWeight;
      t.style.fontStyle = s.fontStyle;
      t.style.fontVariationSettings = s.fontVariationSettings;
      t.style.letterSpacing = s.letterSpacing;
    });

    // The halo is the figure again, with the ink taken out of it: the text
    // is the site's own text at the site's own size, so the overspray can
    // never come away from the glyphs it belongs to.
    const halo = document.createElement('span');
    halo.className = 'st-halo';
    halo.setAttribute('aria-hidden', 'true');
    [...fig.children].forEach(ch => {
      const c = ch.cloneNode(true);
      c.removeAttribute('data-live');
      c.querySelectorAll('[data-live]').forEach(n => n.removeAttribute('data-live'));
      halo.appendChild(c);
    });
    fig.appendChild(card);
    fig.appendChild(halo);
    return true;
  };

  const stSpray = (fig, first) => {
    if (fig.dataset.spray) return;              // one can at a time
    const rolls = first ? [...fig.querySelectorAll('.roll')] : [];
    fig.dataset.spray = '1';
    const wait = first ? Math.max(ST_AGAIN, stRoll.get(fig) || 0) : ST_AGAIN;
    fig.style.setProperty('--st-cure', (wait + ST_HOLD) + 'ms');
    fig.classList.remove('st-done');
    fig.classList.add('st');
    if (!stBuild(fig)) {                        // nothing to cut: leave it alone
      fig.classList.remove('st');
      fig.style.removeProperty('--st-cure');
      delete fig.dataset.spray;
      return;
    }
    void fig.offsetWidth;                       // the card starts above the wall
    fig.classList.add('st-in');
    rolls.forEach(w => w.classList.add('in'));  // the wheels turn under it
    const halo = fig.querySelector('.st-halo');
    setTimeout(() => {
      fig.classList.add('st-spray');            // the columns have landed
      if (halo) halo.style.filter = 'url(#oa-spray)';
      setTimeout(() => {
        fig.classList.remove('st');             // Cure is already timed to here
        fig.classList.add('st-lift');
        setTimeout(() => {
          fig.classList.remove('st-in', 'st-spray', 'st-lift');
          fig.classList.add('st-done');         // the halo settles
          if (halo) halo.style.filter = '';     // and nothing is filtered again
          const c = fig.querySelector('.st-card');
          if (c) c.remove();
          delete fig.dataset.spray;
        }, ST_LIFT + ST_SETTLE);
      }, ST_HOLD);
    }, wait);
  };

  /* A respray is the same sequence without the wheels: the figure is at its
     value already, so the card comes down, the paint goes back through it
     and it lifts. A pointer that can hover gets it on the way in; a finger
     gets it on the way down, and never at the cost of the tap itself — the
     figures on a card sit inside a link, and that link still navigates. */
  figures.forEach(f => {
    if (fine) f.addEventListener('pointerenter', e => {
      if (e.pointerType !== 'touch') stSpray(f, false);
    });
    else f.addEventListener('pointerdown', () => stSpray(f, false));
  });

  /* --- Spray: a can writes the wordmark ------------------------------
     Owner: "Is there any way to have a can of spray paint spray 'Open Air
     Gallery' underneath the hero as a section builder?"

     The band, the word and the can are all in the server HTML (build.py
     spray_band()). What is built here is the two things that have to be
     measured: the overspray halo, which is a clone of the word with the
     ink taken out of it so the halo can never come away from the glyphs
     it belongs to, and the runs of paint, which are hung off the bottom
     of particular letters and so have to be asked where those letters
     actually are.

     Nothing here drives the pass frame by frame. The can and the wet edge
     carry the same CSS animation on the same clock — the stylesheet has
     the why — and this only says go, puts the aerosol filter on the halo
     while the can is open, starts a run of paint as the nozzle goes past
     the letter it comes off, and takes the filter off again at the end.

     The letters are measured with a Range rather than by wrapping every
     glyph in a span: a range over one character reports exactly where
     that character is without changing the document, which keeps the word
     one text node and the no-script render the render it always was.

     It sprays once on the way in, like Roll rather than like Live. A
     hover on a fine pointer and a tap on a coarse one spray it again, and
     the band is not a link, so a tap costs nothing.                    */
  const SP_T = 2050, SP_WRITE = 0.24, SP_DRIP = 640, SP_SEEN = 0.5, SP_HEAVY = 'OAG';
  const spKit = window.oagKit;

  const spBuild = (band) => {
    if (band.dataset.spBuilt) return true;
    const word = band.querySelector('.spray-word');
    if (!word) return false;
    const halo = word.cloneNode(true);
    halo.classList.add('spray-halo');
    halo.setAttribute('aria-hidden', 'true');
    word.after(halo);
    band.dataset.spBuilt = '1';
    band.style.setProperty('--sp-t', SP_T + 'ms');
    return true;
  };

  /* Where the runs go: the heaviest letters on each line — O, A and G —
     at most two to a line and never two within a third of the word of
     each other, so three drips are spread across the band rather than
     bunched at its left edge. A drip off a line that is not the last one
     is half the length: it has the next line under it. */
  const spDrips = (band) => {
    const stage = band.querySelector('.spray-stage');
    const word = band.querySelector('.spray-word');
    if (!stage || !word) return [];
    stage.querySelectorAll('.spray-drip').forEach(n => n.remove());
    const sr = stage.getBoundingClientRect();
    if (!sr.width) return [];
    const fs = parseFloat(getComputedStyle(word).fontSize) || 16;
    const w = Math.max(2, fs * 0.036);
    const lines = [...word.children];
    const probe = document.createElement('i');
    probe.className = 'st-probe';
    const out = [];
    lines.forEach((line, li) => {
      const node = line.firstChild;
      if (!node || node.nodeType !== 3) return;
      const t = node.nodeValue;
      const last = li === lines.length - 1;
      // Where the letters actually stand. A range rect is the line's box,
      // which on a face set at .92 line-height is nowhere near the feet of
      // the glyphs; a zero-height inline-block stands its bottom edge on
      // the baseline, which is the only way to ask the page where one is —
      // the same probe Stencil measures its cut from.
      line.appendChild(probe);
      const base = probe.getBoundingClientRect().bottom - sr.top;
      probe.remove();
      let took = 0, prev = -1e9;
      for (let i = 0; i < t.length && took < 2; i++) {
        if (SP_HEAVY.indexOf(t[i].toUpperCase()) < 0) continue;
        const rg = document.createRange();
        rg.setStart(node, i); rg.setEnd(node, i + 1);
        const r = rg.getBoundingClientRect();
        if (!r.width) continue;
        const x = r.left + r.width / 2 - sr.left;
        if (x - prev < sr.width * 0.33) continue;
        prev = x; took++;
        out.push({ x, y: base - fs * 0.05, len: fs * (last ? 0.3 : 0.17) });
      }
    });
    const drips = out.slice(0, 3);
    drips.forEach(d => {
      const el = document.createElement('span');
      el.className = 'spray-drip';
      el.setAttribute('aria-hidden', 'true');
      el.style.cssText = 'left:' + (d.x - w / 2).toFixed(1) + 'px;top:' + d.y.toFixed(1) +
        'px;--dw:' + w.toFixed(1) + 'px;--dh:' + d.len.toFixed(1) + 'px;--dt:' + SP_DRIP + 'ms';
      el.innerHTML = '<i class="spray-run"></i><i class="spray-bead"></i>';
      stage.appendChild(el);
      d.el = el;
      d.at = SP_T * (SP_WRITE + (1 - SP_WRITE) * Math.min(1, d.x / sr.width)) + 200;
    });
    return drips;
  };

  const spSpray = (band) => {
    if (band.dataset.spraying) return;           // one can at a time
    if (!spBuild(band)) return;
    band.dataset.spraying = '1';
    (band.oaSpT || []).forEach(clearTimeout);
    band.oaSpT = [];
    band.classList.remove('spray-go', 'spray-done');
    void band.offsetWidth;                       // a respray starts over
    const drips = spDrips(band);
    const halo = band.querySelector('.spray-halo');
    band.classList.add('spray-go');
    if (halo) halo.style.filter = 'url(#oa-spray)';
    // Muted is the default and the state is the one the wall and the
    // washer already persist: this asks, it never turns anything on.
    if (spKit) spKit.sound.rattle();
    band.oaSpT.push(setTimeout(() => {
      if (spKit) { spKit.sound.canOn(); spKit.sound.canAt(0.62); }
    }, SP_T * SP_WRITE));
    drips.forEach(d => band.oaSpT.push(setTimeout(() => d.el.classList.add('run'), d.at)));
    band.oaSpT.push(setTimeout(() => {
      band.classList.remove('spray-go');
      band.classList.add('spray-done');          // the halo settles
      if (halo) halo.style.filter = '';          // and nothing is filtered again
      if (spKit) spKit.sound.canOff();
      delete band.dataset.spraying;
    }, SP_T));
  };

  spBands.forEach(b => {
    spBuild(b);
    if (fine) b.addEventListener('pointerenter', e => {
      if (e.pointerType !== 'touch') spSpray(b);
    });
    else b.addEventListener('pointerdown', () => spSpray(b));
  });

  const targets = [...document.querySelectorAll('.rv,.dims,.stat-n')];
  const live = [...document.querySelectorAll('[data-live]')];
  const glowing = [...document.querySelectorAll('[data-glow]')];
  const painted = [...document.querySelectorAll('[data-brush]')];
  const reels = [...document.querySelectorAll('video[data-inview]')];
  const reelLive = new Set();   // the reels this script actually took over
  if (!targets.length && !live.length && !glowing.length && !painted.length
      && !spBands.length && !reels.length) return;

  // No observer means no way to unhide: show everything now rather than
  // making the visitor wait for the 2.8s self-reveal. A live element with
  // no observer is simply at its value, which is what the page says.
  if (!('IntersectionObserver' in window)) {
    targets.concat(live).forEach(el => el.classList.add('in'));
    glowing.forEach(g => g.style.setProperty('--g', '.45'));   // the mid value
    painted.forEach(el => el.style.setProperty('--paint', '1'));  // the rule, painted
    spBands.forEach(b => b.classList.add('spray-done'));         // the word, sprayed
    // A reel keeps its controls: with no observer there is nothing to tell
    // it when it is on screen, and a clip that can only be watched by
    // scrolling luck is worse than one with a play button on it.
    return;
  }

  /* The progress reel. It is in the server HTML with `controls` on it and no
     autoplay, because that is the render a visitor gets with no script or with
     reduced motion asked for, and there it has to be something they can play.
     Here — html.motion, an observer, and not a metered connection — the
     controls come off and the clip runs itself while it is on screen. It is
     the same rule the hero clip follows on data-saver: the poster stays and
     nothing is fetched. */
  reels.forEach(v => {
    const c = navigator.connection;
    if (c && c.saveData) { v.preload = 'none'; return; }
    v.controls = false;
    v.removeAttribute('controls');
    v.muted = true;
    reelLive.add(v);
  });

  /* One observer, two contracts. A .rv or a .dims is revealed once and let
     go — Roll and Cure do not repeat. An element marked data-live is never
     unobserved: it takes .in on the way in and loses it on the way out,
     every time, because the owner asked to see motion scrolling up as well
     as down. LIVE is the share of it that has to be on screen to count; the
     .12 below is the reveal threshold this observer has always used, kept
     as a floor so the reveals fire exactly where they fired before. */
  const LIVE = 0.35;
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    const el = e.target;
    if (el.hasAttribute('data-inview')) {
      // Plays while it is on screen and stops when it is not, both ways,
      // like the rest of Live — a clip running behind the visitor's back is
      // battery spent on something nobody is watching. A reel left with its
      // controls (data-saver) is not in reelLive and is not touched.
      if (!reelLive.has(el)) return;
      if (e.intersectionRatio >= LIVE) el.play().catch(() => {});
      else el.pause();
      return;
    }
    if (el.hasAttribute('data-glow')) {
      if (e.isIntersecting) glows.add(el);
      else { glows.delete(el); el.style.setProperty('--g', '0'); }
      pump();
      return;
    }
    if (el.hasAttribute('data-spray')) {
      // Spray runs once on the way in, the way Roll does: it is the
      // wordmark arriving, not something that replays as the page moves.
      // Half the band rather than the eighth the reveals use, because the
      // top of a band is its padding: an eighth of it can be showing under
      // a hero with the word itself still below the fold, and a wordmark
      // written where nobody is looking has not been written at all.
      if (e.isIntersecting && e.intersectionRatio >= SP_SEEN) {
        spSpray(el);
        io.unobserve(el);
      }
      return;
    }
    if (el.hasAttribute('data-brush')) {
      // The rect the observer already measured lands the rule exactly on 0
      // or 1 as it leaves, so a section scrolled past is finished and one
      // scrolled off the bottom is bare.
      const beats = rules.get(el) || [...el.querySelectorAll('.beat')];
      brushTo(el, beats, e.boundingClientRect, innerHeight || 1);
      if (e.isIntersecting) rules.set(el, beats); else rules.delete(el);
      pump();
      return;
    }
    if (el.hasAttribute('data-live')) {
      // A card is a reveal as well as a live thing. Roll still runs once,
      // at the threshold it has always run at, and .rolled is what holds
      // it open afterwards — .in comes and goes underneath it.
      if (e.intersectionRatio >= 0.12 && el.classList.contains('rv')) el.classList.add('rolled');
      // Roll it in: a card is queued as it arrives and the next one
      // 120ms behind it, on every pointer — the wall paints itself and
      // a hover only ever gets there first.
      if (e.intersectionRatio >= 0.12 && el.classList.contains('pcard')) queue(el);
      el.classList.toggle('in', e.intersectionRatio >= LIVE);
      if (el.classList.contains('pcard')) {
        if (e.isIntersecting) cards.add(el); else cards.delete(el);
        pump();
      }
      return;
    }
    if (!e.isIntersecting || e.intersectionRatio < 0.12) return;
    el.classList.add('in');
    // Stencil: a figure is sprayed on the first time it is seen, and after
    // that only when the visitor asks for it again.
    if (el.classList.contains('dims') || el.classList.contains('stat-n')) stSpray(el, true);
    io.unobserve(el);                // Cure runs once, and only once
  }), { threshold: [0, 0.12, LIVE, SP_SEEN], rootMargin: '0px 0px -6% 0px' });
  targets.concat(live, glowing, painted, spBands, reels).forEach(el => io.observe(el));
})();

/* =====================================================================
   Swipe rails — the project galleries.

   The rail itself is CSS: a scroll-snap strip you can already throw with a
   finger and walk with the keyboard. This adds the arrows, the dots and a
   mouse drag, all of which the stylesheet keeps behind html.js, so with no
   script there is no control on the page that cannot do anything.
   ===================================================================== */
(function () {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n));

  let smooth = true;
  try { smooth = !matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  $$('[data-swipe]').forEach(sw => {
    const rail = $('[data-rail]', sw);
    if (!rail) return;
    const slides = $$('.swipe-slide', rail);
    const dots = $$('.swipe-dot', sw);
    const prev = $('[data-prev]', sw), next = $('[data-next]', sw);

    // One slide is not a carousel: take the furniture away rather than
    // leave arrows that go nowhere.
    if (slides.length < 2) {
      $$('.swipe-arw,.swipe-dots,.swipe-hint', sw).forEach(el => el.remove());
      return;
    }

    // Where slide i lands once the rail has run out of room to scroll.
    const target = i => {
      const s = slides[i], end = Math.max(0, rail.scrollWidth - rail.clientWidth);
      return clamp(s.offsetLeft - (rail.clientWidth - s.offsetWidth) / 2, 0, end);
    };
    const at = () => {
      let best = 0, bd = Infinity;
      slides.forEach((s, i) => {
        const d = Math.abs(target(i) - rail.scrollLeft);
        if (d < bd) { bd = d; best = i; }
      });
      return best;
    };
    const sync = () => {
      const i = at(), end = rail.scrollWidth - rail.clientWidth;
      sw.classList.toggle('fits', end < 6);   // nothing to swipe: no furniture
      dots.forEach((d, n) => d.classList.toggle('is-on', n === i));
      if (prev) prev.disabled = rail.scrollLeft <= 4;
      if (next) next.disabled = rail.scrollLeft >= end - 4;
    };
    const to = i => rail.scrollTo({
      left: target(clamp(i, 0, slides.length - 1)),
      behavior: smooth ? 'smooth' : 'auto',
    });

    let raf = 0;
    rail.addEventListener('scroll', () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(sync);
    }, { passive: true });
    if (prev) prev.addEventListener('click', () => to(at() - 1));
    if (next) next.addEventListener('click', () => to(at() + 1));
    dots.forEach((d, n) => d.addEventListener('click', () => to(n)));
    rail.addEventListener('keydown', e => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      e.preventDefault();
      to(at() + (e.key === 'ArrowRight' ? 1 : -1));
    });

    // Throw it with a mouse the way a finger already can.
    let down = false, sx = 0, sl = 0, moved = 0;
    rail.addEventListener('pointerdown', e => {
      if (e.pointerType === 'touch' || e.button) return;
      down = true; moved = 0; sx = e.clientX; sl = rail.scrollLeft;
      try { rail.setPointerCapture(e.pointerId); } catch (_) {}
    });
    rail.addEventListener('pointermove', e => {
      if (!down) return;
      const dx = e.clientX - sx;
      moved = Math.abs(dx);
      if (moved > 4) rail.classList.add('dragging');
      rail.scrollLeft = sl - dx;
    });
    const stop = () => {
      if (!down) return;
      down = false;
      rail.classList.remove('dragging');
      if (moved > 4) to(at());
    };
    rail.addEventListener('pointerup', stop);
    rail.addEventListener('pointercancel', stop);
    // A drag that ends on a link must not also count as a click on it.
    rail.addEventListener('click', e => {
      if (moved > 6) { e.preventDefault(); e.stopPropagation(); moved = 0; }
    }, true);

    addEventListener('resize', sync, { passive: true });
    sync();
  });
})();

/* =====================================================================
   The contact form.

   Three states, and the page is complete in all of them:

     endpoint set    POST the fields as JSON, say so, reset the form.
     endpoint unset  hand the message to the visitor's own mail app,
                     addressed to the studio. This is today's state and it
                     needs no account anywhere.
     no script       every field, label and option is in the server HTML and
                     the note under the button gives the address to write to.

   Ported from /root/dronegodmax-src/site/js/site.js:51-73, with two
   differences: an unknown ?service= is ignored rather than added to the
   select — the form offers what the company actually sells — and the
   honeypot is checked before anything leaves the page.
   ===================================================================== */
(function () {
  const form = document.querySelector('#contact-form');
  if (!form) return;
  const $ = (s, c = document) => c.querySelector(s);
  const CFG = window.OAG || {};
  const ENDPOINT = CFG.form || '';
  const TO = CFG.email || '';

  // /contact?service=Graffiti%20removal arrives from the services links and
  // from the graffiti band: choose that option if the form has it.
  const want = (new URLSearchParams(location.search).get('service') || '').trim().toLowerCase();
  const sel = $('#service');
  if (want && sel) {
    const opts = [...sel.options];
    const hit = opts.find(o => o.value.toLowerCase() === want)
             || opts.find(o => o.value.toLowerCase().startsWith(want));
    if (hit) hit.selected = true;
  }

  const status = $('.form-status');
  const say = (h) => { if (status) { status.innerHTML = h; status.classList.add('on'); } };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(form).entries());
    if (d._gotcha) return;                 // a robot filled the hidden field
    delete d._gotcha;

    const subject = `[Open Air Gallery] ${d.service || 'Enquiry'} — ${d.name || ''}`.trim();
    const body = [
      `Name: ${d.name || '-'}`,
      `Email: ${d.email || '-'}`,
      `Phone: ${d.phone || '-'}`,
      `Company: ${d.company || '-'}`,
      `Location: ${d.location || '-'}`,
      `Service: ${d.service || '-'}`,
      `Budget: ${d.budget || '-'}`,
      '',
      d.message || '',
    ].join('\n');

    if (ENDPOINT) {
      try {
        const r = await fetch(ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({ ...d, _subject: subject }),
        });
        if (r.ok) { say('Message sent. We will come back to you shortly.'); form.reset(); return; }
      } catch (_) {}
    }
    location.href = `mailto:${TO}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    say(`Your email app should open with the brief ready to send. If it did not, write to <a href="mailto:${TO}">${TO}</a> directly.`);
  });
})();

/* =====================================================================
   Before / after — the mint divider.

   The component is complete without this: two labelled pictures side by
   side in the server HTML (css/site.css, ".ba"). Everything here does is
   turn that pair into one frame with a divider across it, so it is gated
   on html.motion exactly like the Wash mechanic on the same page — a
   visitor who has asked for reduced motion, or whose script never
   arrived, reads the two walls side by side instead, which is the same
   information with nothing hidden.

   One pointer handler, one rAF, one custom property. The divider is a
   real <button>: the arrow keys walk it, Home and End take it to the
   ends, and setPointerCapture means a drag that leaves the frame keeps
   working until the finger or the mouse comes up. No number is ever
   shown — the wall does the talking.
   ===================================================================== */
(function () {
  const root = document.documentElement;
  if (!root.classList.contains('motion')) return;
  let reduced = false;
  try { reduced = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (reduced) return;

  const clamp = (n) => Math.min(1, Math.max(0, n));

  [...document.querySelectorAll('[data-ba]')].forEach(ba => {
    const stage = ba.querySelector('[data-ba-stage]');
    const handle = ba.querySelector('[data-ba-handle]');
    if (!stage || !handle) return;

    let x = 0.5, raf = 0;
    const paint = () => { raf = 0; stage.style.setProperty('--bx', (x * 100).toFixed(2) + '%'); };
    const set = (v) => { x = clamp(v); if (!raf) raf = requestAnimationFrame(paint); };
    const fromEvent = (e) => {
      const r = stage.getBoundingClientRect();
      if (r.width) set((e.clientX - r.left) / r.width);
    };

    let dragging = false;
    stage.addEventListener('pointerdown', e => {
      if (e.button) return;
      dragging = true;
      stage.classList.add('is-live');
      try { stage.setPointerCapture(e.pointerId); } catch (_) {}
      fromEvent(e);
      e.preventDefault();          // no text selection, no image drag
    });
    stage.addEventListener('pointermove', e => { if (dragging) fromEvent(e); });
    const stop = (e) => {
      if (!dragging) return;
      dragging = false;
      stage.classList.remove('is-live');
      try { stage.releasePointerCapture(e.pointerId); } catch (_) {}
    };
    stage.addEventListener('pointerup', stop);
    stage.addEventListener('pointercancel', stop);

    handle.addEventListener('keydown', e => {
      const step = { ArrowLeft: -0.02, ArrowRight: 0.02, Home: -1, End: 1 }[e.key];
      if (step === undefined) return;
      e.preventDefault();
      set(Math.abs(step) === 1 ? (step + 1) / 2 : x + step);
    });
  });
})();

/* =====================================================================
   Scale — the six-foot figure, dragged (PLAN.md §4a).

   She is already on the wall: server-rendered at --fx:.12, sized
   (6 / ft) of the picture, captioned "6 ft". That is a static scale bar
   and it is the whole answer with no script. This lets a visitor walk
   her along the baseline, which is the only way to feel how little of
   an eighty-one-foot wall a person is.

   Gated on html.motion, so reduced motion binds nothing and renders the
   static figure — the plan asks for exactly that. One pointer handler
   per figure, one rAF, one custom property, listeners bound only while
   the wall is on screen. Nothing here displays a number.
   ===================================================================== */
(function () {
  const root = document.documentElement;
  if (!root.classList.contains('motion')) return;
  let reduced = false;
  try { reduced = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (reduced) return;

  const figures = [...document.querySelectorAll('[data-scale]')];
  if (!figures.length) return;

  const clamp = (n) => Math.min(1, Math.max(0, n));

  // Tilt is an extra on a phone that already has the drag, so it is only
  // ever layered on where it costs nothing: browsers that hand out
  // deviceorientation without a permission prompt. Where iOS would put up a
  // dialog — requestPermission is a function there and nowhere else — it is
  // simply not offered, because a modal is not worth a parlour trick.
  const TILT_FREE = (() => {
    try {
      return 'DeviceOrientationEvent' in window &&
             typeof DeviceOrientationEvent.requestPermission !== 'function';
    } catch (e) { return false; }
  })();

  figures.forEach(scale => {
    const fig = scale.querySelector('[data-fig]');
    if (!fig) return;

    let fx = parseFloat(getComputedStyle(scale).getPropertyValue('--fx')) || 0.12;
    let raf = 0;
    const paint = () => { raf = 0; scale.style.setProperty('--fx', fx.toFixed(4)); };
    const set = (v) => { fx = clamp(v); if (!raf) raf = requestAnimationFrame(paint); };

    // She is a fixed fraction of the picture wide, and travels the rest of
    // it, so the pointer maps onto the same range the stylesheet gives her.
    const fromEvent = (e) => {
      const r = scale.getBoundingClientRect();
      const w = fig.getBoundingClientRect().width;
      const run = r.width - w;
      if (run > 0) set((e.clientX - r.left - w / 2) / run);
    };

    let used = false;
    const mark = () => { if (!used) { used = true; scale.classList.add('is-used'); } };

    /* --- the drag ---------------------------------------------------- */
    let dragging = false;
    scale.addEventListener('pointerdown', e => {
      if (e.button) return;
      dragging = true;
      scale.classList.add('is-live');
      try { scale.setPointerCapture(e.pointerId); } catch (_) {}
      mark();
      fromEvent(e);
      e.preventDefault();               // no image drag, no text selection
    });
    scale.addEventListener('pointermove', e => { if (dragging) fromEvent(e); });
    const stop = (e) => {
      if (!dragging) return;
      dragging = false;
      scale.classList.remove('is-live');
      try { scale.releasePointerCapture(e.pointerId); } catch (_) {}
    };
    scale.addEventListener('pointerup', stop);
    scale.addEventListener('pointercancel', stop);

    /* --- the keyboard: she is a real button --------------------------- */
    fig.addEventListener('keydown', e => {
      const step = { ArrowLeft: -0.02, ArrowRight: 0.02, Home: -1, End: 1 }[e.key];
      if (step === undefined) return;
      e.preventDefault();
      mark();
      set(Math.abs(step) === 1 ? (step + 1) / 2 : fx + step);
    });

    /* --- the tilt ----------------------------------------------------- */
    // Only after a first drag: a figure that wanders because the phone is in
    // a hand is a bug until the visitor knows she is theirs to move. Damped,
    // capped at 30 Hz, and detached the moment the wall scrolls away.
    let tilting = false, last = 0;
    const onTilt = (e) => {
      const g = e.gamma;
      if (g == null) return;
      const now = e.timeStamp || Date.now();
      if (now - last < 33) return;      // 30 Hz is plenty for a lean
      last = now;
      if (!scale.classList.contains('is-tilting')) scale.classList.add('is-tilting');
      const target = clamp(0.5 + Math.max(-25, Math.min(25, g)) / 50);
      set(fx + (target - fx) * 0.12);   // low-pass, so a wobble is not a jump
    };
    const tiltOn = () => {
      if (tilting || !TILT_FREE || !used) return;
      tilting = true;
      addEventListener('deviceorientation', onTilt);
    };
    const tiltOff = () => {
      if (!tilting) return;
      tilting = false;
      scale.classList.remove('is-tilting');
      removeEventListener('deviceorientation', onTilt);
    };
    scale.addEventListener('pointerup', tiltOn);

    /* --- in view only -------------------------------------------------- */
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(es => es.forEach(en => {
        if (en.isIntersecting) { if (used) tiltOn(); } else { tiltOff(); }
      }), { threshold: 0.05 }).observe(scale);
    }
  });
})();

/* =====================================================================
   Splat, and the brush as the page transition (the fifth verb).

   The owner asked for the first half in one sentence: "a paintbrush paints
   the screen or splatters on the screen when you click buttons on home
   page." Then, seeing it, for the second: "When it switches pages it should
   have that paint animation for transition, add it for any page transition
   back to home page or from menu." So there are two classes of link, and
   this block is the whole of both:

     a.btn                 the hit. A mint burst out of the exact point the
     (every page, and      pointer landed on, drawn as inline SVG under a
      the Send the brief   turbulence displacement so no two edges are the
      submit button)       same shape, in one of three variants so two
                           clicks never match; 120ms later the roller comes
                           in from the side the button is on and covers the
                           viewport in 420ms. Click to navigation: 555ms.

     .brand, .nav-links a  the page transition. The roller alone — nothing
     footer a (internal)   was hit, so nothing splatters — entering from the
                           side the link is on: the wordmark from the left,
                           the desktop nav from the right, and the phone
                           menu, which drops from the top of the screen,
                           from above. Click to navigation: 460ms.

   Nothing here is load-bearing, and the interception is deliberately narrow:

     html.motion only      reduced motion, or no script, and every one of
                           these is a plain link that navigates the way links
                           do, and the form is a plain form.
     plain left clicks     middle-click, ctrl/cmd/shift/alt-click, target
                           _blank, downloads, mailto:, tel: and anything
                           off-origin are never touched.
     not where you are     the link to the page you are already on paints
                           nothing: there is no transition to make.

   Paths are compared after resolving against the document, so the build's
   PREFIX (/p/<slug> on the preview) is on both sides or neither.

   A same-page #anchor on a button gets the splat and nothing else: there is
   nothing to navigate to, so there is nothing to paint over. A second click
   while the pass is running does nothing at all.

   The Contact form is the one non-link: the browser's own validation runs
   first, so an invalid brief never reaches here and gets no paint, and a
   valid one is caught in the capture phase, painted, and then let through to
   the POST or the mail app exactly as before.

   The overlay is fixed, pointer-events:none, aria-hidden and built once; it
   is emptied on pageshow (a bfcache back must not land on a painted page)
   and 1.5s after a click that went nowhere.
   ===================================================================== */
(function () {
  const root = document.documentElement;
  if (!root.classList.contains('motion')) return;
  if (!document.body) return;
  let reduced = false;
  try { reduced = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (reduced) return;

  const NS = 'http://www.w3.org/2000/svg';
  const POP = 120;                       // the blob lands, then the brush comes
  const SWEEP = 420;                     // and covers the screen
  const GO = POP + SWEEP + 15;           // 555ms, click to location.assign
  const GO_S = SWEEP + 40;               // 460ms when there is no blob to wait for
  const CLEAR = 1500;                    // never leave the page painted over
  const SEEDS = [11, 5, 23];             // three turbulence seeds ...
  const TURNS = [0, 40, -70];            // ... and three turns to go with them
  const LEAD = 270;                      // how far the flung drops run ahead
  const TAIL = 340;                      // slack behind, so no far edge shows

  const el = (n, a) => {
    const e = document.createElementNS(NS, n);
    for (const k in a) e.setAttribute(k, String(a[k]));
    return e;
  };

  /* The blob, in the coordinates the mock was drawn in: the click point is
     the origin, so the whole thing is placed by one translate. */
  const BLOB = [
    ['ellipse', { cx: 0, cy: 0, rx: 72, ry: 58, transform: 'rotate(-18)' }],
    ['ellipse', { cx: 95, cy: -30, rx: 24, ry: 18, transform: 'rotate(20 95 -30)' }],
    ['ellipse', { cx: -88, cy: 24, rx: 20, ry: 14 }],
    ['ellipse', { cx: 40, cy: 78, rx: 16, ry: 22 }],
    ['ellipse', { cx: -50, cy: -70, rx: 14, ry: 12 }],
    ['circle', { cx: 130, cy: 30, r: 6 }],
    ['circle', { cx: -120, cy: -30, r: 5 }],
    ['circle', { cx: 70, cy: -90, r: 8 }],
    ['circle', { cx: 150, cy: -70, r: 4 }],
    ['circle', { cx: -30, cy: 110, r: 7 }],
    ['circle', { cx: -140, cy: 60, r: 5 }],
  ];
  // d, stroke width, path length (the dash is wound back over this).
  const DRIPS = [
    ['M-8 50 q4 60 0 120', 9, 122],
    ['M42 96 q3 40 -2 70', 6, 71],
  ];

  /* The roller's lap marks: [% of the stroke's height, which mint]. a is the
     mint itself, b one step down; each band is a narrow line with a 1%
     feather either side. Four faint lines is what a roller leaves when the
     nap reloads -- the first cut had them as 6% opaque stripes and read as
     a flag, not a roller. c (--mint-deep) stays available but unused. */
  const LAP = [
    [0, 'a'], [9, 'a'], [10, 'b'], [12, 'b'], [13, 'a'],
    [32, 'a'], [33, 'b'], [35, 'b'], [36, 'a'],
    [63, 'a'], [64, 'b'], [66, 'b'], [67, 'a'],
    [89, 'a'], [90, 'b'], [92, 'b'], [93, 'a'], [100, 'a'],
  ];
  // Thrown off the bristles, ahead of the edge. x is past the longest finger.
  const FLUNG = [
    ['ellipse', 170, 0.19, { rx: 29, ry: 13 }],
    ['circle', 212, 0.44, { r: 8 }],
    ['ellipse', 158, 0.67, { rx: 26, ry: 12 }],
    ['circle', 196, 0.88, { r: 6 }],
  ];

  /* The bristles are generated rather than written out, and a seeded
     generator is the point: the same fingers every run, so the file stays
     byte-identical build to build. It is the kit's mulberry32, which Wall's
     bristles come out of too. */
  const rng = window.oagKit.rng;

  let layer = null, shot = 0, killer = 0, running = false;
  let brush = null, brushW = 0, brushH = 0, brushV = false;
  let pt = null;            // where the last plain click on a submit button fell
  let replay = false;       // the form's own submit, let back through

  const deck = () => {
    if (!layer) {
      layer = document.createElement('div');
      layer.className = 'splat-layer';
      layer.setAttribute('aria-hidden', 'true');
      document.body.appendChild(layer);
    }
    return layer;
  };

  const clear = () => {
    if (killer) { clearTimeout(killer); killer = 0; }
    running = false;
    if (brush) brush.classList.remove('go');
    if (layer) layer.textContent = '';   // the brush stays cached, detached
  };

  function splat(x, y, v) {
    const W = innerWidth, H = innerHeight;
    const s = W < 640 ? 0.7 : 1;         // a phone gets a smaller throw
    const id = 'oaSplatF' + (++shot);

    const svg = el('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, class: 'sp-splat' });
    const f = el('filter', { id, x: '-30%', y: '-30%', width: '160%', height: '160%' });
    f.appendChild(el('feTurbulence', {
      type: 'fractalNoise', baseFrequency: '0.035', numOctaves: '3',
      seed: SEEDS[v], result: 'n',
    }));
    f.appendChild(el('feDisplacementMap', {
      in: 'SourceGraphic', in2: 'n', scale: '26',
      xChannelSelector: 'R', yChannelSelector: 'G',
    }));
    const defs = el('defs', {});
    defs.appendChild(f);
    svg.appendChild(defs);

    const g = el('g', { class: 'sp-pop', filter: `url(#${id})` });
    g.setAttribute('style',
      `--sx:${x.toFixed(1)}px;--sy:${y.toFixed(1)}px;--sr:${TURNS[v]}deg;` +
      `--s0:${(s * 0.3).toFixed(3)};--s1:${s}`);
    BLOB.forEach(([n, a]) => g.appendChild(el(n, Object.assign({ class: 'sp-ink' }, a))));
    DRIPS.forEach(([d, w, len]) => {
      const p = el('path', { class: 'sp-drip', d, 'stroke-width': w });
      p.style.setProperty('--dl', len);
      g.appendChild(p);
    });
    svg.appendChild(g);
    deck().appendChild(svg);
    return svg;
  }

  /* --- the brush ------------------------------------------------------ */
  /* Built once and kept, because the fingers are ~150 rects and nothing
     about them depends on the click: only the direction does, and that is
     one attribute on the wrapper. Rebuilt when the viewport changes size,
     or when the pass turns from horizontal to vertical.

     The vertical pass is the same brush, built in a box laid on its side —
     it travels `run` and is `across` wide either way — and stood up by the
     one transform on .sp-mirror. So there is a single stroke to maintain,
     and the animation stays the one translateX in the group's own frame. */
  function build(W, H, vert) {
    const run = vert ? H : W;            // how far the pass travels
    const across = vert ? W : H;         // and how wide it is
    const svg = el('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, class: 'sp-stroke' });

    const defs = el('defs', {});
    const lap = el('linearGradient', { id: 'oaLap', x1: 0, y1: 0, x2: 0, y2: 1 });
    LAP.forEach(([o, k]) => lap.appendChild(el('stop', { offset: o + '%', class: 'sp-lap-' + k })));
    defs.appendChild(lap);
    const bf = el('filter', { id: 'oaBristle', x: '-20%', y: '-6%', width: '150%', height: '112%' });
    bf.appendChild(el('feTurbulence', {
      type: 'fractalNoise', baseFrequency: '0.02 0.4', numOctaves: 2, seed: 7, result: 'n',
    }));
    bf.appendChild(el('feDisplacementMap', {
      in: 'SourceGraphic', in2: 'n', scale: 10, xChannelSelector: 'R', yChannelSelector: 'G',
    }));
    defs.appendChild(bf);
    svg.appendChild(defs);

    const mirror = el('g', { class: 'sp-mirror' });
    const sweep = el('g', { class: 'sp-sweep' });
    sweep.setAttribute('style', `--tx0:${-LEAD}px;--tx1:${run + 40}px`);

    // The body. One rect, no filter: this is the thing that covers the screen.
    sweep.appendChild(el('rect', {
      class: 'sp-body', x: -(run + TAIL), y: -2, width: run + TAIL, height: across + 4,
    }));

    // The leading edge: rounded bristle fingers, each overlapping the one
    // above it by 55-90% of its height, all the way down. Three tones.
    const edge = el('g', { class: 'sp-edge', filter: 'url(#oaBristle)' });
    const r = rng(0x5AA5);
    let y = -16, i = 0;
    while (y < across + 8) {
      const h = 10 + r() * 20, len = 20 + r() * 120;
      edge.appendChild(el('rect', {
        class: 'sp-t' + (i % 3), x: 0, y: y.toFixed(1),
        width: len.toFixed(1), height: h.toFixed(1), rx: (h / 2).toFixed(2),
      }));
      y += h * (1 - (0.55 + r() * 0.35));
      i++;
    }
    FLUNG.forEach(([n, x, f, a]) => edge.appendChild(
      el(n, Object.assign({ class: 'sp-t' + (n === 'circle' ? 2 : 1), cx: x, cy: Math.round(across * f) }, a))));
    sweep.appendChild(edge);

    mirror.appendChild(sweep);
    svg.appendChild(mirror);
    return svg;
  }

  function paint(side, W, H) {
    const vert = side === 'top';
    if (!brush || brushW !== W || brushH !== H || brushV !== vert) {
      brush = build(W, H, vert); brushW = W; brushH = H; brushV = vert;
    }
    brush.classList.remove('go');
    const mirror = brush.querySelector('.sp-mirror');
    // Down the screen: the side-on brush turned a quarter and slid over, so
    // its own +x runs down the page and its width covers the page's.
    if (vert) mirror.setAttribute('transform', `translate(${W},0) rotate(90)`);
    // The right-hand pass is the same brush, flipped about the viewport.
    else if (side === 'right') mirror.setAttribute('transform', `translate(${W},0) scale(-1,1)`);
    else mirror.removeAttribute('transform');
    deck().appendChild(brush);
    return brush;
  }

  /* --- who gets one -------------------------------------------------- */
  /* The path of a URL as this site compares them: resolved against the
     document, so PREFIX is on both sides, and with the extension and the
     trailing slash off so /work, /work/ and /work.html are one page. */
  const pathOf = (href) => {
    let p;
    try { p = new URL(href, location.href).pathname; } catch (_) { return null; }
    p = p.replace(/index\.html$/, '').replace(/\.html$/, '').replace(/\/$/, '');
    return p || '/';
  };

  const sideOf = (x, W) => (x < W / 2 ? 'left' : 'right');

  /* Which class of link this is, and which way the stroke comes in from.
     The phone menu is a panel dropped from the top of the screen, and the
     hamburger is display:none above the breakpoint — so a visible toggle is
     how we know the link was tapped in the panel rather than in the bar. */
  function role(a, x, W) {
    if (a.classList.contains('btn')) return ['btn', sideOf(x, W)];
    if (a.classList.contains('brand')) return ['stroke', 'left'];
    if (a.closest('.nav-links')) {
      const t = document.querySelector('.nav-toggle');
      return ['stroke', t && t.offsetParent !== null ? 'top' : 'right'];
    }
    if (a.closest('footer')) return ['stroke', sideOf(x, W)];
    return [null, null];
  }

  document.addEventListener('click', (e) => {
    const plain = !e.button && !e.defaultPrevented &&
                  !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey;
    // Where a click on a submit button landed. The submit event that follows
    // carries no coordinates of its own, and the splat needs the point.
    const sb = e.target && e.target.closest && e.target.closest('button[type="submit"]');
    pt = (plain && sb && e.detail && (e.clientX || e.clientY))
      ? { x: e.clientX, y: e.clientY } : null;
    if (!plain) return;

    const a = e.target && e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    const t = (a.getAttribute('target') || '').trim();
    if (t && t !== '_self') return;
    if (a.hasAttribute('download')) return;

    let url;
    try { url = new URL(a.href, location.href); } catch (_) { return; }
    if (url.protocol !== 'http:' && url.protocol !== 'https:') return;   // mailto:, tel:
    if (url.origin !== location.origin) return;                          // off-site

    // A keyboard Enter on a focused link arrives as a click with no pointer
    // behind it (detail 0, coordinates 0): throw it from the link instead.
    const W = innerWidth, H = innerHeight;
    let x = e.clientX, y = e.clientY;
    if (!e.detail || (!x && !y)) {
      const r = a.getBoundingClientRect();
      x = r.left + r.width / 2;
      y = r.top + r.height / 2;
    }

    const [kind, side] = role(a, x, W);
    if (!kind) return;

    // The page you are already on. The nav marks it, and there is no
    // transition to paint between a page and itself.
    if (kind === 'stroke' && (pathOf(url.href) === pathOf(location.href) ||
        a.classList.contains('active') || a.hasAttribute('aria-current'))) return;

    // A pass already running owns the page: a second click does nothing.
    if (running) { e.preventDefault(); return; }
    clear();

    const hit = kind === 'btn';
    if (hit) splat(x, y, shot % SEEDS.length);

    // A jump to an anchor on this page paints nothing over it: there is no
    // page coming to hide behind the stroke. The splat, and the link works.
    if (url.hash && url.pathname === location.pathname && url.search === location.search) {
      killer = setTimeout(clear, CLEAR);
      return;
    }

    e.preventDefault();
    running = true;
    const st = paint(side, W, H);
    // The blob goes first when there is one; otherwise the roller starts on
    // the next frame, which is the only rAF in this block.
    if (hit) setTimeout(() => st.classList.add('go'), POP);
    else requestAnimationFrame(() => st.classList.add('go'));
    setTimeout(() => location.assign(a.href), hit ? GO : GO_S);
    killer = setTimeout(clear, CLEAR);
  });

  /* --- the brief ------------------------------------------------------ */
  /* The form's own validation runs before any of this: an invalid brief
     never fires submit, so it gets no paint and the browser shows its own
     message. A valid one is caught here in the capture phase, ahead of the
     form's handler further up this file, and handed back to it untouched
     once the paint has run — the POST, or the visitor's mail app, exactly
     as before. */
  document.addEventListener('submit', (e) => {
    const f = e.target;
    if (replay || running) return;
    if (!f || !f.matches || !f.matches('#contact-form')) return;

    const W = innerWidth, H = innerHeight;
    let x, y;
    if (pt) { x = pt.x; y = pt.y; } else {
      const b = f.querySelector('[type="submit"]') || f;
      const r = b.getBoundingClientRect();
      x = r.left + r.width / 2;
      y = r.top + r.height / 2;
    }

    e.preventDefault();
    e.stopPropagation();                 // the form's own listener, in a moment
    clear();
    splat(x, y, shot % SEEDS.length);
    running = true;
    const st = paint(sideOf(x, W), W, H);
    setTimeout(() => st.classList.add('go'), POP);
    setTimeout(() => {
      replay = true;
      try { f.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); }
      finally { replay = false; }
    }, GO);
    // Nothing navigates on the mailto/POST path, so the paint would sit for
    // the full teardown over the "your mail app should open" status. Lift it
    // as soon as the pass has landed instead.
    killer = setTimeout(clear, GO + 160);
  }, true);

  // A page restored from the bfcache must never come back painted.
  addEventListener('pageshow', clear);
})();

/* =====================================================================
   Wall — paint the wall (the ninth verb).

   Concept 3 of the paint mechanics: "The About hero is dark and empty
   behind 'Ephraim and the crew' — a blank wall." So it becomes one. Moving
   the pointer across that hero lays down mint brush strokes; they dry and
   fade over about six seconds; the wall is never full, nothing is counted,
   and there is nothing to finish. The 404 is the same wall with the copy to
   match — "Nothing on this wall yet. Paint something, or head back."

   What a stroke is. A bristled stamp every 6px along the pointer's path,
   the hairs generated once from the kit's seeded random the way Splat's
   brush edge and art.py's brush_rule_svg() are, laid across the direction
   of travel and dragged a little along it. Opacity is speed: a slow pointer
   is a wet, opaque, fully loaded brush, and a fast one is dry-brush —
   the lighter hairs lift off the surface and the stroke goes broken.
   Pause with the brush on the wall and the paint runs: a thin mint drip,
   20 to 60px, out of the bottom of the last stamp.

   Drying. Every 110ms the whole canvas is multiplied down by 5.8% with one
   destination-out fill — one rectangle, not a redraw of a stroke stack,
   which is the cheaper of the two the spec offered and the only one whose
   cost does not grow with how long the visitor has been painting. That is
   ~6s from full to nothing; 6.8s after the last stamp the canvas is cleared
   outright and the loop stops itself, because a destination-out fade in 8-bit
   alpha stalls a few counts short of zero and a wall that is 1% painted is
   not a blank wall.

   The text is never painted over: the canvas sits at z-index -1 inside the
   hero's own stacking context, under the words and over nothing, and it is
   pointer-events:none — the listeners are on the hero itself, so a link in
   the hero is still a link.

   Phone. A finger drag paints, and the page still scrolls. The first 12px
   of a touch decide which: mostly vertical and it is a scroll and this
   never hears from it again; otherwise it is a stroke, the hero takes
   touch-action:none for as long as the stroke lasts, and the move is
   preventDefault'd so a scroll already being considered is called off. A
   two-finger tap wipes the wall.

   Sound: the hiss of a brush on brick while a stroke is being laid, out of
   the kit's sound module — the same AudioContext, the same muted default
   and the same persisted key as the pressure washer on /graffiti-removal.
   The toggle is built here and sits in the corner of the hero.

   No JS, reduced motion: there is no canvas and no toggle. Everything in
   here is built by this block under html.motion, and the server HTML is one
   attribute — data-wall on the hero — so the two renders are the hero
   exactly as it was before any of this.
   ===================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  if (!root.classList.contains('motion')) return;
  var reduced = false;
  try { reduced = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (reduced) return;
  var kit = window.oagKit;
  if (!kit) return;
  var heroes = document.querySelectorAll('.page-hero[data-wall]');
  if (!heroes.length) return;

  /* The paint is the site's mint, read off :root rather than written here:
     a hex outside that block is a bug in this repo, in CSS and in the script
     that draws with it. No mint, no painting. */
  var cs = getComputedStyle(root);
  var MINT = (cs.getPropertyValue('--mint') || '').trim();
  if (!MINT) return;
  var MID = (cs.getPropertyValue('--mint-mid') || '').trim() || MINT;

  var STEP = 6;                 // px of travel between stamps
  var DPR_CAP = 1.5;            // a retina phone does not get 3x of this
  var FADE_MS = 110, FADE_K = 0.058;   // ~6s from wet to gone
  var STOP_MS = 6800;           // then the canvas is cleared and the loop ends
  var PAUSE_MS = 170;           // brush held still: the paint starts to run
  var DRIP_MS = 720;            // how long a run takes to reach its length
  var DRIPS_MAX = 6;
  var HISS_MS = 140;            // silence this long and the stroke is over
  var DECIDE = 12;              // px of a touch before it is scroll or stroke

  var fine = false, coarse = false;
  try {
    fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
    coarse = matchMedia('(pointer:coarse)').matches;
  } catch (e) {}

  /* The bristles, once. Eight to twelve hairs across the ferrule, each with
     its own width, its own load and its own drag, from the kit's seeded
     random — so this is the same brush on every visit and on every hero.
     The numbers are brush_rule_svg()'s hair geometry brought down to the
     size a stamp is drawn at: widths 0.8-1.5 there, the same here, and the
     mint tones alternating so the stroke is not one flat green. */
  var rand = kit.rng(0x1D07);
  var HAIRS = (function () {
    var n = 8 + Math.floor(rand() * 5), out = [], i;
    for (i = 0; i < n; i++) {
      out.push({
        o: (i + 0.5) / n * 2 - 1 + (rand() - 0.5) * 0.14,   // across the brush
        w: 1.4 + rand() * 1.9,                              // how thick a hair
        a: 0.42 + rand() * 0.58,                            // how loaded it is
        l: 3.4 + rand() * 4.0                               // how far it drags
      });
    }
    return out;
  })();

  var Sound = kit.sound;
  var clamp = function (v, a, b) { return v < a ? a : (v > b ? b : v); };

  /* ------------------------------------------------------------ one wall */
  function Wall(hero) {
    this.hero = hero;
    this.cv = null; this.g = null;
    this.w = 0; this.h = 0; this.dpr = 1;
    this.rect = null;
    this.queue = [];            // client-space points waiting for a frame
    this.last = null;           // the last point actually stamped from
    this.acc = 0;               // travel carried over between points
    this.drips = [];
    this.raf = 0; this.live = false;
    this.paintedAt = 0; this.fadedAt = 0;
    this.dripped = true;        // no run until the brush has moved
    this.hissAt = 0; this.hissing = false;
    this.bound = false; this.built = false;
    this.touch = null;          // 'deciding' | 'paint' | 'scroll' | null
    this.t0 = null;
    this.width = coarse ? 30 : 26;   // a finger holds a wider brush
  }

  /* The canvas and the toggle, made the first time the hero comes into view
     and never before: a page nobody scrolls to costs one attribute. */
  Wall.prototype.build = function () {
    if (this.built) return;
    this.built = true;

    var cv = document.createElement('canvas');
    cv.className = 'paint-wall';
    cv.setAttribute('aria-hidden', 'true');
    this.hero.insertBefore(cv, this.hero.firstChild);
    this.cv = cv;
    this.g = cv.getContext('2d');
    this.g.lineCap = 'round';

    // The toggle is the kit's — the tin on /services puts up the same one.
    var b = kit.sndToggle();
    this.hero.appendChild(b);
    this.btn = b;

    this.size();
  };

  Wall.prototype.size = function () {
    var r = this.hero.getBoundingClientRect();
    var w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
    var dpr = Math.min(DPR_CAP, window.devicePixelRatio || 1);
    if (w === this.w && h === this.h && dpr === this.dpr) return;
    this.w = w; this.h = h; this.dpr = dpr;
    this.cv.width = Math.round(w * dpr);
    this.cv.height = Math.round(h * dpr);
    this.g.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.g.lineCap = 'round';
    this.drips.length = 0;
    this.last = null;
  };

  Wall.prototype.clear = function () {
    if (!this.g) return;
    this.g.save();
    this.g.setTransform(1, 0, 0, 1, 0, 0);
    this.g.clearRect(0, 0, this.cv.width, this.cv.height);
    this.g.restore();
    this.drips.length = 0;
    this.last = null; this.acc = 0;
  };

  /* --- the stamp ------------------------------------------------------
     The hairs laid across the direction of travel and dragged along it.
     `wet` is the whole of the speed story: it is the opacity of every hair,
     and below half it is also what decides which hairs are still touching
     the wall at all — the lightly loaded ones lift off first, which is what
     makes a fast stroke broken rather than merely faint. */
  Wall.prototype.stamp = function (x, y, ux, uy, wet) {
    var g = this.g, px = -uy, py = ux, hw = this.width / 2, i, hr, o, bx, by, l;
    /* The load itself, under the hairs: a brush with paint still in it lays
       a body of colour and the bristles are the texture in it, not the whole
       of it. It comes in at half speed and is gone entirely by the time the
       brush is running dry, which is the difference between a wet stroke and
       a scratched one. */
    if (wet > 0.4) {
      g.globalAlpha = (wet - 0.4) * 0.58;
      g.strokeStyle = MINT;
      g.lineWidth = this.width * 0.74;
      g.beginPath();
      g.moveTo(x - ux * 3.2, y - uy * 3.2);
      g.lineTo(x + ux * 3.2, y + uy * 3.2);
      g.stroke();
    }
    for (i = 0; i < HAIRS.length; i++) {
      hr = HAIRS[i];
      if (wet < 0.5 && hr.a < (1 - wet) * 0.72) continue;     // dry brush
      o = hr.o * hw;
      bx = x + px * o; by = y + py * o;
      l = hr.l;
      g.globalAlpha = clamp(wet * hr.a, 0.02, 1);
      g.strokeStyle = (i & 1) ? MID : MINT;
      g.lineWidth = hr.w * (0.7 + wet * 0.8);
      g.beginPath();
      g.moveTo(bx - ux * l, by - uy * l);
      g.lineTo(bx + ux * l, by + uy * l);
      g.stroke();
    }
    g.globalAlpha = 1;
    this.paintedAt = performance.now();
  };

  /* Walk the segment between two points, stamping every STEP px and
     carrying the remainder into the next segment so the spacing is even
     however the pointer is sampled. */
  Wall.prototype.segment = function (p) {
    var a = this.last;
    if (!a) { this.last = p; this.acc = 0; return; }
    var dx = p.x - a.x, dy = p.y - a.y;
    var d = Math.sqrt(dx * dx + dy * dy);
    if (d < 0.05) return;
    var dt = Math.max(1, p.t - a.t);
    var v = d / dt;                                  // px per ms
    var wet = clamp(1.06 - (v - 0.10) * 0.52, 0.18, 1);
    var ux = dx / d, uy = dy / d;
    var k = STEP - this.acc;
    var painted = false;
    while (k <= d) {
      this.stamp(a.x + ux * k, a.y + uy * k, ux, uy, wet);
      k += STEP;
      painted = true;
    }
    this.acc = painted ? d - (k - STEP) : this.acc + d;
    this.last = p;
    if (painted) { this.dripped = false; this.tip = { x: p.x, y: p.y }; }
    this.speed = v;
  };

  /* A run of paint out of the bottom of the last stamp. It is drawn a
     segment at a time as it grows, so the head is the freshest thing on the
     canvas and the tail has already started to dry. */
  Wall.prototype.drip = function () {
    if (!this.tip || this.drips.length >= DRIPS_MAX) return;
    this.drips.push({
      x: this.tip.x, y: this.tip.y + this.width * 0.22,
      len: 20 + rand() * 40,
      w: 1.1 + rand() * 1.7,
      wob: (rand() - 0.5) * 2.2,
      a: 0.5 + rand() * 0.4,
      head: 0, t0: performance.now()
    });
  };

  Wall.prototype.runDrips = function (now) {
    var g = this.g, i, d, to, p0, p1;
    for (i = this.drips.length - 1; i >= 0; i--) {
      d = this.drips[i];
      to = Math.min(d.len, d.len * (now - d.t0) / DRIP_MS);
      if (to > d.head) {
        p0 = d.head; p1 = to;
        g.globalAlpha = d.a * (1 - p1 / d.len * 0.45);
        g.strokeStyle = MINT;
        g.lineWidth = Math.max(0.6, d.w * (1 - p1 / d.len * 0.5));
        g.beginPath();
        g.moveTo(d.x + Math.sin(p0 / d.len * 3.1) * d.wob, d.y + p0);
        g.lineTo(d.x + Math.sin(p1 / d.len * 3.1) * d.wob, d.y + p1);
        g.stroke();
        d.head = to;
        this.paintedAt = now;
      }
      if (d.head >= d.len) {
        // the bead that gathers at the bottom of a run, and that is the end
        g.globalAlpha = d.a;
        g.fillStyle = MINT;
        g.beginPath();
        g.arc(d.x + Math.sin(3.1) * d.wob, d.y + d.len, d.w * 0.8, 0, 6.2832);
        g.fill();
        this.drips.splice(i, 1);
      }
    }
    g.globalAlpha = 1;
  };

  /* One multiply of the whole canvas. Cheap, and its cost is the same on the
     first stroke and the hundredth. */
  Wall.prototype.dry = function () {
    var g = this.g;
    g.globalCompositeOperation = 'destination-out';
    g.globalAlpha = 1;
    g.fillStyle = 'rgba(0,0,0,' + FADE_K + ')';
    g.fillRect(0, 0, this.w, this.h);
    g.globalCompositeOperation = 'source-over';
  };

  Wall.prototype.schedule = function () {
    if (this.raf || !this.built) return;
    var self = this;
    this.live = true;
    this.raf = requestAnimationFrame(function (t) { self.frame(t); });
  };

  /* The whole loop, and it stops itself. Read the box once, stamp the queue,
     run the drips, dry the wall, and when nothing has been painted for
     STOP_MS clear what is left and do not ask for another frame. */
  Wall.prototype.frame = function () {
    this.raf = 0;
    if (!this.built) { this.live = false; return; }
    var now = performance.now();

    if (this.queue.length) {
      this.rect = this.hero.getBoundingClientRect();
      for (var i = 0; i < this.queue.length; i++) {
        var q = this.queue[i];
        this.segment({ x: q.cx - this.rect.left, y: q.cy - this.rect.top, t: q.t });
      }
      this.queue.length = 0;
    }

    // The brush held still on the wall: the paint runs, once per pause.
    if (!this.dripped && this.last && now - this.last.t > PAUSE_MS) {
      this.dripped = true;
      this.drip();
    }
    if (this.drips.length) this.runDrips(now);

    if (!this.fadedAt) this.fadedAt = now;
    while (now - this.fadedAt >= FADE_MS) { this.dry(); this.fadedAt += FADE_MS; }

    if (this.hissing && now - this.hissAt > HISS_MS) {
      this.hissing = false;
      Sound.hissOff();
    }

    if (this.paintedAt && now - this.paintedAt > STOP_MS) {
      this.clear();
      this.live = false;
      this.paintedAt = 0; this.fadedAt = 0;
      return;                                  // nothing left to dry
    }
    this.schedule();
  };

  /* --- input ---------------------------------------------------------- */
  Wall.prototype.push = function (cx, cy, t) {
    this.build();
    this.queue.push({ cx: cx, cy: cy, t: t });
    if (!this.paintedAt) this.paintedAt = performance.now();
    this.fadedAt = this.fadedAt || performance.now();
    if (Sound.get()) {
      if (!this.hissing) { Sound.hissOn(); this.hissing = true; }
      Sound.hissSpeed(clamp((this.speed || 0.3) / 1.2, 0, 1));
      this.hissAt = performance.now();
    }
    this.schedule();
  };

  Wall.prototype.endStroke = function () {
    this.last = null;
    this.acc = 0;
    this.dripped = true;
    if (this.hissing) { this.hissing = false; Sound.hissOff(); }
  };

  Wall.prototype.bind = function () {
    if (this.bound) return;
    this.bound = true;
    var self = this, hero = this.hero;

    this.on = {
      move: function (e) {
        if (e.pointerType === 'touch') return;      // the finger has its own path
        self.push(e.clientX, e.clientY, e.timeStamp || performance.now());
      },
      leave: function () { self.endStroke(); },
      resize: function () { if (self.built) { self.size(); } },

      tstart: function (e) {
        if (e.touches.length > 1) {                 // two fingers: wipe it
          self.build();
          self.clear();
          self.touch = null;
          self.endStroke();
          hero.classList.remove('is-painting');
          return;
        }
        var t = e.touches[0];
        self.t0 = { x: t.clientX, y: t.clientY };
        self.touch = 'deciding';
        self.endStroke();
      },
      tmove: function (e) {
        if (!self.touch || self.touch === 'scroll') return;
        var t = e.touches[0];
        if (!t) return;
        if (self.touch === 'deciding') {
          var dx = t.clientX - self.t0.x, dy = t.clientY - self.t0.y;
          if (Math.sqrt(dx * dx + dy * dy) < DECIDE) return;
          // Mostly vertical is the page being scrolled, and that is the
          // page's, not ours. Anything else is a stroke.
          if (Math.abs(dy) > Math.abs(dx)) { self.touch = 'scroll'; return; }
          self.touch = 'paint';
          hero.classList.add('is-painting');
        }
        e.preventDefault();                          // call off any pending pan
        var evs = e.changedTouches, i;
        for (i = 0; i < evs.length; i++) {
          self.push(evs[i].clientX, evs[i].clientY, e.timeStamp || performance.now());
        }
      },
      tend: function () {
        self.touch = null;
        hero.classList.remove('is-painting');
        self.endStroke();
      }
    };

    if (fine) {
      hero.addEventListener('pointermove', this.on.move, { passive: true });
      hero.addEventListener('pointerleave', this.on.leave, { passive: true });
    }
    if (coarse) {
      hero.addEventListener('touchstart', this.on.tstart, { passive: true });
      hero.addEventListener('touchmove', this.on.tmove, { passive: false });
      hero.addEventListener('touchend', this.on.tend, { passive: true });
      hero.addEventListener('touchcancel', this.on.tend, { passive: true });
    }
    addEventListener('resize', this.on.resize, { passive: true });
  };

  Wall.prototype.unbind = function () {
    if (!this.bound) return;
    this.bound = false;
    var hero = this.hero;
    hero.removeEventListener('pointermove', this.on.move);
    hero.removeEventListener('pointerleave', this.on.leave);
    hero.removeEventListener('touchstart', this.on.tstart);
    hero.removeEventListener('touchmove', this.on.tmove);
    hero.removeEventListener('touchend', this.on.tend);
    hero.removeEventListener('touchcancel', this.on.tend);
    removeEventListener('resize', this.on.resize);
    hero.classList.remove('is-painting');
    this.touch = null;
    this.endStroke();
    if (this.raf) { cancelAnimationFrame(this.raf); this.raf = 0; }
    this.live = false;
    this.paintedAt = 0; this.fadedAt = 0;
    this.clear();
  };

  /* --- in view, and only then ----------------------------------------- */
  var walls = [];
  for (var i = 0; i < heroes.length; i++) walls.push(new Wall(heroes[i]));

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var w = e.target.__wall;
        if (!w) return;
        if (e.isIntersecting) { w.build(); w.size(); w.bind(); }
        else w.unbind();
      });
    }, { threshold: 0, rootMargin: '0px' });
    walls.forEach(function (w) { w.hero.__wall = w; io.observe(w.hero); });
  } else {
    walls.forEach(function (w) { w.hero.__wall = w; w.build(); w.bind(); });
  }

  window.oagWall = { instances: walls };
})();

/* =====================================================================
   Tip — the tin you knock over.

   Owner, 2026-09-19: "Maybe a paint bucket you click and it spills."

   The eleventh verb, and the second a visitor sets off on purpose. A tin
   of mint stands on the floor of the Services hero, beside the headline.
   Click it, or drag it past forty degrees, and it goes over: it rolls on
   the edge of its own base with an overshoot, the paint inside leans to
   the lip and leaves as a sheet, the sheet runs down the hero and gathers
   in a pool along its bottom edge, and the pool drips through onto the
   section below and becomes that section's mint rule — which then takes
   its Cure sheen. Four seconds later the tin rights itself, the sheet
   retracts, the pool drains into the rule and it can be tipped again.

   Nothing here is in the document without it. The tin is (build.py
   tip_can(), art.py can_tipping_svg()) and so is the rule (tip_rule()),
   and both are finished in the server HTML — an upright tin and a painted
   rule — but the sheet, the pool, the run, the sound toggle and the tin's
   own role as a control are all built here, under html.motion. So a page
   with no script, and a visitor who asked for reduced motion, get the
   page that was always there.

   Nothing here can move a box either. The sheet is absolutely positioned
   inside the tin's own box, the pool inside the hero at z-index -1 — the
   layer the hero's shade sits in, so the words are never painted over —
   and the run inside the section below. The hero clips, which is where a
   pour that ran too far stops. The one thing that has a height is the
   pool, and it has it in a box that is already absolutely positioned.

   The geometry is art.py's and is read out of the stylesheet rather than
   written twice: --tip-pvx/--tip-pvy are CAN_TIP_PIVOT, the edge of the
   base the tin rolls on, and --tip-px/--tip-py are CAN_TIP_POUR, where
   the paint leaves it once it is over. Every measurement below is taken
   in client coordinates and turned into an offset inside an element in
   the same breath, so there is nothing here that a scroll could stale and
   this file adds no listener to one.
   ===================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  if (!root.classList.contains('motion')) return;
  var reduced = false;
  try { reduced = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (reduced) return;
  var kit = window.oagKit;
  if (!kit) return;

  var hero = document.querySelector('.page-hero.has-tip');
  var tip = hero && hero.querySelector('[data-tip]');
  var can = tip && tip.querySelector('[data-tip-can]');
  if (!can) return;
  var rule = document.querySelector('[data-tip-rule]');
  var sect = rule && rule.closest('section');

  /* The rule's 2.8s bail-out is the one on this site that runs the other
     way — it paints the rule for a page whose script never arrived — so
     the first thing the script does when it does arrive is call it off.
     Roll it in says the same thing with .rollin and the primer. */
  root.classList.add('tipready');

  var THRESH = 40;                  // degrees of drag before it goes over
  var POUR_AT = 260;                // the rim is past the vertical by here
  var POOL_AT = 720;                // the sheet has reached the bottom
  var DROP_AT = 900;                // and starts through onto the section
  var FILL_AT = 1180;               // the rule fills from where it lands
  var CURE_AT = 2040;               // and cures once it is full
  var HOLD = 4000;                  // then the tin rights itself
  var UP = 780;                     // and this long later it is idle again
  var DROP_MS = 460;                // how long the run takes to reach the rule

  var coarse = false;
  try { coarse = matchMedia('(pointer:coarse)').matches; } catch (e) {}

  /* Tilt is an extra on a phone that already has the tap, so it is only
     offered where it costs nothing: browsers that hand out
     deviceorientation with no permission prompt. Where iOS would put up a
     dialog — requestPermission is a function there and nowhere else — it
     is silently not offered. The same test the scale figure makes. */
  var TILT_FREE = (function () {
    try {
      return 'DeviceOrientationEvent' in window &&
             typeof DeviceOrientationEvent.requestPermission !== 'function';
    } catch (e) { return false; }
  })();

  var num = function (name, dflt) {
    var v = parseFloat(getComputedStyle(hero).getPropertyValue(name));
    return isNaN(v) ? dflt : v;
  };
  var PVX = 0, PVY = 0, PX = 0, PY = 0;   // read off the stylesheet in build()

  var built = false, state = 0, used = false;
  var sheet = null, pool = null, drop = null, timers = [];
  var after = function (ms, fn) { timers.push(setTimeout(fn, ms)); };

  /* ------------------------------------------------------- what it needs */
  function build() {
    if (built) return;
    built = true;
    PVX = num('--tip-pvx', 0.77); PVY = num('--tip-pvy', 0.89);
    PX = num('--tip-px', 1.341); PY = num('--tip-py', 0.784);

    sheet = document.createElement('span');
    sheet.className = 'tip-sheet';
    sheet.setAttribute('aria-hidden', 'true');
    sheet.innerHTML = '<i class="tip-stream"></i><i class="tip-gloss"></i>' +
      '<i class="tip-head"></i><i class="tip-lip"></i>';
    tip.appendChild(sheet);

    pool = document.createElement('span');
    pool.className = 'tip-pool';
    pool.setAttribute('aria-hidden', 'true');
    pool.innerHTML = '<i class="tip-pool-body"><i class="tip-pool-lip"></i></i>' +
      '<i class="tip-pool-mound"></i>';
    hero.appendChild(pool);

    // The same toggle the wall puts in the corner of its hero, off the
    // same persisted key: muted until a visitor asks, here or there.
    hero.appendChild(kit.sndToggle('Sound'));

    // And this is where the tin stops being a picture. It is a <span> in
    // the document on purpose — a control that does nothing without a
    // script is worse than a drawing of a tin — so the role, the tab stop
    // and the name are put on here and nowhere else.
    can.setAttribute('role', 'button');
    can.setAttribute('tabindex', '0');
    can.setAttribute('aria-label', 'Tip the paint can');

    // And the sheet is given its real height straight away. It is invisible
    // until the tin goes over, but it is a box, and a box that is taller
    // than the hero is scrollable overflow inside a hero that clips — the
    // lesson the pool is built around, two elements up.
    measure();
  }

  /* Where the paint leaves the tin, how far it has to fall, and where it
     lands — in client coordinates, turned into offsets inside the hero,
     the section and the rule before anything is written. */
  function measure() {
    var hr = hero.getBoundingClientRect(), tr = tip.getBoundingClientRect();
    var px = tr.left + tr.width * PX, py = tr.top + tr.width * PY;
    hero.style.setProperty('--sheet-h', Math.max(8, Math.round(hr.bottom - py)) + 'px');
    hero.style.setProperty('--tip-x',
      Math.max(0, Math.min(100, (px - hr.left) / hr.width * 100)).toFixed(2) + '%');
    if (rule) {
      var rr = rule.getBoundingClientRect();
      rule.style.setProperty('--tip-x',
        Math.max(0, Math.min(100, (px - rr.left) / rr.width * 100)).toFixed(2) + '%');
    }
    return { px: px, w: tr.width };
  }

  /* The run through onto the section below. It is Spray's drip, markup
     and keyframes and all — a body of mint scaled down from where it
     starts and a bead carried to the end of it — because a run of paint
     is a run of paint and this site already draws one. */
  function makeDrop(m) {
    if (!sect || !rule) return null;
    var sr = sect.getBoundingClientRect(), rr = rule.getBoundingClientRect();
    var dw = Math.max(2, Math.round(m.w * 0.038));
    var dh = Math.max(10, Math.round(rr.top - sr.top));
    var d = document.createElement('span');
    d.className = 'spray-drip tip-drop';
    d.setAttribute('aria-hidden', 'true');
    d.style.cssText = 'left:' + (m.px - sr.left - dw / 2).toFixed(1) + 'px;top:0;--dw:' +
      dw + 'px;--dh:' + dh + 'px;--dt:' + DROP_MS + 'ms';
    d.innerHTML = '<i class="spray-run"></i><i class="spray-bead"></i>';
    sect.appendChild(d);
    return d;
  }

  /* ------------------------------------------------------------- the tip */
  function go() {
    if (state) return;                        // one tin at a time
    state = 1;
    build();
    var m = measure();
    if (drop) { drop.remove(); drop = null; }
    hero.classList.add('tipping');
    // Muted is the default and the key is the one every mechanic shares:
    // this asks for a sound, it never turns one on.
    kit.sound.glug();
    used = true; tiltOn();

    after(POUR_AT, function () { hero.classList.add('pouring'); });
    after(POOL_AT, function () { hero.classList.add('pooled'); });
    after(DROP_AT, function () {
      drop = makeDrop(m);
      if (drop) { void drop.offsetWidth; drop.classList.add('run'); }
    });
    after(FILL_AT, function () {
      if (rule) rule.classList.add('filling');
    });
    after(CURE_AT, function () {
      if (!rule) return;
      // .cured is the state — this rule has been painted — and .curing is
      // the pass that just happened, the way the brush cures a stage.
      rule.classList.add('cured');
      rule.classList.remove('curing');
      void rule.offsetWidth;
      rule.classList.add('curing');
    });
    after(HOLD, right);
  }

  /* It rights itself so it can be tipped again: the tin springs back up,
     the sheet retracts into the rim, and the pool drains away down the
     run it has already made. The rule keeps its paint — paint does not
     come off a wall because the tin stood up. */
  function right() {
    state = 2;
    hero.classList.remove('tipping', 'pouring', 'pooled');
    hero.classList.add('righting');
    if (drop) { drop.classList.remove('run'); drop.classList.add('dry'); }
    after(UP, reset);
  }

  function reset() {
    timers.forEach(clearTimeout);
    timers = [];
    hero.classList.remove('tipping', 'pouring', 'pooled', 'righting', 'is-dragging');
    hero.style.removeProperty('--tipdeg');
    if (drop) { drop.remove(); drop = null; }
    state = 0;
  }

  /* --------------------------------------------------- click, and drag */
  var dragging = false, moved = false, deg = 0, a0 = 0, draf = 0, skip = false;

  // The angle the pointer has carried the tin through, measured about the
  // edge of the base it rolls on. It is a difference from where the drag
  // started, not an absolute bearing, so it does not matter where on the
  // tin the visitor took hold of it.
  function angle(e) {
    var tr = tip.getBoundingClientRect();
    var ox = tr.left + tr.width * PVX, oy = tr.top + tr.height * PVY;
    return Math.atan2(e.clientX - ox, oy - e.clientY) * 180 / Math.PI;
  }

  can.addEventListener('pointerdown', function (e) {
    if (e.button || state) return;
    build();
    dragging = true; moved = false; deg = 0;
    a0 = angle(e);
    try { can.setPointerCapture(e.pointerId); } catch (_) {}
  });

  can.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    var d = angle(e) - a0;
    if (!moved && Math.abs(d) < 2) return;    // a tap is not a drag
    moved = true;
    deg = Math.max(0, Math.min(96, d));
    hero.classList.add('is-dragging');
    if (!draf) draf = requestAnimationFrame(function () {
      draf = 0;
      hero.style.setProperty('--tipdeg', deg.toFixed(1) + 'deg');
    });
    e.preventDefault();                       // no text selection, no pan
  });

  var release = function (e) {
    if (!dragging) return;
    dragging = false;
    try { can.releasePointerCapture(e.pointerId); } catch (_) {}
    if (!moved) return;                       // a plain press: click has it
    skip = true;                              // and a drag is not a click
    hero.classList.remove('is-dragging');
    if (deg >= THRESH) go();
    else hero.style.removeProperty('--tipdeg');   // not far enough: it rocks back
  };
  can.addEventListener('pointerup', release);
  can.addEventListener('pointercancel', release);

  can.addEventListener('click', function () {
    if (skip) { skip = false; return; }
    go();
  });

  // It is a span with a role, so Enter and Space are this file's to honour.
  can.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;
    e.preventDefault();
    go();
  });

  /* ------------------------------------------------------------- the tilt */
  // After the first tap and never before: a pool that moves because the
  // phone is in a hand is a bug until the visitor knows they tipped it.
  // Damped, capped at 30 Hz, and let go the moment the hero leaves.
  var tilting = false, tlast = 0, slosh = 0, sraf = 0;

  function onTilt(e) {
    var g = e.gamma;
    if (g == null) return;
    var now = e.timeStamp || Date.now();
    if (now - tlast < 33) return;
    tlast = now;
    var target = Math.max(-25, Math.min(25, g)) / 25;
    slosh += (target - slosh) * 0.12;         // low-pass: a wobble, not a jump
    if (!sraf) sraf = requestAnimationFrame(function () {
      sraf = 0;
      hero.style.setProperty('--slosh', slosh.toFixed(3));
    });
  }

  function tiltOn() {
    if (tilting || !TILT_FREE || !coarse || !used) return;
    tilting = true;
    addEventListener('deviceorientation', onTilt, { passive: true });
  }

  function tiltOff() {
    if (!tilting) return;
    tilting = false;
    removeEventListener('deviceorientation', onTilt);
    hero.style.removeProperty('--slosh');
  }

  /* The sheet, the pool and the toggle are made the first time the hero is
     on screen and never before — the wall does the same — so a visitor who
     lands further down the page costs one <span>. The tilt is attached at
     the same moment and let go when the hero leaves. */
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (en.isIntersecting) { build(); tiltOn(); } else tiltOff();
      });
    }, { threshold: 0.05 }).observe(hero);
  } else {
    build();
  }

  // A bfcache back must never land on a half-poured hero.
  addEventListener('pageshow', function (e) { if (e.persisted) reset(); });

  window.oagTip = { tip: go, reset: reset, state: function () { return state; } };
})();
