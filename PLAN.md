# Open Air Gallery — new site for openairgallery.art (Ephraim)

> The LodiStudios plan that used to live in this file is canonical at
> `/root/LodiStudios/docs/plan.md` (symlinked from `/root/LodiStudios-plan.md`).
> This file now holds the plan for the Open Air Gallery client site.

## Context

Ephraim owns Open Air Gallery, a **muralist and large-image company** — not a painting
gallery. His roster is national-brand scale plus civic portraits: Gucci in Manhattan
(81′ × 80′), Crown Royal × Trail Blazers in Portland (85′ × 90′), Uber in San Francisco,
Victoria's Secret in Austin, Vitamin Water, Sprite, Ford Mustang, Showtime, Upendo, I Am A Man
in Chicago, and the **John Lewis and Malcolm X murals in Rochester** (53′ × 50′ each). He also
sells graffiti removal, pressure washing and commercial painting.

The current site is Wix (`ns6/ns7.wixdns.net`) and undercuts the work: a tiny-planet hero,
mural slides that lazy-load blurred, a broken black shape mid-page, a headline colliding with a
mint watermark, and Media/Shop links that 404. The brief in one sentence, recorded in
`/root/openairgallery-src/CLAUDE.md`: **the work is far better than the site presenting it.**

Owner decisions (2026-09-18): six pages, no shop; dark canvas with the project dimensions as
the hook and his mint as the single accent; company brand with an artist-led story; preview at
`preview.greenflashusa.com/p/<slug>/`, then **live on a Green Flash subdomain while Wix keeps
serving openairgallery.art** (the real domain switches later, by Ephraim, at Wix); graffiti
removal gets **its own page that looks awesome**, a **home-page band promoting it the way Max's
site advertises Green Flash**, and **an animation of a graffitied brick wall being cleaned to
sparkling new**.

Built the Green Flash way: the Drone God Max static generator as the model, one idea per commit
verified before the next, the motion contract kept, Opus subagents implementing one step each
from this plan, the lead session reviewing.

## Verified facts to build on
- Wix renditions can be fetched at size by rewriting a *rendered* URL's transform segment to
  `/v1/fill/w_2400,h_<H>,al_c,q_90,enc_auto/<name>.jpg` (200, ~900 KB); bare `/media/<id>` 403s.
- The site's mint is `#71EEB8` (companion `#55B38A`); on `#0A0A0B` it is 13.8:1 (AAA).
- Live-site email is inconsistent (`hello@` in the hero, `info@` in the footer) — default to
  `hello@openairgallery.art`, confirm with Ephraim.
- `/root/openairgallery-src` is already a git repo (`b8fab99`) holding `CLAUDE.md`.
- Screenshot tooling exists: `/root/shot/shot.mjs`, playwright 1.63.

## 1. Repo layout — `/root/openairgallery-src`
```
build.py              from /root/dronegodmax-src/build.py, stripped (see below)
projects.py           PROJECTS — single source of truth for the twelve walls
site/css/site.css     hand-written; build.py asset_v() hashes it
site/js/site.js       hand-written
site/*.html           generated, gitignored
assets/               originals, gitignored        out/img/{,t/}  ffmpeg output, gitignored
fetch-wix.py  wix-sources.json  process.sh  publish-preview.sh  deploy.sh
deploy/nginx/ephraim-site.conf   .gitignore   CLAUDE.md
```
**Copy from DGM `build.py`:** `ext()` 133-135, `img()` 171-173, `asset_v()` 628-631,
`layout()` 673-707 (rewrite head: site name, theme-color `#0A0A0B`, fonts), `nav_html()`
200-224, `footer_html()` 226-256, `page_hero()` 636-646, `cta()` 630-634, `swipe()` 613-627,
the `pages` dict + write/sitemap/robots loop 1370-1394, and `gf_band()`/`gf_strip()` 137-169 as
the *shape* of `gr_band()`/`gr_strip()`. Thread `PREFIX = os.environ.get('PREFIX','')` through
`img()`, `nav_html()`, `footer_html()` and every literal `href="/…"` so the preview works under
`/p/<slug>/`.
**Strip:** GF cross-sell content (15-41), `SHOP`/`price_card` (59-132), mavic SVGs (310-427),
swatters (399-558), flight deck (259-610), tee, Instagram OAuth page, WordPress redirects,
`BUBBLES`, the gold/violet tokens and Bebas Neue.
**`projects.py`:** per project `slug, title, client, city, state, dim_w, dim_h, year,
category ('brand'|'portrait'|'civic'), hero, gallery[], story, credit, featured`; a build-time
assert that dims are ints and `hero` exists in `out/img/` (DGM's `price_card` assert discipline,
648-656). `.gitignore`: DGM's, minus `bubbles.json`, plus `wix-cache/`; keep `site/css`, `site/js` tracked.

