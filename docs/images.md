# Images — where they came from and how to replace them

Build step 15. Three files own the whole pipeline:

| File | Job |
|---|---|
| `wix-sources.json` | Hand-written map: project slug → the exact image URLs Ephraim's live Wix site renders. Tracked. |
| `fetch-wix.py` | Fetches a large rendition of each into `assets/`, and writes `assets/_sources.json`. |
| `process.sh` | Turns each `assets/<name>.{jpg,jpeg,png}` into four WebP renditions under `out/img/`. |

`assets/` and `out/` are gitignored. They are a cache: `fetch-wix.py` then
`process.sh` rebuilds both from the tracked JSON in a couple of minutes.

```sh
python3 fetch-wix.py     # ~25 s, polite: 0.5 s between requests
./process.sh             # ~65 s cold, instant when nothing changed
```

## Provenance — these are placeholders

**Every image in `assets/` was pulled from Ephraim's own live Wix site
(`static.wixstatic.com`, via `openairgallery.art`) on 2026-09-18.** They are his
photographs of his own murals, used to build and preview his replacement site.
They are **placeholders until his originals arrive** (PLAN.md §5; CLAUDE.md
decision 5: "originals from Ephraim, with people in frame for scale").

`assets/_sources.json` is the audit trail. Every file has a row giving the exact
URL requested, the as-rendered URL it was derived from, the byte count, the pixel
size, the content type and a sha256. Nothing in `assets/` is unaccounted for.

### How the URLs are built

The rendered Wix URL is the template. `fetch-wix.py` rewrites **only** the
transform segment between `/v1/` and the trailing filename:

```
.../media/b79272_69ff08…~mv2.jpeg/v1/fill/w_147,h_125,…,blur_2,enc_avif,…/Gucci%20Mural….jpeg
.../media/b79272_69ff08…~mv2.jpeg/v1/fit/w_3000,h_3000,q_90,enc_auto/Gucci%20Mural….jpeg
```

The media id, the `~mv2.<ext>` and the filename stay byte-for-byte. A
`/v1/crop/x_,y_,w_,h_/` prefix is kept too — that crop is the client's framing of
his own shot. A bare `/media/<id>` URL is never constructed: Wix answers 403.

Two things that will bite anyone who touches this:

- **The `Accept` header is load-bearing.** `enc_auto` gives the client whatever
  it asks for, so a normal browser `Accept` returns AVIF or WebP bytes wearing a
  `.jpg` name. `fetch-wix.py` sends `image/jpeg,image/png,…` to force a real
  re-encode — which is also all `process.sh` globs for.
- **Wix caps a `fit` request at 3000 px on the long side** and never upscales.
  So the "requested 3000" column below is a ceiling, not a promise.

## Resolution obtained

`native` is the original upload as Wix's own page JSON reports it. `fetched` is
what we actually hold in `assets/`. All 23 succeeded on the first step (`w_3000`);
none needed the step down to 2400 or 1600, and none came back under 60 KB.

### The twelve projects

| Asset | Native on Wix | Fetched | Bytes |
|---|---|---|---|
| `gucci-new-york-hero` | 1242 × 1057 | 1242 × 1057 | 332 KB |
| `crown-royal-trail-blazers-hero` | 1236 × 971 | 1236 × 971 | 279 KB |
| `uber-san-francisco-hero` | 1242 × 1028 | 1242 × 1028 | 217 KB |
| `victorias-secret-austin-hero` | 1242 × 966 | 1242 × 966 | 163 KB |
| `vitamin-water-new-york-hero` | 2732 × 1521 | 2732 × 1521 | 967 KB |
| `sprite-new-york-hero` | 1200 × 800 | 1200 × 800 | 187 KB |
| `ford-mustang-chicago-hero` | 1242 × 1015 | 1242 × 1015 | 239 KB |
| `showtime-dexter-boston-hero` | 1200 × 800 | 1200 × 800 | 297 KB |
| `upendo-los-angeles-hero` | 3024 × 4032 | 2250 × 3000 · capped | 1097 KB |
| `i-am-a-man-chicago-hero` | 1242 × 1273 | 1242 × 1273 | 270 KB |
| `john-lewis-rochester-hero` | 1284 × 861 | 1284 × 861 | 269 KB |
| `john-lewis-rochester-1` | 4762 × 3175 | 3000 × 2000 · capped | 682 KB |
| `malcolm-x-rochester-hero` | 1284 × 1536 | 1284 × 1536 | 443 KB |

