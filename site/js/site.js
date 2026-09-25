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
   THE SIX LIVE TILES — off scroll, and they keep going

   The owner, 2026-09-25: "they should trigger off scroll and keep going after
   they are triggered, tapping should be reserved for learn more."

   So: a card's demo starts when the card is 35% on screen, runs its three
   seconds, HOLDS the state it ended on for a beat and runs again, for as long
   as the card is in view. It pauses when the card leaves and starts a fresh
   cycle when it comes back. Nothing here listens for a hover, a tap or a
   focus: the card is a plain link to its service page and one tap is Learn
   more, always (CLAUDE.md rule 4).

   Every well is already the picture the demo ends on — home.py draws the
   wireframe, the landed figure, the reel, the caption, the quad on its horizon
   and the drawn leads line into the server HTML. This module therefore never
   builds the content and never takes it away:

     arm()    puts the well into the state the run STARTS from
     frame(t) is the run, arithmetic rather than a stack of transitions, so a
              cycle can begin on any frame with nothing left committed
     rest()   strips every inline style the run set, which lands the well back
              on exactly what the server sent

   Two consequences, both of them the bugs the owner reported. Nothing is
   removed at the end of a run, so the Meta counter's figure is on the card at
   every moment of the visit — it counts up, holds, and restarts from zero on
   the next cycle rather than blanking. And because there is no tap handler,
   a tap can no longer either play a demo or fail to.

   The one node this file makes is the website card's cursor: a pointer drawn
   into a static wireframe would be a picture of nothing, so it exists only
   while there is a script to move it. It is built once per card and reused by
   every cycle.
   ===================================================================== */
