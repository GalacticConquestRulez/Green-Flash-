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

## Round three — Ephraim's own references (owner, 2026-09-19)
Ephraim wants the site "more like" **colossalmedia.com** and **overallmurals.com**:
- From **Overall Murals**: the menu runs across the **top of the screen**, not tucked on the
  right — a full horizontal nav beside the wordmark, visible at every width (no hamburger).
- From **Colossal Media**: the **colour contrast** (black / a single loud brand colour / white
  in full-bleed bands, the wavy band edge, the marquee strip) and **multiple typefaces — four or
  five** — used deliberately to make it stand out (Colossal: Druk Wide, TimmonsNY, aktiv-grotesk,
  Tiempos). For Ephraim the loud colour is his mint, and one of the faces is the handstyle
  already in `tools/fonts/` (Permanent Marker) — a muralist gets a marker.
- **Restore point:** the site as it stood before this round is tagged `pre-redesign-2026-09-19`
  and pushed to GitHub as branch `openairgallery-live` of `GalacticConquestRulez/Green-Flash-`;
  the redesign is built on `openairgallery-redesign`. "If he doesn't like it" = check out the
  tag / the live branch and `./deploy.sh`.

### Never state a wall count (owner, 2026-09-19)
"Don't say 12 walls — he has more not on there, and wants to show more of his public works
like Colossal did; he's been to Mexico, Brazil, teen empowerment and more, so don't limit."
So: no "twelve walls", no "12 · walls painted" stat, no "twelve of them" — anywhere. The
twelve in `projects.py` are the walls we *have photographs of*, not his body of work. Copy
speaks of the work as open-ended ("walls in New York, Portland, Chicago, Rochester, Mexico,
Brazil…"), the stats band drops the wall count (square feet stays only if phrased as "and
counting"), and the site gets room for public works and community projects — Mexico, Brazil,
teen-empowerment murals — as their own strand, the way Colossal shows its public art. Ask
Ephraim for those photographs and the stories; until they arrive, leave the section framed
for them rather than pretending the roster is complete.

### Round three palette (owner, 2026-09-19): white ground, his teal, one pop colour
Owner: "Let's do a white background — or maybe do white, his teal and another color that pops
with it." So the redesign flips the canvas: **white** ground with **ink** type, his **mint/teal
`#71EEB8`** as the loud band colour (the Colossal yellow role), and **one third colour that pops
against the mint** for accents — emphasis words, the marker asides, the active nav link, the
primary-on-mint button. Proposed: a coral-orange `#FF4F2E` (the mint's complement, and the
warm note Overall Murals uses). Black stays for the marquee strip, the hero scrim and the
footer only. The dark-canvas site that is live today is the restore point, not the direction.
- **The teal is paint, not a fill (owner, 2026-09-19):** "Maybe make the teal a brush stroke —
  so it looks like he painted on the screen." Every teal band on the redesign is a swept brush
  stroke: tapered, loaded start and feathered end, dry-brush streaks along the stroke, bristle
  break-up on the long edges, a few drips, a degree or two of tilt. Same for the highlight
  behind the hero's mint words. Never a flat rectangle of mint, never a clean wave edge.
  Generate the strokes (seeded, like the tags and the props) so they are byte-stable.

### The paint mechanics, round three (owner, 2026-09-19)
"Add in multi-colour mixing and an on-screen effect that matches that; increase time on
transitions so he can actually enjoy it; the paint-splatter transition should be larger;
increase the quality of the current animations to make them high-definition and less
emoji-like." So, for every paint verb (Splat, the sweep transition, Wall, Spray, Tip, Brush):
- **Two paints plus white, and they mix.** Teal `#71EEB8` and the pop coral `#FF4F2E` (white on
  the dark hero). Where paint lands on paint it mixes like paint — a multiply/mix at the overlap
  with a wet, bleeding edge — never two flat shapes stacked. Splat alternates the two; the Wall
  cycles through them stroke by stroke; the sweep transition carries both as lap marks in one
  pass.
- **Slower, so it can be watched.** The sweep is a beat, not a flash: splat pop ≈ 260 ms, the
  sweep ≈ 900 ms, navigation at ≈ 1.3 s; nav-only strokes ≈ 1 s. Never faster than that again.
- **Bigger.** The splat is roughly twice today's — it should own a third of the screen on
  desktop before the sweep comes — with more satellites and longer drips.
- **Painterly, not clip-art.** No flat vector blobs: layered colour with a darker rim, a gloss
  highlight, grain, bleed at the wet edge, drips that bead; strokes with dry-brush breakup and
  lap marks. Render sharp at 2× (SVG filters or DPR-aware canvas), never a scaled bitmap. The
  same standard as the props in `art.py` and the tags in `wall.py`. If a still of the splat or
  a stroke would look wrong printed at poster size, it is not done.
- **A logo section, like Colossal's (owner, 2026-09-19):** a "Painted for" wall of the brands
  he has painted — Gucci, Crown Royal, Uber, Victoria's Secret, Vitamin Water, Sprite, Ford,
  Showtime, Moncler, Red Bull, Monkey 47, Johnnie Walker, Heineken, Jack Daniel's, Corona — as a
  grid on the home page (and the Services page) — **in each brand's actual colours** (owner:
  "put the logos in actual color for each"). Source each mark as the brand's real logo from its
  press kit or a Wikimedia Commons SVG (record the source URL in `brands.py`); where none is
  available yet, a typographic wordmark set in the brand's own colours. Never trace or redraw a
  logo by hand. **And the faces:** the owner asked to "add in Kylie or mentioned models" — a
  second strand, "Faces we've painted": Kylie Jenner (the mural project), John Lewis, Malcolm X,
  Antwuan (the Uber wall), Dexter (the Showtime wall), and the campaign models once Ephraim
  names them. Named people appear as painted portraits (his photographs of the walls), never as
  stock photos of the person.

