#!/usr/bin/env python3
"""The campaign preview on /meta-ads — a mock Meta campaign a visitor can set.

Drew, 2026-10-11: "Often times clients ask me what they can expect with the
lead amounts if they adjust the budget, but they ask before signing up where
we aren't in the MBS screens. So if I had this on my site it would help a ton
being able to show them and say 'pull up my Mendoza site and we can look to
see what it may be like if we adjust budget or distance'."

Three dials — daily budget, target radius, duration — and four answers:

    total ad spend    exact: budget x 7 x weeks. Paid to Meta, on top of the
                      management fee (his own line: "the client covers the
                      daily ad budget")
    people in range   the towns inside the radius, summed (approximate 2020
                      Census populations, US side only)
    estimated reach   a PROJECTION, as a range
    estimated leads   a PROJECTION, as a range

The two projections are arithmetic on the assumptions in MODEL below, and
the page says so next to them every time they are shown. They are not his
dashboard figures and must never be presented as results (CLAUDE.md rules
7 and 8). The ranges in MODEL are typical local Meta costs, set by us — they
are on CLAUDE.md's list for Drew to replace with his own cost per lead.

The same formula runs twice: compute() here, for the figures in the server
HTML (so the panel is complete with no script, at the defaults), and the
copy in site/js/site.js that runs when a dial moves. Both read MODEL — the
script gets it as JSON on the panel — so the only thing that can drift is
the arithmetic, and the verification shot compares the two at the defaults.
"""
import html
import json
import math

# The dials. Meta's radius targeting runs to 50 miles in the US.
DIALS = dict(
    budget=dict(label='Daily budget', min=5, max=100, step=5, default=20,
                unit='$', suffix='/day'),
    radius=dict(label='Target radius', min=5, max=50, step=5, default=15,
                unit='', suffix=' mi'),
    weeks=dict(label='Duration', min=1, max=12, step=1, default=3,
               unit='', suffix=' wk'),
)

# The assumptions. Ranges, because a single figure would read as a promise.
#   cpm        dollars per 1,000 impressions, local Meta campaign
#   cpl        dollars per lead
#   frequency  how many times the average person sees the ad
#   share      the part of a town's population that is on Facebook or
#              Instagram and can be shown an ad at all
# TODO Drew: his own typical cost per lead (and CPM if he has it) replace
# these, and the page then quotes his experience rather than an industry norm.
MODEL = dict(cpm=[8, 14], cpl=[12, 30], frequency=2.5, share=0.7)

# The places the map draws and the audience sums: (name, lat, lon, people,
# label). Populations are approximate 2020 Census figures for the town or
# city; villages that sit inside a town (Kenmore in Tonawanda, Williamsville
# in Amherst) are left out so nobody is counted twice. `label` is whether the
# map prints the name — the inner suburbs are too close together to name all.
PLACES = [
    ('Grand Island',     43.017, -78.962,  21400, True),
    ('Buffalo',          42.886, -78.878, 278300, True),
    ('Niagara Falls',    43.094, -79.057,  48700, True),
    ('Tonawanda',        42.985, -78.880,  72600, False),
    ('North Tonawanda',  43.039, -78.864,  30200, False),
    ('Amherst',          43.000, -78.770, 129600, True),
    ('Cheektowaga',      42.904, -78.754,  89900, False),
    ('West Seneca',      42.850, -78.800,  45500, False),
    ('Lackawanna',       42.826, -78.823,  19900, False),
    ('Lewiston',         43.172, -79.036,  16300, True),
    ('Wheatfield',       43.100, -78.880,  20000, False),
    ('Lockport',         43.170, -78.690,  41000, True),
    ('Clarence',         43.020, -78.630,  33000, True),
    ('Lancaster',        42.900, -78.670,  45700, False),
    ('Orchard Park',     42.767, -78.744,  29000, True),
    ('Hamburg',          42.730, -78.850,  60000, True),
    ('East Aurora',      42.768, -78.613,  13700, False),
    ('Elma',             42.830, -78.640,  12000, False),
    ('Evans',            42.640, -79.030,  16000, False),
    ('Newfane',          43.290, -78.710,   9500, False),
    ('Newstead',         43.020, -78.490,   8700, False),
    ('Medina',           43.220, -78.387,   5800, True),
    ('Albion',           43.246, -78.193,   5600, False),
    ('Batavia',          42.998, -78.187,  15600, True),
]
# The names the map keeps when it is zoomed out past 30 miles a side, where
# the inner suburbs' labels would sit on top of each other.
MAJOR = {'Buffalo', 'Niagara Falls', 'Lockport', 'Batavia', 'Hamburg', 'Medina'}
WIDE = 30          # half-width, in miles, past which only MAJOR are named
CENTRES = ['Grand Island', 'Buffalo', 'Niagara Falls', 'Amherst', 'Lockport',
           'Orchard Park', 'Batavia']
