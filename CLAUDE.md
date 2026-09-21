# Open Air Gallery — openairgallery.art (Ephraim, owner and painter)

A Green Flash client site. Read this before any design or build here; add to it as the owner
gives rules and the client gives notes. Build and verify in a preview first
(preview.greenflashusa.com/p/openairgallery/), one idea per commit, then promote.

## What the client is
Open Air Gallery is a **muralist and large-image company** led by Ephraim — not a painting
gallery. National brand murals plus civil-rights portraits:
Gucci, New York (81' × 80') · Crown Royal × Trail Blazers, Portland (85' × 90') · Uber,
San Francisco (62' × 23') · Victoria's Secret, Austin (36' × 8') · Vitamin Water, New York
(9' × 20') · Sprite (11' × 16') · Moncler · Red Bull · Monkey 47 · Ford Mustang (23' × 36') ·
Showtime, Boston (18' × 9') · Upendo, Los Angeles (18' × 18') · I Am A Man, Chicago (15' × 32')
· **I Am Speaking: John Lewis, Rochester (53' × 50') · Malcolm X, Rochester (53' × 50')**.
Services on the current site: murals, banners, art, graffiti removal, a shop, a "book a free
consultation" call to action; contact hello@openairgallery.art; Instagram @openairmurals.

## The site being replaced (surveyed 2026-09-18)
Wix (nameservers ns6/ns7.wixdns.net; three Wix IPs). Home / Work / About / Contact / Shop /
Graffiti Removal; **Media and Shop return 404**. Home: a tiny-planet NYC hero, four numbered
mural slides that lazy-load blurred, a broken black shape mid-page, a headline colliding with a
mint watermark, blurred "latest projects" images, an FAQ about payment/shipping/warranty.
Accent: mint green on white; dark nav. 45 media files across Home/Work/About. The work is far
better than the site presenting it — that is the whole brief in one sentence.

## Open questions (answer before designing)
- Scope: replace the whole Wix site on our stack, same sections, or a narrower first cut?
- Ephraim's own notes and any reference sites he likes — the reference is the spec.
- Domain: who holds the Wix/registrar login; move DNS to us or point A records at the droplet.
- Are Shop and Graffiti Removal real offerings to keep, or drop them?
- Original high-resolution mural photos — from Ephraim, or pulled from Wix at native size?
- Company-first (Open Air Gallery) or artist-first (Ephraim) in voice and structure?
- Timeline.

## Decisions (2026-09-18, confirmed by the owner)
1. **Scope:** full replacement, five pages — Home · Work (page per project) · About (Ephraim,
   team, process) · Services (murals, banners, graffiti removal) · Contact (consultation).
   Media and Shop dropped (both 404 today).
2. **References:** show a mockup first, then ask. The reference is the work itself:
   photo-first, full-bleed, **dimensions as the hook** ("81′ × 80′" set large on every
   project), dark canvas so the murals are the only colour, his mint kept as the one accent.
   One kinesthetic touch: a human figure dragged beside each mural for scale.
3. **Domain:** no transfer — Ephraim's Wix login, an A record to the droplet + `www` CNAME,
   certbot. Preview at preview.greenflashusa.com/p/openairgallery/ until approved.
4. **Graffiti removal stays** (Services page); **Shop goes** (Phase 2 if he sells prints).
5. **Photos:** originals from Ephraim (shared folder, people in frame for scale); the mockup
   uses the Wix copies meanwhile.
6. **Voice:** company brand (Open Air Gallery), artist-led story (Ephraim named in the hero,
   his page, his process).
7. **Timeline:** plan + mockup in a day; build 2–3 days; Ephraim reviews on preview; live
   within two weeks, gated only by photos and the Wix login.
First step on "go": one-page plan, HTML mockup of Home + the Gucci project page, screenshot to
Ephraim before any production code.

## Confirmed on 2026-09-18 (supersedes the proposals above where they differ)
- **Six pages, no shop:** Home · Work (page per project) · About · Services (murals, banners)
  · **Graffiti Removal (its own page — "make sure it looks awesome")** · Contact.
- **Design:** dark canvas, dimensions as the hook, mint `#71EEB8` (sampled from his site) as the
  single accent. Company brand, artist-led story.
- **Hosting:** preview at preview.greenflashusa.com/p/<slug>/, then **live on a Green Flash
  subdomain (ephraim.greenflashusa.com) while Wix keeps serving openairgallery.art.** Nothing
  touches Wix or the real domain until Ephraim switches DNS himself, later.
