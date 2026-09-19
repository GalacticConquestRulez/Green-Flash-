#!/usr/bin/env python3
"""strokes.py — the mint is paint, not a fill.

Owner, 2026-09-19: *"Maybe make the teal a brush stroke — so it looks like he
painted on the screen."* So on the white canvas there is no such thing as a
mint rectangle. Every mint band on the site, and the highlight behind the
mint words in the hero, is one swept stroke of a loaded brush:

  * a **loaded start** — the brush lands heavy, so the left end is darker,
    taller and a little ragged where the paint pushed ahead of the bristles;
  * a **feathered end** — the paint runs out, so the right end breaks into
    separate hairs that carry on past where the body stops;
  * **dry-brush streaks** down the length of it, in four tones of the mint,
    because a loaded brush never lays a flat colour;
  * **bristle break-up on the long edges** — short flats laid along the top
    and bottom edges and then chewed by the same displacement the body goes
    through, which is what turns a curve into hairs;
  * **three or four drips**, each one beading at the end;
  * **one or two degrees of tilt**, because nobody paints a level band.

It is never a rectangle and never a clean wave.

Same standard as `art.py` and `wall.py`, and the same three reasons: it is
crisp at any size, it raises no licensing question, and it is **byte-stable**
— every number here comes out of a generator seeded from the stroke's own
`uid`, so a rebuild writes the same bytes and a diff is a change somebody
made. `python3 strokes.py` writes a page of them to /tmp to look at.

The drawing is in a viewBox the band stretches with `preserveAspectRatio =
none`: a stroke is not a photograph, and a stroke stretched over a taller
section is a wider brush, which is the right answer.
"""
import hashlib
import random

# The paint, in the four tones a loaded brush leaves behind, and the pale
# ridge on its wet edge. These mirror --mint and its shades in site.css;
# they are here because an SVG attribute cannot read a custom property.
MINT = '#71EEB8'
MINT_HI = '#A8F7D6'      # the wet, lightly loaded hairs
MINT_PALE = '#8BF3C8'    # where the paint has thinned out
MINT_MID = '#5FD9A5'     # the body where it is fully loaded
MINT_LO = '#4FC494'      # the shadowed side of a lap mark

STREAK_TONES = (MINT_MID, MINT_HI, MINT_LO, MINT_PALE)


def _rng(uid, salt=''):
    """A generator seeded from the stroke's name, so a rebuild is a no-op.

    Python's hash() is salted per process, which would make the same band
    come out differently on every build; md5 of the uid does not.
    """
    return random.Random(int(hashlib.md5((uid + salt).encode()).hexdigest()[:12], 16))


def _n(v):
    """One decimal place, and no trailing '.0' noise in the file."""
    return f'{v:.1f}'.rstrip('0').rstrip('.')


# --------------------------------------------------------------- the outline
def _body(w, h, top, bot):
    """The stroke's own edge: a rise across the top, a sag across the bottom.

    Both ends run off the box by a twenty-fourth of its width, so the band
    is painted past its own edges the way a wall is — what the page shows is
    the middle of the stroke, not the whole of it.
    """
    x0, x1 = -w / 24, w + w / 24
    return (f'M {_n(x0)} {_n(top)} '
            f'C {_n(w * .139)} {_n(top * .667)} {_n(w * .486)} {_n(top * .8)} '
            f'{_n(x1)} {_n(top * .9)} '
            f'L {_n(x1)} {_n(h - bot)} '
            f'C {_n(w * .625)} {_n(h - bot * .74)} {_n(w * .208)} {_n(h - bot * .845)} '
            f'{_n(x0)} {_n(h - bot * 1.12)} Z')


def _defs(uid, w, h, seed, scale):
    """The displacement that makes an edge bristle, and the loaded gradient.

    The turbulence is anisotropic on purpose — 0.008 across and 0.6 down —
    so the noise is long and thin in the direction the brush travelled. That
    is the difference between an edge that looks torn and an edge that looks
    dragged.

    The gradient is the load on the brush: heavy and dark where it lands,
    even through the middle, pale where it runs out.
    """
    return (f'<defs>'
            f'<filter id="{uid}-f" x="-6%" y="-18%" width="112%" height="136%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.008 0.6" numOctaves="2" '
            f'seed="{seed}" result="t"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="t" scale="{scale}" '
            f'xChannelSelector="R" yChannelSelector="G"/>'
            f'</filter>'
            f'<linearGradient id="{uid}-g" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{MINT_MID}"/>'
            f'<stop offset=".15" stop-color="{MINT}"/>'
            f'<stop offset=".85" stop-color="{MINT}"/>'
            f'<stop offset="1" stop-color="{MINT_PALE}"/>'
            f'</linearGradient>'
            f'</defs>')


