#!/usr/bin/env python3
"""art.py — the painter's props, drawn once, reused everywhere.

Three pieces of kit for the motion vocabulary: the can (concept 1, tip it),
the roller (concept 2, roll it in) and the brush (concepts 3 and 4, on the
wall / on the rule). Each is a function returning an inline <svg> at a 200 x 200
viewBox with a transparent background, every id namespaced by `uid` so two
props can share a page.

Everything is drawn here rather than in an editor for the same reason as
wall.py: crisp at any size, no licensing question, byte-stable output
(the bristle and nap fibres come from a seeded generator, never random at
build time), and a change is a diff someone can read.

The owner's brief (2026-09-19): "make each asset look the best it can
possibly look, extra time on brushes and effects". So the bristles are
hundreds of individual hairs, the nap is fibre by fibre, paint has a
meniscus and a gloss, and the metal has reflections. Nothing is a flat shape.
"""
import random

MINT, MINT_HI, MINT_LO, MINT_DEEP = '#71EEB8', '#A8F7D6', '#4FC494', '#2E7D5B'
INK = '#0A0A0B'


def _rng(seed):
    return random.Random(seed)


# ---------------------------------------------------------------- shared defs
def _defs(uid):
    return f'''<defs>
<linearGradient id="{uid}-steel" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#5c5f65"/><stop offset=".14" stop-color="#c9ccd2"/>
 <stop offset=".34" stop-color="#7d8188"/><stop offset=".5" stop-color="#eef0f3"/>
 <stop offset=".68" stop-color="#8a8e95"/><stop offset=".86" stop-color="#d7dadf"/>
 <stop offset="1" stop-color="#43464b"/></linearGradient>
<linearGradient id="{uid}-steelv" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#eef0f3"/><stop offset=".5" stop-color="#8a8e95"/><stop offset="1" stop-color="#43464b"/></linearGradient>
<radialGradient id="{uid}-paint" cx=".38" cy=".3" r=".9">
 <stop offset="0" stop-color="{MINT_HI}"/><stop offset=".45" stop-color="{MINT}"/><stop offset="1" stop-color="{MINT_DEEP}"/></radialGradient>
<linearGradient id="{uid}-wet" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="{MINT_HI}"/><stop offset=".35" stop-color="{MINT}"/><stop offset="1" stop-color="{MINT_DEEP}"/></linearGradient>
<linearGradient id="{uid}-gloss" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="{uid}-shadow" cx=".5" cy=".5" r=".5">
 <stop offset="0" stop-color="#000" stop-opacity=".7"/><stop offset=".7" stop-color="#000" stop-opacity=".25"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<filter id="{uid}-grain" x="0" y="0" width="100%" height="100%">
 <feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="4" result="n"/>
 <feColorMatrix in="n" type="saturate" values="0" result="g"/>
 <feComponentTransfer in="g" result="c"><feFuncA type="table" tableValues="0 .22"/></feComponentTransfer>
 <feComposite in="c" in2="SourceGraphic" operator="in"/></filter>
<filter id="{uid}-soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.2"/></filter>
<filter id="{uid}-blur6" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="{uid}-drop" x="-20%" y="-20%" width="140%" height="160%">
 <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity=".5"/></filter>
</defs>'''


def _drip(x, y, length, width, color, seed=1):
    """A run of paint: a tapering stroke that swells into a drop at the end."""
    r = _rng(seed)
    wobble = r.uniform(-1.5, 1.5)
    return (f'<path d="M{x} {y} q{wobble} {length*.55:.1f} 0 {length}" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" fill="none"/>'
            f'<ellipse cx="{x}" cy="{y+length:.1f}" rx="{width*.62:.1f}" ry="{width*.78:.1f}" fill="{color}"/>'
            f'<ellipse cx="{x-width*.18:.1f}" cy="{y+length-width*.3:.1f}" rx="{width*.16:.1f}" ry="{width*.28:.1f}" fill="#fff" opacity=".45"/>')