**Every one of the twelve projects has a hero. None is missing an image.**
`john-lewis-rochester` is the only one with a second shot.

### Supporting images

| Asset | Native on Wix | Fetched | Bytes | Where it sits on his site |
|---|---|---|---|---|
| `home-hero` | 4995 × 5683 | 2636 × 2999 · capped | 1553 KB | behind "MURALS THAT CAPTURE THE GAZE" |
| `moncler-wide` | 4995 × 3396 | 3000 × 2039 · capped | 2039 KB | same upload, his own `/v1/crop/` framing |
| `moncler` | 8688 × 5792 | 3000 × 2000 · capped | 1228 KB | largest original on the site |
| `red-bull` | 6922 × 3894 | 3000 × 1687 · capped | 701 KB | home, "latest projects" |
| `monkey-47` | 1284 × 773 | 1284 × 773 | 368 KB | home, slide 04 |
| `ephraim-portrait` | 1773 × 1924 | 1773 × 1924 | 2547 KB (PNG) | home, "REACH NEW HEIGHTS" |
| `about-team` | 5760 × 3840 | 3000 × 2000 · capped | 928 KB | lead image on About |
| `about-portrait-small` | 1284 × 1277 | 1284 × 1277 | 297 KB | 90 × 90 avatar by the About contact block |
| `about-preservation` | 1242 × 824 | 1242 × 824 | 186 KB | About, "Mural Preservation" step |
| `contact-band` | 6720 × 4480 | 3000 × 2000 · capped | 835 KB | home, "Let's Get to Work" band |

### What this means for the design

**Ten of the twelve project heroes are ~1200–1284 px wide.** Only Vitamin Water
(2732) and Upendo (2250) clear 1600. PLAN.md step 15's check — "every hero
exists ≥ 1600 w" — **cannot be met from Wix**, because these are the largest
files Ephraim ever uploaded there. This is the concrete argument for his
originals: a dark, full-bleed, photo-first design wants 2400 px heroes and today
half of them would be upscaled on a retina laptop.

Practical consequence for `build.py`: for a source under 1600 px the `.webp` and
`-1600.webp` renditions come out the same pixel size (only the quality differs),
so `pic()` must write `srcset` width descriptors from the **actual** rendition
dimensions, not from the assumed 2400/1600/800. `assets/_sources.json` carries
the source pixel size for every asset if that is easier to read than the files.

## Renditions

`process.sh` writes four WebPs per asset, aspect preserved, never upscaled:

| Output | Max width | Quality | Use |
|---|---|---|---|
| `out/img/<name>.webp` | 2400 | 84 | full-bleed hero |
| `out/img/<name>-1600.webp` | 1600 | 82 | srcset middle |
| `out/img/<name>-800.webp` | 800 | 80 | srcset small / mobile |
| `out/img/t/<name>.webp` | 640 | 76 | cards and thumbnails |

23 sources → 92 renditions, 15.5 MB. Re-runs skip anything whose output is newer
than its input, so dropping in one new photo reprocesses that photo alone.

## Swap procedure — when Ephraim's originals arrive

**The filenames are the contract.** Nothing in `build.py`, the CSS or the HTML
changes; only the bytes behind the names do.

