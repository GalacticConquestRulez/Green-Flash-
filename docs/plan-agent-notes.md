# Design-agent implementation notes (2026-09-18)

The detail behind PLAN.md. Where the two differ on a decision, PLAN.md wins; where PLAN.md is silent, use this.

I have what I need. Here is the plan.

---

# Open Air Gallery — implementation plan

Verified during exploration: the Wix rendered-URL upscale works (`…~mv2.jpg/v1/fill/w_2400,h_1600,al_c,q_90,enc_auto/…jpg` → 200, 894 KB) while bare `/media/<id>` → **403**. The mint sampled from the live pages is **#71EEB8** (18 occurrences; companion **#55B38A**). The Work page confirms the roster with cities. Droplet IP **142.93.198.162**. Playwright lives at `/root/shot/node_modules` (`/root/shot/shot.mjs` is the reusable runner).

## 1. Repo layout — /root/openairgallery-src (git already initialised, 2 commits)

```
CLAUDE.md          exists — append every client correction
build.py           from /root/dronegodmax-src/build.py, stripped
projects.py        the data (below)
site/css/site.css  hand-written, TRACKED (build.py asset_v() reads it back)
site/js/site.js    hand-written, TRACKED
site/*.html        generated — gitignored
assets/            source photos — gitignored
out/img/           ffmpeg output — gitignored
fetch-wix.py  process.sh  deploy.sh  publish-preview.sh
.preview-slug      tracked, so republishes keep the client's link alive
```

**Copy from DGM, keep:** `asset_v()` (build.py:659-663), `layout()` (673-707), `img()` (171-173), `ext()` (133-135), `nav_html()`/`footer_html()` shape (200-256), `cta()` (630-634), `page_hero()` (636-646), `swipe()` (613-628), the pages-dict → `site/*.html` + sitemap + robots writer (1370-1394), the contact handler (site/js/site.js:51-73), the reveal observer (102-107), lightbox (40-50), `.gitignore` verbatim.

**Strip:** `GF_SERVICES`/`GF_FOOTER`/`GF_BOOK` (15-41), `gf_band()`/`gf_strip()` (139-169) — *but keep their markup as the model for the graffiti band*, `SHOP`+`price_card()` (59-132), `mavic_svg` (310-427), swatters (399-558), flight deck (259-610), `vtile()`/`quote()`, tee, Instagram OAuth, the WordPress redirect block in the nginx snippet, and the gold/violet palette + Bebas Neue.

`projects.py` — one `PROJECTS` list of dicts, order = Work index order:
`slug, title, client, city, state, w_ft, h_ft, year, category('brand'|'portrait'|'civic'), hero, gallery[], story (one paragraph), credit, wix (rendered URL)`.

Roster (from the live Work page, dimensions W × H): gucci NYC 81×80 · crown-royal-trail-blazers Portland 85×90 · uber SF 62×23 · victorias-secret Austin 36×8 · vitamin-water NYC 9×20 · sprite NYC 11×16 · ford-mustang Chicago 23×36 · showtime-dexter Boston 18×9 · upendo LA 18×18 · i-am-a-man Chicago 15×32 · **john-lewis Rochester 53×50 · malcolm-x Rochester 53×50** (both `civic`). Moncler/Red Bull/Monkey 47 have no dimensions on Wix — hold as a 13th-15th tranche pending Ephraim.

## 2. Design system (dark only)

```css
:root{
  --bg:#0A0A0B; --bg-2:#121214; --surface:#17171A; --line:rgba(255,255,255,.10);
  --text:#F4F4F2; --muted:#A6A6A2; --dim:#6E6E72;
  --mint:#71EEB8; --mint-deep:#55B38A; --mint-glow:rgba(113,238,184,.14);
  --font-display:"Archivo",system-ui,sans-serif;
  --font-body:"Inter",system-ui,sans-serif;
  --max:1240px; --nav-h:72px; --radius:14px;
}
```

**Contrast (computed):** #71EEB8 on #0A0A0B = **13.8:1** (AAA); #55B38A = 7.7:1 (AA all sizes); #A6A6A2 muted ≈ 8.9:1. Black text on a mint button = 13.8:1. No mint-on-white anywhere.

**Type.** Display **Archivo** (variable `wdth 62..125, wght 400..900`) — a grotesque drawn for headline/sign impact; the width axis lets `81′ × 80′` be set genuinely *wide*, which is the whole hook, and it reads nothing like DGM's Bebas Neue. Body **Inter** (proven in DGM, real tabular numerals). One Google Fonts request, `display=swap`, both `preconnect`s as in `layout()`:684.