DEFAULT_CENTRE = 'Grand Island'

# Miles per degree at this latitude: 69 north-south, 69 x cos(43°) east-west.
_MI_LAT, _MI_LON = 69.0, 69.0 * math.cos(math.radians(43.0))
_LAT0, _LON0 = 43.017, -78.962        # Grand Island: the map's own origin


def miles(lat, lon):
    """(east, north) of Grand Island, in miles."""
    return (round((lon - _LON0) * _MI_LON, 2), round((lat - _LAT0) * _MI_LAT, 2))


POINTS = [dict(name=n, x=miles(la, lo)[0], y=miles(la, lo)[1], pop=p, label=lb)
          for n, la, lo, p, lb in PLACES]
assert all(c in [p['name'] for p in POINTS] for c in CENTRES)

# The water, in the same miles, so the map reads as Western New York rather
# than a target on a blank page: Lake Ontario to the north, Lake Erie to the
# south-west, the Niagara River between them. Coarse on purpose — it is a
# picture of where the ads go, not a chart to measure off — and the panel says
# "approximate map".
ONTARIO = [(-90, 16), (-4.5, 16), (12, 22), (39, 24), (90, 27), (90, 90), (-90, 90)]
ERIE = [(1.5, -8.5), (-14.6, -9.7), (-90, -14), (-90, -90), (-35, -90),
        (-20, -45), (-4.5, -23), (3, -10)]
RIVER = [(1.8, -8.5), (2.2, -3), (-0.5, 2.5), (-4, 6.5), (-4.5, 16)]


def compute(budget, radius, weeks, centre=DEFAULT_CENTRE):
    """The four answers, exactly as site.js computes them."""
    c = next(p for p in POINTS if p['name'] == centre)
    spend = budget * 7 * weeks
    people = sum(p['pop'] for p in POINTS
                 if math.hypot(p['x'] - c['x'], p['y'] - c['y']) <= radius)
    cap = people * MODEL['share']
    out = {}
    # hi end of the range = the cheaper cost; lo end = the dearer one
    for end, cpm, cpl in (('lo', MODEL['cpm'][1], MODEL['cpl'][1]),
                          ('hi', MODEL['cpm'][0], MODEL['cpl'][0])):
        reach_free = spend / cpm * 1000 / MODEL['frequency']
        reach = min(reach_free, cap)
        # When the radius runs out of people, the same budget shows the same
        # people more often: the leads scale down by the reach that was lost.
        leads = spend / cpl * (reach / reach_free if reach_free else 0)
        out['reach_' + end] = reach
        out['leads_' + end] = leads
    out.update(spend=spend, people=people, capped=out['reach_hi'] >= cap > 0)
    return out


def _round(n):
    """Reach and people: to the nearest 100 under 10,000, 1,000 above."""
    step = 100 if n < 10000 else 1000
    # Halves round up, as Math.round does in site.js — Python's round() goes
    # to the even neighbour, and the two would print different figures.
    return int(math.floor(n / step + 0.5) * step)


