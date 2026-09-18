#!/usr/bin/env python3
"""wall.py — "Wash": the graffitied brick wall the visitor cleans.

The graffiti-removal signature (PLAN.md 4b, docs/plan-agent-notes.md 4b). Every
pixel of it is drawn here — a <pattern> of staggered bricks, a grain filter and
three graffiti pieces as <path>s — so it is crisp at any size, weighs a few
kilobytes and raises no licensing question. Photographs can replace the two
layers later without touching the CSS or the JS (see docs/wash.md).

THE TWO CALLS build.py MAKES
---------------------------
    from wall import wall_html

    # 1. Home, inside gr_band() — the compact, non-interactive loop that links
    #    to /graffiti-removal. No pointer handling, no sound, no washer head.
    wall_html(mode='auto', id_prefix='washhome')

    # 2. The Graffiti Removal page — the full mechanic.
    wall_html(mode='interactive', id_prefix='wash')

    layout() must also carry the two assets, next to site.css / site.js:
        <link rel="stylesheet" href="{u('/css/wash.css')}?v={asset_v('css/wash.css')}">
        <script src="{u('/js/wash.js')}?v={asset_v('js/wash.js')}" defer></script>
    (only on the pages that hold a wall — the file is inert everywhere else.)

    id_prefix must differ per instance on a page: it namespaces every SVG id.

THE CONTRACT (site.css "MOTION", site.js)
-----------------------------------------
The figure renders complete with no JavaScript: the finished clean wall, with
the tagged version beside it as a real "before" thumbnail. Everything that
hides anything is scoped to html.motion and carries the 2.8 s self-reveal, so a
page whose wash.js never arrives falls back to that same before/after pair.
No counters, no percentages, no labels — the wall does the talking.

PALETTE RULE: the mint (#71EEB8) is the brand's one accent and the graffiti
never borrows it. The pieces are magenta, electric blue and amber; nothing in
this file is green.
"""

# The drawn field. 16:9 all the way through — the SVG viewBox, the CSS
# aspect-ratio and the 256x144 mask canvas in wash.js are the same rectangle,
# so a stroke lands where the pointer is.
VB_W, VB_H = 1200, 675

# --- brick geometry ---------------------------------------------------------
# One pattern tile is two courses, the second offset half a brick. 104x38 brick
# on a 110x44 grid leaves a 6px mortar joint that closes across the tile seam.
BRICK_W, BRICK_H, GRID_X, GRID_Y = 104, 38, 110, 44

# --- colour -----------------------------------------------------------------
MORTAR      = '#413d3a'
BRICKS      = ('#8b8279', '#837a71', '#8f8680', '#7d746c')
OUTLINE     = '#141318'
PIECES = (
    # (body, shadow, highlight)
    ('#E5305F', '#8E1538', '#FF9BB5'),   # magenta throw-up, left
    ('#4A5DF0', '#1E2480', '#9FB4FF'),   # electric blue wildstyle, right
    ('#F2A63A', '#8F5309', '#FFE08A'),   # amber script, low and wide
)

# Individually toned bricks. Hard-coded rather than random so two builds of the
# same source produce byte-identical HTML (asset_v hashes the output).
# (column, row, fill, opacity)
TONES = (
    (1, 1, '#000', .18), (4, 0, '#fff', .06), (7, 2, '#000', .13),
    (2, 4, '#fff', .07), (9, 3, '#000', .16), (5, 6, '#000', .11),
    (0, 7, '#fff', .06), (8, 8, '#000', .17), (3, 9, '#fff', .05),
    (10, 6, '#000', .12), (6, 11, '#000', .15), (1, 12, '#fff', .06),
    (9, 13, '#000', .13), (4, 14, '#000', .10), (11, 10, '#fff', .06),
    (2, 2, '#000', .10), (7, 5, '#fff', .06), (0, 10, '#000', .14),
    (5, 0, '#000', .12), (8, 1, '#fff', .05), (3, 3, '#000', .09),
    (11, 4, '#000', .15), (6, 7, '#fff', .07), (10, 9, '#000', .10),
    (2, 8, '#000', .16), (7, 10, '#000', .08), (4, 12, '#fff', .05),
    (0, 13, '#000', .15), (9, 15, '#000', .11), (5, 14, '#fff', .06),
)