(function(){
  const mm=window.mm;
  if(!mm||!mm.motion) return;
  const cards=mm.$$('.svc[data-demo]');
  if(!cards.length) return;

  const DUR=3000;                 // one run
  const HOLD=1200;                // the end state, held, before the next one
  const LIVE=0.35;                // the share of a card that has to show
  const clamp=(v,a,b)=>v<a?a:v>b?b:v;
  const ease=k=>k*k*(3-2*k);      // smoothstep
  const vel=k=>4*k*(1-k);         // its speed, normalised to 1
  const seg=(t,a,b)=>clamp((t-a)/(b-a),0,1);

  /* A figure the server printed, as arithmetic.

     home.py puts data-fig (and -prefix/-suffix/-decimals) on the well's own
     figure, straight out of results.py, so a counter can only ever climb to a
     number this page already says. NOT data-count: that attribute belongs to
     the results band's module, which collects it across the whole document
     and would roll this one's digits as well. */
  const figOf=el=>{
    if(!el||!el.dataset||el.dataset.fig===undefined)return null;
    return {n:parseFloat(el.dataset.fig)||0,dp:+(el.dataset.figDecimals||0),
            pre:el.dataset.figPrefix||'',suf:el.dataset.figSuffix||''};
  };
  const figText=(f,k)=>f.pre+(f.n*k).toLocaleString('en-US',
    {minimumFractionDigits:f.dp,maximumFractionDigits:f.dp})+f.suf;

  // Inline styles the run sets and rest() takes off again. Nothing else in
  // this file touches .style, so "back to the server's HTML" is one call.
  const wipe=(el,...props)=>{if(el)props.forEach(p=>el.style.removeProperty(p))};

  /* --- the six demos ---------------------------------------------------
     Each returns {arm, frame, steps, rest} over the nodes the server already
     put in the well, or null if this page does not hold them. */
  const DEMOS={

    // The site draws itself and somebody presses the button on it. The three
    // rules are let go left to right, the button lands, the cursor crosses
    // the well and presses.
    websites(well){
      const wires=mm.$$('.wire',well), btn=mm.$('.wf-btn',well);
      if(!wires.length)return null;
      const cur=document.createElement('i');
      cur.className='mm-cursor';
      cur.setAttribute('aria-hidden','true');
      well.appendChild(cur);
      let tx=0,ty=0;
      wires.forEach(w=>{w.style.transformOrigin='left center'});
      return {
        arm(){
          wires.forEach(w=>{w.style.transform='scaleX(0)'});
          if(btn)btn.style.opacity='0';
          cur.style.opacity='0';
          // The button's centre, in the well's own pixels. Read once a cycle
          // rather than once a frame, and re-read every cycle so a resized
          // window is flown correctly.
          if(btn){tx=btn.offsetLeft+btn.offsetWidth/2;ty=btn.offsetTop+btn.offsetHeight/2}
          else{tx=(well.clientWidth||300)-45;ty=(well.clientHeight||120)*0.82}
        },
        frame(t){
          wires.forEach((w,i)=>{
            w.style.transform='scaleX('+ease(seg(t,i*150,i*150+560)).toFixed(4)+')';
          });
          if(btn){
            const k=ease(seg(t,1050,1360));
            btn.style.opacity=(0.9*k).toFixed(3);
            const press=seg(t,2320,2420)-seg(t,2520,2640);
            btn.style.transform='scale('+(0.82+0.18*k-0.08*press).toFixed(4)+')';
          }
          const walk=ease(seg(t,1380,2300)), press=seg(t,2300,2400)-seg(t,2500,2620);
          const x0=14, y0=(well.clientHeight||120)*0.58;
          cur.style.opacity=(seg(t,1300,1500)-seg(t,2760,2960)).toFixed(3);
          cur.style.transform='translate('+(x0+(tx-x0)*walk).toFixed(1)+'px,'
            +(y0+(ty-y0)*walk).toFixed(1)+'px) scale('+(1-0.42*press).toFixed(3)+')';
        },
        rest(){
          wires.forEach(w=>wipe(w,'transform','transform-origin'));
          wipe(btn,'opacity','transform');
          cur.style.opacity='0';
          wipe(cur,'transform');
        },
      };
    },

    // The campaign runs. The figure climbs to the one the Results band prints
    // and the rise mark lifts off the end of it — and then it STAYS there for
    // the hold and restarts from zero, so the card is never showing an empty
    // box where a number was (the owner, 2026-09-25: "Meta business suite
    // number disappears after popping up").
    'meta-ads'(well){
      const n=mm.$('.mm-num',well), up=mm.$('.mm-up',well), f=figOf(n);
      if(!n||!f)return null;
      const printed=n.textContent;
      return {
        arm(){n.textContent=figText(f,0)},
        frame(t){
          const k=t>=2200?1:1-Math.pow(1-clamp(t/2200,0,1),3);
          const s=k>=1?printed:figText(f,k);
          if(s!==n.textContent)n.textContent=s;
          if(up){
            const p=ease(seg(t,2240,2560));
            up.style.opacity=p.toFixed(3);
            up.style.transform='translateY('+(-8*p).toFixed(2)+'px)';
          }
        },
        rest(){n.textContent=printed;wipe(up,'opacity','transform')},
      };
    },

    // The feed goes past — Kelly's three reel posters, each one filling the
    // well, cross-fading one to the next. The frames are the server's own
    // <img>s (home.py), at the well's full width and height.
    social(well){
      const cells=mm.$$('.mm-reel',well);
      if(cells.length<2)return null;
      const slot=DUR/cells.length;
      const show=i=>cells.forEach((c,j)=>c.classList.toggle('is-on',j===i));
      return {
        arm(){show(0)},
        steps:cells.map((_,i)=>[Math.round(i*slot),()=>show(i)]),
        rest(){show(0)},
      };
    },

    // The mark's caption, set six times — his README's "per-service marks =
    // the Mendoza logo with the text changed", as a verb. The six names are
    // read off the six cards, so this card cannot name a service the grid
    // does not have, and the last of them is the one the server printed.
    logo(well){
      const cap=mm.$('.mm-type',well);
      const names=mm.$$('.svc[data-demo] h3').map(h=>h.textContent.trim()).filter(Boolean);
      if(!cap||!names.length)return null;
      const printed=cap.textContent, slot=DUR/names.length;
      return {
        frame(t){
          const i=clamp(Math.floor(t/slot),0,names.length-1);
          const s=names[i], k=(t-i*slot)/slot;
          // typed over the first two thirds of its slot, held for the rest
          const out=s.slice(0,Math.ceil(s.length*clamp(k/0.66,0,1)));
          if(out!==cap.textContent)cap.textContent=out;
        },
        rest(){cap.textContent=printed},
      };
    },

    // Take off, cross the well, land. This is the one demo flown frame by
    // frame, because a bank that is not proportional to the speed reads as a
    // spin rather than as a turn; the shadow on the horizon is what says the
    // machine left the ground. Each cycle crosses the other way, so the quad
    // patrols the well instead of snapping back to the left between runs.
    drones(well){
      const q=mm.$('.quad',well), sh=mm.$('.mm-shadow',well);
      if(!q)return null;
      let run=0, dir=1;
      q.style.willChange='transform';
      return {
        arm(){
          run=Math.max(24,(well.clientWidth||300)-(q.offsetWidth||46)-28);
          dir=-dir;
        },
        frame(t){
          const up=seg(t,0,420), down=seg(t,2380,2820);
          const k=ease(seg(t,420,2380));
          const alt=up-down;                         // 0 → 1 → 0
          const d=dir>0?1:-1;
          const x=d>0?k*run:run-k*run, y=-16*alt, rot=vel(seg(t,420,2380))*7*(1-down)*d;
          q.style.transform='translateY(-50%) translate('+x.toFixed(1)+'px,'
            +y.toFixed(1)+'px) rotate('+rot.toFixed(2)+'deg)';
          if(sh){
            sh.style.transform='translateX('+x.toFixed(1)+'px) scaleX('
              +(1-0.28*alt).toFixed(3)+')';
            sh.style.opacity=(0.34-0.2*alt).toFixed(3);
          }
        },
        rest(){wipe(q,'transform','will-change');wipe(sh,'transform','opacity')},
      };
    },

    // The daily-leads line draws itself and the Leads Center figure lands on
    // the end of it. Both are the server's: the well's own polyline (Drew's
    // ninety days, thinned) and that tile's figure.
    'lead-conversion'(well){
      const line=mm.$('.mm-line',well), area=mm.$('.mm-area',well),
            fig=mm.$('.mm-fig',well);
      if(!line||!line.getTotalLength)return null;
      const len=Math.ceil(line.getTotalLength())||0;
      if(!len)return null;
      return {
        arm(){line.style.strokeDasharray=len},
        frame(t){
          line.style.strokeDashoffset=(len*(1-ease(seg(t,0,2200)))).toFixed(1);
          if(area)area.style.opacity=(0.13*seg(t,700,1900)).toFixed(4);
          if(fig){
            const p=ease(seg(t,2260,2580));
            fig.style.opacity=p.toFixed(3);
            fig.style.transform='translateY('+(-10*(1-p)).toFixed(2)
              +'px) scale('+(0.86+0.14*p).toFixed(3)+')';
          }
        },
        rest(){
          wipe(line,'stroke-dasharray','stroke-dashoffset');
          wipe(area,'opacity');
          wipe(fig,'opacity','transform');
        },
      };
    },
  };

  /* --- the runner ------------------------------------------------------
     One cycle is arm(), DUR of frames, then HOLD with the last frame left
     standing, then arm() again. The page's one rAF loop drives it and is held
     open with pump(1) only for the cards that are actually on screen, so a
     visitor at the top of the page is paying for nothing below it.

     A demo is built once per card, on the first time it is needed, and its
     nodes live for the rest of the visit — that is what makes the end state
     persist. play()/pause() only add and remove a frame callback. */
  const built=new WeakMap();
  const of=card=>{
    if(built.has(card))return built.get(card);
    const well=mm.$('[data-live]',card), make=DEMOS[card.dataset.demo];
    let d=null;
    if(well&&make){try{d=make(well)}catch(e){d=null}}
    built.set(card,d);
    return d;
  };
  const step=(d,t,from)=>{
    const steps=d.steps||[];
    let i=from;
    while(i<steps.length&&t>=steps[i][0]){try{steps[i][1]()}catch(e){}i++}
    return i;
  };
  const play=card=>{
    if(card.__mmOff)return;
    const d=of(card);
    if(!d)return;
    let t0=0,i=0;
    const arm=()=>{i=0;try{d.arm&&d.arm()}catch(e){}};
    arm();
    card.classList.add('mm-run');
    card.__mmOff=mm.add(now=>{
      if(!t0)t0=now;
      let t=now-t0;
      if(t>DUR+HOLD){t0=now;t=0;arm()}       // the next cycle
      i=step(d,Math.min(t,DUR),i);
      if(d.frame){try{d.frame(Math.min(t,DUR))}catch(e){}}
    });
    mm.pump(1);
  };
  const pause=card=>{
    if(!card.__mmOff)return;
    card.__mmOff();
    card.__mmOff=null;
    mm.pump(-1);
    card.classList.remove('mm-run');
    const d=built.get(card);
    if(d){try{d.rest&&d.rest()}catch(e){}}   // back to the server's own well
  };

  const io=mm.io(es=>es.forEach(e=>{
    if(e.intersectionRatio>=LIVE)play(e.target); else pause(e.target);
  }),{threshold:[0,LIVE]});
  // No IntersectionObserver, no way to know what is on screen — so every card
  // runs. The alternative is six wells that never move on a browser that can
  // still animate them perfectly well.
  if(io)cards.forEach(c=>io.observe(c)); else cards.forEach(play);
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
  // Two bar shapes, because the site has two: Home marks each row with
  // data-bar (its percentage), the inner pages mark the panel with data-bars
  // and leave the rows plain. Neither is read for a value — the inline width
  // the server computed is the width, and this only scales it — so one
  // selector covers both and a row that matches neither simply stays drawn.
  const figs=mm.$$('[data-count]'),
        bars=mm.$$('[data-bar],[data-bars] .bar'),
        charts=mm.$$('[data-chart]');
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
  // .mm-live is the script taking the row over — it is what puts the bar at
  // zero in the first place, and it goes on only now, with the observer that
  // will fill it already made. See 15-motion.css.
  bars.forEach(el=>{el.classList.add('mm-live');io.observe(el)});
  charts.forEach(svg=>{
    const line=mm.$('.chart-line',svg), fill=mm.$('.chart-fill',svg);
    if(!line||!line.getTotalLength)return;
    const L=Math.ceil(line.getTotalLength())||0;
    if(!L)return;
    len.set(svg,L);
    // Suppressed, set, committed, restored — the same trap the tile's little
    // chart fell into: the line is already on screen and already painted, so
    // handing it a full dash with the transition live spends 1.8s wiping a
    // drawn line away rather than starting from an undrawn one.
    line.style.transition='none';
    if(fill)fill.style.transition='none';
    line.style.strokeDasharray=L;
    line.style.strokeDashoffset=L;
    if(fill)fill.style.opacity='0';
    getComputedStyle(line).strokeDashoffset;
    line.style.transition='';
    if(fill)fill.style.transition='';
    io.observe(svg);
  });
})();


