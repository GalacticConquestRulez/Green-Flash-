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


/* =====================================================================
   THE SIX LIVE TILES

   The plan: "on hover/tap the card runs a three-second demo of the service
   — the website card wire-frames itself, the Meta card's counter climbs, the
   drone card flies the little quad across, the social card cycles three reel
   frames, the logo card swaps the Mendoza mark's text, the leads card's
   chart draws — the kinesthetic beat the owner wants, one verb per card,
   nothing scored."

   So: one verb each, three seconds, then rest. Nothing is counted, nothing
   is announced, nothing is left on the card afterwards. A second hover runs
   it again; a hover while it is running is ignored rather than restarting it
   half-way.

   Every demo is built out of what the page already has — the wires and the
   quad that are in the wells, the reels' own posters, the six service names
   off the cards themselves, the results band's figures off their data-count
   attributes and the leads chart's own points. Nothing here invents a
   number: the Meta counter can only climb to the figure printed lower down
   the page, and the leads card can only land on the one in the Leads Center
   tile.

   On a phone there is no hover, so the FIRST tap on a card plays its demo
   instead of following the link and any tap after that goes to the page —
   the standard touch stand-in for a hover, and the only way a tile that
   exists to be felt can be felt with a finger. On a desktop the link is
   never intercepted at all.
   ===================================================================== */