#### What landed, and the numbers to hold (2026-09-19)
The mechanics went in ahead of the page skin — the white ground, the bands and the
typefaces are a separate step, so the pages below still wear the dark canvas. These are
the figures the build settled on; **none of them may get faster or smaller**, and the
verification below is how that is checked.

- **The tokens.** `--pop:#FF4F2E` with `--pop-mid`, `--pop-deep`, `--pop-rim`, `--pop-wet`;
  `--mint-rim` for the mint's own wet edge; `--gloss` (white) for the highlight on fresh
  paint; and **`--mix:#714A21`**, the channel-wise product of `--mint` and `--pop` — what a
  multiply computes at the overlap, named so the mixing has a value that can be looked up
  rather than only looked at. None of them carries type, so none claims a contrast pair.
  As everywhere in this repo, a hex outside `:root` is a bug.
- **The clock.** Splat pop **260ms**, sweep **900ms**, a button navigates at **1300ms** and a
  nav link at **1000ms** — measured in the page (1322 and 1020 on this box), not wall clock.
  Tip's pour is 1.4x: rim past the vertical at 364, sheet down at 1008, the run through at
  1260, the rule filling from 1652 and curing at 2856. Wash is untouched.
- **The size.** The throw's body is rx 151 where round two's was 72, with eleven satellites
  and four runs of 68–132px. 470px across at 1440 on the straight variant and 632 on the
  turned ones — a third of the screen and more. A phone gets 0.667 of the desktop, which is
  1.4x round two: 313px on a 390.
- **Two paints, and they mix.** The throw alternates mint and coral click by click; the
  stroke behind it always carries the other one, as its body and as lap marks of the first
  bleeding back in; the throw multiplies into the stroke, so the overlap is `--mix`. The
  Wall cycles mint, coral and ink stroke by stroke and crossings multiply — mint at hue 154
  and coral at 10 cross at hue 18, a rust that is neither. Spray writes in mint and throws
  coral specks. Tip pours mint and the pool's meniscus picks up coral where the run leaves
  for the rule. The brush on the beat rule paints mint with a coral wet edge.
- **How the Wall mixes without a stroke darkening against itself.** Three canvases, one of
  them on the page: the stroke under the brush is drawn on its own layer with source-over,
  the wall is composed as the laid-down paint with that layer multiplied over it, and the
  layer is merged down and cleared when the stroke ends and its runs have finished. The two
  extra canvases are never in the document, so `.paint-wall` is still one element carrying
  the whole wall. DPR is capped at `min(devicePixelRatio, 2)`.
- **Unchanged and not to be broken:** everything is under `html.motion`; reduced motion and
  no-script render exactly as before (`--reduced --compare` is true/true/true at 390 and
  1440); the Splat interception rules; one rAF; no layout shift; no counters and no labels.

