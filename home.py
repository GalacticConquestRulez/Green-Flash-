#!/usr/bin/env python3
"""The Home page, section by section.

The spec is `docs/mockup/home.html` and the two screenshots beside it — the
mockup the owner reviewed and approved. The order, the proportions and the
words here are that mockup's; what changes is that nothing is typed twice. The
prices come from `content.py`, the dashboard figures from `results.py`, the
drawings from `art.py`, and the links, images and films from build.py's own
helpers, so the page cannot disagree with the rest of the site.

The page is written to be **complete with no script at all**. Every section
renders, every figure is in the server HTML, the bars are drawn at their
widths, the chart is a polyline with real points, the films have their
posters. What step 5 adds is motion on top of a page that already says
everything: the hooks it needs are already on the elements —

    data-demo   a section or card that has a demo to run   (the six cards,
                the logo strip, the stats, the bars, the chart, the reels)
    data-live   the well inside a card where its demo plays
    data-count  a figure to count up to, with data-prefix / data-suffix /
                data-decimals saying how to format it on the way
    data-bar    a bar's target width, as a percentage
    data-chart  the leads polyline, to draw on entry
    data-reel   a reel to play when it comes into view

so nothing in this file has to change when the mechanics arrive.
"""
import html

from content import SERVICES, PRICING, SITE, price_text
import art
import results


# --------------------------------------------------------------------- glue
def _b():
    """build.py, whichever name it is running under.

    This module is a *page of* build.py, not a library it uses: it needs u()
    and pic() and build.py needs home_page(), which is a cycle the moment
    either side imports the other at the top of the file. Resolving it here,
    at call time, out of the modules already loaded keeps build.py's side to
    one plain import line — and, more importantly, never runs build.py twice,
    which is exactly what `from build import u` would do to a build.py that is
    running as __main__.
    """
    import sys
    for name in ('build', '__main__'):
        m = sys.modules.get(name)
        if m is not None and hasattr(m, 'page_hero'):
            return m
    raise RuntimeError('home.py is part of build.py and must be called from it')


def _price(text):
    """'Re-designs {web-redesign}.' → 'Re-designs $600.'

    A sentence on this page may name a price, and CLAUDE.md rule 6 says no
    page body may hold one. So a sentence names the PRICING *key* and this
    fills it in. A key that does not exist raises, which is the point.
    """
    out = text
    while '{' in out:
        k = out[out.index('{') + 1:out.index('}')]
        out = out.replace('{' + k + '}', price_text(k))
    return out


# ------------------------------------------------------------------ the copy
# Drew's words where Drew has words. His current site (netoriouslabs.com,
# saved to incoming/refs/netorious-pages.txt on 2026-09-22) is the source for
# four of the six; the mockup shortened them to one line each and the owner
# approved that shortening.
#
# Drones and Lead conversion have no page on his site at all — those two lines
# are NEW, written in his register, and are on CLAUDE.md's list of things he
# has to approve before launch. They are marked below so nobody later mistakes
# them for his.
#
# content.py's SERVICES[*]['one_line'] is empty today and is where his own
# sentences land in step 4; the moment one is filled in it wins over the line
# here, and this table becomes the fallback it was written as.
HOME_LINES = {
    # his /website-design: "fully responsive across all devices", "5+ custom
    # content pages", the re-design service beneath it.
    'websites': 'Sleek, responsive sites that elevate brands and turn ideas '
                'into launches. Re-designs {web-redesign}.',
    # his /ad-campaign-services: "plan, launch, and manage high-performing ad
    # campaigns through Meta Business Suite", plus the filming his README
    # prices with it.
    'meta-ads': 'Campaigns planned, filmed, launched and managed through '
                'Meta Business Suite.',
    # his /viral-content-management: "weekly custom high-performing short-form
    # reels", "active engagement", "content planning". The three tier names
    # are read off PRICING rather than typed.
    'social': 'Weekly short-form reels, engagement and planning. {tiers}.',
    # his /logo-development: "scale seamlessly across digital and print", "from
    # social media sites to physical signage", "full copyright and usage rights
    # upon delivery".
    'logo': 'A mark that scales from social to signage, with full rights on '
            'delivery.',
    # NEW — his /drone-videography is blank. For Drew to approve.
    'drones': 'Aerial film and stills for listings, businesses and events.',
    # NEW — his /lead-conversion is blank. His README says the service is
    # "closing Meta-ad-generated leads". For Drew to approve.
    'lead-conversion': 'Closing the leads your Meta campaigns generate. '
                       'Commission or hourly.',
}