def _edge_flats(r, w, h, top, bot, n):
    """Bristle break-up: short flats laid along the two long edges.

    They are inside the filtered group, so the displacement chews them into
    the edge rather than leaving them sitting on it — a hair that took paint
    past the edge, and a gap where one did not.
    """
    out = []
    for _ in range(n):
        low = r.random() < .58                       # more of it on the sag
        y = (h - bot + r.uniform(-.14, .28) * bot) if low else (top + r.uniform(-.34, -.02) * top)
        x = r.uniform(-w / 36, w * 1.01)
        out.append(f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(r.uniform(w * .027, w * .152))}" '
                   f'height="{_n(r.uniform(2, 7))}" rx="{_n(r.uniform(1, 3.5))}" '
                   f'fill="{MINT}" opacity="{r.uniform(.5, 1):.2f}"/>')
    return ''.join(out)


def _loaded_start(r, w, h, top, bot):
    """Where the brush landed: more paint, pushed ahead of the bristles."""
    y = top + (h - bot - top) * .5
    rh = (h - bot - top) * .62
    return (f'<ellipse cx="{_n(-w / 60)}" cy="{_n(y)}" rx="{_n(w * .06)}" ry="{_n(rh)}" '
            f'fill="{MINT_MID}" opacity=".85"/>'
            + ''.join(
                f'<rect x="{_n(r.uniform(-w / 30, w * .07))}" '
                f'y="{_n(r.uniform(top + 6, h - bot - 8))}" '
                f'width="{_n(r.uniform(w * .03, w * .1))}" height="{_n(r.uniform(4, 9))}" '
                f'rx="3" fill="{MINT_LO}" opacity="{r.uniform(.3, .6):.2f}"/>'
                for _ in range(6)))


def _feathered_end(r, w, h, top, bot, n):
    """Where it ran out: separate hairs carrying on past the body."""
    return ''.join(
        f'<rect x="{_n(r.uniform(w * .92, w * .995))}" '
        f'y="{_n(r.uniform(top - 12, h - bot + 12))}" '
        f'width="{_n(r.uniform(w * .08, w * .19))}" height="{_n(r.uniform(2.2, 4.2))}" '
        f'rx="3" fill="{MINT}" opacity="{r.uniform(.4, .85):.2f}"/>'
        for _ in range(n))


def _dry_brush(r, w, h, top, bot, n):
    """The streaks down the length of it, outside the filter.

    Outside, because these are the bristles' own marks in the paint — they
    are drawn by the brush, not torn by it, and running them through the
    displacement turns a dragged line into a wobble.
    """
    return ''.join(
        f'<rect x="{_n(r.uniform(-w * .04, w * .95))}" '
        f'y="{_n(r.uniform(top + 4, h - bot - 6))}" '
        f'width="{_n(r.uniform(w * .08, w * .49))}" height="{_n(r.uniform(1.2, 4.8))}" '
        f'rx="{_n(r.uniform(.6, 2.4))}" fill="{r.choice(STREAK_TONES)}" '
        f'opacity="{r.uniform(.26, .7):.2f}"/>'
        for _ in range(n))


def _drips(r, w, h, bot, n):
    """Three or four runs off the bottom edge, each one beading at the end.

    They start inside the paint and finish outside the section, which is why
    the band does not clip: a drip that stops at the edge of its own box is
    a fringe, and a fringe is not a drip.
    """
    y = h - bot * .83
    out = []
    for _ in range(n):
        x = r.uniform(w * .1, w * .92)
        ln = r.uniform(h * .06, h * .16)
        wd = r.uniform(5, 9)
        out.append(
            f'<path d="M{_n(x)} {_n(y)} q{r.uniform(-1.5, 1.5):.1f} {_n(ln * .5)} 0 {_n(ln)}" '
            f'stroke="{MINT}" stroke-width="{_n(wd)}" stroke-linecap="round" fill="none"/>'
            f'<ellipse cx="{_n(x)}" cy="{_n(y + ln)}" rx="{_n(wd * .62)}" ry="{_n(wd * .78)}" '
            f'fill="{MINT}"/>'
            f'<ellipse cx="{_n(x - wd * .2)}" cy="{_n(y + ln - wd * .3)}" rx="{_n(wd * .15)}" '
            f'ry="{_n(wd * .26)}" fill="{MINT_HI}" opacity=".6"/>')
    return ''.join(out)