# --- the three pieces -------------------------------------------------------
# Each is one <path> of two or three letterforms, painted three times by <use>:
# a fat dark outline, the body colour, then a thin offset highlight. Drips hang
# off the letters they belong to.
PIECE_PATHS = (
    ('M 140 396 C 112 306 150 214 236 212 C 306 210 334 268 316 322 '
     'C 300 372 240 388 208 356 C 184 332 196 288 240 288 '
     'M 372 396 C 348 312 372 220 434 216 C 492 212 516 266 504 328 '
     'C 496 372 462 396 432 374 '
     'M 544 236 C 558 296 558 348 548 398'),
    ('M 648 338 L 706 176 L 764 338 L 822 176 L 880 338 '
     'M 926 182 L 926 338 M 1010 182 L 1010 338 M 926 258 L 1010 258 '
     'M 1064 182 L 1064 338 L 1136 338'),
    ('M 286 528 C 322 462 392 470 396 522 C 400 566 356 580 344 546 '
     'C 334 518 368 490 406 504 C 448 520 462 558 500 540 '
     'C 542 520 520 452 562 452 C 602 452 596 516 632 524 '
     'C 674 534 682 480 720 476 C 766 472 776 538 826 518'),
)
# Drips start inside the letter they run off, so they read as paint that ran
# rather than sticks under the piece.
DRIP_PATHS = (
    'M 196 356 L 196 458 M 300 350 L 300 424 M 440 372 L 440 452 M 550 380 L 550 442',
    'M 706 320 L 706 414 M 764 326 L 764 392 M 880 320 L 880 400 M 1010 322 L 1010 386',
    'M 344 540 L 344 620 M 500 528 L 500 594 M 720 512 L 720 584',
)
# The arrow over the wildstyle piece, and a marker tag in the corner.
ARROW_PATH = 'M 940 132 L 1116 132 M 1116 132 L 1064 92 M 1116 132 L 1064 172'
TAG_PATH = ('M 928 570 C 958 528 986 576 1012 546 C 1034 520 1062 562 1088 538 '
            'M 936 606 L 1104 596 M 1048 560 L 1062 616')