# The clients whose logo files he sent, in the mockup's order. The strip is
# introduced as "Trusted by" and closed with the client we have no logo for —
# CLAUDE.md rule 8: this is what we hold, not the length of his client list.
#
# Isle de Grande is the logo he *designed* rather than a client he manages,
# and it is in the strip because the mockup put it there: it is the proof for
# the logo service.
#
# It is the `-profile` rendition rather than the master on purpose.
# `isle-de-grande.webp` is the delivery file: a transparent PNG whose artwork
# is navy and red, which on #050A0A is very nearly invisible. A transparent
# mark in this strip needs a light plate under it; `isle-de-grande-profile` is
# the same artwork already placed on white for Facebook, so it IS that plate
# and needs no special case. Any future logo that arrives transparent goes the
# same way — a profile rendition if one exists, a light plate on .chip if not.
CLIENTS = [
    ('client-buffalo-holistic', 'Buffalo Holistic Center'),
    ('client-zen-zone', 'Zen Zone Property Maintenance'),
    ('client-britt-fitness', 'Britt Fitness'),
    ('client-adams-detailing', "Adam's Detailing & Coatings"),
    ('isle-de-grande-profile', 'Isle de Grande'),
]
# The one chip that is left in colour while the rest are monochrome, so the
# strip reads as a strip and not as a row of grey discs. The mockup lights the
# second; step 5 walks the light along the row.
LIT = 1

# His three beats, from his own About page, verbatim but for the capitals and
# the full stop the mockup tidied ("We Create clean visuals that standout").
BEATS = [
    ('Design', 'We create clean visuals that stand out.'),
    ('Launch', 'We build, test and deploy your vision.'),
    ('Grow', 'We turn traffic into paying customers.'),
]

# His About page's mission sentence, shortened to two lines for the teaser:
# "help small and mid-sized businesses grow and compete online".
ABOUT_LEAD = ('Helping small and mid-sized businesses grow and compete online, '
              'with the same precision on a Meta campaign as on a drone shot. '
              'Based on Grand Island, working across Buffalo and Western New '
              'York.')


def _line(s):
    """One service's sentence: his if content.py has it, the mockup's if not."""
    text = s['one_line'] or HOME_LINES[s['slug']]
    if '{tiers}' in text:
        tiers = [p['tier'] for p in PRICING.values() if p['service'] == s['slug']]
        text = text.replace('{tiers}', ' · '.join(tiers))
    return _price(text)


def _card_price(s):
    """The figure in the corner of a service card.

    Read off PRICING, never typed (CLAUDE.md rule 6). A service with more than
    one package on the table is shown as "from" its headline package, because
    "$500" on a card that opens onto three tiers is a price the visitor will
    find out is wrong.
    """
    rows = [k for k, p in PRICING.items() if p['service'] == s['slug']]
    p = PRICING[s['price_key']]
    if len(rows) > 1 and not p['qualifier']:
        return f"from {p['amount']}"
    return price_text(s['price_key'])