**Verification** (serve the built `site/` on 8099 first):
`node /root/shot/oag-paint-verify.mjs` asserts the timings in-page, the throw's width as a
per cent of the viewport, the satellite and run counts, all three paints plus the mix in one
mid-stroke frame, the Wall's three paints and the third colour where two cross, and an empty
console on `/`, `/about`, `/graffiti-removal` and `/services`. It exits non-zero on any
failure. `node /root/shot/oag-paint-stills.mjs` writes the frames to judge printed.
`splat-verify.mjs`, `splat-stills.mjs`, `shot-oag-gr.mjs`, `shot-oag-build.mjs` and the
wall / spray / tip runs all still pass; splat-verify's and tip-verify's waits were moved to
the new clock, which is the only change any of them needed.

### Concept from Overall Murals' services page (owner, 2026-09-19)
"We really enjoyed Overall Murals' checkerboard negative space and cards describing it with
the full-page image of the murals going behind it" (their /services on desktop). The pattern:
a three-column checkerboard where every other cell is a white card — a big brushed number
(01…06), a short pop-coloured rule, the service title and copy, a "see more →" — and the
other cells are **windows onto a mural photograph fixed behind the grid**, so as the page
scrolls the mural moves behind the cards and shows through the negative space. For Ephraim:
the Services page becomes this board (Murals · Banners & signs · Graffiti removal · Public
works · Paint science · Commercial painting) with his walls behind the windows; the same
window idea can carry the Work grid (cards as negative space over one wall). Photo cells use
`background-attachment: fixed` (desktop; a scroll-linked translate on iOS where fixed is not
honoured), never a static crop. Mockup: scratchpad `oagmock/checker.html`.
- **The board is 3D, and the murals hand over seamlessly (owner, 2026-09-19):** "As you scroll
  the images move behind, making a 3D effect, and how it's set up like a checkerboard the
  transition between photos of murals is seamless." So the photo cells are not six crops — they
  are windows onto **one deep layer** that scrolls slower than the cards (parallax, ~0.5×), so
  the wall appears to sit behind the page. Along that deep layer the murals are laid **end to
  end as one continuous strip**, each wall's top edge feathered into the next (a soft gradient
  seam, never a hard cut), so as the visitor scrolls the Gucci wall gives way to Crown Royal
  gives way to John Lewis without any visible boundary — the checkerboard's gaps are what make
  the changeover invisible. Build: one absolutely-positioned `.deep` strip behind the board,
  `translate3d` on scroll via the Live loop (not `background-attachment: fixed`, which iOS
  ignores and which cannot cross-fade), with the cards above it in the normal flow; reduced
  motion = the strip static; no JS = the strip static at its first position.
- **Paint splatter on the cards, not film grain (owner, 2026-09-19):** Overall dresses its
  cards with a film-grain speckle; Ephraim's get **paint** — a few small flung splatters and a
  single drip on each white card (teal on some, coral on others, seeded per card so no two
  match, kept to the card's edges and corners and never under the type), drawn with the same
  painterly standard as the splat: rim, gloss, bleed. Static by default; on hover the card's
  splatter gets one fresh fleck (a tiny Splat, no sweep). Generated by `strokes.py` alongside
  the brush strokes.
- **Not a checkerboard — a diamond board, and don't copy (owner, 2026-09-19):** "Maybe we
  switch ours up and use some sort of diamond concept, add his teal and a few other colours as
  splatter on the crisp white cards before we add the text — let's not copy." So the Services
  board is Overall's *idea* (cards as negative space over a deep, parallaxing mural layer with
  seamless hand-over) in Ephraim's *form*: the grid is rotated 45° — a lattice of diamonds —
  where the white diamonds are the cards and the gaps between them are the windows onto the
  mural behind. Each card is crisp white, splattered first (teal plus a few other colours —
  coral, a yellow, a violet, the palette of a working drop cloth) and lettered after, so the
  type sits over the paint. The deep layer, the parallax and the feathered hand-over stay.