# ------------------------------------------------------------------ the band
def stroke_svg(uid, w=1440, h=720, *, top=None, bot=None, drips=4,
               streaks=70, flats=110, feather=22, cls='stroke'):
    """One swept stroke of mint, big enough to be a section's background.

    uid namespaces the filter and the gradient (two strokes share a page) and
    is the seed: the same name is the same stroke, always. w and h are the
    viewBox, not pixels — the band stretches it.
    """
    top = h * .1667 if top is None else top
    bot = h * .1611 if bot is None else bot
    r = _rng(uid)
    seed = r.randrange(2, 90)
    disp = r.uniform(18, 26)
    tilt = r.choice((-1, 1)) * r.uniform(1.0, 2.0)
    body = (f'<g filter="url(#{uid}-f)">'
            f'<path d="{_body(w, h, top, bot)}" fill="url(#{uid}-g)"/>'
            f'{_loaded_start(r, w, h, top, bot)}'
            f'{_edge_flats(r, w, h, top, bot, flats)}'
            f'{_feathered_end(r, w, h, top, bot, feather)}'
            f'</g>')
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" preserveAspectRatio="none" '
            f'aria-hidden="true" style="transform:rotate({tilt:.2f}deg) scale(1.04)">'
            f'{_defs(uid, w, h, seed, _n(disp))}'
            f'{body}'
            f'{_dry_brush(r, w, h, top, bot, streaks)}'
            f'{_drips(r, w, h, bot, drips)}'
            f'</svg>')


# ------------------------------------------------- the highlight in the hero
def highlight_svg(uid, w=1000, h=200):
    """The stroke behind the mint words of a headline.

    The same brush at a tenth of the size, so it keeps the tilt, the dragged
    edges and the streaks and loses the drips — paint on a word runs down
    the letters, and a drip there would be read as a descender.
    """
    top, bot = h * .16, h * .15
    r = _rng(uid, 'hl')
    seed = r.randrange(2, 90)
    return (f'<svg class="hl-stroke" viewBox="0 0 {w} {h}" preserveAspectRatio="none" '
            f'aria-hidden="true">'
            f'<defs>'
            f'<filter id="{uid}-hf" x="-5%" y="-22%" width="110%" height="144%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.01 0.55" numOctaves="2" '
            f'seed="{seed}" result="t"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="t" scale="14"/>'
            f'</filter>'
            f'<linearGradient id="{uid}-hg" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{MINT_MID}"/>'
            f'<stop offset=".18" stop-color="{MINT}"/>'
            f'<stop offset=".84" stop-color="{MINT}"/>'
            f'<stop offset="1" stop-color="{MINT_PALE}"/>'
            f'</linearGradient>'
            f'</defs>'
            f'<g filter="url(#{uid}-hf)">'
            f'<path d="{_body(w, h, top, bot)}" fill="url(#{uid}-hg)"/>'
            f'{_edge_flats(r, w, h, top, bot, 26)}'
            f'{_feathered_end(r, w, h, top, bot, 7)}'
            f'</g>'
            f'{_dry_brush(r, w, h, top, bot, 9)}'
            f'</svg>')


if __name__ == '__main__':
    out = ['<!doctype html><meta charset=utf-8>'
           '<style>body{background:#fff;margin:0;font:14px system-ui}'
           '.b{position:relative;height:340px;margin:0 0 40px}'
           '.b svg{position:absolute;inset:0;width:100%;height:100%}'
           '.h{position:relative;display:inline-block;margin:40px}'
           '.h svg{position:absolute;inset:-6% -2%;width:104%;height:112%;z-index:-1}'
           '.h em{font:900 64px/1 Impact;font-style:normal}</style>']
    for name in ('band-always', 'band-cta', 'band-services'):
        out.append(f'<div class="b">{stroke_svg(name)}</div>')
    out.append(f'<div class="h">{highlight_svg("hero")}<em>CAPTURE THE GAZE</em></div>')
    open('/tmp/strokes.html', 'w').write(''.join(out))
    print('wrote /tmp/strokes.html')
