/* Mendoza Marketing — site scripts.
 *
 * The base layer, and nothing else yet: the nav, the active link, the reveal
 * observer and the lightbox shell. Taken from /root/dronegodmax-src/site/js/
 * site.js, which is where the shape and the bug fixes come from.
 *
 * Nothing in here is load-bearing. Every page renders complete with this file
 * missing, blocked or broken — the reveal classes are only hidden under
 * html.motion, and the stylesheet reveals them by itself after 2.8s.
 */
(function(){
  const $=(s,c=document)=>c.querySelector(s), $$=(s,c=document)=>[...c.querySelectorAll(s)];

  /* ---- nav ----------------------------------------------------------- */
  // Guarded: a page with no nav must not take the rest of the file down with
  // it. DGM learned this the expensive way — one unguarded querySelector on
  // its bare /play page killed every effect below it.
  const nav=$('.nav'), toggle=$('.nav-toggle');
  if(nav){
    const onScroll=()=>nav.classList.toggle('scrolled',scrollY>24);
    onScroll(); addEventListener('scroll',onScroll,{passive:true});
    if(toggle) toggle.addEventListener('click',()=>{
      const open=nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded',open);
      document.body.style.overflow=open?'hidden':'';
    });
  }
  // Services ▾ — click opens it on a phone, CSS hover opens it on a desktop.
  $$('.has-menu>button').forEach(b=>b.addEventListener('click',e=>{
    e.preventDefault();
    const li=b.parentElement, was=li.classList.contains('open');
    $$('.has-menu.open').forEach(x=>x.classList.remove('open'));
    li.classList.toggle('open',!was);
    b.setAttribute('aria-expanded',String(!was));
  }));
  document.addEventListener('click',e=>{
    if(!e.target.closest('.has-menu')) $$('.has-menu.open').forEach(x=>x.classList.remove('open'));
  });

  /* ---- active link ---------------------------------------------------- */
  // Compared on the path as served, so it is right under the preview prefix
  // (/p/<slug>/websites) as well as at the domain root.
  const here=location.pathname.replace(/index\.html$/,'').replace(/\.html$/,'').replace(/\/$/,'')||'/';
  $$('.nav-links a').forEach(a=>{
    const p=(a.getAttribute('href')||'').replace(/\/$/,'')||'/';
    if(p===here||(p!=='/'&&p!==''&&here.startsWith(p+'/'))) a.classList.add('active');
  });

  /* ---- reveal on scroll ----------------------------------------------- */
  const io=new IntersectionObserver(es=>es.forEach(e=>{
    if(!e.isIntersecting)return;
    e.target.classList.add('in');
    io.unobserve(e.target);
  }),{threshold:.12,rootMargin:'0px 0px -6% 0px'});
  $$('.rv').forEach(el=>io.observe(el));

  /* ---- lightbox shell -------------------------------------------------- */
  // The container is rendered by layout(); anything with data-img or data-video
  // opens in it. Nothing on the site uses it yet.
  const lb=$('.lb');
  if(lb){
    const inner=$('.lb-inner',lb), cap=$('.lb-cap',lb);
    const close=()=>{lb.classList.remove('on');inner.innerHTML='';document.body.style.overflow=''};
    const open=(markup,caption)=>{
      inner.innerHTML='<button class="lb-close" type="button" aria-label="Close">'+
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'+
        '<path d="M18 6L6 18M6 6l12 12"/></svg></button>'+markup;
      cap.textContent=caption||'';
      lb.classList.add('on');
      document.body.style.overflow='hidden';
      const x=$('.lb-close',lb); if(x)x.focus();
    };
    lb.addEventListener('click',e=>{if(e.target===lb||e.target.closest('.lb-close'))close()});
    addEventListener('keydown',e=>{if(e.key==='Escape'&&lb.classList.contains('on'))close()});
    $$('[data-img]').forEach(el=>el.addEventListener('click',e=>{
      e.preventDefault();
      open(`<img src="${el.dataset.img}" alt="${el.dataset.cap||''}">`,el.dataset.cap);
    }));
    $$('[data-video]').forEach(el=>el.addEventListener('click',e=>{
      e.preventDefault();
      open(`<video src="${el.dataset.video}" controls autoplay playsinline></video>`,el.dataset.cap);
    }));
  }

  /* ---- the year in the footer ------------------------------------------ */
  const y=$('#year'); if(y) y.textContent=new Date().getFullYear();
})();


/* =====================================================================
   mm — the motion kit.

   Step 5's layer. Everything below this line is enhancement on a page that
   is already complete: every module returns on its first line unless
   html.motion is on the document, and html.motion is only on it when the
   browser runs JavaScript and the visitor has not asked for reduced motion.
   Nothing here supplies a word, a figure or a frame that the server HTML
   does not already hold.

   One rAF loop for the whole page, the DGM way (window.dgmLoop is the same
   shape): add() registers a callback for good, and pump(+1)/pump(-1) is how
   a module that needs frames holds the loop open and lets it go. A page with
   nothing moving asks for no frames at all.

   The flags are read once, here, rather than in six places:
     motion  html.motion — the whole contract
     fine    a real pointer that can hover; a phone gets taps instead
     save    the visitor is on a metered connection — no film is fetched

   `window.mmPick`, the hero's 4K/1080 picker, is NOT here: it has to exist
   before the hero <video> parses, so it is defined inline in the head by
   build.py's layout(). This file is deferred and would arrive far too late.
   ===================================================================== */
(function(){
  const root=document.documentElement;
  const mq=q=>{try{return matchMedia(q).matches}catch(e){return false}};
  const q=[]; let ticking=false, pumps=0;
  const onFrame=now=>{
    ticking=false;
    for(let i=0;i<q.length;i++){try{q[i](now)}catch(e){}}
    if(pumps>0) tick();
  };
  const tick=()=>{if(!ticking){ticking=true;requestAnimationFrame(onFrame)}};
  // add() hands back its own remover, so a demo that has finished stops
  // costing the loop a function call on every frame for the rest of the visit.
  const add=f=>{q.push(f);return ()=>{const i=q.indexOf(f);if(i>=0)q.splice(i,1)}};
  const pump=d=>{pumps=Math.max(0,pumps+d);if(pumps>0)tick()};
  // One factory so a module never has to remember the feature test. No
  // IntersectionObserver (or a browser old enough not to have one) means the
  // module simply does not run and the page stays as the server wrote it.
  const io=(cb,opt)=>('IntersectionObserver' in window)?new IntersectionObserver(cb,opt):null;
  window.mm={
    motion:root.classList.contains('motion'),
    fine:mq('(hover:hover) and (pointer:fine)'),
    save:(()=>{try{const n=navigator.connection;return !!(n&&n.saveData)}catch(e){return false}})(),
    add, pump, tick, io,
    $:(s,c=document)=>c.querySelector(s),
    $$:(s,c=document)=>[...c.querySelectorAll(s)],
  };
})();
