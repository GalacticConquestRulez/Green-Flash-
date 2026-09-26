# Ephraim's drop, 2026-09-25 — the films

The owner put fifteen video files loose in the repo root and asked for them on the site.
They are in `assets/source/drop-2026-09-25/` now, under slug names (gitignored, like the
drop before them; `make-drop-films.sh` and `make-drop-stills.sh` are the record of what
comes out of them).

**Seven of them arrived twice.** The `copy_*.MOV` files are the better copy of seven of
the other eight — same film, same duration to the frame, and in four cases a much bigger
picture. The copy is the one every rendition is built from; the lesser one is kept beside
it as `*-lesser.*` and is used for nothing.

| Source (slug name) | What it is | Picture | Duration | The lesser copy |
|---|---|---|---|---|
| `asap-rocky-ray-ban.mov` | A$AP Rocky × Ray-Ban, New York: the wall from the block, the painter at the face, the aerial | 3840×2160 H.264 24 | 46.08 s | `…-lesser.mov`, identical size |
| `moncler.mov` | Moncler, New York: paint mixed, the eye painted, the drone pulling away from the finished wall | 3840×2160 H.264 23.976 | 39.53 s | `…-lesser.mp4`, identical size |
| `fords-gin.mov` | Fords Gin, New York — **shot portrait** | 2160×3840 H.264 30 | 33.37 s | `…-lesser.mov`, identical size |
| `louboutin-shun-sudo.mov` | Christian Louboutin × Shun Sudo, New York — **shot portrait** | 2160×3840 HEVC 24 | 19.47 s | `…-lesser.mp4` is only 1080×1920 |
| `open-air-gallery-film.mov` | **The studio film.** Four minutes on Open Air Gallery: Gucci, Moncler, Louboutin, paint being mixed, a base coat tagged over, Ephraim at the wall, the Rochester portraits going up | 3840×2160 HEVC 30 | 245.60 s | `…-lesser.mp4` is only 1920×1080 |
| `capabilities.mp4` | **The capabilities showreel.** Flower City title card, New York walls, the lifts, the crowd on the High Line, ending on "How high will you go?" | 3840×2160 H.264 24 | 65.63 s | none — this one came once |
| `reel-block-therapy.mov` | A phone screen recording of his **Block Therapy** reel — the Upendo wall, Los Angeles | 2244×2160 HEVC, VFR flagged 60 | 29.98 s | `…-lesser.mov` is only 888×854 |
| `reel-keep-it-oscar.mov` | A phone screen recording of the Oscar Mayer **Keep it Oscar** reel | 2160×2358 HEVC, VFR flagged 120 | 61.44 s | `…-lesser.mov` is only 886×968 |

Two of the identities in the brief were wrong and the films corrected them, which is why
every one of them was read frame by frame before anything was built:

- The brief called the first reel "BLOCK THERAPY" and left it at that. Its title card
  reads **UPENDO**, then **"BLOCK THERAPY"**, and the street sign in the second shot reads
  **Sunset Bl** — so it is the **Upendo wall in Los Angeles**, which is already on the
  roster (`upendo-los-angeles`). It is in the feed strip as a reel; it is not a second
  Upendo project.
- The second reel was to be named "from what the title card says". It says **Keep it
  Oscar / Oscar Mayer** — "Oscar Mayer invited local artists in NY, Chicago, and LA to top
  hot dog murals their city's way" — with **Mike Perry (NYC)**, **JC Rivera (Chicago)** and
  **Jiaqi (LA)** named on screen. So the slug is `reel-keep-it-oscar`, not `reel-food-wall`.

## What each one became

| Where | Film | Files |
|---|---|---|
| **Home**, first thing under the hero | the capabilities showreel, whole, muted, looping, with a button that turns the sound on and starts it from the front | `film-capabilities.{mp4,webp}` + `-1080.mp4` |
| **Home** (before the graffiti band) and **About** (before the graffiti strip) | the studio film, whole, with its sound, behind a play button — "The film" | `film-open-air-gallery.{mp4,webp}` + `-1080.mp4` |
| `/work/moncler-new-york` | hero (muted loop) and the play button under it — the same file | `film-moncler.*` |
| `/work/asap-rocky-ray-ban-new-york` | the same | `film-asap-rocky-ray-ban.*` |
| `/work/fords-gin-new-york` | the same, **in a portrait frame** | `film-fords-gin.*` |
| `/work/louboutin-shun-sudo-new-york` | the same, **in a portrait frame** | `film-louboutin-shun-sudo.*` |
| **Work**, under the grid | "Straight off the phone" — the two reels, in phone frames, muted, tap for sound | `reel-block-therapy-1080.mp4`, `reel-keep-it-oscar-1080.mp4` |

