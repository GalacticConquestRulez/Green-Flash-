#!/usr/bin/env python3
"""Seeded paint splatter for the Services board's diamonds.

CLAUDE.md, round three, the owner's own words: *"use some sort of diamond
concept, add his teal and a few other colours as splatter on the crisp white
cards before we add the text — let's not copy."* And, earlier: Overall
Murals dresses its cards with a film-grain speckle; Ephraim's get **paint**.

So this is paint, not grain and not clip-art, and it goes on the card first —
the type is lettered over it, the way a sign is lettered over a painted panel.
It holds to the same standard as the splat in site.js and the props in art.py
(CLAUDE.md, "Painterly, not clip-art"): every blob has a **rim** a shade darker
than its body, a **gloss** highlight where the paint is still wet, and a **bleed**
at the edge — here an SVG turbulence displacement, so the outline is a wet
edge rather than a vector curve. One drip per cluster, beading at the end.

Two rules shape where it lands:

* **Corners only.** A diamond's four points are the corners of its square, and
  the type sits in the square inscribed inside it (the middle ~71%). Clusters
  are anchored at the points, so paint is never under a word.
* **Seeded, so no two cards match and every build matches the last.** The
  generator is a small deterministic PRNG, not `random`, for the same reason
  the tags in wall.py and the strokes are seeded: the HTML has to be byte
  stable or every rebuild is a diff.

The drop-cloth palette is the round-three mint and pop plus the two the owner
asked for — "a few other colours" — a yellow and a violet. They are declared
as tokens in the stylesheet's PAGES block; the hexes are passed in from
build.py so this module never names a colour of its own.
"""

MASK = (1 << 31) - 1


class Rand:
    """A small deterministic PRNG. Park–Miller, same as the tag generator.

    `random` is not used anywhere that writes markup: it is seeded globally,
    so two modules drawing in the same build would pull from one stream and a
    change in one would move the other. A generator per splatter cannot.
    """

    def __init__(self, seed):
        self.s = (seed * 2654435761) % MASK or 1

    def next(self):
        self.s = (self.s * 48271) % MASK
        return self.s / MASK

    def f(self, lo, hi):
        return lo + (hi - lo) * self.next()

    def i(self, lo, hi):
        return int(self.f(lo, hi + 1 - 1e-9))

    def pick(self, seq):
        return seq[self.i(0, len(seq) - 1)]


def _shade(hexcol, k):
    """A darker tone of the same paint — the rim round a wet edge."""
    h = hexcol.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02X%02X%02X' % (int(r * k), int(g * k), int(b * k))


# The four corners of the card, which — because the card is turned forty-five
# degrees — are the four *points* of the diamond. The type lives in the square
# inscribed inside it, 14.6 to 85.4, so a cluster anchored in a corner and flung
# outward toward its point never crosses a word.
CORNERS = (('nw', 13, 13), ('ne', 87, 13), ('se', 87, 87), ('sw', 13, 87))

# Screen-down, in the drawing's own coordinates. The diamond is the card
# turned 45 degrees, so a run that is drawn straight down here comes out
# diagonal on the page; this is the direction that comes out vertical.
_R2 = 0.70710678
DOWN = (_R2, _R2)


