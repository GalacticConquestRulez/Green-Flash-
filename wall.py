#!/usr/bin/env python3
"""wall.py — "Wash": the graffitied brick wall the visitor cleans.

The graffiti-removal signature (PLAN.md 4b, docs/plan-agent-notes.md 4b). Every
pixel of it is drawn here — a <pattern> of staggered bricks, a grain filter and
a wall of tags — so it is crisp at any size, weighs a few kilobytes gzipped and
raises no licensing question. Photographs can replace the two layers later
without touching the CSS or the JS (see docs/wash.md).

THE TAGS
--------
The graffiti has to read as a wall someone actually painted, so the words are
real handstyle letterforms — outlines traced from Sedgwick Ave, Sedgwick Ave
Display and Permanent Marker by tools/make-tags.py and checked in as
tag_paths.py. build.py therefore never needs fontTools, the site ships no font
file, and two builds of the same source are byte-identical. Change a word, a
face or a size in tools/make-tags.py, re-run it, commit tag_paths.py with the
wall. Never bubble letters: see CLAUDE.md.

They are layered the way a wall accumulates, oldest at the bottom: a buffed
patch with a ghost under it, the big throw-up, the silver handstyle, a blue
tag, then marker scrawls over everything. Every spray piece carries a dark
outline, a few drips and an overspray halo; the grime is under the paint and
the light and the vignette are over it, so the paint sits in the same light as
the brick.

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
never borrows it. The paint is red, silver, blue and marker black; nothing in
this file is green.
"""
from tag_paths import TAGS, WORDS as TAG_WORDS

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
# The paint, oldest to newest. Nothing here is the mint.
BUFF        = '#9a9288'    # the grey the last buff job used: close, not right
GHOST       = '#e8e2d8'    # the tag still showing through it
RED         = '#D7263D'    # the throw-up
SILVER      = '#d9d7d2'    # the handstyle
BLUE        = '#2743D8'
MARKER      = '#17161b'
MARKER_RED  = '#B31F52'
INK         = '#16141a'    # outline around the throw-up
INK_2       = '#1a1a1f'    # outline around the silver

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
    """Pattern, grain and — on the tagged layer — the paint's filters and words.

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
    paint = _paint_defs(uid) if tagged else ''
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
</radialGradient>{paint}
</defs>'''


def _paint_defs(uid):
    """The filters the paint is made of, and every word as one path.

    spray  the aerosol: turbulence displaces the outline by a few units and a
           hair of blur takes the vector edge off it, which is the whole
           difference between a can and a shape tool.
    soft   a marker: no displacement, the nib is not spraying anything.
    halo   the overspray — the same word blurred wide and faint under itself.
    buff   the blur on the painted-out patch, a roller edge rather than a cut.

    The words live in <defs> once and are painted three or four times through
    <use>: halo, outline shadow, outline, body. Repeating the path data per
    pass would be 30 KB of coordinates per wall, and the wall is inlined twice
    in every figure.
    """
    words = ''.join(f'<path id="{uid}-w-{k}" d="{d}"/>' for k, (d, _adv) in TAGS.items())
    return (
        f'<filter id="{uid}-spray" x="-10%" y="-10%" width="120%" height="120%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="2" '
        f'seed="5" result="t"/>'
        f'<feDisplacementMap in="SourceGraphic" in2="t" scale="6" '
        f'xChannelSelector="R" yChannelSelector="G"/>'
        f'<feGaussianBlur stdDeviation="1.1"/></filter>'
        f'<filter id="{uid}-soft" x="-10%" y="-10%" width="120%" height="120%">'
        f'<feGaussianBlur stdDeviation="0.5"/></filter>'
        f'<filter id="{uid}-halo" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur stdDeviation="14"/></filter>'
        f'<filter id="{uid}-buff" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur stdDeviation="6"/></filter>'
        + words)


def _tag(uid, key, x, y, rot=0, fill=RED, outline=None, halo=True, drips=(),
         opacity=1, blend='multiply', spray=True, extra=''):
    """One word on the wall.

    Passes, in the order a can puts them down: the overspray halo, the
    outline's own shadow, the outline, the body, then any drips. The outline
    is a fat stroked copy of the same letterform rather than a second path, so
    it can never come away from the letters it belongs to. A drip is a
    tapering curve off a letter bottom ending in the drop that stopped there.

    Sizes come out of tag_paths.WORDS, so the outline weight and the offset
    stay proportional to whatever the letterforms were traced at.
    """
    d, _adv = TAGS[key]
    size = TAG_WORDS[key][2]
    ref = f'#{uid}-w-{key}'
    sw = f'{size * .11:.1f}'
    out = [f'<g transform="translate({x},{y}) rotate({rot})" opacity="{opacity}" '
           f'style="mix-blend-mode:{blend}">']
    if halo:
        out.append(f'<use href="{ref}" fill="{fill}" filter="url(#{uid}-halo)" opacity=".38"/>')
    if outline:
        for tr in (f' transform="translate({size * .04:.1f},{size * .05:.1f})"', ''):
            out.append(f'<use href="{ref}" fill="{outline}" stroke="{outline}" '
                       f'stroke-width="{sw}" stroke-linejoin="round" '
                       f'filter="url(#{uid}-spray)"{tr}/>')
    out.append(f'<use href="{ref}" fill="{fill}" '
               f'filter="url(#{uid}-{"spray" if spray else "soft"})"/>')
    for dx, dy, ln, wd in drips:
        out.append(f'<path d="M{dx} {dy} q{wd * .15:.1f} {ln * .5:.0f} 0 {ln}" '
                   f'stroke="{fill}" stroke-width="{wd}" stroke-linecap="round" '
                   f'fill="none" opacity=".92"/>'
                   f'<circle cx="{dx}" cy="{dy + ln}" r="{wd * .7:.1f}" fill="{fill}"/>')
    out.append(extra)
    out.append('</g>')
    return ''.join(out)


def _tags(uid):
    """The wall as it accumulated, oldest first.

    Nobody starts a wall; they add to one. So it reads bottom-up in time: a
    buff job that did not match and the tag still ghosting through it, then
    the throw-up someone put over the middle of it, the silver handstyle that
    took the top right, a blue tag in the corner, and marker over all of it —
    including a name crossed out by whoever came next.
    """
    return (
        # 1. the buff patch, and what is still under it
        f'<g style="mix-blend-mode:normal">'
        f'<rect x="620" y="330" width="470" height="210" fill="{BUFF}" opacity=".42" '
        f'filter="url(#{uid}-buff)"/>'
        + _tag(uid, 'KWEST', 660, 470, rot=-2, fill=GHOST, halo=False,
               opacity=.2, blend='normal')
        + '</g>'
        # 2. the throw-up: red, fat outline, four drips
        + _tag(uid, 'SEKR', 90, 400, rot=-4, fill=RED, outline=INK, blend='normal',
               opacity=.94,
               drips=((70, -6, 95, 12), (250, -4, 140, 14),
                      (432, -8, 70, 11), (560, -6, 115, 13)))
        # 3. silver handstyle, top right
        + _tag(uid, 'NOVA', 720, 210, rot=4, fill=SILVER, outline=INK_2,
               blend='normal', opacity=.94,
               drips=((112, -6, 62, 8), (318, -4, 44, 7)))
        # 4. marker tags, and a blue one low on the right
        + _tag(uid, 'ZEK27', 700, 620, rot=-6, fill=MARKER, halo=False, spray=False,
               opacity=.9)
        + _tag(uid, 'TVR', 60, 120, rot=3, fill=MARKER, halo=False, spray=False,
               opacity=.85)
        + _tag(uid, 'YOKO', 930, 600, rot=-8, fill=BLUE, blend='normal', opacity=.92,
               drips=((72, -4, 52, 7),))
        + _tag(uid, 'TVR_SM', 400, 160, rot=-4, fill=MARKER_RED, halo=False,
               spray=False, opacity=.8)
        # 5. beef: a name crossed out by whoever came next
        + _tag(uid, 'ARO', 300, 640, rot=2, fill=MARKER, halo=False, spray=False,
               opacity=.85,
               extra=f'<path d="M-10 -20 L 150 -34 M-6 -50 L 150 -8" stroke="{RED}" '
                     f'stroke-width="9" stroke-linecap="round" '
                     f'filter="url(#{uid}-spray)"/>'))


def brick_svg(tagged=False, uid='wash'):
    """One layer of the wall: the bricks, and on the tagged variant the grime
    and everything that has been painted on it. Both variants draw the
    identical brick geometry, so the layers register exactly and a washed
    stroke reveals the same course.

    tagged=False is the clean wall, tagged=True the one that needs the crew.
    uid namespaces every id in the file: two walls on one page must not share.

    Order matters and is the order of the real thing: grime, then paint, then
    the light and the vignette over both — so the tags are lit by the same
    afternoon as the brick instead of floating in front of it.
    """
    label = ('A brick wall under years of graffiti — a big red throw-up with '
             'drips, a silver handstyle, a blue tag, marker scrawls and a '
             'patch someone painted out'
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
            + _tags(uid))
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