(function(){
  const mm=window.mm;
  if(!mm||!mm.motion) return;
  const cards=mm.$$('.svc[data-demo]');
  if(!cards.length) return;

  const SVG='http://www.w3.org/2000/svg';
  const clamp=(v,a,b)=>v<a?a:v>b?b:v;
  const ease=k=>k*k*(3-2*k);              // smoothstep
  const vel=k=>4*k*(1-k);                 // its speed, normalised to 1

  // A node the demo owns. .mm-fx is the mark that says "the script built
  // this": rest() sweeps every one of them out of the well, so the well the
  // visitor is left with is the well the server sent.
  const mk=(tag,cls,parent)=>{
    const e=document.createElement(tag);
    e.className=cls+' mm-fx';
    parent.appendChild(e);
    return e;
  };
  const mkNS=(tag,cls,parent)=>{
    const e=document.createElementNS(SVG,tag);
    e.setAttribute('class',cls+(parent?' mm-fx':''));
    if(parent)parent.appendChild(e);
    return e;
  };

  /* A figure off the results band, as data rather than as text.

     results.py prints the figure and hands the count-up the arithmetic to
     get back to it (data-count, -prefix, -suffix, -decimals). Reading those
     rather than the rendered string means the demo is reading the same
     source the tile is, it is unaffected by the rolling wheels the results
     module lays over that tile, and at k=1 it formats to exactly the string
     the server printed. */
  const statBy=rx=>{
    const st=mm.$$('.stat').find(s=>{
      const k=mm.$('.stat-k',s);
      return k&&rx.test(k.textContent.trim());
    });
    const v=st&&mm.$('[data-count]',st);
    if(!v)return null;
    const d=v.dataset;
    return {n:parseFloat(d.count)||0,dp:+(d.decimals||0),
            pre:d.prefix||'',suf:d.suffix||''};
  };
  const figText=(f,k)=>f.pre+(f.n*k).toLocaleString('en-US',
    {minimumFractionDigits:f.dp,maximumFractionDigits:f.dp})+f.suf;

  /* --- the six demos ---------------------------------------------------
     Each returns {dur, steps:[[ms,fn]…], frame(t), rest()} or null if the
     page does not hold what it needs. `steps` are fired once, in order, by
     the loop; `frame` is for the two demos that are really interpolating
     something rather than handing a transition a destination. */
  const DEMOS={

    // The site draws itself, then somebody clicks the button on it. The
    // three wires are the server's own (home.py puts them in the well so the
    // no-script page shows what the demo is about); they are scaled to
    // nothing, let go left to right, and given their widths back at rest.
    websites(well){
      const wires=mm.$$('.wire',well);
      if(!wires.length)return null;
      wires.forEach((w,i)=>{
        w.style.transformOrigin='left center';
        w.style.transform='scaleX(0)';
        w.style.transition='transform .55s var(--ease) '+(i*0.14).toFixed(2)+'s';
      });
      void well.offsetWidth;            // the 0 has to be a rendered state
      const btn=mk('i','mm-btn',well), dot=mk('i','mm-dot',well);
      return {
        dur:3000,
        steps:[
          [0,   ()=>wires.forEach(w=>{w.style.transform='scaleX(1)'})],
          [1100,()=>btn.classList.add('on')],
          [1400,()=>dot.classList.add('go')],
          [2320,()=>{dot.classList.add('tap');btn.classList.add('hit')}],
          [2620,()=>{dot.classList.remove('tap');btn.classList.remove('hit')}],
        ],
        rest(){wires.forEach(w=>{
          w.style.removeProperty('transform');
          w.style.removeProperty('transition');
          w.style.removeProperty('transform-origin');
        })},
      };
    },

    // The campaign runs: views climb from nothing to the figure the results
    // band prints, and the rise mark lifts off the end of them.
    'meta-ads'(well){
      const f=statBy(/^views/i);
      if(!f)return null;
      const n=mk('b','mm-num mono',well), up=mk('i','mm-up mono',well);
      up.textContent='↑';
      n.textContent=figText(f,0);
      return {
        dur:3000,
        steps:[[2260,()=>{n.textContent=figText(f,1);up.classList.add('on')}]],
        frame(t){
          if(t>=2260)return;             // the step above lands it exactly
          n.textContent=figText(f,1-Math.pow(1-clamp(t/2200,0,1),3));
        },
      };
    },

    // The feed goes past: the three reels' own posters, one window at a
    // time. The posters are the ones the reels lower down the page carry, so
    // the card is showing the work rather than a drawing of it.
    social(well){
      const posters=mm.$$('video[data-reel]')
        .map(v=>v.getAttribute('poster')).filter(Boolean);
      if(!posters.length)return null;
      const win=mk('i','mm-feed',well);
      const col=document.createElement('i');
      col.className='mm-feed-col';
      col.style.height=(posters.length*100)+'%';
      posters.forEach(p=>{
        const c=document.createElement('i');
        c.style.flex='0 0 '+(100/posters.length)+'%';
        c.style.backgroundImage='url("'+p.replace(/"/g,'%22')+'")';
        col.appendChild(c);
      });
      win.appendChild(col);
      const slot=2600/posters.length;
      return {
        dur:3000,
        steps:posters.map((_,i)=>[Math.round(i*slot),()=>{
          col.style.transform='translateY('+(-i*100/posters.length).toFixed(4)+'%)';
        }]),
      };
    },

    // The mark's caption, set six times — his README's "per-service marks =
    // the Mendoza logo with the text changed", as a verb. The six names are
    // read off the six cards, so this card cannot name a service the grid
    // does not have.
    logo(well){
      const names=mm.$$('.svc[data-demo] h3').map(h=>h.textContent.trim()).filter(Boolean);
      if(!names.length)return null;
      const cap=mk('b','mm-type mono',well);
      cap.setAttribute('aria-hidden','true');
      const slot=3000/names.length;
      return {
        dur:3000,
        frame(t){
          const i=clamp(Math.floor(t/slot),0,names.length-1);
          const s=names[i], k=(t-i*slot)/slot;
          // typed over the first two-thirds of its slot, held for the rest
          const out=s.slice(0,Math.ceil(s.length*clamp(k/0.66,0,1)));
          if(out!==cap.textContent)cap.textContent=out;
        },
      };
    },

    // Take off, cross, land. The quad is the server's own (art.quad(), parked
    // at the left of the well); this is the only demo that is really flown
    // frame by frame, because a bank that is not proportional to the speed
    // reads as a spin rather than as a turn. The shadow is what says it left
    // the ground.
    drones(well){
      const q=mm.$('.quad',well);
      if(!q)return null;
      const sh=mk('i','mm-shadow',well);
      const run=Math.max(30,(well.clientWidth||300)-46-28);
      q.style.willChange='transform';
      return {
        dur:3000,
        frame(t){
          const up=clamp(t/420,0,1), down=clamp((t-2380)/440,0,1);
          const k=clamp((t-420)/1960,0,1);
          const alt=up-down;                       // 0 → 1 → 0
          const x=ease(k)*run, y=-15*alt, rot=vel(k)*7*(1-down);
          q.style.transform='translateY(-50%) translate('+x.toFixed(1)+'px,'
            +y.toFixed(1)+'px) rotate('+rot.toFixed(2)+'deg)';
          sh.style.transform='translateX('+x.toFixed(1)+'px) scaleX('
            +(1-0.28*alt).toFixed(3)+')';
          sh.style.opacity=(0.34-0.2*alt).toFixed(3);
        },
        rest(){
          q.style.removeProperty('transform');
          q.style.removeProperty('will-change');
        },
      };
    },

    // The leads line draws itself and the Leads Center figure lands on the
    // end of it. Both come off the results band below: the polyline's own
    // ninety points, thinned to thirty for a 56px well, and that tile's
    // data-count. Drew's shape, Drew's number, at card size.
    'lead-conversion'(well){
      const src=mm.$('.chart-line'), f=statBy(/lead/i);
      if(!src||!f)return null;
      const raw=(src.getAttribute('points')||'').trim().split(/\s+/);
      if(raw.length<4)return null;
      const pts=raw.filter((_,i)=>i%3===0||i===raw.length-1).join(' ');
      const svg=mkNS('svg','mm-chart',well);
      svg.setAttribute('viewBox','0 0 300 100');
      svg.setAttribute('preserveAspectRatio','none');
      svg.setAttribute('aria-hidden','true');
      const line=mkNS('polyline','mm-line',svg);
      line.setAttribute('points',pts);
      line.setAttribute('vector-effect','non-scaling-stroke');
      const len=(line.getTotalLength&&line.getTotalLength())||600;
      line.style.strokeDasharray=len;
      line.style.strokeDashoffset=len;
      const fig=mk('b','mm-fig mono',well);
      fig.textContent=figText(f,1);
      fig.setAttribute('aria-hidden','true');
      void well.offsetWidth;
      return {
        dur:3000,
        steps:[[0,()=>{line.style.strokeDashoffset='0'}],
               [2280,()=>fig.classList.add('on')]],
      };
    },
  };

  /* --- the runner ------------------------------------------------------
     One demo per card at a time, driven off the page's one rAF loop, which
     is held open with pump(1) only while something is actually running. A
     finished demo takes its callback back out of the loop, sweeps its own
     nodes and puts back anything it borrowed. */
  const running=new WeakSet();
  const start=card=>{
    const well=mm.$('[data-live]',card);
    if(!well||running.has(card))return;
    const make=DEMOS[card.dataset.demo];
    if(!make)return;
    let d=null;
    try{d=make(well)}catch(e){d=null}
    if(!d)return;
    running.add(card);
    card.classList.add('mm-on');
    let t0=0,i=0,off=null;
    const stop=()=>{
      if(off)off();
      mm.pump(-1);
      running.delete(card);
      card.classList.remove('mm-on');
      try{d.rest&&d.rest()}catch(e){}
      mm.$$('.mm-fx',well).forEach(n=>n.remove());
    };
    off=mm.add(now=>{
      if(!t0)t0=now;
      const t=now-t0;
      const steps=d.steps||[];
      while(i<steps.length&&t>=steps[i][0]){
        try{steps[i][1]()}catch(e){}
        i++;
      }
      if(d.frame){try{d.frame(Math.min(t,d.dur))}catch(e){}}
      if(t>=d.dur)stop();
    });
    mm.pump(1);
  };

  cards.forEach(card=>{
    if(mm.fine){
      card.addEventListener('pointerenter',e=>{
        if(e.pointerType==='touch')return;      // a tap is not a hover
        start(card);
      });
    }else{
      // The card is a link to the service's page. On a coarse pointer the
      // first tap is the hover this device does not have — it plays the demo
      // and stays put; every tap after that opens the page. Nothing is
      // intercepted on a desktop, and Enter on a focused card always follows
      // the link.
      card.addEventListener('click',e=>{
        if(card.__mmSeen)return;
        card.__mmSeen=true;
        e.preventDefault();
        start(card);
      });
    }
    // A keyboard visitor gets the demo too: the card is a link, so tabbing
    // onto it is the closest thing they have to pointing at it.
    card.addEventListener('focus',()=>start(card));
  });
})();