- **Home page references graffiti removal the way Max's site advertises Green Flash** — a
  distinct band (`gr_band()`, modelled on DGM's `gf_band()`), placed after the process.
- **The graffiti-removal signature is an animation of a graffitied brick wall being cleaned to
  sparkling new** — "Wash" in the motion vocabulary (Roll · Scale · Cure · Wash). Drawn wall by
  default; his real before/after photos if he sends them.
- **Splat — the fifth verb (owner, 2026-09-19), and sitewide.** He asked for it in one
  sentence: *"Add a painting animation where a paintbrush paints the screen or splatters on the
  screen when you click buttons on home page."* So the vocabulary is now **Roll · Scale · Cure ·
  Wash · Splat**, and Splat is the only one a visitor sets off on purpose. Clicking any
  button-styled link — every `.btn`, on all six page types, including the nav's mint "Book a
  free consult" pill — throws a mint SVG blob (turbulence-displaced, three seeds and three turns
  in rotation, drips running out over 300ms) from the exact click point; 120ms later a roller
  pass sweeps in from the side the button is on, covers the viewport in 420ms behind a bristled
  leading edge with lap marks down it, and the link is followed at 555ms. The Contact form's
  "Send the brief" is the one non-link that gets it: the browser's own validation runs first, so
  an invalid brief gets no paint and its message instead, and a valid one splats, sweeps, and
  *then* does what it always did — the FORM_ENDPOINT POST, or the visitor's mail app.
  Then, having seen it, he asked for the second half: *"When it switches pages it should have
  that paint animation for transition, add it for any page transition back to home page or from
  menu."* So **the roller alone is the page transition**, and there are exactly two classes of
  link: **`.btn` is splat + stroke**, and **the nav's links, the wordmark `.brand` and the
  footer's own internal links are stroke only** — nothing was hit, so nothing splatters. That
  stroke enters from the side of the link it came from: the wordmark from the left, the desktop
  nav from the right, and a link tapped in the open phone menu from the top, which is the same
  brush built in a box laid on its side and stood up by one rotate. Click to navigation is 460ms
  there, against the button's 555ms; both read as a hit rather than a wait. **There is no
  per-page gate any more** — `data-splat` and `layout(splat=)` are gone, and `site.js` binds
  everywhere under `html.motion`. It only ever touches a plain left click, with no modifier key,
  on a same-origin http(s) link: middle-click, ctrl/cmd/shift/alt-click, `target=_blank`,
  downloads, `mailto:` and `tel:` all go through as ordinary links, a same-page `#` anchor gets
  the splat and no stroke, the link to the page you are already on paints nothing at all, and a
  second click during a pass does nothing. It lives entirely under `html.motion`, so reduced
  motion and a page whose script never arrived get plain links and a plain form — the contract
  in PLAN.md §4 is unchanged. The overlay is fixed, `pointer-events:none`, `aria-hidden`, and is
  torn down on `pageshow` and 1.5s after a click that went nowhere, so a bfcache back never
  lands on a painted page. Mint only; no sound, no counter, no label.
- **Live — the sixth verb (owner, 2026-09-19), and the first that runs both ways.** He asked for
  it in one sentence: *"Try to animate the numbers on his site, add more motion to the cards as
  well as an ambient glow in places that's tasteful. I'd like him to see motion as he scrolls up
  and down from them."* So the vocabulary is **Roll · Scale · Cure · Wash · Splat · Live**, and
  the phrase that shapes it is **up and down**: Roll and Cure fire once and are done, Live
  replays every time, in both directions, for as long as the visitor keeps scrolling.
  **What rolls:** every figure on the site — the four on the stats band (12 · 23,294 · 90′ · 8)
  and every `.dims` on a card, a project hero, the Work grid and the Rochester pair — is a
  mechanical counter. Each digit is a column of 0–9 that rolls up to its value as the figure
  comes on screen and back to 0 as it leaves; speed scales with the figure (23,294 ≈ 1.1s, 8 ≈
  .4s) and the wheels set off right to left 40ms apart. The real text stays in the server HTML
  and is what sizes the box, so nothing shifts and nothing is lost: site.js lays aria-hidden
  wheels over the characters and the text underneath is still what a screen reader reads and a
  visitor selects. The mint prime marks and the `×` never move.
  **What drifts:** the project cards. The photograph lags its frame as the card rides up the
  screen (±6%, and the picture is hung 12% taller so it always covers), the card rises 18px into
  place and settles back as it leaves, and on a desktop it leans up to 4° toward the pointer.
  The hover it already had — mint hairline, photograph to 1.04 — is composed with, never
  replaced: the lift, the lean and the rise are three custom properties on one transform.
  **What glows:** four places and no more — the stats band, the Rochester pair, the closing call
  to action, and the head of the words under a project's wall, which is the foot of that page's
  hero and the only dark band there. A large soft mint radial, brightest as its section centres
  and gone as it leaves, with a six-second idle breath on top. **Tasteful is written down:** mint
  at 9% at its very brightest and never more, the softness from the gradient's own falloff and
  never a `filter: blur` on page content, the core never under type and never over a photograph,
  and **one glow lit at a time** — site.js lights only the one nearest the middle of the screen
  and puts every other one out, so the rule holds whatever the page does next.
  All of it under `html.motion`, off one extended IntersectionObserver (`data-live` elements are
  never unobserved and toggle `.in` on both crossings; `.rolled` pins a card's Roll open so the
  reveal is not replayed) and one passive scroll listener with one rAF for the whole file.
  **Reduced motion gets no glow at all** — the bootstrap withholds `html.motion` from a visitor
  who asked for reduced motion, so there was never a glow to hold still; the numbers and the
  cards are the static page they are today. No counters, no scores, no labels: a figure rolling
  is motion, not a number going up.