# ---------------------------------------------------------------- the can
def can_svg(uid='can'):
    d = _defs(uid)
    label = f'''<linearGradient id="{uid}-label" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#b9b6ae"/><stop offset=".16" stop-color="#f4f3ef"/>
 <stop offset=".5" stop-color="#e9e7e2"/><stop offset=".86" stop-color="#d0cdc6"/><stop offset="1" stop-color="#9f9c95"/></linearGradient>
<clipPath id="{uid}-labelclip"><path d="M45 90 L48 158 Q100 169 152 158 L155 90 Q100 101 45 90 Z"/></clipPath>'''
    d = d.replace('</defs>', label + '</defs>')
    body = f'''
<ellipse cx="100" cy="184" rx="66" ry="8" fill="url(#{uid}-shadow)"/>
<!-- tin body: a cylinder read through one vertical gradient -->
<path d="M42 62 L46 178 Q100 190 154 178 L158 62 Z" fill="url(#{uid}-steel)"/>
<path d="M42 62 L46 178 Q100 190 154 178 L158 62 Z" fill="#000" opacity=".18" filter="url(#{uid}-grain)"/>
<!-- rolled ribs -->
<g fill="none" stroke-linecap="round">
 <path d="M43.5 80 Q100 92 156.5 80" stroke="#1f2023" stroke-width="2.6" opacity=".6"/>
 <path d="M43.5 78.6 Q100 90.6 156.5 78.6" stroke="#fff" stroke-width="1" opacity=".35"/>
 <path d="M45.4 166 Q100 178 154.6 166" stroke="#1f2023" stroke-width="2.6" opacity=".6"/>
 <path d="M45.4 164.6 Q100 176.6 154.6 164.6" stroke="#fff" stroke-width="1" opacity=".3"/>
</g>
<!-- a dent, because it has been on a lift -->
<path d="M134 118 q9 16 -1 32" stroke="#1f2023" stroke-width="3.2" fill="none" opacity=".45" filter="url(#{uid}-soft)"/>
<path d="M136 120 q6 14 0 26" stroke="#fff" stroke-width="1.2" fill="none" opacity=".25"/>
<!-- label -->
<path d="M45 90 L48 158 Q100 169 152 158 L155 90 Q100 101 45 90 Z" fill="url(#{uid}-label)"/>
<path d="M45 90 L48 158 Q100 169 152 158 L155 90 Q100 101 45 90 Z" fill="#000" opacity=".5" filter="url(#{uid}-grain)"/>
<g clip-path="url(#{uid}-labelclip)">
 <rect x="45" y="93" width="110" height="2" fill="{INK}" opacity=".85"/>
 <text x="100" y="121" text-anchor="middle" font-family="Archivo,Inter,Arial,sans-serif" font-weight="900" font-size="13" letter-spacing=".4" fill="{INK}">OPEN AIR</text>
 <text x="100" y="131.5" text-anchor="middle" font-family="Archivo,Inter,Arial,sans-serif" font-weight="700" font-size="5" letter-spacing="1.3" fill="{INK}">GALLERY · WALL PAINT</text>
 <rect x="72" y="138" width="56" height="10" rx="1" fill="{MINT}"/>
 <text x="100" y="145.4" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-weight="700" font-size="5.6" letter-spacing="1.2" fill="{INK}">MINT · NO. 71</text>
 <rect x="45" y="156" width="110" height="1.4" fill="{INK}" opacity=".6"/>
 <!-- a wear scuff on the label -->
 <path d="M52 120 q10 -6 22 2" stroke="#fff" stroke-width="3" opacity=".35" stroke-linecap="round" fill="none" filter="url(#{uid}-soft)"/>
</g>
<!-- rim: lip with thickness, then the dark inside, then the paint with a meniscus -->
<path d="M39 62 Q100 76 161 62 Q100 48 39 62 Z" fill="url(#{uid}-steelv)"/>
<path d="M39 62 Q100 76 161 62 L161 65 Q100 79 39 65 Z" fill="#3a3c40"/>
<path d="M46 62 Q100 72 154 62 Q100 52 46 62 Z" fill="#17181a"/>
<path d="M51 62 Q100 70.5 149 62 Q100 54 51 62 Z" fill="url(#{uid}-paint)"/>
<path d="M58 60.5 Q100 55.5 142 60.5 Q100 57.5 58 60.5 Z" fill="#fff" opacity=".35"/>
<!-- skin of dried paint over the lip, and two runs -->
<path d="M57 62 q7 -3 14 0 q6 3 13 -1 q8 -4 16 0 q6 3 13 -1 q7 -3 14 1" stroke="{MINT}" stroke-width="3.4" fill="none" stroke-linecap="round" opacity=".95"/>
<path d="M57 62 q7 -3 14 0 q6 3 13 -1 q8 -4 16 0 q6 3 13 -1 q7 -3 14 1" stroke="#fff" stroke-width="1" fill="none" stroke-linecap="round" opacity=".35" transform="translate(0,-1.2)"/>
{_drip(139, 64, 46, 5.2, MINT, 2)}
{_drip(66, 65, 22, 3.8, MINT, 3)}
{_drip(104, 66, 9, 3, MINT, 4)}
<!-- specular stripe down the tin -->
<path d="M66 84 L69 176" stroke="#fff" stroke-width="5" opacity=".14" stroke-linecap="round" filter="url(#{uid}-soft)"/>
<!-- wire handle with its bend and lugs -->
<path d="M41 63 Q100 -10 159 63" stroke="#3a3c40" stroke-width="4.4" fill="none" stroke-linecap="round"/>
<path d="M41 63 Q100 -10 159 63" stroke="url(#{uid}-steel)" stroke-width="2.8" fill="none" stroke-linecap="round"/>
<path d="M41 63 Q100 -10 159 63" stroke="#fff" stroke-width=".9" fill="none" stroke-linecap="round" opacity=".5" transform="translate(-.6,-.8)"/>
<rect x="91" y="13.5" width="18" height="8" rx="3" fill="#2b2c2f"/><rect x="92" y="14.5" width="16" height="3" rx="1.5" fill="#55575c"/>
<circle cx="41.5" cy="63" r="2.6" fill="#2b2c2f"/><circle cx="158.5" cy="63" r="2.6" fill="#2b2c2f"/>'''
    return (f'<svg class="prop prop-can" viewBox="0 0 200 200" width="200" height="200" aria-hidden="true" focusable="false">'
            f'{d}{body}</svg>')