# ------------------------------------------------------------------ sections
def hero():
    """The film, the two-tone headline, the promise, two buttons.

    The film is his own real-estate reveal, and it is served the way OAG
    serves a hero: the poster is in the server HTML and is what a crawler,
    reader mode, a no-script visitor and a reduced-motion visitor all get; the
    element is preload="none" with no autoplay attribute, so nothing is
    fetched for them at all. The <source> names the **1080** companion — the
    file a phone should be given — and the 4K master is named on data-hi for
    the picker to swap in on a wide screen.

    The picker call sits inside the element and ahead of the <source>, which
    is the only place it works: a <source> appended to an empty media element
    starts the resource selection algorithm immediately, so by the next tag
    the browser has already chosen. Ahead of it there is nothing to undo. It
    is guarded (`window.mmPick && …`) because step 5 is what defines mmPick —
    today the call is inert and costs nothing, and when the picker lands no
    markup here changes.
    """
    b = _b()
    for rel in ('video/hero-drone.mp4', 'video/hero-drone-1080.mp4',
                'video/hero-drone.webp'):
        b.have(rel)
    poster = b.u('/assets/video/hero-drone.webp')
    src = b.u('/assets/video/hero-drone-1080.mp4')
    hi = b.u('/assets/video/hero-drone.mp4')
    return f'''<section class="home-hero">
  <div class="hero-media">
    <video class="hero-video" data-autoplay data-hi="{hi}" muted loop playsinline
           preload="none" poster="{poster}" aria-hidden="true" tabindex="-1"><script>window.mmPick&&window.mmPick(document.currentScript.parentNode)</script><source src="{src}" type="video/mp4"></video>
  </div>
  <div class="hero-shade"></div>
  <div class="wrap"><div class="hero-inner rv">
    <div class="eyebrow">{SITE['name']} · {SITE['place'].split(' · ')[0]}, NY</div>
    <h1 class="h-two">Content. Websites.<span>Drones.</span></h1>
    <p class="lead">Data-driven digital marketing built to strengthen brand
      visibility and drive measurable results.</p>
    <div class="btn-row">
      <a class="btn" href="{b.u('/contact')}">Get a quote {b.ICONS['arrow']}</a>
      <a class="btn btn-ghost" href="{b.u('/results')}">See the results</a>
    </div>
  </div></div>
</section>'''


def logo_strip():
    """The clients' own marks, monochrome, with one left in colour.

    The filter is CSS and so is the colour on hover: with no script the strip
    is complete and a mouse still lights a logo. data-demo hands step 5 the
    row so the light can walk along it.
    """
    b = _b()
    chips = ''.join(
        f'<li class="chip{" is-lit" if i == LIT else ""}">'
        f'{b.pic(slug, name, "64px")}</li>'
        for i, (slug, name) in enumerate(CLIENTS))
    return f'''<section class="strip band" aria-label="Clients">
  <div class="wrap rv">
    <span class="strip-k mono">Trusted by</span>
    <ul class="strip-logos" data-demo="logos">{chips}</ul>
    <span class="strip-k mono">+ Kelly&rsquo;s Country Store</span>
  </div>
</section>'''


def _head(eyebrow, title, aside='', cls=''):
    """A section's heading row: the label and the two-tone headline on the
    left, a button or a sentence on the right."""
    return (f'<div class="sec-head rv{" " + cls if cls else ""}">'
            f'<div><div class="eyebrow">{eyebrow}</div>'
            f'<h2 class="h-two">{title}</h2></div>{aside}</div>')


def services():
    """The module grid: six cards, each one service, each with a well.

    The card is a link to the service's page — the mockup's card is inert
    because a mockup has nowhere to go, and a card that describes a page you
    can read is a card that should open it.

    Every well carries data-live so step 5 can run its three-second demo in
    it. Two of them are not empty today: the website card draws the three
    wireframe lines it will later animate, so the no-JS page shows what the
    demo is about, and the drone card parks the quad that will fly across it.
    """
    b = _b()
    cards = []
    for s in SERVICES:
        slug = s['slug']
        well = ''
        if slug == 'websites':
            well = ('<i class="wire w1"></i><i class="wire w2"></i>'
                    '<i class="wire w3"></i>')
        elif slug == 'drones':
            well = art.quad()
        cards.append(
            f'<a class="svc rv" href="{b.u("/" + slug)}" data-demo="{slug}">'
            f'<div class="svc-top"><span class="ico">{art.icon(slug)}</span>'
            f'<span class="svc-price mono">{html.escape(_card_price(s))}</span></div>'
            f'<h3>{html.escape(s["name"])}</h3>'
            f'<p>{_line(s)}</p>'
            f'<div class="svc-demo" data-live="{slug}">{well}</div></a>')
    aside = (f'<a class="btn btn-ghost" href="{b.u("/pricing")}">'
             f'Every package {b.ICONS["arrow"]}</a>')
    return f'''<section class="services">
  <div class="wrap">
    {_head('Six services, one team',
           'Everything your brand needs.<span>Priced up front.</span>', aside)}
    <div class="svc-grid">{''.join(cards)}</div>
  </div>
</section>'''


