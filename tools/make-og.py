#!/usr/bin/env python3
"""Cut Drew's mark out of his logo and render the site's icons and share cards.

    python3 tools/make-og.py            → out/img/{favicon.*,apple-touch-icon.png,og*.png}

Everything this writes lands in out/img/, which is gitignored like the rest of
the media: the repo holds the generator, never its output. build.py references
the files and records a miss (rule 10) if they are not there yet, so a fresh
clone builds, warns, and is fixed by running this once.

WHAT IT MAKES

    favicon.ico          16/32/48 px, the mark on his black
    favicon-32.png       the same at 32 px, for browsers that prefer a PNG
    favicon.svg          the mark as a vector-wrapped bitmap, for the tab strip
                         on a high-DPI screen and for pinned tabs
    apple-touch-icon.png 180 px with the padding iOS expects, no alpha
    og.png               1200x630, the mark over "Content · Websites · Drones"
    og-<slug>.png        the same card with a service named on it, one per
                         service in content.SERVICES

THE MARK

Drew has not sent the transparent PNG or the vector yet (CLAUDE.md, "Still
owed"), so the mark is cut out of the 2000x2000 JPEG he did send: the bright
pixels above the wordmark, squared up, with an alpha channel derived from
luminance so his black drops out and the white/green artwork does not. When the
transparent PNG arrives, point LOGO_SRC at it and delete `_alpha_from_luma` —
nothing else in this file or in build.py changes.

THE FONTS

Space Grotesk and Inter, the two faces the site already loads, fetched from
github.com/google/fonts into assets/fonts/ (gitignored) on first run. Both are
published under the SIL Open Font License 1.1, whose only conditions are that
the licence travels with the font and that a derivative is not sold on its own;
rendering words with it, as here, is exactly what it is for. The licence text
is downloaded alongside each font as <Family>-OFL.txt.
"""
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)
from content import SITE, SERVICES                                # noqa: E402

# Drew's transparent PNG (2026-09-23). Before it arrived this read logo.jpg and
# cut the black away by luminance; the alpha channel is now the real edge.
LOGO_SRC = os.path.join(SRC, 'assets', 'logo.png')
FONT_DIR = os.path.join(SRC, 'assets', 'fonts')
OUT = os.path.join(SRC, 'out', 'img')

# The three colours build.py names in the HTML, and the muted grey the
# stylesheet uses for a sub-line. Same values, same reasons; see the contrast
# block at the top of site/css/site.css.
BG = (5, 10, 10)            # #050A0A
GREEN = (45, 232, 181)      # #2de8b5
INK = (221, 228, 225)       # #DDE4E1 — the type grey, as site.css --ink
MUTE = (154, 170, 170)      # #9AAAAA — 8.6:1 on the black

# name → (path under google/fonts, local filename)
FONTS = {
    'grotesk': ('ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf', 'SpaceGrotesk[wght].ttf'),
    'inter':   ('ofl/inter/Inter%5Bopsz,wght%5D.ttf', 'Inter[opsz,wght].ttf'),
}
LICENCES = {
    'grotesk': ('ofl/spacegrotesk/OFL.txt', 'SpaceGrotesk-OFL.txt'),
    'inter':   ('ofl/inter/OFL.txt', 'Inter-OFL.txt'),
}
RAW = 'https://raw.githubusercontent.com/google/fonts/main/'


# ----------------------------------------------------------------- the fonts
def fetch_fonts():
    """Put the two faces and their licences in assets/fonts/, once."""
    os.makedirs(FONT_DIR, exist_ok=True)
    for path, name in list(FONTS.values()) + list(LICENCES.values()):
        dest = os.path.join(FONT_DIR, name)
        if os.path.exists(dest):
            continue
        print('fetching', name)
        with urllib.request.urlopen(RAW + path, timeout=60) as r:
            data = r.read()
        with open(dest, 'wb') as f:
            f.write(data)


def face(which, size, weight, opsz=None):
    """One instance of a variable font. Pillow sets the axes by position, in
    the order the font declares them — Space Grotesk is [wght], Inter is
    [opsz, wght]."""
    f = ImageFont.truetype(os.path.join(FONT_DIR, FONTS[which][1]), size)
    f.set_variation_by_axes([weight] if opsz is None else [opsz, weight])
    return f


# ------------------------------------------------------------------ the mark
def _alpha_from_luma(im):
    """His black becomes transparent; his white and his green do not.

    The JPEG is artwork on a flat black field, so brightness is a good enough
    stand-in for the alpha channel he has not sent us. x3 with a clamp keeps
    the mid-greys of the shirt's shading opaque and only lets the field itself
    go through.
    """
    r, g, b = im.split()
    luma = (Image.merge('RGB', (r, g, b)).convert('L')
            .point(lambda v: 0 if v <= 8 else min(255, (v - 8) * 3)))
    out = im.convert('RGBA')
    out.putalpha(luma)
    return out


