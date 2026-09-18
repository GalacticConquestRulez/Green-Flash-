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