# ---------------------------------------------------------------- the roller
def roller_svg(uid='roller'):
    r = _rng(11)
    # The sleeve, drawn axis-aligned then rotated: nap fibres along both long
    # edges so the silhouette is furry, the wet half loaded with mint.
    fibres = []
    for i in range(520):
        x = 21 + r.uniform(0, 138)
        top = r.random() < .5
        y = 96.5 if top else 139.5
        ln = r.uniform(.8, 2.6)
        wet = x < 100
        col = (MINT if wet else '#e8e6df') if r.random() < .75 else (MINT_LO if wet else '#b9b6ad')
        dx = r.uniform(-1.2, 1.2)
        fibres.append(f'<path d="M{x:.1f} {y} l{dx:.1f} {-ln if top else ln:.1f}" stroke="{col}" stroke-width="{r.uniform(.45,.8):.2f}" stroke-linecap="round" opacity=".9"/>')
    texture = []
    for i in range(260):
        x = 24 + r.uniform(0, 132); y = 99 + r.uniform(0, 38)
        wet = x < 100
        col = (MINT_LO if r.random() < .6 else MINT_HI) if wet else ('#d3d0c8' if r.random() < .6 else '#fff')
        texture.append(f'<path d="M{x:.1f} {y:.1f} l{r.uniform(-2,2):.1f} {r.uniform(-1.5,1.5):.1f}" stroke="{col}" stroke-width="{r.uniform(.5,.9):.2f}" stroke-linecap="round" opacity=".7"/>')
    d = _defs('roller' if uid == 'roller' else uid)
    d = d.replace('</defs>', f'''<linearGradient id="{uid}-nap" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#fbfaf6"/><stop offset=".55" stop-color="#d6d3cb"/><stop offset="1" stop-color="#8c8a82"/></linearGradient>
<linearGradient id="{uid}-grip" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#8f3a12"/><stop offset=".35" stop-color="#f08a45"/><stop offset=".55" stop-color="#ffb27c"/><stop offset="1" stop-color="#7a2f0d"/></linearGradient>
<clipPath id="{uid}-sleeve"><rect x="20" y="96" width="140" height="44" rx="21"/></clipPath></defs>''')
    body = f'''
<ellipse cx="84" cy="182" rx="74" ry="7" fill="url(#{uid}-shadow)"/>
<!-- the pass it just made, behind everything -->
<path d="M14 166 q64 -44 138 -30" stroke="{MINT}" stroke-width="34" fill="none" stroke-linecap="round" opacity=".22"/>
<path d="M14 166 q64 -44 138 -30" stroke="{MINT_HI}" stroke-width="2" fill="none" stroke-linecap="round" opacity=".25" transform="translate(0,-12)"/>
{_drip(30, 170, 16, 4.4, MINT, 5)}{_drip(48, 173, 9, 3.4, MINT, 6)}
<g transform="rotate(-28 90 118)">
 <!-- sleeve body -->
 <rect x="20" y="96" width="140" height="44" rx="21" fill="url(#{uid}-nap)"/>
 <g clip-path="url(#{uid}-sleeve)">
  <rect x="20" y="96" width="82" height="44" fill="url(#{uid}-wet)"/>
  <!-- ragged wet edge -->
  <path d="M100 96 q4 6 -2 11 q6 5 0 11 q5 6 -1 11 q4 5 3 11 L96 140 L96 96 Z" fill="{MINT}"/>
  <path d="M102 96 q-5 6 1 11 q-6 5 0 11 q-5 6 1 11 q-4 5 -2 11 L100 140 L100 96 Z" fill="{MINT_LO}" opacity=".8"/>
  {''.join(texture)}
  <!-- highlight along the top of the cylinder, shade along the bottom -->
  <rect x="20" y="96" width="140" height="14" fill="url(#{uid}-gloss)"/>
  <rect x="20" y="128" width="140" height="12" fill="#000" opacity=".22"/>
 </g>
 {''.join(fibres)}
 <!-- end cap and the cage -->
 <ellipse cx="160" cy="118" rx="7.5" ry="22" fill="#d9d6ce"/><ellipse cx="160" cy="118" rx="7.5" ry="22" fill="#000" opacity=".25" filter="url(#{uid}-grain)"/>
 <ellipse cx="160" cy="118" rx="4.2" ry="15" fill="#3a3a37"/><ellipse cx="160" cy="118" rx="2" ry="8" fill="#141413"/>
 <path d="M160 118 h16 q12 0 12 -12 v-58" stroke="#2a2b2e" stroke-width="7.5" fill="none" stroke-linecap="round"/>
 <path d="M160 118 h16 q12 0 12 -12 v-58" stroke="url(#{uid}-steel)" stroke-width="5.4" fill="none" stroke-linecap="round"/>
 <path d="M160 118 h16 q12 0 12 -12 v-58" stroke="#fff" stroke-width="1.2" fill="none" stroke-linecap="round" opacity=".55" transform="translate(-1.2,-1)"/>
 <!-- the grip: shaped, ribbed, with a hang hole -->
 <path d="M176 -2 q12 -4 24 0 l2 60 q-14 6 -28 0 z" fill="url(#{uid}-grip)"/>
 <g stroke="#000" stroke-width="1.2" opacity=".28"><path d="M178 12 h20 M178 22 h20 M178 32 h20 M178 42 h20"/></g>
 <path d="M181 4 v48" stroke="#fff" stroke-width="1.6" opacity=".35" stroke-linecap="round"/>
 <circle cx="188" cy="6" r="2.4" fill="{INK}" opacity=".8"/>
</g>'''
    return (f'<svg class="prop prop-roller" viewBox="0 0 200 200" width="200" height="200" aria-hidden="true" focusable="false">'
            f'{d}{body}</svg>')