def mark(size):
    """The mark alone, square, `size` px, RGBA with the black cut away.

    The logo is a stacked lockup: mark, MENDOZA MARKETING, CONTENT | WEBSITES |
    DRONES. The mark is whatever is lit in the top two thirds; its bounding box
    is measured rather than hard-coded, so a re-export that sits differently on
    the canvas still crops correctly.
    """
    im = Image.open(LOGO_SRC).convert('RGBA')
    w, h = im.size
    lit = im.split()[-1].point(lambda v: 255 if v > 40 else 0)
    box = lit.crop((0, 0, w, int(h * 0.66))).getbbox()
    assert box, f'{LOGO_SRC}: nothing in the top two thirds'
    x0, y0, x1, y1 = box
    # Square it about its own centre, with a hair of air so the circle never
    # touches the edge of the icon.
    side = int(max(x1 - x0, y1 - y0) * 1.04)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    im = im.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))
    return im.resize((size, size), Image.LANCZOS)


def on_bg(rgba, pad=0.0):
    """Composite a square RGBA mark onto his black, optionally with padding."""
    s = rgba.width
    if pad:
        inner = int(s * (1 - 2 * pad))
        rgba = rgba.resize((inner, inner), Image.LANCZOS)
    card = Image.new('RGB', (s, s), BG)
    card.paste(rgba, ((s - rgba.width) // 2, (s - rgba.height) // 2), rgba)
    return card


# ----------------------------------------------------------------- the cards
def centred(d, y, text, font, fill, tracking=0):
    """Draw one line centred on a 1200-wide card. Returns the line's height.

    Pillow has no letter-spacing, so a tracked line is drawn glyph by glyph —
    the eyebrow and the tagline are set wide the way the stylesheet sets them.
    """
    if not tracking:
        w = d.textlength(text, font=font)
        d.text((600 - w / 2, y), text, font=font, fill=fill)
    else:
        w = sum(d.textlength(c, font=font) + tracking for c in text) - tracking
        x = 600 - w / 2
        for c in text:
            d.text((x, y), c, font=font, fill=fill)
            x += d.textlength(c, font=font) + tracking
    return font.getbbox(text)[3]


def card(headline=None):
    """1200x630. The mark centred on his black, his tagline under it, and —
    on a service card — the service named in green between the two."""
    im = Image.new('RGB', (1200, 630), BG)
    d = ImageDraw.Draw(im)

    m = mark(300 if headline is None else 240)
    top = 84 if headline is None else 105
    im.paste(m, (600 - m.width // 2, top), m)
    y = top + m.height + (44 if headline is None else 30)

    if headline:
        centred(d, y, headline, face('grotesk', 58, 700), INK)
        y += 78
        centred(d, y, SITE['name'], face('inter', 26, 600, opsz=26), GREEN, tracking=1.5)
        y += 46
        centred(d, y, SITE['tagline'], face('inter', 22, 400, opsz=22), MUTE, tracking=1)
    else:
        centred(d, y, SITE['name'], face('grotesk', 64, 700), INK)
        y += 88
        centred(d, y, SITE['tagline'], face('inter', 30, 400, opsz=30), GREEN, tracking=2.5)

    # The one hairline the site draws under everything, in the accent.
    d.rectangle([0, 626, 1199, 629], fill=GREEN)
    return im


# ------------------------------------------------------------------- the run
def main():
    fetch_fonts()
    os.makedirs(OUT, exist_ok=True)
    wrote = []

    def save(name, im, **kw):
        path = os.path.join(OUT, name)
        im.save(path, **kw)
        wrote.append((name, os.path.getsize(path)))

    big = mark(512)
    save('favicon.ico', on_bg(big.resize((48, 48), Image.LANCZOS)),
         sizes=[(16, 16), (32, 32), (48, 48)])
    save('favicon-32.png', on_bg(big.resize((32, 32), Image.LANCZOS)))
    save('apple-touch-icon.png', on_bg(big.resize((180, 180), Image.LANCZOS), pad=0.11))

    # An SVG favicon so the tab is sharp at any DPI. There is no vector of the
    # mark yet, so the file is his bitmap wrapped in SVG — the shape a browser
    # wants, with the artwork we actually hold. It is replaced outright the day
    # the vector lands.
    import base64, io
    buf = io.BytesIO()
    big.resize((128, 128), Image.LANCZOS).save(buf, format='PNG', optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" '
           'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 64 64">'
           '<title>Mendoza Marketing</title>'
           '<rect width="64" height="64" fill="#050A0A"/>'
           f'<image x="0" y="0" width="64" height="64" xlink:href="data:image/png;base64,{b64}"/>'
           '</svg>')
    with open(os.path.join(OUT, 'favicon.svg'), 'w') as f:
        f.write(svg)
    wrote.append(('favicon.svg', os.path.getsize(os.path.join(OUT, 'favicon.svg'))))

    save('og.png', card())
    for s in SERVICES:
        save(f"og-{s['slug']}.png", card(s['name']))

    for name, size in wrote:
        print(f'  out/img/{name:28} {size / 1024:7.1f} KB')
    print(f'{len(wrote)} files')


if __name__ == '__main__':
    main()