## 2. Design system
**Tokens** (`:root`): `--ink:#0A0A0B` · `--ink-2:#121214` · `--ink-3:#1A1A1D` ·
`--paper:#F4F3EF` · `--muted:#A6A49E` · `--dim:#6E6C67` · `--mint:#71EEB8` ·
`--mint-deep:#55B38A` · `--wall:#E9E7E2` · `--line:rgba(244,243,239,.10)` · `--radius:4px`
(near-square — signwriting, not SaaS) · `--max:1240px` · `--nav-h:72px`. **Dark only.**
Contrast verified: mint/ink 13.8:1, mint-deep/ink 7.7:1, muted/ink ~7.6:1, ink-on-mint 13.8:1.
Rule: mint never carries body copy under 16px and never sits on `--wall`.

**Type:** display **Archivo** variable (`wght 400..900, wdth 62..125`) — the dimension figures at
`wdth 125 / wght 800` so they are *physically wide*; eyebrows at `wdth 75`, tracked. Body
**Inter** 400/600/700, tabular numerals. One `fonts.googleapis.com/css2` link, `display=swap`,
preconnects, and a metric-near fallback stack.

**The dimensions hook** — `dims(w, h, size)` in build.py emits
`<div class="dims"><span class="n">81</span><span class="f">′</span><span class="x">×</span><span class="n">80</span><span class="f">′</span></div>`;
`.dims{font-size:clamp(3.4rem,11vw,9rem);line-height:.82;color:var(--paper)}`, `.f`/`.x` at
`.38em` in `--mint`. Mint touches only the prime marks and the × — one accent stays one accent.
**Project card** `.pcard.rv`: `<picture>` at 4:3, bottom scrim, `.dims` small, title + `City, ST`,
hairline border → mint on hover/focus. **Project page:** full-bleed hero (2400w,
`fetchpriority=high`) → title + `.dims` large → the scale strip (§4) → story → `swipe()` gallery
→ credit → prev/next → `cta()`.
**Nav:** wordmark · `Work · Graffiti Removal · Services · About · Contact` · mint
`Book a free consult` pill; DGM hamburger, no dropdowns. **Footer:** brand + `@openairmurals` +
email · Work (top six) · Company (Services, Graffiti Removal, About, Contact) ·
"Murals · Banners · Signs · Graffiti removal · New York and nationwide".
**Breakpoints** mobile-first: base, 640 (2-up), 960 (3-up, nav expands), 1240 (wrap cap);
`section{padding:clamp(4.5rem,10vw,8rem) 0}`.