- **Brush — the seventh verb (owner, 2026-09-19), and the second that runs both ways.** He
  asked for it in one sentence: *"Add an animated paintbrush in more places on his site."* So
  the vocabulary is **Roll · Scale · Cure · Wash · Splat · Live · Brush**, and Brush is the one
  that is neither a reveal nor a click: it is tied to the scroll, both ways, like Live.
  **The mint rule his three stages sit on is painted rather than drawn.** On Home's "Prep,
  paint, preservation" row and on About's three stages in full, the rule is scaled from the left
  by one custom property, `--paint`, and a brush rides its leading edge with a faint wet ridge
  directly behind the bristles. `--paint` is 0 as the rule crosses the bottom of the window and
  1 while the last stage is still on screen (the list's own height plus a fifth of a window,
  held between .45 and .8 of a window so a long list on a phone still finishes in front of the
  visitor). Scrolling back up runs the same sum backwards: the rule un-paints and the brush
  retreats. **Each stage takes the Cure sheen as the brush goes over it** — under the stage's
  number, on every pass, in either direction, which is what `.cured` (the state) and `.curing`
  (the pass that just happened) are for. The brush is `art.py`'s, in a second variant —
  `brush_rule_svg()`, the same wood, ferrule and mint-loaded bristles turned 48° and anchored on
  the point where the leading hairs touch, at 26% across and 83% down its box, which is how
  site.css puts its bristles on the line at any size — drawn at 64px, 44px on a phone. It is
  never over the stage text: it rides the line itself, in a clipping track that is absolutely
  positioned over the list's top hairline, so the mechanic adds nothing to the layout and a
  brush at the end of the rule can never widen the document. Desktop and mobile are the same
  mechanic because it is scroll-tied. **No JS / reduced motion: the rule is simply painted and
  there is no brush** — the markup is all in the server HTML and only the motion is gated, so
  the two renders stay the same document. It runs off the Live IIFE's one scroll listener and
  one rAF, and the same IntersectionObserver, which now has a third contract: a `[data-brush]`
  element is never unobserved and is repainted on every crossing.
