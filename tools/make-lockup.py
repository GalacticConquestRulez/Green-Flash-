#!/usr/bin/env python3
"""The horizontal lockup for the nav: Drew's mark, then MENDOZA over MARKETING.

Drew asked (2026-09-23) for the header to carry "the words Mendoza with
Marketing underneath next to the logo", sized like the Decision Frameworks
header he sent: the two text lines stacked to the right of the mark, the text
block as tall as the mark. Nothing here is set in a font — the mark and both
words are cut out of his own transparent PNG (assets/logo.png), so the nav
shows his lettering, his tracking and his colours, only rearranged.

Reads  assets/logo.png   the stacked lockup on transparency, from Drew
Writes out/img/lockup.webp   the horizontal lockup, RGBA, 2x the nav height
       out/img/lockup.png    the same as PNG, for anyone who needs the file

The three pieces are found by scanning the alpha channel for horizontal bands
of ink: the first band is the mark, the second MENDOZA, the third MARKETING
(with its dots); the fourth, CONTENT | WEBSITES | DRONES, is left out of the
nav. A re-export that sits differently on the canvas still cuts correctly.
"""
import os
import sys

from PIL import Image

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(SRC, 'assets', 'logo.png')
OUT = os.path.join(SRC, 'out', 'img')

H = 240          # output height in px — the nav shows it at 44–58, so this is > 4x
GAP = .13        # air between the mark and the words, as a fraction of H
LINE_GAP = .12   # air between MENDOZA and MARKETING, as a fraction of H


def bands(alpha, thresh=32):
    """(y0, y1) of every run of rows that carry ink."""
    w, h = alpha.size
    mask = alpha.point(lambda v: 255 if v > thresh else 0)
    out, start = [], None
    for y in range(h):
        row = mask.crop((0, y, w, y + 1)).getbbox() is not None
        if row and start is None:
            start = y
        elif not row and start is not None:
            out.append((start, y))
            start = None
    if start is not None:
        out.append((start, h))
    return out


def piece(im, band):
    """One band, cropped to its ink on both axes."""
    w = im.width
    strip = im.crop((0, band[0], w, band[1]))
    box = strip.split()[-1].point(lambda v: 255 if v > 32 else 0).getbbox()
    return strip.crop(box)


def fit_height(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def fit_width(im, w):
    return im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)


def main():
    if not os.path.exists(LOGO):
        sys.exit(f'make-lockup: {LOGO} missing — the transparent PNG from Drew')
    im = Image.open(LOGO).convert('RGBA')
    found = bands(im.split()[-1])
    assert len(found) >= 3, f'expected mark, MENDOZA, MARKETING; found {found}'
    mark, mendoza, marketing = (piece(im, b) for b in found[:3])

    # The mark takes the full height. The two words share it: both are set to
    # the same width (his own lockup stacks them flush), then the pair is
    # scaled so the block is exactly as tall as the mark.
    mark = fit_height(mark, H)
    wide = max(mendoza.width, marketing.width)
    mendoza, marketing = fit_width(mendoza, wide), fit_width(marketing, wide)
    gap_px = round(LINE_GAP * H)
    block_h = mendoza.height + marketing.height
    scale = (H - gap_px) / block_h
    mendoza = fit_width(mendoza, round(wide * scale))
    marketing = fit_width(marketing, mendoza.width)

    x_text = mark.width + round(GAP * H)
    canvas = Image.new('RGBA', (x_text + mendoza.width, H), (0, 0, 0, 0))
    canvas.alpha_composite(mark, (0, 0))
    y = (H - (mendoza.height + gap_px + marketing.height)) // 2
    canvas.alpha_composite(mendoza, (x_text, y))
    canvas.alpha_composite(marketing, (x_text, y + mendoza.height + gap_px))

    os.makedirs(OUT, exist_ok=True)
    canvas.save(os.path.join(OUT, 'lockup.png'), optimize=True)
    canvas.save(os.path.join(OUT, 'lockup.webp'), quality=92, method=6, lossless=True)
    print(f'lockup {canvas.width}x{canvas.height}: mark {mark.width}w, '
          f'words {mendoza.width}w ({mendoza.height}+{gap_px}+{marketing.height})')


if __name__ == '__main__':
    main()