The four project pages get their gallery from the films as well: twenty 4K frames pulled
by `make-drop-stills.sh` into `assets/`, because **no photographs of these four walls have
ever reached us**. That is exactly what was done for Flower City Arts Center in the drop
before this one.

## The rule this drop was built on: nothing is cut

The drop of 2026-09-20 built each page hero out of three beats trimmed out of a longer
film (`make-rains-clip.sh` and friends). **Nothing here is trimmed.** A film on this site
is now played whole or not at all: the muted loop behind the words is the entire film, and
the button beside it is that same film with its sound.

That has three consequences worth writing down:

1. **The Home hero is untouched.** CLAUDE.md records the Johnnie Walker clip as the
   owner's own choice — he uploaded that footage and asked for it as "the motion
   background at the top" (2026-09-19). So the showreel did not replace it; it is the
   first thing under it, which is what the brief asked for in that case.
2. **One encode per film, not two.** `make-films.sh`, from the last drop, keeps a silent
   crf-23 cut for the loop and a straight remux of the delivered master for the play
   button, at the bitrate it was delivered in — which is why `film-rains.mp4` is 317 MB.
   That was free there, because those sources were already H.264. Four of these are HEVC
   and have to be re-encoded whatever we do, and the four that are not are 50–77 Mbit
   camera masters: handing a visitor 380 MB for a thirty-nine second wall is not a
   feature. So each film is encoded once, at its own size and its own frame rate, with its
   sound kept, and that one file is both the loop and the film the button unmutes. Native
   resolution and frame rate are untouched, the phone gets the lighter copy and nobody
   else does, and the whole film is there. The delivered masters stay in
   `assets/source/drop-2026-09-25/`.
3. **A portrait film is shown portrait.** Two of these walls were filmed standing up, and
   a 2160×3840 film in a full-bleed hero is nine tenths cropped away. `portrait_hero()`
   gives it the film's own shape in a column beside the words, and `film_band()` gives the
   band `--film-ar` so the frame is always the film's own rectangle — never stretched,
   never cropped to fit one.

## The renditions, and what they weigh

`./make-drop-films.sh` writes, for every film: the master at the camera's own size and
rate (H.264, crf 23, capped at 12 Mbit / 24M buffer), a companion with its **short** side
at 1080 (crf 26, 5 Mbit / 10M — so a landscape master lands on 1920×1080, a portrait one
on 1080×1920, and a near-square screen recording stays near-square), and a WebP poster
1920 on its long side. Every encode is `-fps_mode passthrough`: three of these are
variable-rate phone recordings flagged at 60 and 120 fps, and forcing one to a constant
rate would be the last drop's judder bug again.

**The server HTML names the companion** and hangs the master on `data-hi`; `PICK_FILM` —
one line inside the element, ahead of its `<source>` — swaps the master in above 900 px,
while the parser is still standing there. Unlike `oagPick` it never touches `preload`, so
a film stays `preload="none"` and nothing at all is fetched until somebody presses play.

| File | Picture | Size |
|---|---|---|
| `film-asap-rocky-ray-ban.mp4` | 3840×2160 | 66.7 MB |
| `film-asap-rocky-ray-ban-1080.mp4` | 1920×1080 | 18.0 MB |
| `film-asap-rocky-ray-ban.webp` | 1920×1080 poster | 271 KB |
| `film-moncler.mp4` | 3840×2160 | 57.4 MB |
| `film-moncler-1080.mp4` | 1920×1080 | 17.6 MB |
| `film-moncler.webp` | 1920×1080 poster | 93 KB |
| `film-fords-gin.mp4` | 2160×3840 | 48.1 MB |
| `film-fords-gin-1080.mp4` | 1080×1920 | 13.6 MB |
| `film-fords-gin.webp` | 1080×1920 poster | 147 KB |
| `film-louboutin-shun-sudo.mp4` | 2160×3840 | 26.1 MB |
| `film-louboutin-shun-sudo-1080.mp4` | 1080×1920 | 5.8 MB |
| `film-louboutin-shun-sudo.webp` | 1080×1920 poster | 101 KB |
| `film-capabilities.mp4` | 3840×2160 | 88.2 MB |
| `film-capabilities-1080.mp4` | 1920×1080 | 28.3 MB |
| `film-capabilities.webp` | 1920×1080 poster | 119 KB |
| `film-open-air-gallery.mp4` | 3840×2160 | 267.5 MB |
| `film-open-air-gallery-1080.mp4` | 1920×1080 | 63.4 MB |
| `film-open-air-gallery.webp` | 1920×1080 poster | 123 KB |
| `reel-block-therapy-1080.mp4` | 1122×1080 | 3.8 MB |
| `reel-block-therapy.webp` | 1920×1848 poster | 69 KB |
| `reel-keep-it-oscar-1080.mp4` | 1080×1180 | 10.6 MB |
| `reel-keep-it-oscar.webp` | 1758×1920 poster | 121 KB |