def fmt(r):
    """The strings the panel prints, from compute()'s numbers."""
    def span(a, b):
        return f'{a:,}' if a == b else f'{a:,}–{b:,}'
    return dict(
        spend=f"${r['spend']:,.0f}",
        people=f"{_round(r['people']):,}",
        reach=span(_round(r['reach_lo']), _round(r['reach_hi'])),
        leads=span(math.floor(r['leads_lo']), math.ceil(r['leads_hi'])),
    )


def _pts(poly):
    return ' '.join(f'{x},{-y}' for x, y in poly)


def zoom(radius):
    """How far the map zooms in: the ring plus half again of margin, never
    closer than 16 miles each side nor wider than the 60 the drawing holds.
    Returned as the scale on the world (60 / the half-width shown)."""
    half = min(60.0, max(16.0, radius * 1.45))
    return round(60.0 / half, 4)


def world_style(k, c):
    """The world group's transform: zoomed by k about the centre town. Inline
    CSS rather than the SVG attribute, so site.js can change it with a
    transition (an attribute change cannot be eased)."""
    return f'transform:scale({k}) translate({-c["x"]}px,{c["y"]}px)'


def mark_style(k):
    """The counter-scale on a dot, a label or a pin, so a town is the same
    size on screen at every zoom."""
    return f'transform:scale({round(1 / k, 4)})'


