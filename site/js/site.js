/* =====================================================================
   Open Air Gallery — site scripts.

   Nothing in here is load-bearing. The pages render complete without it;
   this only adds the mobile menu, the scrolled state on the nav, the
   current-page marker and the copyright year.
   ===================================================================== */
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
   The motion layer — Roll · Scale · Cure.

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

  const targets = [...document.querySelectorAll('.rv,.dims')];
  if (!targets.length) return;

  // No observer means no way to unhide: show everything now rather than
  // making the visitor wait for the 2.8s self-reveal.
  if (!('IntersectionObserver' in window)) {
    targets.forEach(el => el.classList.add('in'));
    return;
  }

  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in');
    io.unobserve(e.target);          // Cure runs once, and only once
  }), { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  targets.forEach(el => io.observe(el));
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
   Splat — paint thrown from a Home-page button (the fifth verb).

   The owner asked for it in one sentence: "a paintbrush paints the screen
   or splatters on the screen when you click buttons on home page." Both
   halves are here. First the splatter: a mint burst out of the exact point
   the pointer hit, drawn as inline SVG under a turbulence displacement so
   no two edges are the same shape, in one of three variants so two clicks
   never match. Then, 120ms later, the brush — a roller pass in from the
   side the button was on that covers the viewport in 420ms, at which point
   the link is followed. Click to navigation is 555ms.

   Nothing here is load-bearing, and it is deliberately narrow:

     html.motion only      reduced motion, or no script, and a button is a
                           plain link that navigates the way links do.
     [data-splat] only     build.py marks Home and nothing else.
     plain left clicks     middle-click, ctrl/cmd/shift/alt-click, target
                           _blank, downloads, mailto:, tel: and anything
                           off-origin are never touched.

   A same-page #anchor gets the splat and nothing else: there is nothing to
   navigate to, so there is nothing to paint over. A second click while the
   pass is running does nothing at all.

   The overlay is fixed, pointer-events:none, aria-hidden and built once;
   it is emptied on pageshow (a bfcache back must not land on a painted
   page) and 1.5s after a click that went nowhere.
   ===================================================================== */
(function () {
  const root = document.documentElement;
  if (!root.classList.contains('motion')) return;
  if (!document.body || !document.body.hasAttribute('data-splat')) return;
  let reduced = false;
  try { reduced = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (reduced) return;

  const NS = 'http://www.w3.org/2000/svg';
  const POP = 120;                       // the blob lands, then the brush comes
  const SWEEP = 420;                     // and covers the screen
  const GO = POP + SWEEP + 15;           // 555ms, click to location.assign
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
     byte-identical build to build. mulberry32. */
  const rng = (seed) => {
    let t = seed >>> 0;
    return () => {
      t = (t + 0x6D2B79F5) >>> 0;
      let r = Math.imul(t ^ (t >>> 15), 1 | t);
      r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
      return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    };
  };

  let layer = null, shot = 0, killer = 0, running = false;
  let brush = null, brushW = 0, brushH = 0;

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
     about them depends on the click: only the side does, and that is one
     attribute on the wrapper. Rebuilt when the viewport changes size. */
  function build(W, H) {
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
    sweep.setAttribute('style', `--tx0:${-LEAD}px;--tx1:${W + 40}px`);

    // The body. One rect, no filter: this is the thing that covers the screen.
    sweep.appendChild(el('rect', {
      class: 'sp-body', x: -(W + TAIL), y: -2, width: W + TAIL, height: H + 4,
    }));

    // The leading edge: rounded bristle fingers, each overlapping the one
    // above it by 55-90% of its height, all the way down. Three tones.
    const edge = el('g', { class: 'sp-edge', filter: 'url(#oaBristle)' });
    const r = rng(0x5AA5);
    let y = -16, i = 0;
    while (y < H + 8) {
      const h = 10 + r() * 20, len = 20 + r() * 120;
      edge.appendChild(el('rect', {
        class: 'sp-t' + (i % 3), x: 0, y: y.toFixed(1),
        width: len.toFixed(1), height: h.toFixed(1), rx: (h / 2).toFixed(2),
      }));
      y += h * (1 - (0.55 + r() * 0.35));
      i++;
    }
    FLUNG.forEach(([n, x, f, a]) => edge.appendChild(
      el(n, Object.assign({ class: 'sp-t' + (n === 'circle' ? 2 : 1), cx: x, cy: Math.round(H * f) }, a))));
    sweep.appendChild(edge);

    mirror.appendChild(sweep);
    svg.appendChild(mirror);
    return svg;
  }

  function paint(side, W, H) {
    if (!brush || brushW !== W || brushH !== H) {
      brush = build(W, H); brushW = W; brushH = H;
    }
    brush.classList.remove('go');
    const mirror = brush.querySelector('.sp-mirror');
    // The right-hand pass is the same brush, flipped about the viewport.
    if (side === 'right') mirror.setAttribute('transform', `translate(${W},0) scale(-1,1)`);
    else mirror.removeAttribute('transform');
    deck().appendChild(brush);
    return brush;
  }

  /* --- who gets one -------------------------------------------------- */
  document.addEventListener('click', (e) => {
    if (e.defaultPrevented || e.button) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const a = e.target && e.target.closest && e.target.closest('a.btn');
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
    let x = e.clientX, y = e.clientY;
    if (!e.detail || (!x && !y)) {
      const r = a.getBoundingClientRect();
      x = r.left + r.width / 2;
      y = r.top + r.height / 2;
    }

    // A pass already running owns the page: a second click does nothing.
    if (running) { e.preventDefault(); return; }
    clear();
    splat(x, y, shot % SEEDS.length);

    // A jump to an anchor on this page paints nothing over it: there is no
    // page coming to hide behind the stroke. The splat, and the link works.
    if (url.hash && url.pathname === location.pathname && url.search === location.search) {
      killer = setTimeout(clear, CLEAR);
      return;
    }

    e.preventDefault();
    running = true;
    const W = innerWidth, H = innerHeight;
    const st = paint(x < W / 2 ? 'left' : 'right', W, H);
    setTimeout(() => st.classList.add('go'), POP);
    setTimeout(() => location.assign(a.href), GO);
    killer = setTimeout(clear, CLEAR);
  });

  // A page restored from the bfcache must never come back painted.
  addEventListener('pageshow', clear);
})();
