# Mendoza Marketing — drew.greenflashusa.com (Drew, Grand Island NY)

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

**Owner decisions:** the site lives at **drew.greenflashusa.com**; scope is the
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

1. **One accent.** `#2de8b5` is the only colour on the page that is not black,
   grey or white — links, rules, icons, eyebrows, the primary button. `#7FF2D1`
   is *hover and glow only*, never a second accent. A page with two loud
   colours on it is wrong.
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
   move are Drew's own dashboard figures. No sound.
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
assets/                  the originals Drew sent            (gitignored)
out/img, out/video       the renditions the pipeline makes  (gitignored)
site/assets/             symlinks into out/ so `python3 -m http.server -d site`
                         serves a complete site locally     (gitignored)
publish-preview.sh       build under /p/<slug> and swap it into
                         /srv/sitebuilder/p/ — noindex, fixed slug
deploy.sh                build and rsync to /var/www/drew   (NOT run yet)
deploy/nginx/drew-site.conf   the server body                (NOT installed yet)
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
`https://preview.greenflashusa.com/p/FpneVVmTCTqRO_sI7peZHg/`. Not published
yet.

Git: branch `main`, remote `gf`
(`git@github.com:GalacticConquestRulez/Green-Flash-.git`), pushed to
**`drew-main`** there — the same remote Open Air Gallery uses with its own
branch names. One idea per commit.

---

## Still owed by Drew

- **The transparent logo (PNG) and the vector file.** He said a day or two. The
  build uses the JPG on black (`out/img/logo.webp`), so the swap is by filename
  and nothing in the markup changes.
- **A horizontal lockup, or permission to crop the mark out of the square
  one.** What he sent is a square stacked lockup — mark, MENDOZA MARKETING,
  CONTENT | WEBSITES | DRONES. In a 72px nav bar at 58px tall the two lines of
  small caps are not readable. It works; a wide lockup would work better.
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