# ---------------------------------------------------------------- the brush
def brush_svg(uid='brush', loaded=True):
    r = _rng(7)
    # Bristles: ~220 hairs from the ferrule down, each a slightly curved path,
    # natural tan up top, mint from the load line down, flagged (split) tips.
    hairs = []
    for i in range(220):
        x0 = 76 + r.uniform(0, 48)
        curve = r.uniform(-4, 4) + (x0 - 100) * .2
        ln = r.uniform(58, 70)
        w = r.uniform(.55, 1.05)
        tan = r.choice(['#e3d2ab', '#c9b07e', '#b0945e', '#f0e3c4'])
        # the natural part
        hairs.append(f'<path d="M{x0:.1f} 106 q{curve*.5:.1f} {ln*.55:.1f} {curve:.1f} {ln:.1f}" stroke="{tan}" stroke-width="{w:.2f}" stroke-linecap="round" fill="none"/>')
        if loaded:
            # the mint load from ~45% down, slightly heavier
            col = r.choice([MINT, MINT, MINT_LO, MINT_HI])
            hairs.append(f'<path d="M{x0+curve*.45:.1f} {106+ln*.45:.1f} q{curve*.3:.1f} {ln*.3:.1f} {curve*.55:.1f} {ln*.55:.1f}" stroke="{col}" stroke-width="{w*1.25:.2f}" stroke-linecap="round" fill="none"/>')
        # flagged tip
        if r.random() < .35:
            hairs.append(f'<path d="M{x0+curve:.1f} {106+ln:.1f} l{r.uniform(-1.5,1.5):.1f} {r.uniform(2,4.5):.1f}" stroke="{MINT_LO if loaded else tan}" stroke-width="{w*.6:.2f}" stroke-linecap="round"/>')
    d = _defs(uid)
    d = d.replace('</defs>', f'''<linearGradient id="{uid}-wood" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#5a3316"/><stop offset=".22" stop-color="#b5732f"/><stop offset=".45" stop-color="#e9b374"/>
 <stop offset=".62" stop-color="#d0924e"/><stop offset=".85" stop-color="#8a4f1f"/><stop offset="1" stop-color="#4a2a10"/></linearGradient>
<linearGradient id="{uid}-ferrule" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#6a6d73"/><stop offset=".3" stop-color="#d9dce1"/><stop offset=".5" stop-color="#f3f4f6"/><stop offset=".7" stop-color="#a5a9b0"/><stop offset="1" stop-color="#4b4e53"/></linearGradient>
<clipPath id="{uid}-handleclip"><path d="M84 6 q16 -7 32 0 l5 74 q-21 7 -42 0 z"/></clipPath></defs>''')
    grain = ''.join(f'<path d="M{86+i*5.5:.1f} 8 q{r.uniform(-2,2):.1f} 36 {r.uniform(-1,1):.1f} 70" stroke="#3a1e08" stroke-width="{r.uniform(.4,.9):.2f}" fill="none" opacity="{r.uniform(.18,.4):.2f}"/>' for i in range(6))
    stroke_hairs = ''.join(
        f'<path d="M{30+r.uniform(0,6):.1f} {146+i*1.9:.1f} q40 -{10+r.uniform(0,4):.1f} 88 {r.uniform(1,5):.1f} q30 8 62 {r.uniform(-3,3):.1f}" '
        f'stroke="{r.choice([MINT, MINT, MINT_LO, MINT_HI])}" stroke-width="{r.uniform(.8,2.2):.2f}" fill="none" stroke-linecap="round" opacity="{r.uniform(.6,1):.2f}"/>'
        for i in range(12))
    body = f'''
<ellipse cx="98" cy="186" rx="66" ry="7" fill="url(#{uid}-shadow)"/>
<!-- the stroke it just laid, fibre by fibre, with a wet gloss -->
<path d="M32 158 q42 -14 90 2 q30 10 62 -2" stroke="{MINT}" stroke-width="20" fill="none" stroke-linecap="round" opacity=".9"/>
{stroke_hairs}
<path d="M40 151 q42 -12 84 2" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" opacity=".3"/>
{_drip(46, 166, 15, 4, MINT, 8)}{_drip(120, 167, 9, 3.2, MINT, 9)}
<g transform="rotate(-38 100 100)">
 <!-- handle -->
 <path d="M84 6 q16 -7 32 0 l5 74 q-21 7 -42 0 z" fill="url(#{uid}-wood)"/>
 <g clip-path="url(#{uid}-handleclip)">{grain}
  <path d="M90 10 q2 36 4 68" stroke="#fff" stroke-width="2.4" opacity=".3" stroke-linecap="round" fill="none"/></g>
 <circle cx="100" cy="16" r="3" fill="{INK}"/><circle cx="100" cy="16" r="3" fill="none" stroke="#fff" stroke-width=".6" opacity=".5"/>
 <!-- ferrule with crimps and rivets -->
 <path d="M73 78 h54 v30 h-54 z" fill="url(#{uid}-ferrule)"/>
 <g stroke="#2b2d31" stroke-width="1" opacity=".55"><path d="M73 84 h54 M73 102 h54"/></g>
 <g stroke="#fff" stroke-width=".8" opacity=".5"><path d="M73 85.2 h54 M73 103.2 h54"/></g>
 <circle cx="83" cy="93" r="2.4" fill="#2b2d31"/><circle cx="82.4" cy="92.4" r="1" fill="#c9ccd2"/>
 <circle cx="117" cy="93" r="2.4" fill="#2b2d31"/><circle cx="116.4" cy="92.4" r="1" fill="#c9ccd2"/>
 <!-- the underbody of the bristles, so the mass reads before the hairs -->
 <path d="M76 106 h48 l6 62 q-30 12 -60 0 z" fill="#8d7a52" opacity=".9"/>
 <path d="M78 136 l44 0 l6 32 q-28 12 -56 0 z" fill="{MINT_DEEP}"/>
 <g fill="none" stroke-linecap="round">{''.join(hairs)}</g>
 <path d="M74 106 h52 v9 h-52 z" fill="#000" opacity=".28" filter="url(#{uid}-soft)"/>
 <!-- gloss on the wet load -->
 <path d="M86 140 q14 -4 28 0" stroke="#fff" stroke-width="3" opacity=".22" stroke-linecap="round" fill="none" filter="url(#{uid}-soft)"/>
 <!-- a bead of paint about to drop -->
 <ellipse cx="112" cy="178" rx="2.6" ry="3.4" fill="{MINT}"/><circle cx="111.2" cy="176.8" r=".8" fill="#fff" opacity=".7"/>
</g>'''
    return (f'<svg class="prop prop-brush" viewBox="0 0 200 200" width="200" height="200" aria-hidden="true" focusable="false">'
            f'{d}{body}</svg>')


