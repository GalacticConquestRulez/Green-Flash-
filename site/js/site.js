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
