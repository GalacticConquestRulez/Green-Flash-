#!/usr/bin/env python3
"""make-tags.py — trace the wall's handstyle words into SVG path data.

The graffiti on the Wash wall (wall.py) has to read as a real tagged wall, and
real handstyle is a letterform, not a shape someone drew with a mouse. So the
words come from three handstyle fonts — Sedgwick Ave Display and Sedgwick Ave
for the spray pieces, Permanent Marker for the marker tags — and this script
turns each word into one <path> d.

It runs by hand, never at build time:

    python3 tools/make-tags.py        # rewrites tag_paths.py beside wall.py

wall.py imports tag_paths, so build.py never needs fontTools, the site carries
no webfont for graffiti that is only ever four words, and two builds of the
same source stay byte-identical (asset_v hashes the output, so a coordinate
that wobbled by a rounding step would churn every cache-busting URL on the
site). Coordinates are rounded to whole units for the same reason, and for
weight: half a unit of a 1200-wide field is under half a CSS pixel at the size
the wall is ever drawn, the spray filter displaces the outline by six units
anyway, and the rounding takes a third off a file that is inlined twice per
figure.

Each word is traced at the exact size it is drawn at, because the outline and
the spray filter in wall.py are sized in the same user units: scaling a traced
path in the SVG would scale the grain of the spray with it. Two entries can
therefore share a text (TVR is up twice, at two sizes) and they are separate
keys. WORDS below is the one place a word, its font or its size is written
down: change it here, re-run, and commit tag_paths.py with the wall.

Fonts live in tools/fonts/ with their licences (see tools/fonts/LICENSES).
"""
import os

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(HERE, 'fonts')
OUT = os.path.join(os.path.dirname(HERE), 'tag_paths.py')

# key, text, font file stem, size in SVG units, extra letter-spacing
# The invented names are the point: nothing here is a real crew.
WORDS = (
    ('KWEST',  'KWEST',  'SedgwickAve',        120, 0),
    ('SEKR',   'SEKR',   'SedgwickAveDisplay', 250, 0),
    ('NOVA',   'NOVA',   'SedgwickAve',        150, 0),
    ('YOKO',   'YOKO',   'SedgwickAve',         96, 0),
    ('ZEK27',  'ZEK 27', 'PermanentMarker',     62, 0),
    ('TVR',    'TVR',    'PermanentMarker',     54, 0),
    ('TVR_SM', 'TVR',    'PermanentMarker',     48, 0),
    ('ARO',    'ARO',    'PermanentMarker',     70, 0),
)

_FONTS = {}


def font(stem):
    if stem not in _FONTS:
        _FONTS[stem] = TTFont(os.path.join(FONTDIR, stem + '.woff2'))
    return _FONTS[stem]


def _n(v):
    """One coordinate, to the whole unit, with no -0."""
    s = f'{v:.0f}'
    return '0' if s == '-0' else s


def word_path(text, stem, size, letter_space=0):
    """(d, advance) for one word at `size`, baseline at y=0, pen starting at x=0.

    The glyph outlines come out of the font in font units with y up; the
    transform scales them to `size` and flips y, which is the coordinate
    system the SVG viewBox uses. A character the font has no glyph for opens
    a gap rather than raising — the space in "ZEK 27" is a real glyph, but a
    word typed later might not be.
    """
    f = font(stem)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    upm = f['head'].unitsPerEm
    s = size / upm
    hmtx = f['hmtx']
    x = 0.0
    parts = []
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None:
            x += size * .3
            continue
        pen = SVGPathPen(gs, ntos=_n)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
        d = pen.getCommands()
        if d:
            parts.append(d)
        x += hmtx[g][0] * s + letter_space
    return ' '.join(parts), round(x, 1)


HEAD = '''"""tag_paths.py — GENERATED FILE. Do not edit by hand.

The Wash wall's handstyle words as SVG path outlines, traced from the fonts in
tools/fonts/ by tools/make-tags.py. Regenerate with:

    python3 tools/make-tags.py

TAGS maps a key to (d, advance): the path data with the baseline at y=0 and
the pen starting at x=0, and how wide the word came out. WORDS records what
each key was traced from — wall.py reads the size back out of it, so the
outline and the spray grain stay in step with the letterforms.

Letterforms (c) their authors, under the licences in tools/fonts/LICENSES:
Sedgwick Ave and Sedgwick Ave Display (SIL Open Font License 1.1),
Permanent Marker (Apache License 2.0).
"""

# key: (text, font, size, letter_space)
WORDS = {
'''


def main():
    rows, words = [], []
    for key, text, stem, size, ls in WORDS:
        d, w = word_path(text, stem, size, ls)
        rows.append(f'    {key!r}: (\n        {d!r},\n        {w},\n    ),\n')
        words.append(f'    {key!r}: ({text!r}, {stem!r}, {size}, {ls}),\n')
    body = HEAD + ''.join(words) + '}\n\n# key: (d, advance)\nTAGS = {\n' + \
        ''.join(rows) + '}\n'
    with open(OUT, 'w') as f:
        f.write(body)
    print(f'wrote {OUT} — {len(WORDS)} words, {len(body)} bytes')
    for key, text, stem, size, ls in WORDS:
        print(f'  {key:7} {text:6} {stem:18} {size:4}px')


if __name__ == '__main__':
    main()