if __name__ == '__main__':
    import sys
    html = f'''<!doctype html><meta charset=utf-8><style>
body{{margin:0;background:{INK};display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;padding:40px;height:900px;box-sizing:border-box}}
.cell{{display:flex;align-items:center;justify-content:center;border:1px solid rgba(244,243,239,.1)}} svg{{width:380px;height:380px;overflow:visible}}
</style><div class="cell">{can_svg()}</div><div class="cell">{roller_svg()}</div><div class="cell">{brush_svg()}</div>'''
    out = sys.argv[1] if len(sys.argv) > 1 else 'research/props.html'
    open(out, 'w').write(html); print('wrote', out, len(html), 'bytes')


# ------------------------------------------------- the brush that rides a rule
def brush_rule_svg(uid='brushrule', loaded=True):
    """The same brush, laid over to paint a horizontal line left to right.

    `brush_svg()` is the upright display piece: 200 x 200, the brush stood on
    end with the stroke it just laid underneath it. A brush riding a rule is a
    different shape — it has to meet the line at a working angle, put its
    bristles *on* the line, and carry nothing below the line to be clipped —
    so this is that brush, same wood, same ferrule, same loaded bristles,
    turned 48 degrees and anchored on the point where the leading hairs touch.

    The contact point is at (52, 166) of the 200 x 200 viewBox — 26% across and
    83% down — and site.css positions the element by those two fractions so the
    bristles sit on the rule whatever size the brush is drawn at. Everything
    else is above and behind that point: the handle leans forward over the wet
    end of the rule, the hairs drag back over the paint just laid. The hair
    count is lower than the display piece's 220 because this is drawn at 44-64
    px and 90 hairs is already more than a retina screen can resolve there.
    """
    r = _rng(11)
    hairs = []
    for i in range(70):
        x0 = 76 + r.uniform(0, 48)
        curve = r.uniform(-4, 4) + (x0 - 100) * .2
        ln = r.uniform(58, 70)
        w = r.uniform(.8, 1.5)
        tan = r.choice(['#e3d2ab', '#c9b07e', '#b0945e', '#f0e3c4'])
        hairs.append(f'<path d="M{x0:.0f} 106q{curve*.5:.0f} {ln*.55:.0f} {curve:.0f} {ln:.0f}" stroke="{tan}" stroke-width="{w:.1f}"/>')
        if loaded:
            col = r.choice([MINT, MINT, MINT_LO, MINT_HI])
            hairs.append(f'<path d="M{x0+curve*.45:.0f} {106+ln*.45:.0f}q{curve*.3:.0f} {ln*.3:.0f} {curve*.55:.0f} {ln*.55:.0f}" stroke="{col}" stroke-width="{w*1.3:.1f}"/>')
        if r.random() < .3:
            hairs.append(f'<path d="M{x0+curve:.0f} {106+ln:.0f}l{r.uniform(-1.5,1.5):.0f} {r.uniform(2,3.5):.0f}" stroke="{MINT_LO if loaded else tan}" stroke-width="{w*.6:.1f}"/>')
    grain = ''.join(f'<path d="M{86+i*5.5:.1f} 8 q{r.uniform(-2,2):.1f} 36 {r.uniform(-1,1):.1f} 70" stroke="#3a1e08" stroke-width="{r.uniform(.4,.9):.2f}" fill="none" opacity="{r.uniform(.18,.4):.2f}"/>' for i in range(6))
    # The hairs that are actually touching: after the turn they lie along the
    # rule, dragging back over the paint just laid.
    drag = ''.join(
        f'<path d="M{50-r.uniform(0,3):.0f} {163+i*1.5:.0f}q-{12+r.uniform(0,10):.0f} {r.uniform(-1.2,1.2):.0f} -{22+r.uniform(0,16):.0f} {r.uniform(-1,1):.0f}" '
        f'stroke="{r.choice([MINT, MINT, MINT_HI, MINT_LO])}" stroke-width="{r.uniform(.5,1.2):.1f}" opacity="{r.uniform(.35,.85):.1f}"/>'
        for i in range(7))
    defs = f'''<defs>
<linearGradient id="{uid}-wood" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#5a3316"/><stop offset=".22" stop-color="#b5732f"/><stop offset=".45" stop-color="#e9b374"/>
 <stop offset=".62" stop-color="#d0924e"/><stop offset=".85" stop-color="#8a4f1f"/><stop offset="1" stop-color="#4a2a10"/></linearGradient>
<linearGradient id="{uid}-ferrule" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#6a6d73"/><stop offset=".3" stop-color="#d9dce1"/><stop offset=".5" stop-color="#f3f4f6"/><stop offset=".7" stop-color="#a5a9b0"/><stop offset="1" stop-color="#4b4e53"/></linearGradient>
<clipPath id="{uid}-handleclip"><path d="M84 6 q16 -7 32 0 l5 74 q-21 7 -42 0 z"/></clipPath>
<filter id="{uid}-soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.2"/></filter>
</defs>'''
    body = f'''
<g transform="translate(-76 -8) rotate(48 128 174)">
 <path d="M84 6 q16 -7 32 0 l5 74 q-21 7 -42 0 z" fill="url(#{uid}-wood)"/>
 <g clip-path="url(#{uid}-handleclip)">{grain}
  <path d="M90 10 q2 36 4 68" stroke="#fff" stroke-width="2.4" opacity=".3" stroke-linecap="round" fill="none"/></g>
 <circle cx="100" cy="16" r="3" fill="{INK}"/><circle cx="100" cy="16" r="3" fill="none" stroke="#fff" stroke-width=".6" opacity=".5"/>
 <path d="M73 78 h54 v30 h-54 z" fill="url(#{uid}-ferrule)"/>
 <g stroke="#2b2d31" stroke-width="1" opacity=".55"><path d="M73 84 h54 M73 102 h54"/></g>
 <g stroke="#fff" stroke-width=".8" opacity=".5"><path d="M73 85.2 h54 M73 103.2 h54"/></g>
 <circle cx="83" cy="93" r="2.4" fill="#2b2d31"/><circle cx="82.4" cy="92.4" r="1" fill="#c9ccd2"/>
 <circle cx="117" cy="93" r="2.4" fill="#2b2d31"/><circle cx="116.4" cy="92.4" r="1" fill="#c9ccd2"/>
 <path d="M76 106 h48 l6 62 q-30 12 -60 0 z" fill="#8d7a52" opacity=".9"/>
 <path d="M78 136 l44 0 l6 32 q-28 12 -56 0 z" fill="{MINT_DEEP}"/>
 <g fill="none" stroke-linecap="round">{''.join(hairs)}</g>
 <path d="M74 106 h52 v9 h-52 z" fill="#000" opacity=".28" filter="url(#{uid}-soft)"/>
 <path d="M86 140 q14 -4 28 0" stroke="#fff" stroke-width="3" opacity=".22" stroke-linecap="round" fill="none" filter="url(#{uid}-soft)"/>
</g>
<g fill="none" stroke-linecap="round">{drag}</g>
<ellipse cx="50" cy="166" rx="4.2" ry="2.4" fill="{MINT_HI}" opacity=".55"/>'''
    return (f'<svg class="prop prop-brush-rule" viewBox="0 0 200 200" width="200" height="200" aria-hidden="true" focusable="false">'
            f'{defs}{body}</svg>')


