#!/usr/bin/env python3
"""Contrast gate for the Open Air Gallery palette.

Round three flipped the canvas: white ground, ink type, the mint as the loud
colour a band is painted in and the coral as the one accent. That gives three
kinds of pair to hold, and none of them is a preference — they are what keeps
the site readable:

  * ink and its two greys on the white page, and on the two panels off it;
  * type on one of the three black bands that are left (the marquee, the
    scrim over a photograph, the footer);
  * type on paint — ink on mint, ink on coral.

Two colours carry no type at all and so claim no pair: the mint is 1.5:1 on
white and the coral is 3.28:1, which is large-text contrast. The coral is
allowed exactly that much — the marker asides and a shouted word in a
headline, 24px and up, never body copy — and the floor below says so.

This reads the tokens out of site/css/site.css and refuses the build if any
pair drops below its floor, or if a colour build.py has to name in HTML has
drifted from the token it mirrors.

Run on its own to print the table:  python3 docs/contrast.py
"""
import os, re, sys

MIN_INK_ON_MINT = 13.0
MIN_LARGE = 3.0


def _srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour):
    h = hex_colour.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.2126 * _srgb_to_linear(r)
            + 0.7152 * _srgb_to_linear(g)
            + 0.0722 * _srgb_to_linear(b))


def ratio(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def tokens(css_path):
    """The hex custom properties declared in the stylesheet's :root block."""
    css = open(css_path, encoding='utf-8').read()
    root = re.search(r':root\s*\{(.*?)\}', css, re.S)
    assert root, f'{css_path}: no :root block'
    return dict(re.findall(r'(--[a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{3,8})\s*;', root.group(1)))


# The pairs that have to hold, as (foreground token, background token, floor).
PAIRS = [
    ('--ink', '--paper', 7.0),              # the page: type on the ground
    ('--muted', '--paper', 7.0),            # the reading copy under a heading
    ('--dim', '--paper', 4.5),              # labels, captions, small print
    ('--dim', '--paper-2', 4.5),            # the same, on the alt band
    ('--muted', '--paper-2', 7.0),
    ('--ink', '--mint', MIN_INK_ON_MINT),   # the mint band, and its button
    ('--ink', '--pop', 4.5),                # the coral button
    ('--pop', '--paper', MIN_LARGE),        # the marker asides — large only
    ('--on-ink', '--ink', 7.0),             # the footer and the marquee
    ('--on-ink-mute', '--ink', 7.0),
    ('--mint', '--ink', MIN_INK_ON_MINT),   # the accent where it is black
    ('--mint-deep', '--ink', 7.0),
    ('--ink', '--wall', 7.0),               # the scrubbed-clean panel
]


def check(css_path, mirrors=None, quiet=True):
    """Assert the palette still clears its floors. Raises AssertionError."""
    t = tokens(css_path)
    rows = []
    for fg, bg, floor in PAIRS:
        assert fg in t and bg in t, f'{css_path}: missing {fg} or {bg} in :root'
        r = ratio(t[fg], t[bg])
        rows.append((fg, bg, r, floor))
        assert r >= floor, (
            f'contrast: {fg} ({t[fg]}) on {bg} ({t[bg]}) is {r:.2f}:1, '
            f'below the {floor}:1 floor this design depends on')
    # Colours build.py has to repeat in HTML (theme-color, the inline favicon)
    # must be the same colours the stylesheet declares.
    for name, value in (mirrors or {}).items():
        assert name in t, f'{css_path}: build.py mirrors {name}, which :root does not declare'
        assert t[name].lower() == value.lower(), (
            f'{name} drifted: build.py says {value}, site.css says {t[name]}')
    if not quiet:
        for fg, bg, r, floor in rows:
            print(f'  {fg:>12} on {bg:<10} {r:6.2f}:1  (floor {floor})')
    return rows


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    css = os.path.join(os.path.dirname(here), 'site', 'css', 'site.css')
    try:
        check(css, quiet=False)
    except AssertionError as e:
        print('FAIL:', e)
        sys.exit(1)
    print('contrast OK')