The two reels have **no master beside them**, for the same reason the RAINS progress reel
has none (CLAUDE.md, 2026-09-21): the frame is a few hundred pixels wide at every width,
so a 2244-pixel rendition is bytes no screen can ever show.

**The two reel companions carry level 5.1, not the 4.2 every other companion carries.**
They are variable-rate screen recordings whose container is flagged 60 and 120 fps, and
x264 sizes the level off that flag rather than off the ~37 frames a second actually in
them: at 4.2 it wrote a stream whose own macroblock rate exceeded its declared level, and
said so. Same crf, same picture, a level a hardware decoder will accept.

**`-preset fast`, not the `-preset slow` the older scripts use.** Measured on this box,
slow runs at about 1 frame a second on 4K, and this drop is some twelve thousand frames of
it. `fast` measured 4.2 fps on the same clip and came out 0.9% larger than `medium`. crf
is what fixes the picture and it is unchanged; the trade is a few per cent of file for a
job that finishes in an hour instead of four.

## Verified, both checkouts (2026-09-26)

`/root/shot/oag-drop2-verify.mjs` against a local copy of each build: Home, Work, About and
the four new project pages, at 1440 and at 390, then the same seven with JavaScript off and
with `prefers-reduced-motion: reduce`. **Zero failures on both.** What it asserts:

- console, `pageerror`, `requestfailed` and 4xx all empty; no horizontal overflow; no
  hidden sections in any render.
- The rendition the browser actually fetched: **the 4K master at 1440 and the 1080
  companion at 390**, on every hero clip and every film band.
- Every `<video>` has a poster, and every film band is still `preload="none"` with nothing
  fetched until the button is pressed.
- **Every play button gives the whole film with its sound**: duration within 0.1 s of the
  source on all eight, `muted` false, `loop` off, controls back, playing.
- **The frame is the film's own shape** everywhere except the full-bleed hero band, which
  is `object-fit: cover` by design and is cropped to the band, never stretched. The two
  portrait films sit in portrait frames: 418×745 against a 2160×3840 film.
- With no script and under reduced motion every section is present and every film still
  carries the browser's own control.

`oag-paint-verify.mjs` and `splat-verify.mjs` both still pass on the preview build.

**One deliberate difference from the no-script render.** `oagPickFilm()` is not gated on
`html.motion`, unlike `oagPick()`: a hero clip is `display:none` under reduced motion so
downloading it would be waste, but a film behind a button is visible and playable in every
render, and a visitor who asked for less animation has not asked for a smaller picture —
the owner's rule is that footage is lightened for phones and for nothing else. So at
≥ 900 px a reduced-motion render carries a `src` attribute the no-script render does not,
and `shot-oag-build.mjs --reduced --compare` reports `bodyHtmlIdentical: false` there. The
rendered page is identical (`viewportRenderIdentical: true`) and nothing is hidden or
missing. (That comparison is not green site-wide on this branch today in any case: it
fails on all three counts on `/services`, which this drop never touched.)

## The facts — and the ones to confirm with Ephraim

Confirmed **off the films themselves**, frame by frame, and nowhere else:

- **Moncler** — a woman in a green mask, "Where Dreams Are Made Of" under her, MONCLER at
  the foot and **MONCLER GENIUS** tagged in yellow on the brick beside it. The street sign
  in the film reads **Grand St / Centre St**, so the corner is not a guess.