## 3. Pages and copy direction (reuse his true sentences; they are good and already indexed)
**Home** — hero: full-bleed Gucci, headline `MURALS THAT CAPTURE THE GAZE` (his line), sub
naming Ephraim and three walls ("81 feet of Gucci in Manhattan, 85 feet of Crown Royal in
Portland, John Lewis and Malcolm X in Rochester"). Then: a **scale statement** band ("Twelve
walls. Over 19,000 square feet." — computed from `projects.py`, never typed); **featured
projects** (Gucci, Crown Royal, John Lewis, Uber, Malcolm X, Upendo); the **Rochester civic
beat** as its own section — John Lewis and Malcolm X side by side, 53′ × 50′ each; the
**process** in three beats, verbatim source: *"it starts from a small image and explodes onto a
massive canvas… the ability to scale and project is what differs an artist and a muralist"* /
*"There is a science to paint… we analyze the way the paint will decay over time and how the
light will affect its colour"* / the environmentally friendly anti-vandalism coating; then the
**graffiti-removal band** (§3a); then `cta()` "Book a free consultation".

**3a. `gr_band()`** — modelled on `gf_band()` (DGM build.py 139-156), placed after the process
and before the final CTA, exactly where DGM places the GF band. It is **the one scrubbed-clean
block on a dark site**: a `--wall #E9E7E2` panel, near-black type, with a faint diagonal ghost of
overpaint fading to nothing across the top-left (`linear-gradient(115deg, rgba(10,10,11,.10),
transparent 42%)`) — the pitch in one image — and, as its visual, a **compact non-interactive
loop of the wall going from tagged to clean** (§4b, the same drawn wall, scroll-tied or looping,
no interaction). Eyebrow `ALSO FROM OPEN AIR`, headline `We take it off, too.`, body: *"Open Air
Gallery removes unsightly graffiti and stains with industrial-strength cleaning, available in
NYC — the same crew that paints the wall knows how to clean it."* Chips: Graffiti removal ·
Pressure washing · Commercial painting. Primary `See graffiti removal →` (ink on mint) to
`/graffiti-removal`; ghost `Send a photo, get a quote` to `/contact?service=graffiti`.
`gr_strip()` (the slim one-liner, from `gf_strip()` 158-169) goes on Services, Work and About.

**Work** `/work` — `.dims`-forward grid of all twelve; filter chips `All · Brands · Portraits ·
Civic` as plain anchors that work without JS. Twelve pages at `/work/<slug>`: gucci-new-york,
crown-royal-trail-blazers, uber-san-francisco, victorias-secret-austin, vitamin-water-new-york,
sprite-new-york, ford-mustang-chicago, showtime-dexter-boston, upendo-los-angeles,
i-am-a-man-chicago, john-lewis-rochester, malcolm-x-rochester.

**Graffiti Removal** `/graffiti-removal` — a product page: hero `COMMERCIAL GRAFFITI REMOVAL`
with **the wall-cleaning mechanic as the hero itself** (§4b); sub *"Attract more customers ·
Increase safety · Beat the competition"* (his); the three services verbatim (graffiti removal /
pressure washing / commercial painting); a **before/after** presentation (`.ba[data-ba]`: two
stacked images with a draggable mint divider; side by side, labelled, with JS off) using his
real photos if he has them, the drawn wall otherwise; the **process** in four beats —
assessment (surface analysis), removal method matched to the substrate, anti-graffiti coating,
maintenance — extending his real "Take a picture · Send us an email · Pay a 50% deposit"; **who
it's for** (property managers, brands and franchises, cities and BIDs); its own CTA `Send a
photo, get a quote`.

**Services** `/services` — murals (scale/projection), banners and signs (the roster's sign work:
Heineken, Jack Daniels, Corona, Black Crow, House of Pizza), the paint-science and preservation
paragraphs; `gr_strip()` near the bottom. **About** `/about` — Ephraim named and photographed
(placeholder until he sends one); *"we pour our hearts into every brushstroke"*; the team; the
process in full; where they work. **Contact** `/contact` — name, email, phone, company,
location, service (select, pre-filled from `?service=`), budget, message, `_gotcha` honeypot;
sidebar with email, `@openairmurals`, response expectation.

## 4. Mechanics — motion vocabulary **Roll · Scale · Cure · Wash**
- **Roll** — reveals arrive like a roller pass: `.rv` clip-path wipe left→right + 18px rise.
- **Scale** — the figure (§4a); `.dims` grow `wdth 100→125` on entry.
- **Cure** — the settle: one slow mint sheen across a `.dims` rule when it lands, never repeated.
- **Wash** — the graffiti wall (§4b).
Contract for all four: pages render complete without JS; everything hidden is scoped to
`html.motion` (added by the inline script in `layout()` only when JS runs and
`prefers-reduced-motion` is off) with `animation: oaSelf 0s linear 2.8s forwards` self-reveal;
one IntersectionObserver adds `.in` (DGM site.js 102-107); every effect checks reduced motion;
real text in the server output. No counters, scores or labels anywhere. Sound: none shipped;
if ever added, muted by default behind a persistent toggle.

**4a. The scale figure.** Each project hero: `<div class="scale" data-scale data-ft="81">` with
the photo, a 1px mint baseline, and `<button class="fig" data-fig aria-label="Drag the figure
for scale">` holding an inline 6-foot silhouette SVG. Figure height = `(6 / ft) × wall pixels`
— on Gucci it is genuinely tiny, which is the point. **Desktop** (`(hover:hover) and
(pointer:fine)`): pointer drag along the baseline, `setPointerCapture`, one rAF writing `--fx`
(0–1); a small mint `6 ft` mark rides above it; arrow keys move it 2% (it is a real button).
**Mobile**: touch-drag primary; `deviceorientation` tilt layered on only after a first drag and
only where no permission prompt is needed (present on Android, silently absent on iOS),
`gamma` ±25° → `--fx`, damped, throttled to 30 Hz, detached on scroll-away. **No JS:** the
figure renders at `--fx:.12`, correctly sized, captioned `6 ft` — a static scale bar.
**Reduced motion:** the static state; no listeners, no transitions; the "Drag me" hint exists
only inside `html.motion`.

