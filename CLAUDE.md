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
- **Splat — the fifth verb (owner, 2026-09-19), and Home only.** He asked for it in one
  sentence: *"Add a painting animation where a paintbrush paints the screen or splatters on the
  screen when you click buttons on home page."* So the vocabulary is now **Roll · Scale · Cure ·
  Wash · Splat**, and Splat is the only one a visitor sets off on purpose. Clicking any
  button-styled link on Home — every `.btn`, including the nav's mint "Book a free consult" pill
  — throws a mint SVG blob (turbulence-displaced, three seeds and three turns in rotation, drips
  running out over 300ms) from the exact click point; 120ms later a roller pass sweeps in from
  the side the button is on, covers the viewport in 420ms behind a bristled leading edge with
  lap marks down it, and the link is followed at 555ms. It is **Home only because that is what
  he asked for**: `build.py` writes `data-splat` on Home's `<body>` and `site.js` binds nothing
  on a page without it — do not spread it to the other five pages without asking. It only ever
  touches a plain left click, with no modifier key, on a same-origin http(s) link: middle-click,
  ctrl/cmd/shift/alt-click, `target=_blank`, downloads, `mailto:` and `tel:` all go through as
  ordinary links, a same-page `#` anchor gets the splat and no stroke, and a second click during
  a pass does nothing. It lives entirely under `html.motion`, so reduced motion and a page whose
  script never arrived get plain links — the contract in PLAN.md §4 is unchanged. The overlay is
  fixed, `pointer-events:none`, `aria-hidden`, and is torn down on `pageshow` and 1.5s after a
  click that went nowhere, so a bfcache back never lands on a painted page. Mint only; no sound,
  no counter, no label.
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