def _brick_xy(col, row):
    """Top-left of one brick in the drawn field."""
    x = 2 + GRID_X * col - (GRID_X // 2 if row % 2 else 0)
    return x, 3 + GRID_Y * row


def _tones():
    out = []
    for col, row, fill, op in TONES:
        x, y = _brick_xy(col, row)
        out.append(f'<rect x="{x}" y="{y}" width="{BRICK_W}" height="{BRICK_H}" '
                   f'rx="2" fill="{fill}" opacity="{op}"/>')
    return ''.join(out)


def _defs(uid, tagged):
    """Pattern, grain and — on the tagged layer — the three piece paths.

    The grain is filtered inside a small pattern tile, not over the whole
    field: feTurbulence across 1200x675 is a real cost on a phone, across
    120x120 it is nothing, and at this frequency the repeat is invisible.
    """
    # The half-bricks at x=-53 and x=167 are the two ends of ONE brick meeting
    # across the tile seam: give them different fills and a light stripe runs
    # down the wall every 220 units. They share BRICKS[3].
    courses = ''.join(
        f'<rect x="{x}" y="{y}" width="{BRICK_W}" height="{BRICK_H}" rx="2" fill="{fill}"/>'
        for x, y, fill in (
            (2, 3, BRICKS[0]), (112, 3, BRICKS[1]),
            (-53, 47, BRICKS[3]), (57, 47, BRICKS[2]), (167, 47, BRICKS[3]),
        ))
    pieces = ''.join(f'<path id="{uid}-p{i}" d="{d}"/>'
                     for i, d in enumerate(PIECE_PATHS)) if tagged else ''
    return f'''<defs>
<pattern id="{uid}-brick" width="220" height="88" patternUnits="userSpaceOnUse">
<rect width="220" height="88" fill="{MORTAR}"/>{courses}</pattern>
<filter id="{uid}-grainf" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n"/>
<feColorMatrix in="n" type="saturate" values="0"/>
</filter>
<pattern id="{uid}-grain" width="120" height="120" patternUnits="userSpaceOnUse">
<rect width="120" height="120" filter="url(#{uid}-grainf)"/></pattern>
<linearGradient id="{uid}-light" x1="0" y1="0" x2=".35" y2="1">
<stop offset="0" stop-color="#fff" stop-opacity=".10"/>
<stop offset=".55" stop-color="#fff" stop-opacity="0"/>
<stop offset="1" stop-color="#000" stop-opacity=".26"/>
</linearGradient>
<radialGradient id="{uid}-vig" cx=".5" cy=".5" r=".72">
<stop offset=".55" stop-color="#000" stop-opacity="0"/>
<stop offset="1" stop-color="#000" stop-opacity=".38"/>
</radialGradient>
<radialGradient id="{uid}-soot" cx=".5" cy=".5" r=".5">
<stop offset="0" stop-color="#000" stop-opacity=".34"/>
<stop offset="1" stop-color="#000" stop-opacity="0"/>
</radialGradient>{pieces}
</defs>'''


def _piece(uid, i):
    """Outline, body, highlight — the three passes that make a throw-up read."""
    body, shadow, hi = PIECES[i]
    ref = f'#{uid}-p{i}'
    return (
        f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{DRIP_PATHS[i]}" stroke="{OUTLINE}" stroke-width="28"/>'
        f'<path d="{DRIP_PATHS[i]}" stroke="{shadow}" stroke-width="17"/>'
        f'<path d="{DRIP_PATHS[i]}" stroke="{body}" stroke-width="9" opacity=".8"/>'
        f'<use href="{ref}" stroke="{OUTLINE}" stroke-width="52"/>'
        f'<use href="{ref}" stroke="{shadow}" stroke-width="38"/>'
        f'<use href="{ref}" stroke="{body}" stroke-width="30"/>'
        f'<use href="{ref}" stroke="{hi}" stroke-width="7" opacity=".85" '
        f'transform="translate(-7,-9)"/>'
        f'</g>')


def brick_svg(tagged=False, uid='wash'):
    """One layer of the wall: the bricks, and on the tagged variant the grime
    and the three pieces. Both variants draw the identical brick geometry, so
    the layers register exactly and a washed stroke reveals the same course.

    tagged=False is the clean wall, tagged=True the one that needs the crew.
    uid namespaces every id in the file: two walls on one page must not share.
    """
    label = ('A brick wall covered in graffiti — three pieces in magenta, blue '
             'and amber, with drips'
             if tagged else 'The same brick wall, washed clean')
    grime = ''
    if tagged:
        grime = (
            # Soot and old rain, heaviest at the foot of the wall. Feathered
            # with a radial stop: flat ellipses read as blobs, not dirt.
            f'<rect width="{VB_W}" height="{VB_H}" fill="#000" opacity=".11"/>'
            f'<ellipse cx="180" cy="660" rx="400" ry="170" fill="url(#{uid}-soot)"/>'
            f'<ellipse cx="1020" cy="676" rx="440" ry="170" fill="url(#{uid}-soot)"/>'
            f'<ellipse cx="620" cy="90" rx="380" ry="140" fill="url(#{uid}-soot)" opacity=".7"/>'
            + ''.join(_piece(uid, i) for i in range(len(PIECE_PATHS)))
            + f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">'
              f'<path d="{ARROW_PATH}" stroke="{OUTLINE}" stroke-width="26"/>'
              f'<path d="{ARROW_PATH}" stroke="{PIECES[1][0]}" stroke-width="14"/>'
              f'<path d="{TAG_PATH}" stroke="{OUTLINE}" stroke-width="13" opacity=".7"/>'
              f'<path d="{TAG_PATH}" stroke="#F4F3EF" stroke-width="6"/>'
              f'</g>')
    return (
        f'<svg class="wall-svg" viewBox="0 0 {VB_W} {VB_H}" width="100%" height="100%" '
        f'preserveAspectRatio="xMidYMid slice" role="img" aria-label="{label}">'
        f'{_defs(uid, tagged)}'
        f'<rect width="{VB_W}" height="{VB_H}" fill="url(#{uid}-brick)"/>'
        f'{_tones()}'
        f'<rect width="{VB_W}" height="{VB_H}" fill="url(#{uid}-grain)" opacity=".26" '
        f'style="mix-blend-mode:overlay"/>'
        f'{grime}'
        f'<rect width="{VB_W}" height="{VB_H}" fill="url(#{uid}-light)"/>'
        f'<rect width="{VB_W}" height="{VB_H}" fill="url(#{uid}-vig)"/>'
        f'</svg>')


# The washer head that replaces the cursor: the wand comes in over the
# shoulder from the top left and the nozzle tip sits exactly on the pointer,
# where the stroke is actually landing. The CSS centres the box on the
# pointer, so everything here is drawn around (36,36).
HEAD_SVG = (
    '<svg viewBox="0 0 72 72" width="72" height="72" aria-hidden="true" focusable="false">'
    '<g transform="rotate(45 36 36)">'
    '<path d="M-6 36.5 L6 36.5" stroke="#F4F3EF" stroke-opacity=".22" stroke-width="6" '
    'stroke-linecap="round"/>'
    '<rect x="2" y="31" width="22" height="11" rx="5" fill="#2B2B31"/>'
    '<rect x="14" y="41" width="9" height="10" rx="3" fill="#2B2B31"/>'
    '<rect x="22" y="32.5" width="8" height="8" rx="2.5" fill="#3A3A42"/>'
    '<rect x="28" y="33.5" width="8" height="6" rx="2" fill="#8B8279"/>'
    '</g>'
    '<circle cx="36" cy="36" r="14" fill="#F4F3EF" opacity=".13"/>'
    '<circle cx="36" cy="36" r="7" fill="#F4F3EF" opacity=".3"/>'
    '<circle cx="36" cy="36" r="2.4" fill="#F4F3EF"/>'
    '<circle cx="47" cy="30" r="1.6" fill="#F4F3EF" opacity=".55"/>'
    '<circle cx="44" cy="45" r="1.2" fill="#F4F3EF" opacity=".45"/>'
    '<circle cx="28" cy="47" r="1.4" fill="#F4F3EF" opacity=".4"/></svg>')

# A speaker with, and without, the two little waves.
SND_ON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/>'
          '<path d="M18.5 5.5a9 9 0 0 1 0 13"/></svg>')