def _stat(f):
    """One dashboard figure as a tile. Every string on it comes from
    results.py; data-count and its friends are how step 5 counts up to the
    number that is already printed."""
    hooks = f' data-count="{f["count"]}"' if f['count'] is not None else ''
    if f['prefix']:
        hooks += f' data-prefix="{f["prefix"]}"'
    if f['suffix']:
        hooks += f' data-suffix="{f["suffix"]}"'
    if f['decimals']:
        hooks += f' data-decimals="{f["decimals"]}"'
    up = f'<span class="stat-up mono">{f["delta"]}</span>' if f['delta'] else ''
    note = f'<span class="stat-note">{f["note"]}</span>' if f['note'] else ''
    return (f'<div class="stat rv">'
            f'<span class="stat-k mono">{html.escape(f["label"])}</span>'
            f'<b class="stat-v mono"{hooks}>{f["value"]}</b>'
            f'{up}{note}</div>')


def _bars():
    """Views by content type. The widths are computed from the numbers, so the
    shape of the row cannot drift from the figures printed beside it; they are
    inline styles rather than classes because they are data, and they are in
    the server HTML so the row is drawn with no script."""
    c = results.CONTENT_TYPES
    rows = ''
    for label, value, n in c['rows']:
        pct = results.bar_pct(n, c['rows'])
        rows += (f'<div class="bar" data-bar="{pct}">'
                 f'<span class="bar-k">{label}</span>'
                 f'<span class="bar-track"><b style="width:{pct}%"></b></span>'
                 f'<span class="bar-v mono">{value}</span></div>')
    t = c['total']
    return (f'<div class="panel rv" data-demo="bars">'
            f'<div class="panel-k mono">{html.escape(c["label"])} · '
            f'{t["value"]} {t["label"].lower()}</div>{rows}</div>')


def _chart():
    """The daily-leads line, drawn from results.LEADS.

    A polyline and the area under it, in a 300×100 box stretched to whatever
    width the panel is. The stroke does not stretch with it
    (vector-effect="non-scaling-stroke"), so the line is 2px at every width
    instead of 2px tall and half a pixel wide. The whole series is in the
    server HTML: step 5 wipes it in, it does not supply it.
    """
    pts = results.leads_points()
    line = ' '.join(f'{x},{y}' for x, y in pts)
    area = f'{line} {pts[-1][0]},100 {pts[0][0]},100'
    lo, hi = min(results.LEADS['series']), max(results.LEADS['series'])
    label = (f'{results.LEADS["label"]}, {results.LEADS["range"]}: '
             f'between {lo} and {hi} a day')
    return (f'<div class="panel rv">'
            f'<div class="panel-k mono">{html.escape(results.LEADS["label"])} · '
            f'{html.escape(results.LEADS["range"])}</div>'
            f'<div class="chart-box"><svg class="chart" viewBox="0 0 300 100" '
            f'preserveAspectRatio="none" role="img" data-chart="leads" '
            f'aria-label="{html.escape(label)}">'
            f'<polygon class="chart-fill" points="{area}"/>'
            f'<polyline class="chart-line" points="{line}" '
            f'vector-effect="non-scaling-stroke"/></svg></div></div>')


def results_band():
    """His dashboards, rebuilt in his own colours. Never the screenshots."""
    aside = ('<p class="lead">From client pages under Mendoza Marketing '
             'management, last 28&ndash;90 days.</p>')
    tiles = ''.join(_stat(f) for f in results.HOME_STATS)
    return f'''<section class="results band">
  <div class="wrap">
    {_head('Results', 'Real dashboards.<span>Real numbers.</span>', aside)}
    <div class="stats" data-demo="stats">{tiles}</div>
    <div class="panels">{_bars()}{_chart()}</div>
  </div>
</section>'''


# The three Kelly's reels, in the mockup's order: the long ad first.
REELS = [
    ('reel-santa', 'Santa at Kelly&rsquo;s Country Store'),
    ('reel-pretzels', 'Chocolate pretzels being packed'),
    ('reel-rice-krispies', 'Rice Krispie bars being finished'),
]