## Ephraim's drop, 2026-09-20 — RAINS and Flower City Arts Center
The owner dropped `Ephraim website.zip` (1.28 GB) in and said *"he wants that content
integrated into his site."* The whole brief, the file table and the seven commits it
became are **`docs/ephraim-drop-2026-09-20.md`** — read that before touching either wall.
The short version:
- **RAINS**, New York, for **AMC — Angel Media Co.** (the placard on the brick reads
  "AMC angelmediaco."). His drone edit is the page hero film, his portrait reel is "the
  wall going up" under the story, and four of his photographs are the gallery. AMC is on
  the "Painted for" wall as type in the navy sampled off that placard.
- **Flower City Arts Center**, Rochester — a community wall on the underpass by the
  ballpark, **filmed by Max, @omgmaxgod**, which is the only photo credit on the site.
  Hero and gallery are 4K frames from his film. It is the picture `public_works()` leads
  with now, in place of the crew on a lift.
- **Dimensions may now be None** — both or neither — and `dims()` gives back nothing for
  a wall without them. Every figure counts `measured()` and the stats band says so. A
  wall with no feet cannot carry the scale figure, so its page opens on `page_hero` with
  the film over the photograph instead of `scale_hero`.
- **Every hero clip is built twice** (the `make-*.sh` scripts): the cut at the camera's
  own size and rate, and a 1920-wide companion at crf 24. The server HTML names the
  companion — a phone, a no-script visitor and a reduced-motion visitor must never be
  asked for the 4K file — and `PICK`, one line in the body after each `<video>`, swaps
  the master in above 900px *while the parser is still there*. Never move that into
  site.js: it is deferred, and by then the 1080 file is already on the wire.
- **Both films are on their pages whole, with sound, behind a play button** —
  `film_band()`, `out/video/film-*.mp4`, remuxed with no re-encode. The element is
  `preload="none"`, so nothing is fetched until somebody clicks; the button is built by
  site.js under `html.motion` and with no script the browser's own control is already
  there. Splat does not touch it: the click mechanic only acts on `a[href]` and a form's
  submit.

### The two holes, and they are the same hole twice
- **The feet for both walls.** Nobody has measured either for us, so both carry
  `dim_w=None, dim_h=None` and the card, the page and the project nav say *feet to come*
  in his own hand. Ask him; fill in two numbers and four places on the site change
  themselves. **Do not estimate them off a photograph.**
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

### Needed from Ephraim — round three (2026-09-19)
The brands wall and the faces strand are built to be finished by him, not by us. Each
line below is a hole the build already has a shape for: fill it and one row changes,
nothing else on the page moves. Nothing here is invented in the meantime.

- **A photograph of the Kylie Jenner wall.** She is named in the faces strand
  (`FACES` in build.py) because the owner asked for her, and she is the one face there
  that links nowhere: no photograph of that wall has reached us, and linking a name to
  somebody else's wall would be worse than linking it to nothing. Send the photograph
  and a city and she becomes a project row like the other four.
- **The campaign models' names.** The strand ends on a marker aside, `+ the campaign
  models`, because Ephraim has not named them. It says there are more without inventing
  who; name them and they join the row.

### Brands and faces — where every mark came from (2026-09-19)
The "Painted for" wall is `brands.py` + `brand_wall()`; `process-brands.sh` downloads the
marks into `assets/brands/` and copies them to `out/img/brands/`. Both directories are
gitignored, the way every other image on this site is, so **brands.py plus that script is
the record** — running it on a clean clone rebuilds the wall byte for byte, and a file
already on disk is never overwritten, so a mark Ephraim supplies by hand survives a re-run.

One rule shaped all of it (round three, above): *never trace or redraw a logo by hand.* A
mark is either the brand's own file or it is type; there is no third thing on this wall.

**Eleven are the brand's own SVG**, each Public Domain on Wikimedia Commons as a wordmark
below the threshold of originality, each still a registered trademark and used the one way
a contractor may use a client's mark — nominatively, to say whose wall he painted,
unaltered, not as an endorsement. The licence line and the optical height of each are in
`brands.py`.

| Brand | Commons file | Page |
|---|---|---|
| Gucci | `File:Gucci Logo.svg` | https://commons.wikimedia.org/wiki/File:Gucci_Logo.svg |
| Uber | `File:Uber logo 2018.svg` | https://commons.wikimedia.org/wiki/File:Uber_logo_2018.svg |
| Victoria's Secret | `File:Victoria's Secret.svg` | https://commons.wikimedia.org/wiki/File:Victoria%27s_Secret.svg |
| Sprite | `File:Sprite 2022.svg` | https://commons.wikimedia.org/wiki/File:Sprite_2022.svg |
| Ford | `File:Ford logo flat.svg` | https://commons.wikimedia.org/wiki/File:Ford_logo_flat.svg |
| Showtime | `File:Showtime.svg` | https://commons.wikimedia.org/wiki/File:Showtime.svg |
| Moncler | `File:Logo Moncler Group.svg` | https://commons.wikimedia.org/wiki/File:Logo_Moncler_Group.svg |
| Red Bull | `File:Logo of Red bull.svg` | https://commons.wikimedia.org/wiki/File:Logo_of_Red_bull.svg |
| Johnnie Walker | `File:Johnnie Walker wordmark.svg` | https://commons.wikimedia.org/wiki/File:Johnnie_Walker_wordmark.svg |
| Heineken | `File:Heineken logo.svg` | https://commons.wikimedia.org/wiki/File:Heineken_logo.svg |
| Corona | `File:Corona Extra text logo.svg` | https://commons.wikimedia.org/wiki/File:Corona_Extra_text_logo.svg |