1. Put his files into `assets/` under the **same names** —
   `gucci-new-york-hero.jpg`, `upendo-los-angeles-hero.jpg`,
   `john-lewis-rochester-1.jpg`, `ephraim-portrait.png` … Extension may change
   (`.png` → `.jpg` is fine); **delete the old file** if it does, or `process.sh`
   will warn about two sources claiming one name and skip the second.
2. Delete those rows from `assets/_sources.json` — they described Wix copies that
   no longer exist, and an inaccurate audit trail is worse than none. Leave the
   rows for anything still coming from Wix.
3. Re-run `./process.sh`. Only the replaced images rebuild.
4. Rebuild and redeploy the site, then screenshot Home and one project page at
   1440 and 390 before calling it done.
5. One commit: *"Photos: Ephraim's originals replace the Wix renditions."*
   Update the resolution table above and drop the "placeholders" language from
   `CLAUDE.md` once every project is his own file.

Do **not** re-run `fetch-wix.py` after a swap — it skips names that already
exist, so it is harmless, but `--force` would overwrite his originals with Wix
copies. If you ever need the Wix copy back, delete the file and re-run.

## Known gaps

- **Graffiti Removal has no photographs at all.** His Wix site does have a
  `/graffiti-removal` page (he spells it "Graffitti Removal", two Ts), but only
  Home, Work and About were saved in `research/wix/`, so not one image URL from
  that page exists. Either re-save the page or — better — ask Ephraim for real
  before/after shots. Until then the page's "Wash" mechanic uses the drawn brick
  wall, as CLAUDE.md already plans. `about-preservation` is the nearest thing we
  have to a coating/cleaning photo.
- **Signs and banners** — the lower half of his Work page is a grid of nine sign
  and banner jobs (Corona, Heineken, Jack Daniels, Black Crow, Marion's,
  Flattrack, House of Pizza, G Street Loft, one untitled). URLs and native sizes
  are recorded under `not_fetched.signs_and_banners` in `wix-sources.json`; move
  an entry into `extras` and re-run `fetch-wix.py` when the Services page needs
  them.
- **Three more murals** appear on his home page but not in CLAUDE.md's project
  list — Snickers, The Inn, GST Loft. Recorded under
  `not_fetched.other_home_murals`. Worth asking whether they belong on Work.
- **Background videos** — two exist on his home page; only their poster frames
  are in the saved HTML. Ask him for the source files if we want motion.

## Things in his Wix URLs worth knowing

- Two filenames carry a **literal apostrophe**, not `%27`:
  `Victoria's%20Secret%20Mural….jpg` and `Showtime's%20Dexter%20Mural….jpeg`.
  Kept as rendered. Anything that re-encodes these URLs must not "fix" them.
- The site-wide `og:image` percent-encodes the tilde as `%7E`
  (`b79272_2838f3…%7Emv2.jpg`) while every other URL uses a literal `~`. Both
  forms work; URL handling must survive both.
- **Sprite is the only project whose file is not project-named** — it is
  `IMG_0296.jpeg`. Matched by its position on the Work page and the "Sprite"
  heading beside it. The same photo is uploaded **twice** under two different
  media ids (the Work copy and a Home copy); we fetch one.
- **One upload serves three purposes.** `1P1A7854.jpg` (4995 × 5683) is the home
  hero uncropped *and* both Moncler thumbnails, via two different
  `/v1/crop/` framings of the same file.
- **`ephraim-portrait` is filed as `Akbar Portrait_edited.png`.** Its `alt` text
  is the only place on the entire site that gives a surname — "Ephraim Gebre".
  Confirm with him before captioning it.
- The About page's "Paint Analysis" illustration is an **Unsplash stock photo**
  (`nsplsh_…`, "Image by David Pisnoy"), not his work. Deliberately not fetched.
- The highest-resolution mural shot on the whole site is
  `IAMPROJECTLEWIS-2612.jpg` (4762 × 3175) — and it is on the *About* page
  illustrating "Mural Prep", not on the John Lewis project. It is pulled in as
  `john-lewis-rochester-1`.