- **A$AP Rocky × Ray-Ban** — a pale blue wall with A$AP Rocky in Ray-Bans, a second
  portrait beside him, and the roundel that reads **A$AP ROCKY · Ray-Ban** with **AWGE**
  set around its rim.
- **Fords Gin** — the wall reads "NEW YORK / Thank You FOR THE / MARTINI / Sincerely,
  **FORDS GIN** / PLEASE COCKTAIL RESPONSIBLY". No apostrophe: the brand is *Fords Gin*,
  and that is how `projects.py` names the client.
- **Christian Louboutin × Shun Sudo** — the wall is signed **Christian Louboutin × SHUN
  SUDO** with `WWW.CHRISTIANLOUBOUTIN.COM` along the foot. Shun Sudo himself is in the
  film, watching it from the street.
- **The studio film** carries its own title card: **OPEN AIR GALLERY 2024**, over the
  Gucci × Ken Scott flower wall.

**Nothing below is on the site. Ask him:**

1. **The feet, on all four walls.** None of them has any, so all four carry the
   `feet to come` marker where the figure goes — the path kept alive for exactly this
   (CLAUDE.md, 2026-09-21). Four numbers would fill the hook on four project pages, four
   Work cards, the square-foot total and the widest/tallest sentence on Home.
2. **The years, on all four.** `year=None` on every row; the Year line is simply not
   written rather than guessed. The one date-shaped thing in the drop is the legal card at
   the end of the Fords Gin film — *"Fords Gin is a registered trademark. ©2025
   Brown-Forman Corporation"* — which is a copyright notice on a video, not a statement
   about when a wall was painted. **Is 2025 the year of that wall?** And the studio film's
   own card says **2024** — is that the year of the film, or of the work in it?
3. **The building.** The owner identifies both the A$AP Rocky and the Fords Gin walls as
   the **Landmark Coffee Shop building on Grand Street**. The Fords Gin film does show a
   **LANDMARK** storefront under the wall and a **SILVERCAST** sign on the brick (Silvercast
   Media owns that spectacular), and Moncler's street sign puts that wall at Grand and
   Centre. The site says "New York, NY" and, for Moncler only, "Grand and Centre", because
   that is the part the film proves. Confirm the addresses and the copy can say more.
4. **Who is speaking in the Block Therapy reel.** The brief says Ephraim; the reel shows a
   masked painter and never names him, so the strip credits "the painter's own words"
   rather than putting words in a named mouth.
5. **Which of the three Keep it Oscar walls is his.** The reel names Mike Perry (NYC),
   JC Rivera (Chicago) and Jiaqi (LA) as the designing artists and shows walls in all
   three cities. Open Air Gallery paints other people's designs — that is the business —
   but the reel does not say which of these it painted, so the copy describes the campaign
   and claims none of the three.
6. **The Upendo reel and the Upendo project.** `upendo-los-angeles` is already on the
   roster with its own photograph and 18 × 18 feet. The Block Therapy reel is that same
   wall. It is in the feed strip for now; it could equally sit on the Upendo page as "the
   wall going up" does on RAINS. His call.
7. **Whether Moncler's project page and the Moncler mark on the "Painted for" wall should
   link to each other.** The brand wall is `brands.py` and knows nothing about
   `projects.py`; now that Moncler has a page, a brand cell could be a link. Out of scope
   here, worth a line when he next reviews.

## Still open from the last drop

`16_9 VFX.mp4` is still damaged — it stops at 50.35 s of 58.45, so `film-rains.mp4` still
loses the tail of the closing pull-away. **Ask him to send that file again** and re-run
`./make-films.sh`; the duration is how you check it arrived. Nothing in this drop touches
it.

## What was committed, one idea at a time

1. The sources under slug names, this file, and the two `make-drop-*.sh` scripts.
2. A film is played whole, with its sound, at the shape it was shot — `film_shape()`,
   `film_sources()`, the new `film_band()`, `PICK_FILM`, the button that unmutes a looping
   band in `site.js`, and `--film-ar` on `.film-frame`.
3. The four walls join the roster, and a film shot standing up opens the page standing up
   — `projects.py`, `portrait_hero()`, `.thero`.
4. The showreel, first thing under the Home hero.
5. "The film" — the studio film on Home and on About.
6. "Straight off the phone" — the two reels on the Work page.
7. This file pointed at from CLAUDE.md.