**4b. The wall — "Wash".** A drawn (SVG/CSS) brick wall with drawn graffiti, two layers:
*tagged* over *clean*. **Desktop:** the visitor drags a pressure-washer head; the stroke punches
through the tagged layer (canvas or `mask-image` from a small offscreen mask) with a soft wet
edge and a few drips; when ~80% is clean the remainder wipes itself, a specular glint sweeps the
bricks, a handful of sparkle particles fire once, and the wall rests clean. **Mobile:** finger
strokes do the same; optional tilt "rinse" lets water run down; particle counts capped. **Home
band:** the same wall as a compact non-interactive loop (tagged → clean → hold → reset) or a
`--scroll`-tied reveal, linking to the page. **No JS:** the finished clean wall with a small
"before" thumbnail beside it — real content, no motion. **Reduced motion:** a plain crossfade
tagged → clean, no particles. **Assets:** drawn by default (crisp at any size, no licensing
question); an optional swap to Ephraim's real before/after photos as the two layers, same code.
Performance: one rAF-batched pointer handler, `will-change` only while dragging, listeners
bound only when in view, no layout shift.

## 5. Image sourcing
`wix-sources.json` — hand-written `slug → {hero: <exact rendered URL>, gallery: [...]}` harvested
from the saved Work/Home HTML (filenames are already project-named, e.g.
`Gucci%20Mural%20by%20Open%20Air%20Gallery.jpeg`). `fetch-wix.py` — parse the
`/v1/(fill|fit|crop)/…` segment, keep the media id, `~mv2.ext` and trailing filename
byte-for-byte, rewrite the transform to `w_2400,h_<round(2400*h/w)>,al_c,q_90,enc_auto`, send a
browser UA and `Referer: https://www.openairgallery.art/`, write `assets/<slug>-hero.jpg`, skip
if present (`wix-cache/`), log the width; never build a bare `/media/<id>` URL. `process.sh`
(DGM's, retargeted): `out/img/<slug>.webp` ≤2400w q84, `-1600` q82, `-800` q80, `t/<slug>` ≤640w
q76; favicons from the wordmark. `img()` becomes `pic(slug, alt, sizes)` emitting `<picture>`
with a three-width srcset and explicit width/height. **Swap when originals arrive:** drop them
in `assets/` under the same names, delete `wix-cache/`, re-run `process.sh`, deploy — filenames
are the contract. CLAUDE.md records that Wix copies are placeholders and the date pulled.

## 6. Build steps — one commit each, an Opus agent per step, the lead reviews each
Every step ends with `python3 build.py` succeeding and a screenshot pass:
`/root/shot/shot-oag-build.mjs <url> <prefix>` (a copy of `shot.mjs` shooting 1440×900 and
390×844, collecting `pageerror`/`console.error`, printing JSON) returning `errors: []`.

| # | Commit | Files | Reuse (DGM) | Verify |
|---|---|---|---|---|
| 1 | Scaffold | `build.py`, `.gitignore`, empty css/js | `build.py` 673-707, 1370-1394 | build writes `site/index.html` |
| 2 | Tokens + type | `site/css/site.css` | css 1-36 | contrast script: mint/ink ≥ 13:1 |
| 3 | Layout, nav, footer, PREFIX | `build.py` | `nav_html()`, `footer_html()` | shots both widths; hamburger at 390 |
| 4 | Motion layer (Roll·Scale·Cure) | css, js | site.js 102-107; css 392-418 | JS-blocked: every section visible; reduced-motion shot = static |
| 5 | `projects.py` + `dims()` + `pcard` | `projects.py`, `build.py`, css | assert pattern 648-656 | build fails on a bad dim |
| 6 | Home | `build.py` | `page_hero()`, `cta()` | shots; JS-off text present; square-foot total computed |
| 7 | Work index + 12 pages | `build.py`, css | `swipe()` 613-627 | 13 files; every `.dims` matches `projects.py` |
| 8 | About | `build.py` | — | shots |
| 9 | Services + `gr_strip()` | `build.py`, css | `gf_strip()` 158-169 | shots |
| 10 | Graffiti Removal page (before/after, process, who-for) | `build.py`, css, js | `page_hero()` | before/after side by side with JS off |
| 11 | **Wash** — the wall mechanic on the page hero | js, css, `build.py` | motion IIFE 84-107 | playwright drag cleans ≥80% and triggers the glint; JS-off shows the clean wall + before thumb; no console errors |
| 12 | `gr_band()` on Home with the wall loop | `build.py`, css | `gf_band()` 139-156 | band visible at 1440 and 390; link resolves |
| 13 | Contact + Formspree | `build.py`, `site.js` | site.js 51-73; `FORM_ENDPOINT` 86 | endpoint unset → `mailto:` fallback; honeypot present |
| 14 | Scale figure | js, css, `build.py` | `shot.mjs --drag` | drag moves the figure; keyboard moves it; no errors |
| 15 | Images pipeline | `fetch-wix.py`, `wix-sources.json`, `process.sh` | `process.sh` | every hero exists ≥1600w |
| 16 | SEO | `build.py` | `layout()`, sitemap 1380-1394 | 18 URLs incl. `/graffiti-removal`; JSON-LD parses |
| 17 | Preview publish | `publish-preview.sh` | `publisher.py` 88-105 | `curl -I` → 200 + `X-Robots-Tag` |
| 18 | Owner + Ephraim review | `CLAUDE.md` | house rule | corrections recorded |
| 19 | Subdomain go-live | `deploy.sh`, `deploy/nginx/ephraim-site.conf` | `deploy.sh`, `/etc/nginx/sites-enabled/max` | §7 |

**JSON-LD:** site-wide `LocalBusiness` (name, email, `areaServed` NYC + US, `sameAs` Instagram,
`founder` Person Ephraim); each project a `CreativeWork` (`creator`, `locationCreated`,
`width`/`height` as `QuantitativeValue` in feet, `dateCreated`); `/graffiti-removal` a `Service`
(`serviceType: "Graffiti removal"`, `provider` → the business, `areaServed` New York);
`/services` an `OfferCatalog`.

## 7. Deploy
**`publish-preview.sh`** mirrors `/srv/sitebuilder/bot/sitebuilder/publisher.py` 88-105 without
the bot: `PREFIX=/p/$SLUG BASE_URL=https://preview.greenflashusa.com/p/$SLUG python3 build.py`
→ copy `site/` + `out/img/` into `/srv/sitebuilder/p/.staging-$SLUG/` → `robots.txt` =
`User-agent: *\nDisallow: /` → `chmod 755/644` → swap into `/srv/sitebuilder/p/$SLUG` via
rename → print the URL. `SLUG` is a fixed 22-char `secrets.token_urlsafe(16)` stored in the
script so republishes keep Ephraim's link alive.
**Subdomain go-live:** `gd-dns add ephraim --ip 142.93.198.162` → `dig` → `certbot certonly
--nginx -d ephraim.greenflashusa.com` → `mkdir /var/www/ephraim && chown www-data:www-data` →
`deploy/nginx/ephraim-site.conf` = `/etc/nginx/snippets/dronegodmax-site.conf` with
`root /var/www/ephraim`, same headers/gzip/`try_files`/immutable `/assets/` cache, minus every
WordPress and Instagram block, installed to `/etc/nginx/snippets/`; vhost at
`/etc/nginx/sites-available/ephraim.greenflashusa.com` modelled on `sites-enabled/max` (serving,
not redirecting) → `BASE_URL=https://ephraim.greenflashusa.com ./deploy.sh` (rsync `site/`
`--delete --exclude assets/`, rsync `out/img/` → `/var/www/ephraim/assets/img/`, chown,
`nginx -t && systemctl reload nginx`).
**Nothing touches Wix or openairgallery.art now.** Later, as its own step: Ephraim adds an A
record at Wix → `142.93.198.162` and a `www` CNAME; `certbot certonly --nginx -d
openairgallery.art -d www.openairgallery.art`; `server_name` change; redeploy with the real
`BASE_URL`; the subdomain becomes a 301 exactly as `sites-enabled/max` does today.

## 8. Verification (whole site)
Per page at 1440 and 390: screenshot; `errors: []` from the console collector; a
`javaScriptEnabled:false` context screenshot showing every section; a reduced-motion context
matching the static render; `curl -sI` showing `X-Content-Type-Options`, `X-Frame-Options`,
`Referrer-Policy`, `Cache-Control: …immutable` on `/assets/`; an HTML-parser spot-check;
`curl -s <url> | grep -c "81′"` proving real text for crawlers; `xmllint --noout site/sitemap.xml`;
the Wash and Scale mechanics driven by playwright pointer sequences; the preview URL returning
`X-Robots-Tag: noindex`.

## 9. Risks
(a) **Photo quality** — Wix renditions are re-compressed; cap hero display at 1600 CSS px, push
hard for originals, keep the swap one command. (b) **Wix image terms** — his own photographs on
his own new site, treated as temporary, pull date recorded. (c) **Mechanics on mobile** —
rAF-batched, one custom property, listeners only in view, particle caps. (d) **Fonts** — two
families, `display=swap`, preconnect, metric-near fallback. (e) **Contrast** — verified; hold
the mint rules. (f) **Scope creep** — Shop and Media stay dead; Phase 2 if asked.

## 10. Needed from Ephraim (does not block the build)
A photo of himself and a short bio; the original mural photos (people in frame for scale);
real before/after graffiti photos if he has them; which email is correct; a Formspree form id
(or we create one on the Green Flash account); later, the Wix DNS change.