def reels():
    """Three phone frames with the reels in them.

    The posters are the server HTML's; the films are preload="none" and do not
    autoplay, so nothing is fetched until step 5 plays them in view. Muted,
    looped, inline — these carry sound as ad creatives and the site never
    starts sound by itself (CLAUDE.md rule 4).
    """
    b = _b()
    frames = ''
    for slug, alt in REELS:
        poster, src = b.clip(slug)
        frames += (f'<div class="phone rv">'
                   f'<video class="reel" data-reel="{slug.replace("reel-", "")}" '
                   f'muted loop playsinline preload="none" poster="{poster}" '
                   f'aria-label="{alt}">'
                   f'<source src="{src}" type="video/mp4"></video>'
                   f'<span class="play" aria-hidden="true">{b.ICONS["play"]}</span>'
                   f'</div>')
    return f'''<section class="reels-sec">
  <div class="wrap">
    {_head('Content in action',
           'Made for the feed.<span>Filmed for the client.</span>')}
    <div class="reels" data-demo="reels">{frames}</div>
    <p class="reels-cap">Kelly&rsquo;s Country Store &middot; Fall Fest and
      holiday campaigns</p>
  </div>
</section>'''


def beats():
    """Design · Launch · Grow — his three, in his words."""
    items = ''.join(
        f'<li class="beat rv"><span class="f-ico">{art.feature(name)}</span>'
        f'<div class="beat-k mono">'
        f'{str(i + 1).zfill(2)} &middot; {name}</div><h3>{line}</h3></li>'
        for i, (name, line) in enumerate(BEATS))
    return (f'<section class="beats-sec band"><div class="wrap">'
            f'<ol class="beats">{items}</ol></div></section>')


def about():
    """The teaser: his photograph, his mission sentence, a way through."""
    b = _b()
    sizes = '(min-width:960px) 420px, 100vw'
    return f'''<section class="about-sec">
  <div class="wrap about">
    <div class="about-pic rv">{b.pic('drew-headshot', 'Drew Mendoza', sizes)}</div>
    <div class="about-txt rv">
      <div class="eyebrow">About</div>
      <h2 class="h-two">Drew Mendoza.<span>Content, websites, drones.</span></h2>
      <p class="lead">{ABOUT_LEAD}</p>
      <a class="btn btn-ghost" href="{b.u('/about')}">Meet Drew {b.ICONS['arrow']}</a>
    </div>
  </div>
</section>'''


def twin():
    """The two ways to start, which is how the page ends.

    Home closes on these rather than on cta(): the twin cards ARE the call to
    action, and two of them stacked would be the same ask twice.

    Both go to /contact today. "Book a call" is a booking link the moment Drew
    gives us one; until then the quote form is the way a call gets arranged,
    and CLAUDE.md records the gap.
    """
    b = _b()
    return f'''<section class="twin-sec band">
  <div class="wrap twin">
    <div class="tw rv">
      <div class="eyebrow">Get in touch</div>
      <h3>Tell us what you&rsquo;re building.</h3>
      <p>A quote comes back within a business day, priced to the package.</p>
      <a class="btn" href="{b.u('/contact')}">Get a quote {b.ICONS['arrow']}</a>
    </div>
    <div class="tw rv">
      <div class="eyebrow">Book a call</div>
      <h3>Twenty minutes, no pitch deck.</h3>
      <p>We&rsquo;ll talk through what you need and what it costs.</p>
      <a class="btn btn-ghost" href="{b.u('/contact')}">Schedule a call</a>
    </div>
  </div>
</section>'''


def flight_layer():
    """The Flight Path's aircraft, parked at the end of the page.

    One div and one drawing, and they are here rather than in flight.js for
    the same reason the Drones card's quad is: a machine that only exists once
    a script has run is a machine that is missing from exactly the renders
    CLAUDE.md rule 4 says have to be complete. So the layer is server HTML and
    16-flight.css's one rule outside `html.motion` — `.flight{display:none}` —
    is what makes it decoration: with no script, or with reduced motion asked
    for, it is not in the render at all and this page is the page it was
    before the flight existed.

    It is last in <main> on purpose. It is absolutely positioned over the
    whole document (the layer, the route and the flying are all in
    site/js/flight.js), so it is in no section, it is `aria-hidden` because it
    says nothing the page does not already say, and nothing in flow can move
    because of it.

    The Drones card keeps its own quad. That one is the demo of the service;
    this one is the survey of the page.
    """
    return (f'<div class="flight" data-flight aria-hidden="true">'
            f'{art.quad("flight-quad")}</div>')


def home_page():
    """The whole page, in the mockup's order."""
    return '\n'.join([hero(), logo_strip(), services(), results_band(),
                      reels(), beats(), about(), twin(), flight_layer()])