- **Roll it in — Roll's second use (owner, 2026-09-19), on every project card.** The vocabulary
  stays **Roll · Scale · Cure · Wash · Splat · Live · Brush**: this is not an eighth verb but the
  first one used a second way. Roll the reveal arrives by itself; **Roll it in the visitor lays
  down himself**, and it makes the twelve-wall grid feel like twelve walls going up. Every
  `.pcard` photograph waits under **primer** — a whitewashed wall: the photograph at 12% of its
  colour, the contrast almost flat and the whole thing lifted toward `--wall` (`--primer`, a CSS
  filter on the `<img>` and only while the card is unpainted, so no filter is ever left on a page
  element). **Every card rolls itself in as it arrives — desktop as much as phone.** The
  stagger is what paints the wall, 120ms between cards and a 350ms grace before the first of a
  run, off the same observer: *a portfolio can never sit whitewashed waiting for a hover that may
  never come* (owner, 2026-09-19, on review). Each pass is 600ms — a mask wipe left to right, the
  same mechanism as Roll and for the same reason (a mask is paint-only, a clip-path would collapse
  the observer's rectangle), with `art.py`'s `roller_pass_svg()` riding the leading edge and a
  faint wet sheen immediately behind the nap. **The hover is the shortcut, not the trigger:** over
  the grids the pointer *is* the roller (the same symbol serialised at 40px into a
  `cursor:url(data:…)`, hotspot on the nap), and a card the pointer reaches before the stagger
  does paints at once — the grace is there so a pointer already resting on a card when the grid
  arrives paints that one first, under the roller. Because everything gets painted in the end the
  **roller cursor is a passing beat**: the pointer is handed back the moment the last card lands.
  Either way it is **once and for good** — this is Roll, which runs one way, not Live, which runs
  both. It composes with Live rather than
  replacing any of it: the drift, the rise, the tilt, the mint hairline and the photograph to 1.04
  are all untouched, and nothing in it changes a box. **No JS / reduced motion: full-colour
  photographs, no primer, no roller** — the primer is `html.motion` only, it is on the img from
  the first paint so there is no flash of colour, and it carries the same 2.8s bail-out every
  hidden thing here carries, called off by `.rollin` the moment site.js runs. The second, unprimed
  copy of the photograph that the wipe reveals is cloned by site.js and removed the frame the
  primer comes off, so a crawler is never handed the same mural twice and the no-JS document is
  the document it always was.
- **Stencil — the eighth verb (owner, 2026-09-19), and the one that happens to the hook.** Concept
  5 of the paint mechanics: *"When a `.dims` figure enters view it is sprayed on: a stencil card
  slides over, the numbers appear through it with overspray at the edges, the card lifts away."*
  So the vocabulary is **Roll · Scale · Cure · Wash · Splat · Live · Brush · Stencil**, and it is
  the site's own measurements — every `.dims` and every figure on the stats band — that get it.
  A card of matte board comes down over the figure in 180ms, the numbers are sprayed through the
  cut, and the card lifts in 220ms leaving the overspray behind. **The cut is the figure's own
  glyphs, never a drawing of digits:** site.js measures each run of text on the line where it
  actually sits — the baseline read off a zero-height inline-block, which is the only way to ask
  the page where a baseline is — and lays it into an SVG `<mask>` in the same font, size and
  width axis, cut a hair wide the way a stencil is cut. **The overspray is `--paper` spreading
  six to ten pixels outside the glyphs**, a copy of the figure with no ink in it at all whose
  `text-shadow` is the only thing that paints: it is displaced by `wall.py`'s own aerosol
  (`feTurbulence` 0.045 + `feDisplacementMap` 6) for the 380ms the can is open and by nothing
  afterwards, so **no live feTurbulence is ever left on a settled page** — it fades in with the
  figure at .35 and settles to .12. **The mint prime marks and the `×` are never sprayed:** they
  are already painted, so they sit over the card rather than coming through it, and they take no
  halo. It composes with the two verbs already on a figure rather than replacing either: Scale's
  `wdth` grow is snapped to its end value under the card (which is where it was going, and what
  keeps the cut true), Live's columns **roll under the stencil** and the spray is the moment they
  land — `min(1.2s, .4 + .175·(n−1))`, the roll's own sum — and Cure is timed by one custom
  property, `--st-cure`, so the sheen sets off as the card is lifted and a figure that never gets
  a stencil still cures at the .4s it always did. **Hover resprays it on a fine pointer, a tap
  resprays it on a coarse one**, and the tap never costs the link a card's figure sits in. Nothing
  in it can move a box — the card and the halo are absolutely positioned inside the figure — and
  **no JS / reduced motion gets the figures exactly as they are today**: the whole mechanic is
  built by site.js under `html.motion`, so there is no card, no halo and no filter to withhold.
- **Wall — the ninth verb (owner, 2026-09-19), and the only blank one.** Concept 3 of the paint
  mechanics: *"The About hero is dark and empty behind 'Ephraim and the crew' — a blank wall."*
  So it becomes one, and so does the **404**, which is the same hero with the copy to match —
  *"Nothing on this wall yet. Paint something, or head back."*, Home and Work underneath. The
  vocabulary is **Roll · Scale · Cure · Wash · Splat · Live · Brush · Stencil · Wall**, and Wall
  is the only verb with nothing to reveal, nothing to finish and nothing to get right: **moving
  the pointer over the hero paints it**, and what is painted dries and is gone.
  **A stroke is a bristled stamp every 6px along the pointer's path** — eight to twelve hairs
  from the kit's seeded random, the same generator Splat's brush edge comes out of and the same
  geometry as `art.py`'s `brush_rule_svg()`, laid across the direction of travel and dragged
  along it, on a canvas sized to the hero and device-pixel-ratio aware to a cap of 1.5×.
  **Opacity is speed and nothing else:** a slow pointer is a wet, fully loaded brush and lays a
  body of mint with the bristles as texture in it; a fast one is dry-brush — the body is gone and
  the lightly loaded hairs lift off, so the stroke goes broken. **Hold the brush still and the
  paint runs:** one thin mint drip, 20 to 60px, out of the bottom of the last stamp, drawn as it
  grows and gathering a bead at the end. **It dries over about six seconds** — one destination-out
  multiply of the whole canvas every 110ms, which is the cheap half of the choice (its cost does
  not grow with how long the visitor has been painting) — and 6.8s after the last stamp the canvas
  is cleared outright and the loop stops itself, because that fade stalls a few counts short of
  zero in 8-bit alpha and a wall that is 1% painted is not a blank wall. **The wall can never fill
  up and there is nothing to score.**
  **The words are never painted over:** the canvas sits at z-index -1 inside `.page-hero`'s own
  stacking context — where the shade sits on a hero that has a photograph — and is
  `pointer-events:none`, so the listeners are on the hero and a link in the hero is still a link.
  **On a phone a finger drag paints and the page still scrolls:** the first 12px of a touch decide
  which — mostly vertical and it is the page's gesture and this never hears from it again;
  anything else is a stroke, the hero takes `touch-action:none` for as long as that stroke lasts
  and the move is `preventDefault`ed so a pan already being considered is called off. **A
  two-finger tap wipes the wall.** **Sound:** the hiss of a brush on brick while a stroke is being
  laid, behind the same muted-by-default toggle, in the corner of the hero — and the
  AudioContext behind it now lives in **`site.js`'s kit (`window.oagKit`)** along with the seeded
  random, because `wash.js` had the only copy and two files were about to have two. `wash.js` asks
  the kit for it (and its script tag moved out of the head to below `site.js` so it is there when
  it asks), so `/about`, `/404` and `/graffiti-removal` share one context and one persisted key.
  **No JS / reduced motion: the hero exactly as it is today** — there is no canvas and no toggle
  to withhold, because site.js builds both under `html.motion`; the server HTML is one attribute,
  `data-wall`, and the `--nojs` render of `/about` is byte-identical to the one before this.
- **Spray — the tenth verb (owner, 2026-09-19), and the one that writes.** He asked for it in
  one sentence: *"Is there any way to have a can of spray paint spray 'Open Air Gallery'
  underneath the hero as a section builder?"* So the vocabulary is **Roll · Scale · Cure · Wash ·
  Splat · Live · Brush · Stencil · Wall · Spray**, and Spray is the first verb that is a
  *section builder*: `spray_band(text)` in `build.py` is reusable, takes a word, splits it on a
  slash into the lines it stacks as, and gives back a full-width band. Its first use is Home,
  directly under the Johnnie Walker hero and before the stats band.
  **The word is real server-rendered text in the wordmark's own face** — Archivo at the
  `.brand` treatment (`wdth` 125, `wght` 800, uppercase), set at headline size and stacked two
  lines the way `.brand` stacks — and it is the only thing in the band with a height.
  **As the band comes into view the can writes it.** `art.py`'s rattle can, in a second variant
  — `spraycan_pass_svg()`, the same tin, label, mint cap and dented body turned 82 degrees and
  anchored on the nozzle's own orifice at 75% across and 50% down its box — enters from the left
  at 120px (84px on a phone), travels the line at letter height, and the letters appear behind
  the nozzle through a feathered edge that advances with it. **The nozzle and the wet edge are
  in step by construction, not by a number passed between them:** the can's track is the width
  of the word, the mask is sized on the word, and both carry the same CSS animation — same
  duration, same linear clock, the same keyframe offsets — so the left edge of the track and the
  edge of the paint are the same percentage of the same box at every frame, measured at three
  moments and identical to a third of a pixel. Eighty-two degrees is a sum rather than a look:
  the can leans 14 degrees inside its own drawing, so 82 on top puts the jet six degrees below
  the horizontal and the label a hair past vertical, reading down the can the way a label on a
  can lying on its side does.
  **Three things ride with it.** An overspray halo — a clone of the word with the ink taken out
  of it, the way Stencil's is, wearing the same `#oa-spray` aerosol while the can is open and
  **nothing at all once the paint is dry**, settling from .30 to a static .12. A mist cloud just
  ahead of the nozzle, a mint radial's own falloff and never a blur filter, smaller in
  proportion on a phone because a 390 word is a third of the width a desktop one is. And two or
  three runs off the heaviest letters — O, A and G, at most two to a line and never two within a
  third of the word of each other — each one starting **after** the can has gone past the letter
  it comes off, hung on the baseline a zero-height probe finds (Stencil's `.st-probe`) because a
  range rect on a face set at .92 line-height is nowhere near the feet of the glyphs.
  **It sprays once on the way in, like Roll rather than like Live**, and at half the band rather
  than the eighth the reveals use: the top of a band is its padding, and a wordmark written
  where nobody is looking has not been written at all. **Hover resprays it on a fine pointer, a
  tap on a coarse one**, and the band is not a link, so a tap costs nothing.
  **Sound is the ball bearing and the hiss** — four short knocks as the can comes in, then the
  can's own named voice while it writes — behind the toggle the wall and the washer already
  share, muted by default and read off the same persisted key. **Home has no toggle of its own:**
  its wash band runs in auto mode and never had one, and a second toggle on Home is not wanted,
  so the band is silent there unless the visitor turned sound on elsewhere.
  **No JS / reduced motion: the wordmark as plain text, no can, no halo, no drips.** The halo
  and the drips are built by site.js under `html.motion` and nowhere else, the can is
  `display:none` outside it, and the mask that hides the letters before the can reaches them
  changes no metric of the text at all — the word's box is the same to two decimal places in all
  three renders, and `/`'s `--nojs` and `--reduced --compare` are still identical on every count.
  It runs off the Live IIFE's one observer, which now has a fourth contract: a `[data-spray]`
  band is sprayed once at half visibility and then unobserved.
- **Tip — the eleventh verb (owner, 2026-09-19), and the second a visitor sets off on purpose.**
  Concept 1 of the paint mechanics, in his words: *"Maybe a paint bucket you click and it
  spills."* So the vocabulary is **Roll · Scale · Cure · Wash · Splat · Live · Brush · Stencil ·
  Wall · Spray · Tip**, and Tip is the only one whose payoff lands on a *different section* from
  the one it happens in.
  **A tin of mint stands on the floor of the Services hero**, bottom-left of the text column, at
  150px on a desktop and 96px on a phone. It is `art.py`'s own tin — `can_tipping_svg()`, which
  is `can_svg()`'s drawing rather than a second one: the file's six pieces (defs, shadow, tin,
  rim, paint, handle) are shared, `can_svg()` still emits the same bytes it always did, and the
  variant differs in three things only — the paint in the rim is its own group so it can be held
  level and drained, a lens of wet paint over the outer lip that is invisible until it pours, and
  the shadow in a group of its own, because a tin at seventy-six degrees does not cast the shadow
  of one standing up.
  **Click it, or drag it past forty degrees, and it goes over.** It rolls on the right-hand edge
  of its own base (`CAN_TIP_PIVOT`) and overshoots to ninety-two before settling on
  seventy-six (`CAN_TIP_DEG`) — a tin has weight, and one that arrives at its angle and stops has
  none. The drag holds it wherever the pointer has carried it and the spring takes over from
  exactly there; let go short of forty and it rocks back upright. **The paint leaves it as a
  glossy sheet** from the point the rim is low at that angle (`CAN_TIP_POUR`, a third of the
  tin's width outside its own box), with a meniscus at the rim, a highlight down the body and a
  fat head running in front of the fall; it **pools along the hero's bottom edge** — a CSS height
  with a wobble on the waterline, deepest where the sheet came down and thinning to the ends —
  and **drips through onto the first section, where it becomes that section's mint rule**, filling
  outward from the drip point and then taking its Cure sheen. The run is Spray's drip, markup and
  keyframes and all. **After four seconds it rights itself** — the tin springs up, the sheet
  retracts into the rim, the pool drains down the run — and it can be tipped again. The rule keeps
  its paint: paint does not come off a wall because the tin stood back up.
  **On a phone a tap tips it, and after that first tap `deviceorientation` leans the pool toward
  the low side** — damped, 30Hz, half a degree at full tilt, and only where no permission prompt
  is needed (Android; on iOS `requestPermission` is a function and it is silently not offered).
  **Sound is a slosh and three glugs** — a band of noise swept down as the body of paint leaves,
  then the air going back into the tin — behind the same muted-by-default toggle the wall and the
  washer share, on the same persisted key. That toggle now lives in the kit (`oagKit.sndToggle`)
  rather than inside Wall, because Tip was the second thing about to build one.
  **Nothing in it moves a box**: the tin, the sheet, the pool and the run are all absolutely
  positioned, the hero reserves the tin's own height in every render, and the section's rule is
  already in the server HTML. `.page-hero` is `overflow:hidden`, which makes it a *scrollport* —
  so a meniscus two pixels proud of the water, or a sheet taller than the hero, is scrollable
  overflow that a `scrollIntoView` or a `focus()` will scroll the hero's own words by. That is
  why the pool is two boxes, the meniscus is inside the water, and the pour's head stops with its
  bottom on the hero's bottom edge. **No JS / reduced motion: the tin stands upright and the rule
  is already mint** — there is no pool, no sheet and no toggle, and the tin is not even a control
  there (site.js is what gives it its role, its tab stop and its name, because a button that does
  nothing is worse than a picture of a tin). The rule's 2.8s bail-out is the one on the site that
  runs the other way — it paints the rule for a page whose `site.js` never arrived — so site.js
  calls it off the moment it binds (`html.tipready`), exactly as `.rollin` calls off the primer's.
- **The graffiti has to read as a real tagged wall — never cartoon bubble letters.** The first
  drawn version was three bubble-letter pieces in magenta, blue and amber, evenly spaced, all
  plainly painted the same afternoon by the same hand; the owner's verdict was *"that graffiti
  looks horrendous"*, and on a page selling graffiti removal a clip-art idea of graffiti is the
  one thing we cannot put up. So: **handstyle letterforms traced from real spray and marker
  fonts** (`tools/make-tags.py` → `tag_paths.py`; faces and their licences in `tools/fonts/`),
  **layered by age** — a buffed patch with an older tag ghosting through it, then a throw-up,
  then a handstyle, then marker over everything, including a name crossed out by whoever came
  next — and every sprayed piece carrying a **dark outline, drips off the letter bottoms and an
  overspray halo** (the blurred copy of itself underneath, which is what says "sprayed" more
  than the letters do). Grime goes under the paint, the light and the vignette over it. Names
  are invented: no real crew, nothing readable as a slur, and nothing green — the mint is the
  brand's one accent and graffiti never borrows it. To change a word, its face or its size:
  edit `WORDS` in `tools/make-tags.py`, run `python3 tools/make-tags.py`, place it in `_tags()`
  in `wall.py`, and commit the regenerated `tag_paths.py` with the wall. `docs/wash.md` is the
  long version.
- The full build plan is `PLAN.md` in this repo (copied from the approved plan). Opus subagents
  implement one step each from it; the lead session reviews each commit.
- `research/wix/` holds the saved Wix pages and a full-page screenshot from the audit
  (untracked) — the source for `wix-sources.json` and for quoting his own copy.
- **Subdomain name (owner, 2026-09-18): `ephraim.greenflashusa.com`.** Web root `/var/www/ephraim`,
  nginx snippet `ephraim-site.conf`, `gd-dns add ephraim`.
- `docs/plan-agent-notes.md` holds the design agent's refined implementation notes (the wall
  mechanic's canvas/mask/completion details, the fetch step-down, the vhost model, `.preview-slug`,
  `BASE_PATH`, `assets/_sources.json`). Where PLAN.md is the frame, those notes are the detail.

## Images — what the Wix site actually holds (2026-09-18, from the pipeline run)
- All twelve heroes fetched (`assets/`, renditions in `out/img/`, provenance in
  `assets/_sources.json`, procedure in `docs/images.md`). **Ten of twelve are only ~1,200–1,284 px
  wide** — the largest files Ephraim ever uploaded to Wix. Only Vitamin Water (2,732) and Upendo
  (2,250) clear 1,600. A full-bleed dark photo-first site wants 2,400: **his originals are needed
  before launch**, and `pic()` must use real rendition widths in `srcset`, with heroes capped at
  ~1,600 CSS px meanwhile.
- The highest-resolution mural photo on the whole site (4,762 × 3,175, John Lewis) was on the
  About page, not the project page — pulled as `john-lewis-rochester-1`.
- **Wix's `enc_auto` honours the Accept header**: a browser Accept returns AVIF bytes named
  `.jpg`. `fetch-wix.py` sends `image/jpeg,image/png` on purpose. Do not "simplify" that.
- **Surname:** the portrait's alt text on Wix reads "Ephraim Gebre" — the only place a surname
  appears. **Unconfirmed; do not caption with it until the owner confirms.**
- `research/wix/graffiti-removal.html` is saved (he spells it "Graffitti"). Its copy is real and
  reusable (three services, each with a paragraph; "Book Your Free Consult"; "See Our Process").
  Its only non-stock image is `b79272_2838f371…~mv2.jpg` (served at w_2500) — add it to
  `wix-sources.json` extras when the page is built. The rest are stock placeholders — never use.
- Extras (nine signs/banners, Snickers, The Inn, GST Loft) are recorded under `not_fetched` in
  `wix-sources.json` with exact URLs; move one to `extras` and re-run to pull it.

## The Home hero clip — Johnnie Walker (2026-09-19)
The owner uploaded Ephraim's own footage of the **Johnnie Walker Blue wall in
Manhattan** (drone reveal, Ephraim painting on the lift, the aerial down the
block) and asked for it as "the motion background at the top". It lives at
`assets/source/johnnie-walker.mov` (gitignored; keep a copy), is cut by
`make-hero-clip.sh` into `out/video/hero-johnnie-walker.{mp4,webp}`, and
`page_hero(..., video=...)` lays it over the Gucci photograph on Home. The
photograph stays: it is the LCP element, the crawler's image, and what
reduced-motion, data-saver and no-script visitors see.
- **The Johnnie Walker wall is not in `projects.py`** — no dimensions, year or
  client line were supplied, and nothing is invented. Ask Ephraim for the feet;
  it then becomes the thirteenth wall and the hero copy can name it.
- nginx serves `/assets/video/` with `mp4;` and immutable caching (snippet
  updated); `deploy.sh` syncs `out/video/`.

## Ephraim's drop, 2026-09-20 — RAINS and Flower City Arts Center
The owner dropped `Ephraim website.zip` (1.28 GB) in and said *"he wants that content
integrated into his site."* The whole brief and the file table are
**`docs/ephraim-drop-2026-09-20.md`** — read that before touching either wall. It was
written against the round-three redesign, so two of the seven commits it lists are not
here: this branch has no "Painted for" brand wall for AMC and no `public_works()` strand.
Everything else in it landed on this branch, restyled to the dark canvas and the one mint
accent. The short version:
- **RAINS**, New York, for **AMC — Angel Media Co.** (the placard on the brick reads
  "AMC angelmediaco."). His drone edit is the page hero film, his portrait reel is "the
  wall going up" under the story, and four of his photographs are the gallery.
- **Flower City Arts Center**, Rochester — a community wall on the underpass by the
  ballpark, **filmed by Max, @omgmaxgod**, which is the only photo credit on the site.
  Hero and gallery are 4K frames from his film. It is civic, so the Work page's Civic
  filter picks it up on its own.
- **Dimensions may still be None** — both or neither — and `dims()` gives back nothing
  for a wall without them. Every figure counts `measured()` and the stats band says so.
  No wall on the roster is unmeasured today (the owner sent the last two on 2026-09-21),
  and the path is kept for the next one that arrives without a tape measure.
- **A wall opens on `film_hero()` because it has a film, not because it lacks feet.**
  That used to be the same test and stopped being one on 2026-09-21. `scale_hero()` is
  for a wall with feet and no film; RAINS and Flower City have both and keep the film,
  because the film is what the drop was for — the figure moved down into the words under
  it, where it is the first thing after the title.
- **`ROCHESTER` is not "the civic category" and not "the civic Rochester walls" either.**
  Flower City is civic *and* in Rochester *and* now has feet, and the Home band is headed
  "Two walls in Rochester" and calls the two the same size to the foot in the same breath.
  So the list is the civic Rochester walls that **share a measurement** (53 × 50, twice),
  with an assert behind it. Change the copy before you change the filter.
- **Every hero clip is built twice** (the `make-*.sh` scripts): the cut at the camera's
  own size and rate, and a 1920-wide companion at **crf 26, capped at 5 Mbit with a
  10M buffer** (2026-09-21; it was crf 24 at 12 Mbit, which was a 4K file's bitrate at a
  fifth of a 4K file's pixels). The server HTML names the companion — a phone, a
  no-script visitor and a reduced-motion visitor must never be asked for the 4K
  file — and `PICK`, one line **inside** each `<video>` ahead of its
  `<source>`, sets the element's own src to the master above 900px. It has to be exactly
  there: a `<source>` in an empty media element starts resource selection, so a script
  after the element is already too late, and site.js is deferred, which is later still.
- **The portrait reel names one file and only one** (2026-09-21). `progress_band()` has
  no `data-hi`: the frame is 300px wide at every width, so the 1080×1920 companion is
  already more picture than it can hold and there is nothing for a wide screen to swap
  in. `out/video/rains-progress.mp4`, the 2160×3840 master, is a build intermediate the
  poster is cut from and is not shipped — `clip_sources(name, hi=False)` does not ask for
  it on disk.
- **Both films are on their pages whole, with sound, behind a play button** —
  `film_band()`, `out/video/film-*.mp4`, remuxed with no re-encode. The element is
  `preload="none"`, so nothing is fetched until somebody clicks; the button is built by
  site.js under `html.motion` and with no script the browser's own control is already
  there. Splat does not touch it: the click mechanic only acts on `a[href]` and a form's
  submit.

### The one hole left
- **The feet arrived** (the owner, 2026-09-21): RAINS **15 × 15**, Flower City Arts
  Center **25 × 50** — in his words, *"15x15 on rains and 25x50 on flower city"*, written
  wide by tall like every other wall on the site. Two numbers filled four places on their
  own: the hook on each project page, the figure on each Work card, the square-foot total
  and the widest/tallest sentence on the stats band. **The optional-feet path stays** —
  `dim_w=None, dim_h=None`, `measured()`, `feet_note()` and the `.dims`-or-note branch in
  `pcard()` and `project_page()` are all still there, because the next wall he sends may
  arrive unmeasured too.
- **The years are answered** (the owner, 2026-09-20): RAINS **2024**, Flower City
  **2023** — the years he posted the films, not dates read off the walls, so they sit in
  the Year row of the project meta and nowhere else in the copy.
- **`16_9 VFX.mp4` in the drop is damaged.** It has a corrupt packet at 50.35 s (frame
  3021 of 3507) and every reader stops dead there — `-err_detect ignore_err` does not get
  past it, because the NAL length written in the file is wrong and there is nothing after
  it to resynchronise on. So `film-rains.mp4` is 50.35 s of Ephraim's 58.45 s cut: it
  loses the tail of the closing pull-away and nothing else, and the hero cut is
  untouched because its last beat ends at 49.3 s. `16_9 No FX.mp4` reads end to end but
  is the same flight *without* the grade and the title card, so it is not a substitute.
  **Ask Ephraim to send `16_9 VFX.mp4` again**, drop it in and re-run `./make-films.sh`;
  the duration is how you check it arrived.

### And the standing rule both walls sit under
**Never state a wall count** (the owner, 2026-09-19): *"Don't say 12 walls — he has more
not on there, and wants to show more of his public works like Colossal did; he's been to
Mexico, Brazil, teen empowerment and more, so don't limit."* The rows in `projects.py`
are the walls we have photographs of, not his body of work. No "twelve walls", no wall
count on the stats band, no "six of them here" over the Home row — square feet stays only
because it is phrased "and counting", and it now counts `measured()` alone.
