# Wash — the graffitied wall the visitor cleans

The graffiti-removal signature (PLAN.md §4b, `docs/plan-agent-notes.md` §4b), and the
fourth verb in the motion vocabulary: **Roll · Scale · Cure · Wash**.

| file | what it is |
| --- | --- |
| `wall.py` | every pixel of the wall, as server-rendered SVG, and the figure's markup |
| `tag_paths.py` | **generated** — the tagged layer's words as SVG outlines |
| `tools/make-tags.py` | the generator that writes it, run by hand |
| `tools/fonts/` | the three handstyle faces it traces, and `LICENSES` |
| `site/css/wash.css` | staging only; nothing in it is load-bearing |
| `site/js/wash.js` | the mechanic: the mask canvas, the payoff, both ways out |
| `research/wash-test.html` | the bench — gitignored, never deployed |

`build.py` calls `wall_html(mode, id_prefix)` twice: `mode='auto'` for the compact home
band inside `gr_band()`, `mode='interactive'` for the Graffiti Removal page. `id_prefix`
namespaces every SVG id in the instance, so two walls on one page never collide, and the
page that holds a wall also has to load `css/wash.css` and `js/wash.js` — the files are
inert everywhere else.

## The contract

The figure is complete with no JavaScript: the finished clean wall at full size with the
tagged version beside it as a real "before" thumbnail, which *is* the before/after the
page needs. Everything that hides anything is scoped to `html.motion` and carries
`animation: … 0s linear 2.8s forwards`, so a page whose `wash.js` never arrives falls
back to that same pair 2.8 seconds later. `wash.js` returns before touching the DOM
unless `html.motion` is present and reduced motion is off, which makes the
reduced-motion render the same document as the no-script one. No counter, no percentage,
no label, ever — the wall does the talking. The stage has a fixed 16:9 `aspect-ratio`
and the foot a `min-height`, so no state changes the figure's box: CLS is 0 by
construction, and the bench asserts it.

## The mechanic

One 256×144 offscreen canvas starts opaque; the stroke punches soft radial holes in it
with `destination-out` and the canvas goes to `.wall-tag` as a PNG data URL in
`--wash-mask`, so the clean layer shows through the stroke. **The mask is on the whole
tagged layer**, which is why anything can be added to or removed from the tagged SVG
without touching the CSS or the JS. 16:9 all the way through — the SVG `viewBox`, the
stage and the mask buffer are the same rectangle, so a stroke lands under the pointer.

Every sixth painted frame, an alpha-sum of every eighth pixel says how much is clean; at
78 % the remainder wipes itself, one glint crosses the bricks, a few sparks fire and the
buffers are released. Twenty frames of a real stroke that cannot hold 40 fps drop the
wall to the crossfade instead (`degrade()`), as does reduced motion. Mobile gets a ×1.3
brush, half the sparks, `touch-action:pan-y`, and a tilt rinse offered only after a first
drag and only where `deviceorientation` needs no permission prompt. Sound is muted by
default behind a toggle that exists only once the script has bound.

## The wall itself

`brick_svg(tagged, uid)` draws both layers from the identical brick geometry — a
`<pattern>` of two staggered courses, a grain filter tiled at 120×120 rather than run
across the whole field, and a hard-coded list of individually toned bricks (hard-coded,
not random, so two builds of the same source are byte-identical: `asset_v` hashes the
output). Because the geometry is identical, a washed stroke reveals the same course that
was under the tag.

The tagged variant adds, in this order: **grime** (a flat 11 % black plus three feathered
soot ellipses), **the paint**, then the light gradient and the vignette — which are drawn
*after* the paint on purpose, so the tags are lit by the same afternoon as the brick
instead of floating in front of it.

### The paint

It has to read as a wall that accumulated, not as one afternoon's work, so it is layered
oldest to newest:

1. **The buff patch** — a not-quite-matching grey rectangle at ~.4, blurred at the edge
   the way a roller leaves it, with the ghost of `KWEST` still showing through at ~.2.
2. **`SEKR`**, the throw-up: 250 px of Sedgwick Ave Display in red `#D7263D`, its outline
   a fat stroked copy of the same letterform plus an offset copy for the shadow, and four
   drips off the letter bottoms, each tapering to the drop that stopped there.
3. **`NOVA`**, a silver handstyle top right with its own dark outline and two drips, and
   **`YOKO`** in blue low on the right with one.
4. **Marker** over all of it, `mix-blend-mode:multiply` so it sinks into the brick rather
   than sitting on it: `TVR` twice (once black, once dark red), `ZEK 27`, and `ARO`
   crossed out by whoever came next.

Two things do most of the work of reading as spray. Every sprayed edge goes through
`feTurbulence` (baseFrequency 0.045) + `feDisplacementMap` at scale 6 and a 1.1 blur, so
the letterform wavers the way a can wavers; markers get the blur alone, because a nib is
not spraying anything. And under each spray piece sits the same word blurred at
`stdDeviation` 14 at ~.38 — the **overspray halo**, which is most of what tells the eye
that paint was thrown at a wall from a foot away.

Palette rule: the mint `#71EEB8` is the brand's one accent and the graffiti never borrows
it. Nothing in `wall.py` is green.

### Changing a word

The letterforms are outlines traced from real handstyle faces — never drawn by hand and
never bubble letters (see `CLAUDE.md`). Each word lives once in `<defs>` and is painted
four times through `<use>`: halo, outline shadow, outline, body.

    # 1. edit WORDS in tools/make-tags.py — key, text, face, size, letter-spacing
    # 2. regenerate the outlines
    python3 tools/make-tags.py            # rewrites tag_paths.py beside wall.py
    # 3. place it in _tags() in wall.py, and commit tag_paths.py with wall.py

`tag_paths.py` is generated and checked in, which is the point of it: `build.py` never
needs fontTools, the site serves no font file, and the output is byte-stable. Words are
traced at the size they are drawn at rather than scaled in the SVG — scaling the path
would scale the grain of the spray with it — so the same text at two sizes is two keys
(`TVR` and `TVR_SM`). Names are invented; nothing is a real crew and nothing reads as a
slur. A new face needs its licence checked and recorded in `tools/fonts/LICENSES` first:
the wall's argument for being drawn rather than photographed is that it raises no
licensing question.

## Swapping in Ephraim's photographs

The two layers can become two `<picture>`s — his real before and after of the same wall —
without touching `wash.css` or `wash.js`, because the mask is on the layer, not on
anything inside it. The only requirements are that both images are the same 16:9 frame
and register to each other.

## Running the bench

`research/wash-test.html` inlines both modes against the real CSS and JS. It is
regenerated from `wall.py` (the generator lives outside the repo, in the scratchpad) and
`research/` is gitignored, so it is never deployed. Then, from the repo root:

    python3 -m http.server 8098
    node /root/shot/shot-wash.mjs [outDir]

It drives the wall at 1440 and at 390 through before / mid-stroke / finish / at rest,
plus the home band, the crossfade, JavaScript off and reduced motion. What has to be
true: `errors` is `[]`, both widths reach `is-done` at ~0.78 cleaned, the no-JS pass
shows the thumbnail at its full width, reduced motion never binds, and the figure's box
is identical before, mid-stroke and after.
