# Mendoza Marketing — mendozamarketing.com (Drew, Grand Island NY)

The house rules for this repo. Read this before designing or building anything
here: the palette, the prices and the rules below are the reference, and the
reference is the spec, not inspiration.

Plan: `/root/.claude/plans/i-want-to-think-adaptive-spindle.md`.
Modelled on `/root/dronegodmax-src` (the generator, the footer) and
`/root/openairgallery-src` (the PREFIX threading, the preview publisher, this
file). Neither of those repos is ever edited from here.

---

## Context — the brief, as it was given

The owner: *"We need a new website for our friend Drew … take a look at the
readme for business name as well as a few sites he wants you to use as
inspiration, also reach to DroneGodMax.com for inspiration from our currently
built projects."*

**Drew's README (relayed by the owner) in full:** **Mendoza Marketing**
("Content · Websites · Drones"), logo uploaded (a no-background PNG and a vector
file follow in a day or two); current site netoriouslabs.com ("basic, never
fleshed out; the Lead Conversion and Drones pages are blank; the drone page
should be similar to Max's; lead conversion is closing Meta-ad-generated
leads"); sites he wants to mirror: midnightmarketing.com,
digitalgrowthcatalyze.com, **ellesmereui.com ("uses my color theme and I really
like how it looks")**; his hex colours — main green `#2de8b5`, black `#050A0A`,
dark grey `#1A1F1F`, lighter grey `#2E3535`, white `#f0ffff`, accent green
`#7FF2D1`; **pricing** — web design from $1,250, website re-design $600, Meta ad
setup & filming $750, social media packages Emerald $500 / Sapphire $1,000 /
Diamond $2,000, logo design $500, lead conversion TBD (commission or hourly),
drone session $1,000; product descriptions are on the current site; per-service
marks = the Mendoza logo with the text changed; **a footer similar to Max's; a
quote form; a results section using the dashboards; "dynamic / professional
enough to give clients the desire to want a site similar to mine"; pretty
flexible.**

**Owner decisions:** the site lives at **mendozamarketing.com** (Drew's own domain,
live since 2026-09-23; `drew.greenflashusa.com`, `www.*` and `mendozamarketing.net`
redirect to it); scope is the
marketing site (Home, the services, Results, Work, About Drew, Contact/quote)
**with the prices on it**.

### The prices, as `content.py` holds them

| key | package | price |
|---|---|---|
| `web-design` | Website design | from **$1,250** |
| `web-redesign` | Website re-design | **$600** |
| `meta-ads` | Meta ad setup & filming | **$750** |
| `social-emerald` | Social media — Emerald | **$500** |
| `social-sapphire` | Social media — Sapphire | **$1,000** |
| `social-diamond` | Social media — Diamond | **$2,000** |
| `logo` | Logo design | **$500** |
| `lead-conversion` | Lead conversion | **Commission or hourly, priced to the need** |
| `drone-session` | Drone session | **$1,000** |

**Three of these disagree with netoriouslabs.com today** and the README is what
we built to — ask Drew before launch: the README says re-design **$600** (his
site says $500) and logo **$500** (his site says $750), and the README's Meta
line is $750 for *setup and filming* where his site prices *management* at $500
plus the client's daily ad budget. If the current site is right, change
`PRICING` in `content.py` and nothing else: no page holds a figure of its own.

---

## The rules

0. **Type is a refined grey, not white.** `--ink` is `#DDE4E1`, a cool grey a
   shade off his green, and every word on the site is set in it or in
   `--muted`/`--green`. The README's `#f0ffff` is *not* used for type — the
   owner (2026-09-23): "Use a refined grey instead of pure white for the text
   on the site, boutique premium readability." The only white left is the
   MENDOZA lettering inside his own logo files. 15.4:1 on the canvas, 12.9:1
   on a panel — still AAA, so nothing else had to change.
1. **One accent.** `#2de8b5` is the only colour on the page that is not black,
   grey or white — links, rules, icons, eyebrows, the primary button. `#7FF2D1`
   is *hover and glow only*, never a second accent. A page with two loud
   colours on it is wrong. The service cards on Home are *green-led* (the
   owner, 2026-09-23: "make services text/elements green, keep visual
   hierarchy strong"): name, price, icon and hairlines in the accent
   (`--green-line`, the green at 35%, for the borders), the description in
   `--muted`. Name > price > description is the order; do not green the body.
   Feature boxes — the Included trio on every service page, the Design ·
   Launch · Grow beats on Home and About — each carry one small icon
   (`art.feature(heading)`, a 24px drawing in a 40px well, `.f-ico`): the
   owner, 2026-09-23, "premium icons, minimal and consistent". Keyed by the
   heading, so a renamed heading needs its drawing renamed in `art.FEATURES`
   or the build stops. One object per icon, no decoration, no second style.
2. **Two-tone headlines.** Line one `--ink`, line two `--green` — the Ellesmere
   move Drew picked out. `.h-two` on the heading, a `<span>` around the second
   line. `page_hero()` passes its title through as markup so it can do this.
3. **Three faces, one job each.** Space Grotesk 700 display, Inter 400/600
   body, JetBrains Mono 400/600 labels, prices and dashboard figures. Not
   Bebas: this site must not read as a DroneGodMax clone.
4. **The motion contract.** Everything hidden for effect is hidden under
   `html.motion` only, and carries the 2.8s self-reveal bail-out. No-JS and
   `prefers-reduced-motion` must render the page **complete** and identical to
   each other. No counters, scores, XP or checklists — the only numbers that
   move are Drew's own dashboard figures. The site never starts sound: the three Kelly's
   reels play muted, and a visitor can turn one reel's sound on with a tap (a "Sound on"
   chip shows it, one reel at a time, off again when it leaves view). Nothing else makes a
   sound.

   **The six service cards run off scroll, and they keep going.** The owner,
   2026-09-25: *"they should trigger off scroll and keep going after they are
   triggered, tapping should be reserved for learn more."* A card's demo starts
   when the card is 35% on screen, runs three seconds, holds the state it ended
   on for 1.2s and runs again, for as long as the card is in view; it pauses
   when the card leaves and starts a fresh cycle on the way back. **No hover,
   tap or focus handler goes anywhere near a card** — the card is a plain link
   and one tap is Learn more, always. The first-tap-plays behaviour that used
   to stand in for hover on a phone is gone: whether a tap opened the page
   depended on invisible state, which is what the owner hit as *"sometimes you
   click and it doesn't pop up it just goes to the page."*

   **The well already holds what the demo ends on.** `home.py`'s `_well(slug)`
   draws each card's finished state into the server HTML — the drawn
   wireframe, the landed Views figure, a full-bleed reel poster, the caption,
   the quad on its horizon, the drawn leads line and its figure — so no-JS and
   reduced motion get a finished box, not an empty one. `site.js` never builds
   or removes that content: `arm()` sets the state a run starts from,
   `frame(t)` is the run written as arithmetic (inline styles, no committed
   transitions, so a cycle can begin on any frame), `rest()` strips those
   inline styles and lands the well back on exactly what the server sent.
   **Nothing an end state leaves on screen may be removed or faded out at the
   end of a run** — the owner, of the old sweep: *"Meta business suite number
   disappears after popping up."* The counter counts up, holds its figure, and
   restarts from zero on the next cycle; it is a number at every moment.
   One well style for all six: 120px (106 on a phone), one radius, one
   `--green-line` hairline, never dashed. Verified by
   `/root/shot/drew-demos.mjs`.
5. **PREFIX.** Every root-absolute link goes through `u()`, every image through
   `img()`/`pic()`. `PREFIX=/p/test python3 build.py` must be as correct as a
   plain build — that is what makes the preview work.
6. **Prices live in `content.py`.** `price_card()` takes a *key* and reads the
   row; it cannot be handed a figure. Never type a price into a page body.
7. **Drew's words are Drew's.** Copy comes from his own pages
   (`incoming/refs/netorious-pages.txt`) or from him. Where we have none —
   Drones, Lead conversion — new copy is written in his register and **flagged
   for him to approve** before it goes live. Nothing is invented and presented
   as his.
8. **Never let our data file describe his career.** The client logos, films and
   dashboards in `out/` are what we happen to hold, not the size of Drew's
   business. No "six clients", no "twelve reels" — phrase it open-ended.
9. **Contrast is computed, not eyeballed.** Every text/background pair is in the
   comment block at the top of `site/css/site.css` with its ratio. Add a pair,
   add the number.
10. **Assets are soft until the media lands.** A missing rendition warns and is
    listed at the end of the build; it never fails it. Once the pipeline is
    done, the warning list should be empty — a warning that has become
    permanent is a bug.

---

## The files

```
build.py                 the generator: u(), img()/pic(), nav_html(),
                         footer_html(), page_hero(), cta(), swipe(),
                         price_card(), layout(), the pages dict, the write
                         loop, sitemap.xml + robots.txt
content.py               SITE, SERVICES (six), PRICING (nine rows), TODO
site/css/site.css        the tokens, the contrast table, type, buttons, the
                         glass nav, the footer, the reveal contract
site/js/site.js          the base layer only: nav, active link, reveal
                         observer, lightbox shell
process.sh               logos, client logos, photos → webp sets  (media builder)
make-clips.sh            the hero film, the drone rail, Kelly's reels (media builder)
tools/make-og.py         the mark cut out of assets/logo.png → the favicon set
                         and the 1200x630 share cards, into out/img/
tools/make-lockup.py     the nav lockup (mark, MENDOZA over MARKETING) cut
                         out of assets/logo.png → out/img/lockup.webp
assets/                  the originals Drew sent            (gitignored)
out/img, out/video       the renditions the pipeline makes  (gitignored)
site/assets/             symlinks into out/ so `python3 -m http.server -d site`
                         serves a complete site locally     (gitignored)
publish-preview.sh       build under /p/<slug> and swap it into
                         /srv/sitebuilder/p/ — noindex, fixed slug
deploy.sh                build and rsync to /var/www/drew   (live)
deploy/nginx/drew-site.conf   the server body, installed as
                         /etc/nginx/snippets/drew-site.conf and included by
                         /etc/nginx/sites-available/mendozamarketing.com
incoming/                everything he sent, as it arrived  (gitignored)
```

Build and look at it:

```bash
python3 build.py                                  # the domain root
PREFIX=/p/test python3 build.py                   # under a preview prefix
python3 -m http.server 8079 -d site               # serve it
node /root/shot/shot-drew.mjs http://127.0.0.1:8079/index.html /tmp/x --nav
```

Preview slug (fixed, in `publish-preview.sh`): `FpneVVmTCTqRO_sI7peZHg` →
`https://preview.greenflashusa.com/p/FpneVVmTCTqRO_sI7peZHg/`. Published; it
stays the place to show Drew a change before `deploy.sh` puts it live.

Git: branch `main`, remote `gf`
(`git@github.com:GalacticConquestRulez/Green-Flash-.git`), pushed to
**`drew-main`** there — the same remote Open Air Gallery uses with its own
branch names. One idea per commit.

---

## SEO

Every page carries the same head, built in `layout()`: a `<title>` from
`seo_title()` (the brand, an em dash, what the page is — asserted at 60
characters, which is what a search result prints), a `description` asserted at
155, a canonical, `og:type/site_name/title/description/url/image` with the
card's real pixel size, `twitter:card summary_large_image`, `theme-color`
`#050A0A`, and the four icons. Absolute URLs — canonical, `og:url`,
`og:image`, every `@id` in the graph — are built from `BASE_URL` plus a bare
path and **never** through `u()`: on the preview `BASE_URL` already ends in
`/p/<slug>`, so prefixing twice makes every share card 404.

| page | carries, beyond the head |
|---|---|
| `/` | `LocalBusiness` |
| the six services | `LocalBusiness` + `Service` with an `Offer` per package the page prints, priced from `PRICING`; `og-<slug>.png` |
| `/pricing` | `LocalBusiness` + `OfferCatalog`, all nine rows |
| `/work`, `/results` | `LocalBusiness` |
| `/about` | `LocalBusiness` + `Person` (Drew) |
| `/contact` | `LocalBusiness` + `ContactPage` |
| `/404` | noindex, no graph, not in the sitemap |

Descriptions for the six service pages live in `content.SEO` beside the copy
they were shortened from — they are Drew's own opening sentences, fewer words.
The rest are written where their page is defined. Prices in the graph come from
`PRICING` like everything else (rule 6); lead conversion is an `Offer` with his
sentence and **no price**, because commission-or-hourly is not a number.

`tools/make-og.py` makes the icons and the cards out of `assets/logo.png` —
the mark measured out of the top two thirds by its alpha channel.
Run it once after a fresh clone, or the build warns (rule 10) and the tabs have
no icon. It fetches Space Grotesk and Inter from google/fonts into
`assets/fonts/` with their SIL OFL text.

`sitemap.xml` lists every public page with `lastmod` = the build date.
`robots.txt` is `Allow: /` with the sitemap line at the domain root, and
`Disallow: /` under `PREFIX` — belt and braces, since `publish-preview.sh`
already overwrites robots and deletes the sitemap in its staging copy *after*
the rsync.

**Live since 2026-09-23 at `https://mendozamarketing.com`.** DNS is in Drew's own
GoDaddy account (token at `/root/.config/godaddy-drew.env`, root-only, never
copied here — see the memory `drew-godaddy-account.md`): apex A/AAAA on
mendozamarketing.com and .net, www as CNAME. Certificate: one Let's Encrypt
cert covering the five names, renewed by certbot's timer. The server block
redirects every other name (www, .net, drew.greenflashusa.com) to the apex.

1. `BASE_URL` — `deploy.sh` exports `https://mendozamarketing.com`, and every canonical, `og:url`, `@id` and sitemap
   entry follows it. It also rsyncs `out/img/` to `/var/www/drew/assets/img/`,
   which is how the icons and the share cards get to the server; nothing extra
   to do, but if a card 404s in a link preview, that rsync is where to look.
2. The canonicals then point at the live domain rather than the preview, which
   is the moment the site becomes indexable. Check `robots.txt` on the server
   reads `Allow: /` and that `/sitemap.xml` is there.
3. `sameAs` in the `LocalBusiness` block is `[url for ... in SITE['socials']
   if url]` — an empty list today. The day Drew sends his Instagram and
   Facebook URLs, filling them in `content.SITE['socials']` links his profiles
   to his business in the graph and lights up the footer icons at the same
   time. Nothing else needs touching.

The business `image`/`logo` in the graph is `og.png`, the card cut from his
transparent PNG. When the vector lands, re-run `tools/make-og.py` and
`tools/make-lockup.py` and everything improves without a code change. There is no street
address, no opening hours and no rating in the graph, because the site
publishes none of them.

---

## Still owed by Drew

- **The vector file.** The transparent PNG arrived 2026-09-23 and is
  `assets/logo.png`; the nav, footer, icons and share cards are all cut from
  it (`tools/make-lockup.py`, `tools/make-og.py`). The vector is still owed
  and is what the per-service marks need (below).
- **The header lockup is settled.** Drew asked for "the words Mendoza with
  Marketing underneath next to the logo", sized like the Decision Frameworks
  header he sent (mark left, two stacked lines as tall as the mark).
  `out/img/lockup.webp` is exactly that, cut from his own artwork — his
  lettering, tracking and colours, rearranged, nothing set in a font. The
  footer keeps his stacked lockup. Do not rebuild either in Space Grotesk.
- **The social-media tier contents.** Emerald $500 / Sapphire $1,000 / Diamond
  $2,000 are priced, but what is *in* each tier is not written down anywhere we
  hold. `/social` and `/pricing` cannot be finished without it.
- **Copy approval for Drones and Lead conversion.** Both pages are blank on his
  current site. Whatever we write for them is new, is in his register, and goes
  to him before launch.
- **The Formspree endpoint id** for the quote form. Until it is set the form
  falls back to the visitor's own mail app, which works but is not what he
  wants.
- **Email, phone and the two social accounts.** `content.py` carries the ones
  published on netoriouslabs.com today (drew@netoriouslabs.com,
  716-860-5991) — the email still names the old brand, so confirm whether a
  mendozamarketing.* address replaces it. Instagram and Facebook URLs we do not
  have at all; the footer draws their icons unlinked until we do.
- **Kelly's Country Store and Gator Jon's BBQ logos.** Both are clients linked
  from his current site and neither sent a logo file, so neither can appear in
  the /work logo strip yet.
- **The three price disagreements** listed under Context.
- **The vector, again — the per-service marks depend on it.** His README asks
  for "the Mendoza logo with the text changed" on each service page. What we
  hold is a 2000×2000 JPEG with CONTENT | WEBSITES | DRONES baked into the
  pixels, so swapping that line means setting it in his typeface at his
  tracking and compositing it into his mark — which needs the vector (or the
  transparent PNG **and** the name of the face). Until then
  `art.service_mark(slug)` renders his logo with the service named under it in
  the site's own mono: the same information, plainly set, rather than a
  forgery of his artwork in the wrong typeface. When the vector arrives, that
  one function changes and no page that calls it does.
- **Two sentences that promise something on his behalf.** Home's twin cards say
  "A quote comes back within a business day" and "Twenty minutes, no pitch
  deck". Both came from the mockup the owner approved, and both are commitments
  only Drew can make — confirm or reword before launch. `/contact` repeats both
  on purpose rather than inventing a third: the hero's lede is the first
  sentence, the "Book a call" card is the second, and form.js says "Sent — Drew
  will reply within a business day" when a send succeeds. One decision from him
  changes all four; they are in `contact.py` (`contact_page`, `sidebar`) and
  `site/js/form.js`.
- **A booking link.** There is none, so every "book a call" on the site is a
  stand-in: Home's card goes to `/contact`, and the button on `/contact` opens
  a `mailto:` to Drew with the subject already written ("Booking a call —
  Mendoza Marketing", `contact.sidebar()`). A Calendly or equivalent URL makes
  both real buttons and nothing else changes.
- **The Home one-liners for Drones and Lead conversion** (`HOME_LINES` in
  `home.py`) are new copy in his register, because those two pages are blank
  on his current site. Flagged here as well as in `content.py`'s TODO: the
  moment `SERVICES[*]['one_line']` is filled with his own sentence, his wins
  automatically and the fallback stops being used.
- **The daily-leads numbers, if he has them.** `results.LEADS['series']` was
  read back off the pixels of his chart screenshot (dash-6) — accurate to
  about one lead a day, with his real peaks and his real floor. A table, a CSV
  or a fresh export from the Leads Center would replace it exactly; nothing
  else on the page would change.

## His name is Drew Pitts

The business is Mendoza Marketing; the man is **Drew Pitts**, not Drew Mendoza. The first
build assumed the surname from the brand and the owner corrected it on 2026-09-25. Every
`Person` record, alt text, heading and page title uses "Drew Pitts".