**Dimension hook (`.dim`).** `font-family:var(--font-display);font-variation-settings:'wdth' 125,'wght' 800;font-size:clamp(3.4rem,11vw,9rem);line-height:.82;letter-spacing:-.02em`. Prime marks `′` as real characters; `×` as `&times;` with `0.12em` side margins in `--mint`. On a project page it sits over the hero bottom-left; on a card it is the largest thing in the card. `.dim-sub` under it: `CITY, ST · YEAR · CLIENT` in `.72rem/.22em` uppercase `--muted`.

**Project card.** Full-bleed image, 4:3, `object-fit:cover`; the card *is* the link; `.dim` overprinted bottom-left over a `linear-gradient(0deg,rgba(0,0,0,.72),transparent 55%)` shade; mint 1px rule grows across the bottom on hover/focus. Work index = CSS grid, `repeat(auto-fill,minmax(min(100%,420px),1fr))`, gap `clamp(1rem,2vw,1.6rem)`; the two Rochester civic murals get a `.span-2` row of their own.

**Project page.** Hero (full-bleed 2400w `<picture>`, `fetchpriority=high`) → `.dim` block + meta row → the scale figure strip → one-paragraph story (max 62ch) → gallery (masonry-ish grid, lightbox reuses DGM's `.lb`) → credit line → prev/next project → `cta()`.

**Nav/footer.** Nav: wordmark left (`OPEN AIR` / `GALLERY` stacked, `wdth 125`), links `Work · About · Services · Graffiti Removal · Contact`, mint pill CTA "Book a free consult". No dropdowns — drop DGM's `has-menu` branch in `nav_html()`:206-211. Footer: three columns (studio + IG `@openairmurals` + email, Work list of 12, Services) over a mint hairline.

**Breakpoints** mobile-first: base, `560px`, `860px`, `1180px`.

## 3. Pages and copy direction

Reuse the client's own true sentences (they are good) — quoted from the live About page:

> "When it comes to mural creations, it starts from a small image and explodes onto a massive canvas. It takes meticulous prep work… The ability to scale and project is what differs an artist and a muralist."
> "There is a science to paint and an understanding for the preservation of the environment. We analyze the way the paint will decay over time and how the light will affect it's color." (fix `it's` → `its`)
> "…we apply environmentally friendly coating that will make it easy to clean any future vandalism without damaging the art work."

**Home.** (1) Hero: full-bleed Gucci mural, H1 `MURALS AT BUILDING SCALE`, sub-line *"Open Air Gallery is Ephraim's studio. Eighty-one feet of Gucci on a New York wall; fifty-three feet of John Lewis in Rochester."* (2) Scale statement band: one `.dim` reading `81′ × 80′` with the scale figure beside it. (3) Featured projects — 6 cards. (4) Process — three steps from the quotes above (Prep · Paint analysis · Preservation). (5) **Rochester civic beat** — its own dark full-bleed diptych, John Lewis + Malcolm X, headline `TWO WALLS IN ROCHESTER`, copy on painting civil-rights portraits at 53′ × 50′ in his own city. (6) **Graffiti removal band** (§3b). (7) `cta()` "Book a free consultation".

**Work.** Index (12 cards, filter chips `All / Brand / Portrait / Civic` as real `<a href="?f=">`-free CSS `:target`-less buttons that only enhance) + 12 pages from one `project_page(p)` template.

**About.** Ephraim named and photographed; the studio "we are driven by our passion for mural creations…" paragraph; the team; the three-stage process at length; client logos as text marquee (DGM `.marquee` at build.py:719).

**Services (murals & banners).** Murals · Hand-painted banners and signs (the Wix "Signs" set: Heineken, Jack Daniels, Corona, Black Crow, Marion's, House of Pizza & Calzones) · Large-image/commercial painting. Each: what it is, where it goes, what you get, cost drivers. Ends with a link to Graffiti Removal and `cta()`.

**Graffiti Removal (own page).** Hero: the brick-wall mechanic (§4b) with H1 `TAKE THE WALL BACK`, eyebrow `COMMERCIAL GRAFFITI REMOVAL`, sub *"Industrial-strength removal, pressure washing and repaint — by the muralists who know what the surface is made of."* Then: **Who it's for** (property managers, brands and retail, cities/BIDs) → **Process** (Assessment: surface material and the right stripping technique · Removal · Anti-graffiti coating, environmentally friendly, future tags wipe off · Maintenance/callback) → the client's real 3-step booking ladder (Take a picture → Send it → 50% deposit holds the date) → before/after presentation → its own consult CTA. Copy adapted from the live `/graffiti-removal` text.

**Contact.** Consultation request form (name, company, role, email, phone, project location, service select incl. Graffiti removal, approximate size, budget band, message) + honeypot `<input name="_gotcha">` visually hidden. Formspree JSON POST with mailto fallback, ported from site/js/site.js:51-73. **Resolve with Ephraim:** the live site shows `hello@` in the home body and `info@` in the footer — confirm before launch.

### 3b. The graffiti-removal home band

Model: `gf_band()` (build.py:137-158) and `gf_strip()` (160-169); CSS model `.gf-strip` at site/css/site.css:375-380. New `gr_band()` in build.py. Placement: after the Rochester beat, before the final CTA — the one block on Home that is *not* a mural. Own colour treatment so it reads as a second business: `background:linear-gradient(100deg,var(--mint-glow),transparent 55%),var(--surface)` inside a 1px `--mint-deep` border, everything else on the page being bare dark. Left: the compact wall loop (§4b). Right: eyebrow `ALSO FROM OPEN AIR`, H2 `GRAFFITI REMOVAL`, one paragraph, a three-item list (Removal · Pressure washing · Anti-graffiti coating), `.btn-mint` → `/graffiti-removal` plus a ghost "Get a quote from a photo". A slim `gr_strip()` variant goes at the foot of Services and About.

## 4. Kinesthetics

**Named motion vocabulary: ROLL · SCALE · STRIP.**
- **roll** — content arrives as if rolled on: `clip-path:inset(0 100% 0 0)` → `inset(0)` left-to-right, 620 ms. Class `.rl` replaces DGM's `.rv`.
- **scale** — the human figure and the growing dimension figures.
- **strip** — the stroke that takes the tag off the brick.

### 4a. Scale figure (`data-scale`)

Server HTML is complete: a mural `<picture>` with the figure `<img class="sf" src="/assets/img/figure.svg" style="--x:6%">` already positioned at 6% from the left, sized by `--sf-h:calc(var(--px-per-ft) * 5.83)` (a 5′10″ person) computed in build.py from the project's `h_ft`, plus a real caption `"Drag the figure — she is 5′10″. The wall is 80 feet."`

- **Desktop** (`matchMedia('(hover:hover) and (pointer:fine)')`): pointerdown on `.sf` → `setPointerCapture`, pointermove writes `--x` (clamped 0-100%) via one rAF; the figure keeps a constant pixel height, so as she travels the mural's own scale never changes — the payoff is purely how small she stays. Arrow keys move her 2%/step (`tabindex="0"`, `role="slider"` omitted deliberately — no numbers). Release = inertial glide, 380 ms.
- **Mobile** (coarse pointer): touchdrag identical; *plus* an optional tilt mode — `DeviceOrientationEvent` (requesting permission only on an explicit tap of "Tilt to walk her across", never on load) leans her along `gamma` with an 0.12 low-pass filter.
- **No JS:** she renders at 6%, the caption is real text, nothing is hidden. **Reduced motion:** `html.motion` is absent, so no glide and no tilt — dragging still works (it is direct manipulation, not animation).
- **Contract:** everything hidden lives under `html.motion`; `.rl` carries `animation:oagSelf 0s linear 2.8s forwards` exactly like site.css:405.
- Sound: none here.

### 4b. The wall (`data-strip`) — Graffiti Removal signature

**Markup (server-rendered, real):** a `<figure class="wall">` containing *both* layers as real content — `<img class="wall-clean">` and `<img class="wall-tag">` — plus a caption. Default asset path: an **inline SVG brick wall** drawn in build.py (`brick_svg()`: a `<pattern>` of staggered bricks, mortar, a grain filter) with a drawn graffiti layer (three `<path>` tags, drips, a mint-free palette so the mint stays the brand's). Crisp at any size, zero licensing question. **Optional swap:** if `p['before']/p['after']` photos arrive, the same component takes two `<picture>`s instead — one CSS class, `.wall.is-photo`.

- **Desktop:** the cursor becomes a washer head (`cursor:none` + a follower element). Pointer drag paints into a small offscreen canvas (`256×144`, scaled by CSS) used as `mask-image` on `.wall-tag`, so the *clean* layer shows through the stroke. Soft wet edge = a radial-gradient brush stamped along the interpolated path; drips = three short downward stamps emitted per ~60 px of travel, fading over 1.2 s.
- **Completion:** a cheap coverage check (alpha-sum of the 256×144 buffer, sampled every 6th frame) — at ≥ 78 % the rest wipes itself (mask scales to full over 500 ms), then **sparkle**: one specular glint sweeps across (a skewed white gradient, 700 ms) and 8 particles (4 on coarse pointers) pop and fade. Then it rests clean. No counter, no percentage, no label.
- **Mobile:** finger strokes, identical; brush radius ×1.3; particle cap 4; optional tilt-rinse (same explicit-permission tap) letting a translucent water sheet run down and erase along `beta`.
- **Sound:** `<button class="snd" aria-pressed="false">` toggle, **muted by default**; spray hiss (looping, gain-ramped by stroke speed) and a squeak on the final clean, both via one `AudioContext` created on first user gesture only.
- **No JS:** the finished clean wall shows at full size with the tagged version beside it as a real "before" thumbnail — that *is* the before/after presentation the page needs. **Reduced motion:** `html.motion` absent → a 900 ms crossfade tagged → clean on scroll-in, no canvas, no particles, no sound.
- **Performance:** `will-change:mask-image` only while dragging; canvas is 256×144 regardless of display size; no element ever changes box size (the figure has a fixed `aspect-ratio`), so CLS = 0.
- **Home band version:** the same component with `data-strip="auto"` — no pointer handling; a `--scroll`-tied mask sweep driven by the shared rAF queue (site.js:93-97 pattern), or a 6 s CSS-only loop when reduced motion is off. It is a link to `/graffiti-removal`.

## 5. Images

`fetch-wix.py` (read-only against Wix, writes only into `assets/`):

1. `WIX_MAP` — a hand-written table `slug → rendered URL` harvested from the live Work/Home pages (filenames already name the projects: `Gucci%20Mural%20-%20Open%20Air%20Gallery…jpeg`, `Malcolm%20X%20Mural…`, etc.).
2. For each, rewrite only the transform segment: `re.sub(r'/v1/(fill|fit)/[^/]+/', '/v1/fit/w_3000,h_3000,q_90,enc_auto/', url)` — keep any `/v1/crop/x_,y_,w_,h_/` prefix intact (the Wix crop is the client's framing). Never construct a bare `/media/<id>` URL: it 403s.
3. Step down 3000 → 2400 → 1600 until 200 with `Content-Length > 60 KB`; send a browser UA and `Referer: https://www.openairgallery.art/`; sleep 0.5 s between.
4. Save `assets/<slug>.jpg`, plus `assets/_sources.json` recording the exact URL and byte size fetched, so the swap is auditable.

`process.sh` (from /root/dronegodmax-src/process.sh) makes four renditions per slug instead of two: `out/img/<slug>-2400.webp` q82, `-1600.webp` q82, `-800.webp` q78, `out/img/t/<slug>.webp` 640w q76. `img()` becomes `picture()` emitting `srcset="…-800.webp 800w, …-1600.webp 1600w, …-2400.webp 2400w"` with `sizes`. Favicons from a mint-on-black `OA` monogram SVG.

**Swap procedure when originals arrive:** drop the files in `assets/` under the same `<slug>.jpg` names (higher resolution, same framing), delete the matching rows from `_sources.json`, re-run `process.sh` then `deploy.sh`. Nothing in build.py or the HTML changes. One commit: *"Photos: Ephraim's originals replace the Wix renditions."*

## 6. Build steps — one commit each, verified before the next

Standing verification for every step (an Opus agent runs all of it):
`python3 build.py` exits 0 → `python3 -m http.server 8099 -d site` → `node /root/shot/shot.mjs http://127.0.0.1:8099/<page> <out-prefix> 0,1200,2400` for **1440×900** and a second run with `devices["iPhone 14 Pro"]` (390) → the script already collects `pageerror`/`console.error`, which must be `[]` → `curl -s http://127.0.0.1:8099/<page> | python3 -c "import sys,html,re;…"` to confirm the headline, `.dim` figures and body copy are present in the *server* HTML → a JS-disabled pass (`chromium.launch()` context with `javaScriptEnabled:false`) screenshot showing a complete page → `python3 -c "import html.parser"`-based well-formedness spot-check or `curl … | grep -c '</html>'`.

| # | Step | Files touched | Reuse | Extra verification |
|---|---|---|---|---|
| 1 | Scaffold | build.py, projects.py, .gitignore | DGM build.py 1-14, 1370-1394; .gitignore verbatim | build writes `site/index.html` |
| 2 | Tokens + base CSS | site/css/site.css | site.css:1-36 | contrast script asserts mint/bg ≥ 7 |
| 3 | layout/nav/footer | build.py, site/js/site.js | `layout()` 673-707, `nav_html()` 200-224, `footer_html()` 226-256, nav JS site.js:6-14 | every page has skip link, `html.motion` bootstrap |
| 4 | Home (no band, no mechanic) | build.py, site.css | `page_hero()` 636-646, `cta()` 630-634, `.marquee` | Rochester beat present in server HTML |
| 5 | Work index + `project_page()` ×12 | build.py, projects.py | `swipe()` 613-628 for galleries | 13 files written; all `.dim` figures match projects.py |
| 6 | About | build.py | — | the three quoted paragraphs present verbatim |
| 7 | Services | build.py | — | |
| 8 | **Graffiti Removal page** | build.py, site.css | `gf_band()` markup shape | six pages in nav + sitemap |
| 9 | **Home graffiti band `gr_band()` + `gr_strip()`** | build.py, site.css | `gf_band()` 137-158 / `gf_strip()` 160-169; `.gf-strip` CSS 375-380 | band links to `/graffiti-removal`; band renders with JS off |
| 10 | Contact + Formspree | build.py, site.js | site.js:51-73; `FORM_ENDPOINT` env pattern build.py:86 | honeypot present; a real submit reaches the new form id |
| 11 | **Scale mechanic** | site.js, site.css, build.py | reveal/rAF queue site.js:93-107 | playwright drag (`shot.mjs --drag` pattern) moves `--x`; reduced-motion pass; JS-off pass |
| 12 | **Wall mechanic** (`data-strip`) | site.js, site.css, build.py (`brick_svg()`) | motion-contract scoping site.css:392-418 | drag over the wall → screenshots at 3 stroke stages + rest-clean; coverage completion fires; sound off by default (`aria-pressed="false"`); reduced-motion = crossfade only; CLS 0 via `getBoundingClientRect` before/after |
| 13 | Images pipeline | fetch-wix.py, process.sh, build.py `picture()` | process.sh | every project has 3 renditions; no `<img>` without width/height |
| 14 | SEO | build.py | `layout()` meta/OG block 680-690, sitemap 1386-1394 | JSON-LD: `LocalBusiness` (Home, `founder` = Ephraim), `CreativeWork`+`size` per project page, **`Service` for graffiti removal** (`serviceType`, `areaServed` NYC/Rochester), `BreadcrumbList`; validate each with `json.loads` |
| 15 | Preview publish | publish-preview.sh | publisher.py:88-105 | live URL loads over HTTPS, `X-Robots-Tag: noindex` present |
| 16 | Owner review | CLAUDE.md | — | corrections appended to CLAUDE.md |
| 17 | Subdomain go-live | deploy.sh, deploy/nginx/ | deploy.sh, `/etc/nginx/sites-enabled/rob.greenflashusa.com` | §7 |

## 7. Deploy

**Preview.** `publish-preview.sh` mirrors `/srv/sitebuilder/bot/sitebuilder/publisher.py:88-105` without the bot: build with `BASE_URL=https://preview.greenflashusa.com/p/$SLUG`; slug read from `.preview-slug` (create once with `python3 -c "import secrets;print(secrets.token_urlsafe(16))"` — 22 chars, then never changes); `rsync` `site/` + `out/img` into `/srv/sitebuilder/p/.staging-$SLUG/`; write `robots.txt` = `User-agent: *\nDisallow: /`; `chmod` dirs 0755, files 0644; `mv` target → `.retiring-$SLUG`, `mv` staging → target, `rm -rf` retiring. The existing vhost `/etc/nginx/sites-enabled/preview.greenflashusa.com` already serves `/p/` with `try_files $uri $uri.html $uri/index.html` and `snippets/preview-headers.conf`. **Note:** site-root-absolute URLs (`/assets/…`) break under `/p/<slug>/`; build with a `BASE_PATH` prefix env var applied in `img()`, `nav_html()` and `footer_html()`, defaulting to `''`.

**Subdomain go-live (`openair.greenflashusa.com`).**
1. `gd-dns add openair --ip 142.93.198.162` (`/usr/local/bin/gd-dns`), confirm with `gd-dns list --type A --name openair`.
2. `mkdir -p /var/www/openair && chown www-data:www-data /var/www/openair`.
3. `certbot certonly --nginx -d openair.greenflashusa.com`.
4. Vhost `/etc/nginx/sites-available/openair.greenflashusa.com` modelled on `/etc/nginx/sites-enabled/rob.greenflashusa.com`, `include /etc/nginx/snippets/openairgallery-site.conf;` — the new snippet copies `/etc/nginx/snippets/dronegodmax-site.conf` minus every WordPress/Instagram block, keeping: security headers, gzip, `error_page 404 /404.html`, `location ~ /\. { deny all; }`, the trailing-slash and `.html`-stripping redirects, `try_files $uri $uri.html $uri/ =404`, immutable `/assets/`, 1-day css/js. Repo copy at `deploy/nginx/`.
5. `deploy.sh` (from `/root/dronegodmax-src/deploy.sh`): `BASE_URL="${BASE_URL:-https://openair.greenflashusa.com}" python3 build.py`; `rsync -a --delete --exclude 'assets/' site/ /var/www/openair/`; `rsync -a out/img/ /var/www/openair/assets/img/`; `chown -R www-data:www-data /var/www/openair`; `nginx -t && systemctl reload nginx`.
6. **Do not touch Wix or openairgallery.art.** The later switch is its own step, weeks out: Ephraim adds an A record → 142.93.198.162 and a `www` CNAME in the Wix DNS panel, then `certbot certonly --nginx -d openairgallery.art -d www.openairgallery.art`, `server_name` gains both names, redeploy with `BASE_URL=https://openairgallery.art`, and `openair.greenflashusa.com` becomes a 301 to it exactly like `/etc/nginx/sites-enabled/max`.

## 8. Whole-site verification

`curl -I https://openair.greenflashusa.com/` shows `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`; `curl -I …/assets/img/gucci-1600.webp` shows `immutable`; `curl -s …/sitemap.xml` lists 18 URLs (6 + 12 projects) and no 404; `curl …/robots.txt` points at the sitemap; every page fetched with `curl` contains its H1 and body copy as text; both viewports screenshotted for all 18 pages; JS-off pass on Home, one project page and Graffiti Removal; reduced-motion pass on the same three; `console.error` empty everywhere; `python3 -c` link-checker walks every internal `href` against `site/`; contrast assertions in the build (fail the build if `--mint` on `--bg` drops below 7:1 — the DGM `assert` pattern at build.py:129-132).

## 9. Risks

1. **Photo quality.** The Wix renditions are re-compressed JPEGs; at 2400 wide, upscaled fills will soften. Mitigation: the step-down loop in `fetch-wix.py`, cap hero at the largest rendition that stays sharp, and hold the whole thing as provisional until Ephraim's originals land (swap is one commit).
2. **Wix image terms.** These are Ephraim's own photographs on his own hosting — he owns them — but the site must not hotlink Wix in production; every image is fetched once, re-encoded, and served from `/assets`. Record the provenance in `assets/_sources.json` and get his written OK in CLAUDE.md before go-live.
3. **Mechanic performance on mobile.** Canvas masking can stutter on older phones. Mitigations: 256×144 buffer, one shared rAF, particle caps (4 on coarse pointers), `will-change` only during a stroke, and a hard fallback — if `navigator.hardwareConcurrency <= 4` or the first 20 frames average under 40 fps, drop to the crossfade path.
4. **Fonts.** Archivo's variable font is ~90 KB; a blocking stylesheet delays LCP. Use `display=swap`, both preconnects, `font-variation-settings` fallbacks on a system grotesque so the `.dim` figures do not reflow catastrophically. If FOUT is ugly at 9rem, self-host the two axes as a subset woff2 in `/assets/fonts`.
5. **Mint contrast.** Verified 13.8:1 on #0A0A0B — AAA. The failure mode is mint *on mint-glow* panels or mint text over a bright mural; enforce `--text` on imagery and reserve mint for rules, eyebrows, buttons and the `×`.
6. **Email ambiguity** (`hello@` vs `info@`) and the three undimensioned projects — both must be settled with Ephraim before step 14.

### Critical Files for Implementation
- /root/openairgallery-src/CLAUDE.md
- /root/dronegodmax-src/build.py
- /root/dronegodmax-src/site/css/site.css
- /root/dronegodmax-src/site/js/site.js
- /root/dronegodmax-src/deploy.sh (with /root/dronegodmax-src/process.sh and /etc/nginx/snippets/dronegodmax-site.conf)