/* =====================================================================
   THE REELS — armed on approach, playing in view, sound only if asked

   Kelly's three films are posters in the server HTML with preload="none",
   so a visitor with no script, with reduced motion asked for, or on a
   metered connection gets three stills and no request at all. That is the
   render, and this module is what happens on top of it:

     approaching   preload flips to metadata and the file is fetched — once,
                   300px before the frame reaches the viewport, so the clip
                   is ready rather than starting on a black frame
     in view       muted, looping, playing
     out of view   paused, and its sound given up

   Sound is never started by this site. The play glyph is decoration until
   here — 10-home.css gives it pointer-events:none — and the script upgrades
   it to a real button on the reels it has taken over, so a tap (a user
   gesture, which is the only thing a browser will unmute for) turns sound on
   for THAT reel and off for any other. Leaving the frame gives it up again:
   sound that carries on out of sight is sound nobody asked for twice.
   ===================================================================== */
(function(){
  const mm=window.mm;
  if(!mm||!mm.motion||mm.save) return;      // saveData: the posters, and nothing else
  const reels=mm.$$('video[data-reel]');
  if(!reels.length) return;

  const near=mm.io(es=>es.forEach(e=>{
    if(!e.isIntersecting)return;
    const v=e.target;
    // preload alone: flipping it off "none" is what starts the fetch, and
    // v.load() here resets the element and aborts the request it has just
    // made — one ERR_ABORTED per reel in the network log, and two requests
    // per film instead of one. Coming into view calls play(), which fetches
    // on any browser that ignored the preload change.
    if(v.preload!=='metadata')v.preload='metadata';
    near.unobserve(v);                      // arming is a once
  }),{rootMargin:'300px 0px'});
  const live=mm.io(es=>es.forEach(e=>{
    const v=e.target;
    if(e.intersectionRatio>=0.4){
      v.muted=(v!==loud);            // only the one that was asked for is heard
      const p=v.play(); p&&p.catch(()=>{});
    }else{
      hush(v);
      try{v.pause()}catch(_){}
    }
  }),{threshold:[0,0.4]});
  if(!near||!live) return;

  let loud=null;                            // the one reel allowed to be heard

  const hush=v=>{
    v.muted=true;
    const ph=v.closest('.phone');
    if(ph){
      ph.classList.remove('is-snd');
      const chip=mm.$('.mm-snd',ph); if(chip)chip.remove();
      const g=mm.$('.play',ph);
      if(g){g.setAttribute('aria-pressed','false');g.setAttribute('aria-label','Play with sound')}
    }
    if(loud===v)loud=null;
  };

  reels.forEach(v=>{
    v.muted=true;
    near.observe(v);
    live.observe(v);
    const ph=v.closest('.phone'), g=ph&&mm.$('.play',ph);
    if(!g)return;
    ph.classList.add('mm-sound');
    g.removeAttribute('aria-hidden');
    g.setAttribute('role','button');
    g.setAttribute('tabindex','0');
    g.setAttribute('aria-pressed','false');
    g.setAttribute('aria-label','Play with sound');
    const toggle=()=>{
      if(loud===v){hush(v);return}
      if(loud)hush(loud);
      loud=v;
      v.muted=false;
      const p=v.play(); p&&p.catch(()=>{});
      ph.classList.add('is-snd');
      if(!mm.$('.mm-snd',ph)){
        const chip=document.createElement('span');
        chip.className='mm-snd mono';
        chip.textContent='Sound on';
        ph.appendChild(chip);
      }
      g.setAttribute('aria-pressed','true');
      g.setAttribute('aria-label','Mute');
    };
    g.addEventListener('click',toggle);
    g.addEventListener('keydown',e=>{
      if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle()}
    });
  });
})();