A logo is not its bounding box — Gucci's wordmark is all cap height and Corona's is two
lines with air round them — so each mark carries its own rendered height (`h`, `hm`) tuned
by eye, and the wall reads as one optical weight rather than fifteen box sizes.

**Four are still typographic**, in the brand's own colour, because no free file exists:

- **Crown Royal** — the wide face, `#52247F`, the purple of the bag and the bottle livery.
  Nothing on Commons under the name but photographs.
- **Vitamin Water** — the wide face, `#E0007A`. The mark is flavour-coloured and the master
  brand asset has not been supplied; this magenta is approximate.
- **Monkey 47** — the serif, ink. Commons holds only a CC BY-SA upload derived from a
  photograph, and a share-alike obligation is not something to put on a client's site.
- **Jack Daniel's** — the serif, ink. Old No. 7 is a drawing, not a wordmark, and everything
  filed under the name is a photograph.

**Two marks are right but not exact.** Commons has the *Moncler Group* lockup and not the
bare MONCLER wordmark, so that cell reads MONCLER with GROUP under it; and Red Bull's free
file is the wordmark alone — the two bulls and the sun are a drawing and are not on Commons
free. Both are flagged below.

#### What Ephraim owes on this section
Each of these is a hole the build already has a shape for. Fill it and one row changes.

- **Brand assets** for Crown Royal, Vitamin Water, Monkey 47 and Jack Daniel's — an SVG or
  an EPS from each brand's press kit. Drop them in `assets/brands/<slug>.svg`, flip that
  row's `mark` from `type` to `svg` in `brands.py`, and the cell stops being type.
- **The plain Moncler wordmark and the full Red Bull mark**, if he has them from the job.
- **A photograph of the Kylie Jenner wall** (see "Needed from Ephraim" above) — she is the
  one face in the strand that links nowhere.
- **The campaign models' names**, which the marker aside `+ the campaign models` stands in
  for until he supplies them.
- **Public-works photographs** — Mexico, Brazil, the teen-empowerment murals. `public_works()`
  is framed for them and says in marker that more is coming; the picture there today is the
  crew on the lift, labelled as the crew.

#### The Services board (the diamond lattice)
`services_board()` + `splatter.py`. The deep strip is five heroes from `DEEP_WALLS`, laid end
to end and cross-faded into each other across exactly the distance they overlap, parallaxing
at roughly half the page's speed through a **named CSS view timeline declared on the board**
— not on the strip, because the board has `overflow:hidden` and is therefore a scroll
container, and an anonymous `view()` inside it measures the strip against a box it never
moves in and comes out frozen. The strip carries `data-deep` / `data-deep-rate` and the CSS
animation stands down the moment `<html>` gains `.deep-js`, so site.js can take the motion
over from the Live loop without the two ever fighting. With no script, or under reduced
motion, the strip is static at its first position — the state the design is drawn for.

Two measurements that must stay paired: the strip is the board **plus exactly the distance
it travels** (`--deep-run`), and each wall overlaps the last by `--feather` and is masked in
across exactly `--feather`. Mixing a percentage margin (which resolves against width) with a
percentage mask (which resolves against height) puts a black band between every wall.