def _cluster(r, colour, cx, cy, out_x, out_y):
    """One thrown cluster: flecks, streaks, a loaded blob and a run.

    The proportions matter more than the count. Paint thrown at a wall is
    mostly small: a dozen specks, a few streaks drawn out along the line of
    flight, one or two satellites with a rim, and a single body that is only
    two or three per cent of the card across. A big round dot with a thick
    straight stalk under it is a balloon, not a splatter, which is what the
    first pass of this looked like at 1440.
    """
    rim = _shade(colour, .62)
    p = []

    # Specks. A drop of paint that is still travelling is not round, so each
    # one is an ellipse turned to the line of flight.
    for _ in range(r.i(9, 15)):
        d = r.f(2, 30)
        fx = cx + out_x * d + r.f(-8, 8)
        fy = cy + out_y * d + r.f(-8, 8)
        rx = r.f(.3, 1.15)
        ang = int(r.f(0, 360))
        p.append(f'<ellipse cx="{fx:.1f}" cy="{fy:.1f}" rx="{rx:.2f}" '
                 f'ry="{rx * r.f(.45, .7):.2f}" transform="rotate({ang} {fx:.1f} {fy:.1f})" '
                 f'fill="{colour}"/>')

    # Streaks: the drops that were still moving when they hit, drawn out
    # along the throw. Two or three, never more — they are the gesture.
    ang_out = 0
    import math
    ang_out = math.degrees(math.atan2(out_y, out_x))
    for _ in range(r.i(2, 3)):
        d = r.f(4, 22)
        sx = cx + out_x * d + r.f(-5, 5)
        sy = cy + out_y * d + r.f(-5, 5)
        ln = r.f(1.6, 4.2)
        p.append(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{ln:.2f}" '
                 f'ry="{ln * r.f(.16, .3):.2f}" '
                 f'transform="rotate({ang_out + r.f(-22, 22):.0f} {sx:.1f} {sy:.1f})" '
                 f'fill="{colour}"/>')

    # One or two satellites, big enough to carry their own rim and gloss.
    for _ in range(r.i(1, 2)):
        d = r.f(4, 13)
        sx = cx + out_x * d + r.f(-5, 5)
        sy = cy + out_y * d + r.f(-5, 5)
        rx = r.f(.9, 1.7)
        ry = rx * r.f(.66, .88)
        p.append(f'<ellipse cx="{sx:.1f}" cy="{sy + .16:.1f}" rx="{rx + .14:.2f}" '
                 f'ry="{ry + .14:.2f}" fill="{rim}"/>')
        p.append(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{colour}"/>')
        p.append(f'<ellipse cx="{sx - rx * .3:.1f}" cy="{sy - ry * .34:.1f}" '
                 f'rx="{rx * .28:.2f}" ry="{ry * .22:.2f}" fill="#fff" opacity=".5"/>')

    # The body: the paint that actually landed. Rim under it, gloss on it.
    bx, by = cx + r.f(-2, 2), cy + r.f(-2, 2)
    brx = r.f(1.5, 2.6)
    bry = brx * r.f(.78, 1.06)
    p.append(f'<ellipse cx="{bx:.1f}" cy="{by + .22:.1f}" rx="{brx + .22:.2f}" '
             f'ry="{bry + .22:.2f}" fill="{rim}"/>')
    p.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{brx:.2f}" ry="{bry:.2f}" fill="{colour}"/>')
    p.append(f'<ellipse cx="{bx - brx * .32:.1f}" cy="{by - bry * .36:.1f}" '
             f'rx="{brx * .3:.2f}" ry="{bry * .2:.2f}" fill="#fff" opacity=".55"/>')

    # And the run. Paint goes down the *card*, never along the flight line:
    # gravity does not care which way it was thrown. The card is turned
    # forty-five degrees on the page, so screen-down is (1,1) over root two
    # in this drawing's own coordinates — DOWN below. Get that wrong and
    # every drip becomes a diagonal stalk with a bead on the end, which is a
    # balloon on a stick and not a run.
    run = r.f(9, 24)
    wob = r.f(-1.8, 1.8)
    dx, dy = DOWN
    sx0, sy0 = bx + dx * bry * .72, by + dy * bry * .72
    # the wobble is across the run, so it is perpendicular to DOWN
    p.append(f'<path d="M{sx0:.1f} {sy0:.1f} q{dx * run * .5 + dy * wob:.1f} '
             f'{dy * run * .5 - dx * wob:.1f} {dx * run:.1f} {dy * run:.1f}" '
             f'stroke="{colour}" stroke-width="{brx * .3:.2f}" '
             f'stroke-linecap="round" fill="none" opacity=".92"/>')
    bead = brx * r.f(.26, .4)
    p.append(f'<ellipse cx="{sx0 + dx * run:.1f}" cy="{sy0 + dy * run:.1f}" '
             f'rx="{bead:.2f}" ry="{bead * 1.25:.2f}" fill="{colour}" '
             f'transform="rotate(-45 {sx0 + dx * run:.1f} {sy0 + dy * run:.1f})"/>')
    return ''.join(p)


def splatter_svg(uid, colour, seed, n=None):
    """The splatter for one card.

    `colour` is a single hex or a sequence of them — the drop-cloth palette,
    so a card carries two or three paints rather than one. `seed` decides
    everything else: which corners are hit, how hard, and where it runs.
    """
    cols = [colour] if isinstance(colour, str) else list(colour)
    r = Rand(seed)
    corners = list(CORNERS)
    # Two or three clusters, on different points, so a card is never loaded
    # all down one side.
    k = n if n is not None else r.i(2, 3)
    chosen = []
    for _ in range(min(k, len(corners))):
        chosen.append(corners.pop(r.i(0, len(corners) - 1)))

    body = []
    for idx, (side, cx, cy) in enumerate(chosen):
        col = cols[idx % len(cols)]
        # Flung outward from the card's corner, toward the diamond's point.
        ox, oy = {'nw': (-_R2, -_R2), 'ne': (_R2, -_R2),
                  'se': (_R2, _R2), 'sw': (-_R2, _R2)}[side]
        ox += r.f(-.5, .5)
        oy += r.f(-.5, .5)
        body.append(_cluster(r, col, cx, cy, ox, oy))

    fid = f'spf-{uid}'
    return (
        f'<svg class="spat" viewBox="0 0 100 100" aria-hidden="true" focusable="false">'
        f'<defs><filter id="{fid}" x="-14%" y="-14%" width="128%" height="128%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="2" '
        f'seed="{seed % 97}" result="t"/>'
        f'<feDisplacementMap in="SourceGraphic" in2="t" scale="1.6" '
        f'xChannelSelector="R" yChannelSelector="G"/></filter></defs>'
        f'<g filter="url(#{fid})">{"".join(body)}</g></svg>')