/* =====================================================================
   THE CLIENT STRIP — the light walks

   The strip is monochrome with one mark left in colour (home.py's LIT), and
   hovering any of them lights it — all of that is CSS and happens with no
   script at all. This is the slow part: under html.motion the lit ring walks
   to the next mark every four seconds, so a visitor who looks at the strip
   for a moment sees each of Drew's clients in their own colours rather than
   whichever one the markup happened to light.

   It pauses while the pointer is on the strip (you are reading it; it should
   hold still) and while the strip is off screen (an interval firing at a
   section nobody is looking at is just a timer). Four seconds is deliberate:
   the plan asks for a slow, gentle highlight, not a carousel.
   ===================================================================== */
(function(){
  const mm=window.mm;
  if(!mm||!mm.motion) return;
  const strip=mm.$('[data-demo="logos"]');
  if(!strip) return;
  const chips=mm.$$('.chip',strip);
  if(chips.length<2) return;

  let i=chips.findIndex(c=>c.classList.contains('is-lit'));
  if(i<0)i=0;
  let timer=null, hover=false, seen=false;
  const step=()=>{
    chips[i].classList.remove('is-lit');
    i=(i+1)%chips.length;
    chips[i].classList.add('is-lit');
  };
  const halt=()=>{if(timer){clearInterval(timer);timer=null}};
  const run=()=>{if(timer||hover||!seen)return;timer=setInterval(step,4000)};

  const io=mm.io(es=>es.forEach(e=>{
    seen=e.isIntersecting;
    seen?run():halt();
  }),{threshold:0.2});
  if(!io) return;

  strip.addEventListener('pointerenter',()=>{hover=true;halt()});
  strip.addEventListener('pointerleave',()=>{hover=false;run()});
  io.observe(strip);
})();