def section(sec_head, money_line):
    """The whole panel: the dials, the map, the answers, the small print.

    `sec_head` is pages.sec_head; `money_line` is the management fee sentence
    from PRICING, so this file never types a price (CLAUDE.md rule 6).

    With no script the dials are drawn at their defaults and disabled, and the
    answers are the defaults' answers — a complete, honest picture of one
    campaign. site.js enables the dials and recomputes on every move.
    """
    d = {k: v['default'] for k, v in DIALS.items()}
    r = compute(d['budget'], d['radius'], d['weeks'])
    f = fmt(r)
    c = next(p for p in POINTS if p['name'] == DEFAULT_CENTRE)

    def dial(key):
        v = DIALS[key]
        shown = f"{v['unit']}{v['default']}{v['suffix']}"
        return (f'<label class="cp-dial"><span class="cp-dial-k">{v["label"]}'
                f'<output class="mono" data-out="{key}">{shown}</output></span>'
                f'<input type="range" name="{key}" min="{v["min"]}" max="{v["max"]}" '
                f'step="{v["step"]}" value="{v["default"]}" disabled '
                f'data-unit="{v["unit"]}" data-suffix="{v["suffix"]}"></label>')

    opts = ''.join(f'<option{" selected" if n == DEFAULT_CENTRE else ""}>{n}</option>'
                   for n in CENTRES)
    centre = (f'<label class="cp-dial cp-centre"><span class="cp-dial-k">Centred on</span>'
              f'<select name="centre" disabled>{opts}</select></label>')

    # The map, in miles, with north up: SVG y runs down, so every y is negated.
    # The world group is zoomed about the centre town (zoom()); every dot,
    # label and pin sits in its own group at its place, counter-scaled, so it
    # stays one size on screen while the land and the ring grow and shrink.
    # site.js changes the zoom, the centre and the ring when a dial moves.
    k = zoom(d['radius'])
    ms = mark_style(k)

    def mark(x, y, inner, cls='cp-mark'):
        return (f'<g transform="translate({x} {-y})"><g class="{cls}" style="{ms}">'
                f'{inner}</g></g>')

    dots = ''
    for p in POINTS:
        on = math.hypot(p['x'] - c['x'], p['y'] - c['y']) <= d['radius']
        lab = (f'<text x="1.9" y="1">{html.escape(p["name"])}</text>'
               if p['label'] else '')
        cls = ' is-in' if on else ''
        cls += ' is-major' if p['name'] in MAJOR else ''
        cls += ' is-centre' if p['name'] == c['name'] else ''
        dots += (f'<g class="cp-place{cls}" data-name="{html.escape(p["name"])}" data-x="{p["x"]}" '
                 f'data-y="{p["y"]}">'
                 + mark(p['x'], p['y'], f'<circle r="1.1"/>{lab}') + '</g>')
    seas = (mark(-2, 30, '<text class="cp-sea">Lake Ontario</text>')
            + mark(-50, -28, '<text class="cp-sea">Lake Erie</text>')
            + mark(-34, -2, '<text class="cp-sea">Canada</text>'))
    wide = ' is-wide' if 60 / k > WIDE else ''
    svg = (f'<svg class="cp-map{wide}" viewBox="-60 -60 120 120" role="img" '
           f'aria-label="Approximate map of Western New York with the target radius '
           f'drawn around the chosen town">'
           f'<g class="cp-world" style="{world_style(k, c)}">'
           f'<polygon class="cp-water" points="{_pts(ONTARIO)}"/>'
           f'<polygon class="cp-water" points="{_pts(ERIE)}"/>'
           f'<polyline class="cp-river" points="{_pts(RIVER)}"/>'
           f'{seas}'
           f'<circle class="cp-area" cx="{c["x"]}" cy="{-c["y"]}" r="{d["radius"]}"/>'
           f'{dots}'
           f'<g class="cp-pinat" transform="translate({c["x"]} {-c["y"]})">'
           f'<g class="cp-mark" style="{ms}"><circle class="cp-pin" r="2"/></g></g>'
           f'</g></svg>')

    out = (f'<div class="cp-out" aria-live="polite">'
           f'<div class="cp-fig cp-fig-main"><span class="cp-k">Total ad spend</span>'
           f'<b class="mono" data-fig="spend">{f["spend"]}</b>'
           f'<span class="cp-n">Paid to Meta for the ads themselves. {money_line}</span></div>'
           f'<div class="cp-fig cp-proj"><span class="cp-k">Estimated reach '
           f'<i>projection</i></span><b class="mono" data-fig="reach">{f["reach"]}</b>'
           f'<span class="cp-n">People who see the ads</span></div>'
           f'<div class="cp-fig cp-proj"><span class="cp-k">Estimated leads '
           f'<i>projection</i></span><b class="mono" data-fig="leads">{f["leads"]}</b>'
           f'<span class="cp-n">Over the whole campaign</span></div>'
           f'<div class="cp-fig cp-fig-wide"><span class="cp-k">People in range</span>'
           f'<b class="mono" data-fig="people">{f["people"]}</b>'
           f'<span class="cp-n">Towns inside the radius, approx.</span></div>'
           f'<p class="cp-cap" data-capped{"" if r["capped"] else " hidden"}>'
           f'The radius is the limit here: a wider one reaches more new people for '
           f'the same budget.</p></div>')

    m = MODEL
    small = (f'<p class="cp-small">Projections, not promises. Reach and leads are '
             f'estimated from typical local Meta costs &mdash; ${m["cpm"][0]}&ndash;'
             f'${m["cpm"][1]} per 1,000 impressions and ${m["cpl"][0]}&ndash;'
             f'${m["cpl"][1]} per lead &mdash; and real results depend on the offer, '
             f'the creative and the season. People in range counts US towns only, '
             f'from approximate 2020 Census figures; the map is approximate.</p>')

    data = html.escape(json.dumps(dict(model=MODEL, places=POINTS)))
    return (sec_head + f'<div class="cp panel rv" data-campaign="{data}">'
            f'<div class="cp-dials">{dial("budget")}{dial("radius")}{dial("weeks")}'
            f'{centre}</div>'
            f'<div class="cp-body"><div class="cp-mapbox">{svg}'
            f'<span class="cp-mapk mono">Approximate map</span></div>{out}</div>'
            f'{small}</div>')