SND_OFF = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M16 9.5 21 15"/><path d="M21 9.5 16 15"/></svg>')


def wall_html(mode='interactive', id_prefix='wash'):
    """The server-rendered Wash figure. Both layers are real content.

    mode='interactive'  the full mechanic for /graffiti-removal: the visitor
                        drags a washer head and the tag comes off under it.
    mode='auto'         the compact loop for the home band: no pointer
                        handling, no sound, no washer head — a CSS sweep that
                        wash.js only lets run while the figure is on screen.

    With no JavaScript, or before wash.js binds, both modes render the same
    honest thing: the finished clean wall, the tagged one beside it as a
    "before" thumbnail, and a caption. Nothing here needs a script to be true.
    """
    if mode not in ('interactive', 'auto'):
        raise ValueError(f"wall_html: mode must be 'interactive' or 'auto', not {mode!r}")
    auto = mode == 'auto'
    uid = id_prefix
    hint = ('' if auto else
            f' <span class="wall-hint">Drag across the brick to wash it off.</span>')
    head = ('' if auto else
            f'<div class="wall-head" data-wash-head aria-hidden="true">{HEAD_SVG}</div>')
    snd = ('' if auto else f'''<button class="wall-snd" type="button" data-wash-snd
      aria-pressed="false" aria-label="Sound">
      <span class="wall-snd-on" aria-hidden="true">{SND_ON}</span><span class="wall-snd-off" aria-hidden="true">{SND_OFF}</span>
      <span class="wall-snd-t">Sound</span></button>''')
    return f'''<figure class="wall" id="{uid}" data-wash="{mode}">
  <div class="wall-stage" data-wash-stage>
    <div class="wall-layer wall-clean">{brick_svg(False, uid + '-c')}</div>
    <div class="wall-layer wall-tag" data-wash-tag>{brick_svg(True, uid + '-t')}</div>
    <div class="wall-glint" aria-hidden="true"></div>
    <div class="wall-rinse" aria-hidden="true"></div>
    <div class="wall-sparks" data-wash-sparks aria-hidden="true"></div>
    {head}
  </div>
  <div class="wall-foot">
    <div class="wall-thumb">{brick_svg(True, uid + '-b')}<span class="wall-thumb-t">Before</span></div>
    <figcaption class="wall-cap">Tagged brick, and the same wall after the crew has been.{hint}</figcaption>
    {snd}
  </div>
</figure>'''


if __name__ == '__main__':      # python3 wall.py > /tmp/wall.html to eyeball it
    import sys
    sys.stdout.write(wall_html(*(sys.argv[1:2] or ['interactive'])))