/* =====================================================================
   THE RESULTS BAND — the figures roll, the bars fill, the line draws

   Both directions, every time, which is Open Air Gallery's Live: its owner
   asked to "see motion as he scrolls up and down from them", and the same
   is true here — the results band is the middle of the page and is as often
   arrived at from below as from above.

   Every value moved here is already in the server HTML and stays there. The
   figures keep their own characters (the wheels are laid over them and are
   aria-hidden), the bars keep results.py's inline widths and are scaled
   rather than resized, and the chart keeps all ninety of its points. This
   module animates the page; it does not supply it.
   ===================================================================== */
(function(){
  const mm=window.mm;
  if(!mm||!mm.motion) return;
  const figs=mm.$$('[data-count]'), bars=mm.$$('[data-bar]'), charts=mm.$$('[data-chart]');
  if(!figs.length&&!bars.length&&!charts.length) return;

  const LIVE=0.35;                 // the share of a thing that has to show
  const STAG=0.04;                 // between one wheel and the next

  /* A figure's digits as columns of 0-9, over the figure's own text.
     Straight out of /root/openairgallery-src/site/js/site.js: the text node
     is replaced by a wrapper holding the original characters (the ghost,
     which is what carries the box) and a row of wheels over them. The wheel
     on the right sets off first, the way a counter's wheels turn, and each
     one's own turn is shortened by the stagger ahead of it so a wide figure
     does not take proportionally longer than a narrow one. */
  const rollUp=host=>{
    const made=[];
    [...host.childNodes].forEach(node=>{
      if(node.nodeType!==3||!/[0-9]/.test(node.nodeValue))return;
      const text=node.nodeValue;
      let n=0;
      for(const ch of text) if(ch>='0'&&ch<='9')n++;
      const span=cls=>{const s=document.createElement('span');s.className=cls;return s};
      const wrap=span('roll'), ghost=span('roll-g'), cols=span('roll-w');
      ghost.textContent=text;                      // the real figure, and the real box
      cols.setAttribute('aria-hidden','true');
      const all=Math.min(1.2,0.4+0.175*(n-1));
      const each=Math.max(0.28,all-STAG*(n-1));
      let right=n;
      for(const ch of text){
        if(ch<'0'||ch>'9'){
          const s=span('roll-x');
          s.textContent=ch;                        // $ , . + % — never rolled
          cols.appendChild(s);
          continue;
        }
        right--;
        const win=span('roll-d'), col=span('roll-c');
        col.setAttribute('style','--v:'+ch+';--rt:'+each.toFixed(3)+'s;--rd:'
          +(right*STAG).toFixed(3)+'s');
        for(let d=0;d<10;d++){
          const cell=document.createElement('span');
          cell.textContent=String(d);
          col.appendChild(cell);
        }
        win.appendChild(col);
        cols.appendChild(win);
      }
      wrap.appendChild(ghost);
      wrap.appendChild(cols);
      node.parentNode.replaceChild(wrap,node);
      made.push(wrap);
    });
    return made;
  };

  /* No observer, nothing to say when a thing is on screen — so nothing is
     taken apart. The figures stay as text, the bars stay at their widths
     (the stylesheet's 2.8s bail-out sees to that) and the line stays drawn.
     This has to be decided BEFORE anything is built, which is why the
     observer is made first. */
  const wheels=new Map(), len=new WeakMap();
  const io=mm.io(es=>es.forEach(e=>{
    const el=e.target, on=e.intersectionRatio>=LIVE;
    const w=wheels.get(el);
    if(w){w.forEach(r=>r.classList.toggle('in',on));return}
    if(el.hasAttribute('data-bar')){el.classList.toggle('in',on);return}
    if(el.hasAttribute('data-chart')){
      const line=mm.$('.chart-line',el), fill=mm.$('.chart-fill',el), L=len.get(el);
      if(line&&L){line.style.strokeDashoffset=on?'0':L}
      if(fill){
        fill.style.transitionDelay=on?'1.15s':'0s';   // it follows the stroke in
        fill.style.opacity=on?'1':'0';
      }
    }
  }),{threshold:[0,LIVE]});
  if(!io) return;

  figs.forEach(el=>{
    const made=rollUp(el);
    if(!made.length)return;
    wheels.set(el,made);
    io.observe(el);
  });
  // .mm-live cancels the stylesheet's 2.8s bail-out on this bar: from here
  // the observer owns it, in both directions. See 15-motion.css.
  bars.forEach(el=>{el.classList.add('mm-live');io.observe(el)});
  charts.forEach(svg=>{
    const line=mm.$('.chart-line',svg), fill=mm.$('.chart-fill',svg);
    if(!line||!line.getTotalLength)return;
    const L=Math.ceil(line.getTotalLength())||0;
    if(!L)return;
    len.set(svg,L);
    line.style.strokeDasharray=L;
    line.style.strokeDashoffset=L;
    if(fill)fill.style.opacity='0';
    io.observe(svg);
  });
})();
