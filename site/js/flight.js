/* Mendoza Marketing — THE FLIGHT PATH.  Home only.
 *
 * The concept the owner picked: "His little quad lifts off the Drones card
 * and flies the site: it rides the scroll, banking through the section gaps,
 * casting a soft shadow on the panels, and every stat it crosses on the
 * Results band lights as it passes overhead. Drag it and it follows your
 * finger with real inertia and a barrel roll on a flick, then rejoins its
 * route. Reaching the footer it lands on the Mendoza mark. An aerial survey
 * of the page, which is the business."
 *
 * Three things make it that rather than a sprite on a timer.
 *
 * THE ROUTE IS THE PAGE.  Nothing here holds a coordinate. The anchors are
 * read off the document every time it is measured — the Drones card's demo
 * well (the pad), the vertical midpoint of every gap between two <section>s
 * alternating left third / right third so the path has to bank, the four
 * figures on the Results band, the three reels, and the Mendoza mark in the
 * footer — and a centripetal Catmull-Rom is drawn through them in DOCUMENT
 * coordinates. Re-measured on resize and whenever the document's height
 * changes, so a route can never describe a page that has moved.
 *
 * THE SCROLL IS THE THROTTLE.  The aircraft holds about 35% down the
 * viewport, so scrolling flies it: it is parked on the pad until the visitor
 * reaches the Drones card, it flies the route ahead of them, and it lands on
 * the mark. A critically damped spring on the along-path parameter is what
 * keeps a scroll wheel's steps from reading as jitter.
 *
 * IT IS DECORATION.  The layer is absolutely positioned over the document
 * with pointer-events:none and `contain: layout paint` (16-flight.css); the
 * only element that takes a pointer is the aircraft itself. Nothing in flow
 * moves, the document's height is unchanged, and with no script or with
 * prefers-reduced-motion the layer is display:none and the page is exactly
 * what the server wrote — CLAUDE.md rule 4.
 *
 * Loaded on Home only, through layout()'s extra_scripts hook, after site.js:
 * `mm` is the page's one rAF loop and this module holds it open with pump(1)
 * only while something is actually moving. A parked aircraft on a page
 * nobody is scrolling asks for no frames at all.
 */