# ------------------------------------------- the roller that rides a wet edge
def roller_pass_svg(uid='rollerpass'):
    """The same roller, stood up to ride a wet edge left to right.

    `roller_svg()` is the upright display piece: 200 x 200, the roller lying
    over at 28 degrees with the pass it has just made, its drips and its
    shadow underneath it. A roller mid-pass on a wall is a different shape —
    the sleeve stands across the direction of travel, the nap has to sit *on*
    the wet edge, and nothing may hang below the art to be clipped — so this
    is that roller, same nap, same mint load, same cage and grip, stood up
    74 degrees and anchored on the point where the nap meets the wall.

    Two things change besides the angle, and neither is a redraw. The load
    line moves down the sleeve (WET) because this roller is in the middle of
    a pass rather than sitting on a bench, so all but the last inch of it is
    carrying paint; and the fibre and texture counts come down from 520 and
    260, because this is drawn at 40-76 px — for the cursor, and for the copy
    riding the edge inside a card — where a hundred hairs is already more
    than a retina screen can resolve.

    The contact point is at (139.6, 133.8) of the 200 x 200 viewBox — 69.8%
    across and 66.9% down — and site.css positions the element by those two
    fractions, so the nap sits on the wet edge whatever size it is drawn at.
    Everything else is behind that point: the arm and the grip trail back
    over the paint just laid, the way a right hand holds a roller going right.
    """
    r = _rng(11)
    WET = 140          # the load line, most of the way up the sleeve
    fibres = []
    for i in range(100):
        x = 21 + r.uniform(0, 138)
        top = r.random() < .5
        y = 96.5 if top else 139.5
        ln = r.uniform(.8, 2.6)
        wet = x < WET
        col = (MINT if wet else '#e8e6df') if r.random() < .75 else (MINT_LO if wet else '#b9b6ad')
        dx = r.uniform(-1.2, 1.2)
        fibres.append(f'<path d="M{x:.0f} {y} l{dx:.0f} {-ln if top else ln:.0f}" stroke="{col}" stroke-width="{r.uniform(.45,.8):.1f}"/>')
    texture = []
    for i in range(55):
        x = 24 + r.uniform(0, 132); y = 99 + r.uniform(0, 38)
        wet = x < WET
        col = (MINT_LO if r.random() < .6 else MINT_HI) if wet else ('#d3d0c8' if r.random() < .6 else '#fff')
        texture.append(f'<path d="M{x:.0f} {y:.0f} l{r.uniform(-2,2):.0f} {r.uniform(-1.5,1.5):.0f}" stroke="{col}" stroke-width="{r.uniform(.5,.9):.1f}"/>')
    defs = f'''<defs>
<linearGradient id="{uid}-nap" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#fbfaf6"/><stop offset=".55" stop-color="#d6d3cb"/><stop offset="1" stop-color="#8c8a82"/></linearGradient>
<linearGradient id="{uid}-grip" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#8f3a12"/><stop offset=".35" stop-color="#f08a45"/><stop offset=".55" stop-color="#ffb27c"/><stop offset="1" stop-color="#7a2f0d"/></linearGradient>
<linearGradient id="{uid}-wet" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="{MINT_HI}"/><stop offset=".35" stop-color="{MINT}"/><stop offset="1" stop-color="{MINT_DEEP}"/></linearGradient>
<linearGradient id="{uid}-gloss" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="{uid}-steel" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#5c5f65"/><stop offset=".14" stop-color="#c9ccd2"/>
 <stop offset=".34" stop-color="#7d8188"/><stop offset=".5" stop-color="#eef0f3"/>
 <stop offset=".68" stop-color="#8a8e95"/><stop offset=".86" stop-color="#d7dadf"/>
 <stop offset="1" stop-color="#43464b"/></linearGradient>
<clipPath id="{uid}-sleeve"><rect x="20" y="96" width="140" height="44" rx="21"/></clipPath>
</defs>'''
    body = f'''
<g transform="translate(41.8 24.6) scale(.88) rotate(-74 90 118)">
 <rect x="20" y="96" width="140" height="44" rx="21" fill="url(#{uid}-nap)"/>
 <g clip-path="url(#{uid}-sleeve)">
  <rect x="20" y="96" width="{WET - 20}" height="44" fill="url(#{uid}-wet)"/>
  <!-- the ragged edge where the load runs out -->
  <path d="M{WET} 96 q4 6 -2 11 q6 5 0 11 q5 6 -1 11 q4 5 3 11 L{WET - 4} 140 L{WET - 4} 96 Z" fill="{MINT}"/>
  <path d="M{WET + 2} 96 q-5 6 1 11 q-6 5 0 11 q-5 6 1 11 q-4 5 -2 11 L{WET} 140 L{WET} 96 Z" fill="{MINT_LO}" opacity=".8"/>
  <g fill="none" stroke-linecap="round" opacity=".7">{''.join(texture)}</g>
  <rect x="20" y="96" width="140" height="14" fill="url(#{uid}-gloss)"/>
  <rect x="20" y="128" width="140" height="12" fill="#000" opacity=".22"/>
 </g>
 <g fill="none" stroke-linecap="round" opacity=".9">{''.join(fibres)}</g>
 <!-- end cap and the cage -->
 <ellipse cx="160" cy="118" rx="7.5" ry="22" fill="#d9d6ce"/>
 <ellipse cx="160" cy="118" rx="4.2" ry="15" fill="#3a3a37"/><ellipse cx="160" cy="118" rx="2" ry="8" fill="#141413"/>
 <path d="M160 118 h16 q12 0 12 -12 v-58" stroke="#2a2b2e" stroke-width="7.5" fill="none" stroke-linecap="round"/>
 <path d="M160 118 h16 q12 0 12 -12 v-58" stroke="url(#{uid}-steel)" stroke-width="5.4" fill="none" stroke-linecap="round"/>
 <path d="M160 118 h16 q12 0 12 -12 v-58" stroke="#fff" stroke-width="1.2" fill="none" stroke-linecap="round" opacity=".55" transform="translate(-1.2,-1)"/>
 <!-- the grip: shaped, ribbed, with a hang hole -->
 <path d="M176 -2 q12 -4 24 0 l2 60 q-14 6 -28 0 z" fill="url(#{uid}-grip)"/>
 <g stroke="#000" stroke-width="1.2" opacity=".28"><path d="M178 12 h20 M178 22 h20 M178 32 h20 M178 42 h20"/></g>
 <path d="M181 4 v48" stroke="#fff" stroke-width="1.6" opacity=".35" stroke-linecap="round"/>
 <circle cx="188" cy="6" r="2.4" fill="{INK}" opacity=".8"/>
</g>'''
    return (f'<svg class="prop prop-roller-pass" viewBox="0 0 200 200" width="200" height="200" aria-hidden="true" focusable="false">'
            f'{defs}{body}</svg>')
