# Ephraim's drop, 2026-09-20 — "Ephraim website.zip"

The owner dropped `Ephraim website.zip` (1.28 GB) into the repo and said: *"he wants that
content integrated into his site."* It is extracted to `assets/source/ephraim-drop/`
(gitignored; the zip is kept beside it). Nine files, all his:

| File | What it is | Use |
|---|---|---|
| `16_9(3).jpg` 2257×1270 | The RAINS wall from the air with the painter on the lift, wall large in frame | **RAINS hero photo** |
| `5_4.jpg` 1250×1000 | The wall straight on, three faces + RAINS, AMC / Angel Media Co. placard | gallery 1 (the mural itself) |
| `16_9.jpg` 1242×994 | Same, wider | gallery 2 |
| `16_9(2).jpg` 3217×1924 | High aerial, the block with the wall small | gallery 3 |
| `16_9(1).jpg` 2078×1169 | Aerial, the wall on the red-brick building | gallery 4 |
| `16_9 VFX.mp4` 4K60 H.264, 58 s | Drone film: opens on the Manhattan skyline with an "Open Air Gallery" title card, descends to the wall, close on the faces and the painter on the lift, pulls away. Same cut as "No FX" but with the graphics. | **RAINS page hero film** |
| `16_9 No FX.mp4` | The same flight without graphics | keep as source, unused — and the only one of the two that reads end to end (see below) |
| `9_16 Progress Visual_.mp4` 2160×3840 60fps, 34 s | Portrait reel: the RAINS artwork card, then the wall going up from the lift, ends on the Open Air Gallery card | **"the wall going up" portrait clip on the RAINS page** |
| `flower-city-arts-center.mov` (was ` .mov`) 4K24 H.264, 60 s | Title card "FLOWER CITY ARTS CENTER — shot by @omgmaxgod". Rochester: an underpass wall by the ballpark, painters on lifts, a community group in front of the finished wall. Film by Max (DroneGodMax). | **Flower City Arts Center public-works project**: hero + gallery frames from the film, page hero film |

## Facts we have, and the ones we do not
- **RAINS**: a mural for **AMC / Angel Media Co.** (the placard on the wall reads exactly
  "AMC angelmediaco."), in **New York, NY** (Manhattan skyline, One WTC in frame). Three
  faces and the word RAINS. Painted from a boom lift. **15 × 15 feet** (the owner,
  2026-09-21). **Year 2024** (the owner, 2026-09-20, from the date Ephraim posted the
  films).
- **Flower City Arts Center**: **Rochester, NY**, a community wall — the civic strand the
  About/Home "Public works" section is framed for. **25 × 50 feet** (the owner,
  2026-09-21) — the one wall on the roster taller than it is wide, which is what a wall
  under a bridge abutment is. **Year 2023** (the owner, 2026-09-20, from the date Ephraim
  posted the films).
  Credit the film: *Film by Max — @omgmaxgod*.
- Nothing is invented: no feet, no client sentence Ephraim did not give. Nothing here was
  ever estimated off a photograph, and nothing needs to be now. The years above are the
  years the films were posted, which is what the owner supplied — they are not dates read
  off the walls, so they sit in the Year row of the project meta and nowhere else in the
  copy.

### The feet arrived (the owner, 2026-09-21)
*"15x15 on rains and 25x50 on flower city"* — wide by tall, the way every other wall in
`projects.py` is written. `dim_w`/`dim_h` on both rows are whole feet now, and two numbers
filled four places on their own: the `.dims` hook under each project's title, the figure on
each Work grid card, the square-foot total on the stats band, and the widest/tallest
sentence beside it. Nothing else on either page moved.

**The optional-feet path stays.** `dim_w=None, dim_h=None`, `measured()`, `feet_note()` and
the `.dims`-or-note branch in `pcard()` and `project_page()` are all still there and still
tested by `check_projects()`: the next wall Ephraim sends may arrive without a tape measure
too, and the site has to keep reading as a portfolio when it does.

**Which hero a project page opens on is now "has it a film", not "has it feet".** Those
used to be the same question. RAINS and Flower City have both, and the film stays — it is
what the drop was for — so the figure moved down into the words under it, where it is the
first thing after the title. `scale_hero()` is for a wall with feet and no film.

**And `ROCHESTER` is the civic Rochester walls that share a measurement.** Flower City is
civic, in Rochester, and now measured, but at 25 × 50 it is not the 53 × 50 the Home band
calls "the same size to the foot" out loud. Having no feet used to be what kept it out of
that pair; feet that do not match are what keep it out now.