(function(){
  const mm=window.mm;
  if(!mm||!mm.motion)return;                       // the whole contract
  const layer=document.querySelector('[data-flight]');
  if(!layer)return;
  const quad=layer.querySelector('.flight-quad');
  if(!quad)return;

  const clamp=(v,a,b)=>v<a?a:v>b?b:v;

  /* The shadow is the only node this module builds. It is the thing that
     says the machine is over the page rather than on it. */
  const shade=document.createElement('i');
  shade.className='flight-shade';
  shade.setAttribute('aria-hidden','true');
  layer.insertBefore(shade,quad);

  /* ---- measuring ------------------------------------------------------
     offsetLeft/offsetTop up the offsetParent chain, not getBoundingClientRect:
     half the page is a .rv holding a translateY(22px) until its reveal fires,
     and a rect would put those anchors 22px below where the section actually
     is. The offset chain is layout, which is what a route should be drawn on. */
  const docBox=el=>{
    let x=0,y=0,n=el;
    while(n){x+=n.offsetLeft;y+=n.offsetTop;n=n.offsetParent}
    const w=el.offsetWidth,h=el.offsetHeight;
    return {l:x,t:y,r:x+w,b:y+h,w:w,h:h,x:x+w/2,y:y+h/2};
  };

  /* ---- the spline -----------------------------------------------------
     Centripetal Catmull-Rom (alpha = .5). Uniform Catmull-Rom loops and
     cusps the moment two anchors are much closer together than their
     neighbours, which on this page happens every time four stat tiles sit in
     one row; centripetal cannot. */
  const crPoint=(p0,p1,p2,p3,t0,t1,t2,t3,t)=>{
    const a1=(t1-t)/(t1-t0), b1=(t-t0)/(t1-t0);
    const a2=(t2-t)/(t2-t1), b2=(t-t1)/(t2-t1);
    const a3=(t3-t)/(t3-t2), b3=(t-t2)/(t3-t2);
    const A1x=a1*p0.x+b1*p1.x, A1y=a1*p0.y+b1*p1.y;
    const A2x=a2*p1.x+b2*p2.x, A2y=a2*p1.y+b2*p2.y;
    const A3x=a3*p2.x+b3*p3.x, A3y=a3*p2.y+b3*p3.y;
    const c1=(t2-t)/(t2-t0), d1=(t-t0)/(t2-t0);
    const c2=(t3-t)/(t3-t1), d2=(t-t1)/(t3-t1);
    const B1x=c1*A1x+d1*A2x, B1y=c1*A1y+d1*A2y;
    const B2x=c2*A2x+d2*A3x, B2y=c2*A2y+d2*A3y;
    return {x:a2*B1x+b2*B2x, y:a2*B1y+b2*B2y};
  };

  const SEG=14;                       // samples per segment
  let R=null;                         // the route: X, Y, S (arc length)
  let lit=[];                         // the tiles that light as it passes
  let edges=[];                       // panel edges, for altitude
  let FQ=.875;                        // how much of the hit box the drawing fills

  const route=()=>{
    const pad=document.querySelector('.svc[data-demo="drones"] .svc-demo');
    const mark=document.querySelector('footer .foot-brand img');
    const secs=[...document.querySelectorAll('main>section')];
    if(!pad||!mark||secs.length<2)return null;
    const W=layer.clientWidth||innerWidth;
    const P=[], sb=secs.map(docBox), pb=docBox(pad);

    P.push({x:pb.x,y:pb.y});                                   // the pad
    // a waypoint in every gap between two sections, alternating thirds, so
    // the path has to cross the page and the aircraft has to bank to do it
    for(let i=0;i<sb.length-1;i++)
      P.push({x:(i%2?W*2/3:W/3), y:(sb[i].b+sb[i+1].t)/2});
    // a row of tiles is flown as a row: each waypoint takes its tile's x and
    // its share of the row's height, so the traverse is a shallow descent at
    // four-across and a straight drop at one-across, from one expression
    const row=(host,sel)=>{
      const h=document.querySelector(host);
      const els=h?[...h.querySelectorAll(sel)]:[];
      if(!h||!els.length)return;
      const hb=docBox(h), bs=els.map(docBox);
      // A row that is really a column — which is every row of this page on a
      // phone — is flown as a serpentine rather than straight down its
      // middle. A fifth of a tile either side of centre is still well inside
      // the tile it is meant to light, and on a 390px page it is the only
      // thing that gives the path any bank at all: a third of that viewport
      // off centre is sixty pixels, which reads as drift, not as a turn.
      const stack=bs.length>1&&bs.every(b=>Math.abs(b.x-bs[0].x)<8);
      bs.forEach((b,i)=>P.push({
        x:stack?b.x+(i%2?1:-1)*Math.min(b.w*.22,96):b.x,
        y:hb.t+(i+.5)/bs.length*hb.h}));
    };
    row('.stats','.stat');
    row('.reels','.phone');
    const mb=docBox(mark);
    P.push({x:mb.x,y:mb.y});                                   // the landing pad

    // everything above the pad is a leg the aircraft never flies
    const y0=P[0].y;
    const pts=[P[0]].concat(P.slice(1).filter(p=>p.y>y0+32))
                    .sort((a,b)=>a.y-b.y);
    // strictly increasing, so "where is the route at this scroll position"
    // is a question with one answer
    for(let i=1;i<pts.length;i++)
      if(pts[i].y<pts[i-1].y+6)pts[i]={x:pts[i].x,y:pts[i-1].y+6};
    if(pts.length<4)return null;

    // phantom ends, so the first and last legs have a tangent
    const k=[{x:2*pts[0].x-pts[1].x,y:2*pts[0].y-pts[1].y}].concat(pts,
      [{x:2*pts[pts.length-1].x-pts[pts.length-2].x,
        y:2*pts[pts.length-1].y-pts[pts.length-2].y}]);
    const T=[0];
    for(let i=1;i<k.length;i++)
      T.push(T[i-1]+Math.max(Math.sqrt(Math.hypot(k[i].x-k[i-1].x,k[i].y-k[i-1].y)),1e-3));

    const X=[],Y=[],S=[];
    for(let i=1;i<k.length-2;i++){
      const last=i===k.length-3;
      for(let j=0;j<SEG+(last?1:0);j++){
        const t=T[i]+(T[i+1]-T[i])*(j/SEG);
        const p=crPoint(k[i-1],k[i],k[i+1],k[i+2],T[i-1],T[i],T[i+1],T[i+2],t);
        // the sampled table is forced monotonic even though centripetal
        // barely overshoots: the scroll lookup below depends on it
        X.push(p.x); Y.push(Y.length?Math.max(p.y,Y[Y.length-1]):p.y);
      }
    }
    S.push(0);
    for(let i=1;i<X.length;i++)
      S.push(S[i-1]+Math.hypot(X[i]-X[i-1],Y[i]-Y[i-1]));
    return {X,Y,S,n:X.length,len:S[S.length-1],y0:Y[0],y1:Y[Y.length-1]};
  };

  /* where the route is, at this much arc length along it */
  const at=(s,o)=>{
    const S=R.S; let lo=0,hi=R.n-1;
    s=clamp(s,0,R.len);
    while(lo<hi-1){const m=(lo+hi)>>1; if(S[m]<=s)lo=m; else hi=m}
    const d=S[hi]-S[lo], k=d>0?(s-S[lo])/d:0;
    o.x=R.X[lo]+(R.X[hi]-R.X[lo])*k;
    o.y=R.Y[lo]+(R.Y[hi]-R.Y[lo])*k;
    const dx=R.X[hi]-R.X[lo], dy=R.Y[hi]-R.Y[lo], L=Math.hypot(dx,dy)||1;
    o.tx=dx/L;                                   // the tangent's x — the bank
    return o;
  };
  /* and how far along it the route is at this document y */
  const sAtY=y=>{
    const Y=R.Y; let lo=0,hi=R.n-1;
    if(y<=Y[0])return 0; if(y>=Y[hi])return R.len;
    while(lo<hi-1){const m=(lo+hi)>>1; if(Y[m]<=y)lo=m; else hi=m}
    const d=Y[hi]-Y[lo], k=d>0?(y-Y[lo])/d:0;
    return R.S[lo]+(R.S[hi]-R.S[lo])*k;
  };

  /* ---- layout ---------------------------------------------------------- */
  let docH=0, padIn=false, padEl=null;
  const measure=()=>{
    FQ=parseFloat(getComputedStyle(layer).getPropertyValue('--fq'))||.875;
    // the body's own in-flow height. The layer is absolute and contributes
    // nothing to it, so setting the layer to exactly this can never grow the
    // document — which is the whole of "no layout shift" for this feature.
    docH=document.body.offsetTop+document.body.offsetHeight;
    layer.style.height=docH+'px';
    const r=route();
    if(!r){layer.style.display='none';return false}
    R=r;
    edges=[...document.querySelectorAll('main>section')].map(s=>docBox(s).t);
    lit.forEach(t=>t.el.classList.remove('fl-lit'));
    lit=[...document.querySelectorAll('.stat,.phone')].map(el=>{
      el.classList.add('fl-lit');
      const b=docBox(el);
      return {el,l:b.l,t:b.t,r:b.r,b:b.b,until:0};
    });
    const p=document.querySelector('.svc[data-demo="drones"] .svc-demo');
    if(p!==padEl&&io){if(padEl)io.unobserve(padEl);padEl=p;if(padEl)io.observe(padEl)}
    return true;
  };

  const io=mm.io(es=>{es.forEach(e=>{padIn=e.isIntersecting});wake()},
                 {rootMargin:'120px 0px'});

  /* ---- state ----------------------------------------------------------- */
  let s=0, sv=0, alt=0, land=0, bank=0;
  const P={x:0,y:0,tx:0};
  let gx=0, gy=0, gvx=0, gax=0, seeded=false;
  let lx=0, ly=0;                   // where the light-sweep last looked
  const off={x:0,y:0,vx:0,vy:0};
  let mode='route';                 // route | held | free | back
  let freeUntil=0, hopAt=-1e9, rollAt=-1e9, rolling=false;
  let last=0, running=false, hidden=false, evenFrame=0, saveSkip=0;

  const wake=()=>{
    if(running||hidden||!R)return;
    running=true; last=performance.now(); mm.pump(1);
  };
  const sleep=()=>{if(!running)return; running=false; mm.pump(-1)};

  /* ---- the light a tile takes as the quad goes over it ------------------
     Judged on the segment the ground point travelled this frame, not on
     where it happens to have landed: on a fast scroll the traverse across
     the Results band is hundreds of pixels in a frame, and a tile the
     aircraft flew straight over is not a tile it missed. */
  const near=(t,x,y)=>{
    const dx=x<t.l?t.l-x:x>t.r?x-t.r:0, dy=y<t.t?t.t-y:y>t.b?y-t.b:0;
    return dx*dx+dy*dy<=8100;                                   // 90px
  };
  const sweep=(x0,y0,x1,y1,now)=>{
    for(let i=0;i<lit.length;i++){
      const t=lit[i];
      if(t.until>now)continue;
      for(let j=0;j<=8;j++){
        const k=j/8;
        if(near(t,x0+(x1-x0)*k,y0+(y1-y0)*k)){
          t.until=now+900;
          t.el.classList.add('overflown');
          break;
        }
      }
    }
  };

  /* ---- the barrel roll --------------------------------------------------
     One 360 about the aircraft's own travel axis. It is flown numerically
     rather than by a keyframe, because a CSS animation on this element would
     outrank the style attribute the route is written into and the quad would
     roll where it stood. */
  const barrel=now=>{
    if(rolling)return;
    rolling=true; rollAt=now; layer.classList.add('roll');
  };

  /* ---- a frame ---------------------------------------------------------- */
  mm.add(now=>{
    if(!running||hidden||!R)return;
    let dt=(now-last)/1000; last=now;
    dt=dt>1/30?1/30:(dt>0?dt:1/60);
    // saveData: the same flight at half the frame rate. Nothing here fetches
    // anything, so lowering the work is all "metered" can mean for this
    // module — the route, the lights and the landing are all unchanged.
    if(mm.save){saveSkip^=1;if(saveSkip){last=now-dt*1000;return}}
    evenFrame^=1;
    const full=evenFrame===0;

    /* where the scroll says it should be. The aircraft rides about 35% down
       the viewport; when the bottom of the document does not give the route
       enough scroll to reach the footer mark at that offset, the mapping is
       stretched so the last of the scroll is the landing rather than the
       aircraft stopping short of its own pad. */
    const vh=innerHeight;
    let ty=scrollY+vh*.35;
    const top=Math.max(0,docH-vh)+vh*.35;
    if(top<R.y1&&top>R.y0) ty=R.y0+(ty-R.y0)*(R.y1-R.y0)/(top-R.y0);
    const parked=ty<=R.y0, landed=ty>=R.y1;
    const sT=parked?0:landed?R.len:sAtY(ty);

    // critically damped: a wheel's steps are a staircase, and a staircase is
    // what makes a scroll-driven thing look like it is stuttering
    const w=9, c=2*w;
    sv+=(-w*w*(s-sT)-c*sv)*dt; s=clamp(s+sv*dt,0,R.len);
    at(s,P);

    /* the drag, as a displacement from the route rather than as a position:
       whatever the visitor does to it, the route underneath keeps moving
       with the scroll and the aircraft rejoins the route it is actually on. */
    if(mode==='held'){
      const K=120, Z=.45, C=2*Z*Math.sqrt(K);        // the Pilot's springs
      const tx=ptr.x-P.x, tyy=ptr.y-P.y;
      off.vx+=(-K*(off.x-tx)-C*off.vx)*dt; off.x+=off.vx*dt;
      off.vy+=(-K*(off.y-tyy)-C*off.vy)*dt; off.y+=off.vy*dt;
    }else if(mode==='free'){
      off.x+=off.vx*dt; off.y+=off.vy*dt;
      const k=Math.pow(.92,dt*60);                   // 0.92 a frame, at any rate
      off.vx*=k; off.vy*=k;
      if(now>freeUntil)mode='back';                  // it keeps what it has left
    }else if(mode==='back'){
      const w2=5, c2=2*w2;                           // home in 1.2s
      off.vx+=(-w2*w2*off.x-c2*off.vx)*dt; off.x+=off.vx*dt;
      off.vy+=(-w2*w2*off.y-c2*off.vy)*dt; off.y+=off.vy*dt;
      if(Math.hypot(off.x,off.y)<.4&&Math.hypot(off.vx,off.vy)<2){
        off.x=off.y=off.vx=off.vy=0; mode='route';
      }
    }

    /* A thrown aircraft stays on the page: the window's edges turn it back,
       the way the swatters bounce, rather than letting a hard flick put it a
       thousand pixels into the margin where nobody can reach it again. */
    if(mode==='free'||mode==='held'){
      const LW=layer.clientWidth||innerWidth;
      const cx=clamp(P.x+off.x,18,LW-18);
      const cy=clamp(P.y+off.y,scrollY+18,scrollY+vh-18);
      if(cx!==P.x+off.x){off.x=cx-P.x; if(mode==='free')off.vx*=-.35}
      if(cy!==P.y+off.y){off.y=cy-P.y; if(mode==='free')off.vy*=-.35}
    }

    /* altitude. 1 in the cruise, higher over a panel edge, nothing on the
       ground. The quad hovers 34px above its shadow at cruise. */
    const hop=now-hopAt<420?.7*Math.sin(Math.PI*(now-hopAt)/420):0;
    let aT;
    if(parked)aT=.18;
    else if(landed)aT=0;
    else{
      let d=1e9;
      for(let i=0;i<edges.length;i++){const e=Math.abs(P.y-edges[i]);if(e<d)d=e}
      aT=1+.42*Math.exp(-(d*d)/(110*110));
    }
    aT+=hop;
    const ease=1-Math.exp(-dt*5);
    alt+=(aT-alt)*ease;
    land+=(((landed&&mode==='route')?1:0)-land)*ease;
    layer.classList.toggle('landed',land>.5);

    const bob=parked?2*Math.sin(now/1600*Math.PI*2):0;
    const nx=P.x+off.x, ny=P.y+off.y;
    if(!seeded){gx=nx;gy=ny;lx=nx;ly=ny;seeded=true}
    const vx=(nx-gx)/dt;
    gax=(vx-gvx)/dt; gvx=vx;

    /* bank: the tangent's x by a gain, capped, plus the lean acceleration
       puts into it. Under the hand it is the hand's own speed that banks it. */
    const bT=(mode==='route'
        ? clamp(P.tx*30,-22,22)
        : clamp(gvx*.02,-22,22))
      + clamp(gax*.0006,-8,8);
    bank+=(clamp(bT,-30,30)-bank)*(1-Math.exp(-dt*11));

    // The scan is every other frame and it looks along the whole segment
    // since the last one, so halving the work cannot make it miss a tile:
    // the traverse across the Results band is hundreds of pixels a frame on
    // a fast scroll either way.
    if(full){sweep(lx,ly,nx,ny,now);lx=nx;ly=ny}
    for(let i=0;i<lit.length;i++){
      const t=lit[i];
      if(t.until&&t.until<=now){t.until=0;t.el.classList.remove('overflown')}
    }
    gx=nx; gy=ny;

    let roll=0;
    if(rolling){
      const k=(now-rollAt)/700;
      if(k>=1){rolling=false;layer.classList.remove('roll')}
      else roll=360*k;
    }

    const sc=(FQ*(1-.02*land)).toFixed(4);
    quad.style.transform='translate3d('+gx.toFixed(1)+'px,'+(gy-34*alt+bob).toFixed(1)+
      'px,0) rotate('+bank.toFixed(2)+'deg) rotate3d(1,0,0,'+roll.toFixed(1)+'deg) scale('+sc+')';
    const sh=(.22+.78*alt).toFixed(3);
    shade.style.transform='translate3d('+gx.toFixed(1)+'px,'+gy.toFixed(1)+'px,0) scale('+sh+')';
    shade.style.opacity=(.40-.15*alt).toFixed(3);

    /* nothing to do and nothing moving: hand the loop back */
    if(mode==='route'&&!rolling&&now-hopAt>420&&
       Math.abs(s-sT)<.4&&Math.abs(sv)<1&&Math.abs(aT-alt)<.004&&
       !(parked&&padIn)&&!lit.some(t=>t.until))sleep();
  });

  /* ---- input ------------------------------------------------------------
     The aircraft is the only thing on the layer that takes a pointer, and
     touch-action:none is on it alone, so a finger on the quad flies it and a
     finger anywhere else scrolls the page. The pointer is captured, so a
     throw survives the quad coming out from under the finger. */
  const ptr={x:0,y:0};
  const buf=[];                                    // ~80ms of samples
  let pid=-1, downAt=0, downX=0, downY=0, moved=0;
  const sample=(x,y,t)=>{
    buf.push(x,y,t);
    while(buf.length>3&&t-buf[2]>80)buf.splice(0,3);
  };
  const speed=t=>{
    if(buf.length<6)return{x:0,y:0,s:0};
    const gap=t-buf[2];
    if(gap<=0)return{x:0,y:0,s:0};
    const vx=(buf[buf.length-3]-buf[0])/gap, vy=(buf[buf.length-2]-buf[1])/gap;
    return{x:vx,y:vy,s:Math.hypot(vx,vy)};                       // px/ms
  };

  quad.addEventListener('pointerdown',e=>{
    if(e.button||!R)return;
    e.preventDefault();
    try{quad.setPointerCapture(e.pointerId)}catch(_){}
    pid=e.pointerId; downAt=performance.now(); downX=e.clientX; downY=e.clientY;
    moved=0; buf.length=0; sample(e.clientX,e.clientY,downAt);
    ptr.x=e.clientX+scrollX; ptr.y=e.clientY+scrollY;
    mode='held'; layer.classList.add('held');
    wake();
  });
  quad.addEventListener('pointermove',e=>{
    if(mode!=='held'||e.pointerId!==pid)return;
    ptr.x=e.clientX+scrollX; ptr.y=e.clientY+scrollY;
    const d=Math.hypot(e.clientX-downX,e.clientY-downY);
    if(d>moved)moved=d;
    sample(e.clientX,e.clientY,performance.now());
    wake();
  });
  const release=e=>{
    if(mode!=='held'||(e&&e.pointerId!==pid))return;
    const now=performance.now();
    layer.classList.remove('held');
    try{quad.releasePointerCapture(pid)}catch(_){}
    pid=-1;
    const v=speed(now);
    if(moved<8&&now-downAt<420){                    // a tap, not a drag
      hopAt=now; mode='back'; off.vx=off.vy=0;
    }else if(v.s>1.2){                              // a flick: it rolls out of it
      barrel(now);
      // Thrown, not launched: a trackpad, a coalesced touch stream or an
      // automated pointer can report tens of pixels a millisecond, and the
      // glide below integrates whatever it is handed for 600ms.
      const k=Math.min(1,2.6/v.s);
      off.vx=v.x*k*1000; off.vy=v.y*k*1000;         // px/ms → px/s
      mode='free'; freeUntil=now+600;
    }else{
      mode='back'; off.vx=off.vy=0;
    }
    wake();
  };
  quad.addEventListener('pointerup',release);
  quad.addEventListener('pointercancel',release);
  quad.addEventListener('lostpointercapture',release);
  quad.addEventListener('dragstart',e=>e.preventDefault());

  addEventListener('scroll',wake,{passive:true});

  /* ---- the page changing shape under it --------------------------------- */
  let t0=0;
  const relayout=()=>{clearTimeout(t0);t0=setTimeout(()=>{if(measure())wake()},150)};
  addEventListener('resize',relayout,{passive:true});
  if('ResizeObserver' in window){
    let h=-1;
    new ResizeObserver(()=>{
      // A page settling by a pixel is not a page that has changed shape, and
      // redrawing the route for it moves the aircraft a pixel for no reason.
      const n=document.body.offsetHeight;
      if(Math.abs(n-h)>2){h=n;relayout()}
    }).observe(document.body);
  }

  /* ---- nothing runs behind the visitor's back --------------------------- */
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden){hidden=true;sleep()}
    else{hidden=false;last=performance.now();wake()}
  });

  if(measure())wake();
})();