### The VFX file is damaged (found 2026-09-21, cutting the full film)
`16_9 VFX.mp4` stops at **50.35 s of 58.45** — a corrupt packet at dts 3020000, frame 3021
of 3507, which no reader gets past (`-err_detect ignore_err` included: the NAL length in
the file is wrong, so there is nothing after it to resynchronise on). The hero cut is
unaffected, because its last beat ends at 49.3 s. The full film on the page is therefore
50.35 s and loses the tail of the closing pull-away. `16_9 No FX.mp4` is whole but is the
same flight without the grade or the title card. **Ask Ephraim to re-send the file** and
re-run `./make-films.sh`. With the feet answered on 2026-09-21 this is **the only thing
still outstanding on either wall**.

## What changes (one commit each, on `openairgallery-redesign`)
1. **Dimensions become optional.** `projects.py` entries may carry `dim_w: None, dim_h: None`.
   `check_projects()` accepts both None (never one). `dims()` returns `''` for None.
   `total_sq_ft()`, `WIDEST`, `TALLEST` and the stats band skip projects without feet.
   `pcard()` and `project_page()` render no `.dims` block for them — the marker note
   *"feet to come"* sits where the figure would (a `.marker` span, mint, small), so the
   card still reads as a wall. The Live/Stencil JS only binds to `.dims` that exist.
   (Both walls were measured on 2026-09-21 and neither shows the note any more; the path
   is kept for the next wall that arrives without one.)
2. **RAINS** joins `PROJECTS` (slug `rains-new-york`, title `Rains`, client
   `AMC × Angel Media Co.`, category `brand`, `featured: True` and added to
   `FEATURED_ORDER` after Gucci), with `hero: rains-new-york-hero` and gallery
   `rains-new-york-1..4` per the table. Assets copied into `assets/` under those names;
   `./process.sh` builds the renditions. Story, two sentences, true only: what is on the
   wall, who it was for, where, painted from the lift — and, since 2026-09-21, its feet.
3. **The RAINS page opens on the film.** A `video` key on a project (`'hero-rains'`) is
   passed to `page_hero(..., video=)` in `project_page()`. Cut with a new
   `make-rains-clip.sh` modelled on `make-hero-clip.sh`: from `16_9 VFX.mp4`, three
   beats — the title-card skyline (0–6 s), the descent to the wall, the close on the faces
   and the painter, the pull-away — about 24 s, 1280×720 30fps crf 30, no audio, plus the
   webp poster. Same reduced-motion / no-JS / data-saver behaviour as Home's hero.
4. **The wall going up.** A new section on the RAINS page under the story: a portrait clip
   (`out/video/rains-progress.mp4`, 720×1280 30fps crf 30, no audio, poster webp) in a
   phone-shaped frame beside a short heading `The wall <em class="pop">going up</em>` and
   one sentence. Muted, loops, plays when in view (one IntersectionObserver, under
   `html.motion`); the poster and a real `<video controls>` otherwise. No layout shift.
5. **Flower City Arts Center** joins `PROJECTS` (slug `flower-city-arts-center-rochester`,
   title `Flower City Arts Center`, client `Flower City Arts Center`, city Rochester NY,
   category `civic`, dims None, credit `Film by Max — @omgmaxgod`, `video: 'hero-flower-city'`).
   Hero and three gallery stills are frames pulled at 4K from the film with ffmpeg (choose
   the finished wall, the lifts at work, the group in front of it); the page hero film is a
   ~20 s cut. (`dims` are 25 × 50 since 2026-09-21.) `public_works()`: its photograph becomes the Flower City hero, its copy says
   three Rochester walls are photographed so far and names Flower City Arts Center; the
   Work page's civic filter includes it.
6. **AMC on the "Painted for" wall.** A `brands.py` row for AMC: a Wikimedia Commons SVG if
   one exists under the PD-textlogo rule (record `commons`/`source_url`/`download`/`licence`
   exactly as the other rows do, and run `process-brands.sh`); otherwise `mark='type'` in
   AMC's own colour with a `colour_note`. Never redrawn.
7. **CLAUDE.md** gets a short "Ephraim's drop, 2026-09-20" note pointing at this file and
   recording what was still missing. Feet and years are both answered now; the note has
   been updated to say so, and the one hole left is the re-send of `16_9 VFX.mp4`.

## Verification, before the preview is republished
`python3 build.py` green with the asserts; `./process.sh` reports the new renditions;
`node /root/shot/shot-oag-build.mjs` on `/`, `/work`, `/work/rains-new-york`,
`/work/flower-city-arts-center-rochester`, `/about` at 1440 and 390 with `errors: []`;
`--nojs` and `--reduced --compare` identical on those pages; `oag-paint-verify.mjs` and
`splat-verify.mjs` still pass; the two films play (video element `readyState ≥ 3`, current
time advancing) on the two project pages; the stats band still computes from the walls that
have feet — 24,769 square feet since 2026-09-21, up from 23,294 — and states no wall count;
`check_no_wall_count()` passes. Then
`./publish-preview.sh` and a screenshot of both new pages for the owner. Live
(`ephraim.greenflashusa.com`) is not deployed: the redesign promotes as one step later.
