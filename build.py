#!/usr/bin/env python3
"""Static site builder for Open Air Gallery. Renders site/*.html from the page
definitions at the bottom of this file.

Modelled on /root/dronegodmax-src/build.py — same shape, same discipline: one
dict of pages, one write loop, a sitemap and robots.txt written from the same
dict, and content hashes on css/js so a browser never serves a stale stylesheet.
Everything specific to DroneGodMax (the shop, the drone, the Green Flash
cross-sell, the flight deck) is gone; what is left is the frame.

Two environment variables move the whole site:

    BASE_URL   absolute origin for canonical/OG URLs and the sitemap
    PREFIX     path the site is served under, e.g. /p/<slug> on the preview

Every root-absolute link in the output goes through u() and every image through
img(), so the same build runs at the domain root and under a preview prefix.
"""
import os, sys, html, json, struct, hashlib

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, 'site')

BASE_URL = os.environ.get('BASE_URL', 'https://ephraim.greenflashusa.com').rstrip('/')
PREFIX = os.environ.get('PREFIX', '').rstrip('/')

SITE_NAME = 'Open Air Gallery'
# The live site is inconsistent — hello@ in the home body, info@ in the footer.
# PLAN.md §"Verified facts" says default to hello@ and confirm with Ephraim.
EMAIL = 'hello@openairgallery.art'
IG_HANDLE = '@openairmurals'
IG = 'https://www.instagram.com/openairmurals'

# The two colours the HTML itself has to name (a <meta> tag and the inline
# favicon cannot read a CSS custom property). They mirror --ink and --mint in
# site/css/site.css, and docs/contrast.py fails the build if they ever drift.
INK = '#0A0A0B'
MINT = '#71EEB8'

# One accent on one dark canvas: if that pair stops being readable the design
# has stopped working, so the build refuses to finish. docs/contrast.py reads
# the tokens straight out of the stylesheet and checks the two constants above
# still match the tokens they mirror.
sys.path.insert(0, os.path.join(SRC, 'docs'))
import contrast
contrast.check(os.path.join(OUT, 'css', 'site.css'), {'--ink': INK, '--mint': MINT})

# One request for both families. Archivo ships the width axis the dimension
# figures need (wdth 62..125); Inter carries the body and its tabular numerals.
FONTS = ('https://fonts.googleapis.com/css2?'
         'family=Archivo:wdth,wght@62..125,400..900&family=Inter:wght@400;600;700&display=swap')

# A drawn mark rather than a file: a mint frame on ink, the wall the work goes
# on. Inline so there is no favicon request to 404 before the images land.
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           f"%3Crect width='64' height='64' fill='{INK.replace('#', '%23')}'/%3E"
           f"%3Crect x='11' y='15' width='42' height='34' fill='none' "
           f"stroke='{MINT.replace('#', '%23')}' stroke-width='6'/%3E%3C/svg%3E")

# The twelve walls. Every project fact on the site comes from here.
from projects import (PROJECTS, FEATURED_ORDER, CATEGORIES, BY_SLUG,
                      featured, total_sq_ft)


def u(path):
    """A root-absolute link, prefixed so the preview works under /p/<slug>/."""
    return PREFIX + path


def ext(href):
    """Attributes for an off-site link."""
    return f'href="{href}" target="_blank" rel="noopener"'


def img(slug, alt='', thumb=False, cls='', extra=''):
    src = u(f"/assets/img/{'t/' if thumb else ''}{slug}.webp")
    c = f' class="{cls}"' if cls else ''
    return f'<img src="{src}" alt="{html.escape(alt)}" loading="lazy" decoding="async"{c} {extra}>'


def webp_size(path):
    """(width, height) straight out of a WebP header. No dependencies: this
    build has to run on the droplet with nothing but python3."""
    with open(path, 'rb') as f:
        h = f.read(30)
    if h[:4] != b'RIFF' or h[8:12] != b'WEBP':
        raise ValueError(f'{path}: not a WebP')
    fmt = h[12:16]
    if fmt == b'VP8 ':
        w, ht = struct.unpack('<HH', h[26:30])
        return w & 0x3FFF, ht & 0x3FFF
    if fmt == b'VP8L':
        b = struct.unpack('<I', h[21:25])[0]
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    if fmt == b'VP8X':
        return ((h[24] | h[25] << 8 | h[26] << 16) + 1,
                (h[27] | h[28] << 8 | h[29] << 16) + 1)
    raise ValueError(f'{path}: unknown WebP chunk {fmt!r}')


def pic(name, alt, sizes, cls='', extra='', lazy=True):
    """<picture> over whichever renditions process.sh actually produced.

    The width descriptors are read off the files, never assumed. Ten of the
    twelve heroes are only ~1,200 px wide on Wix (docs/images.md), and for a
    source under 1,600 the `.webp` and `-1600.webp` renditions come out the
    same pixel size — writing 2400w/1600w/800w by rote would lie to the
    browser about all of them. Identical widths collapse to one entry.
    """
    root = os.path.join(SRC, 'out', 'img')
    by_w = {}
    for rel in (f't/{name}.webp', f'{name}-800.webp', f'{name}-1600.webp', f'{name}.webp'):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            continue
        w, h = webp_size(path)
        by_w.setdefault(w, (rel, w, h))     # first one wins: the smaller file
    assert by_w, (f'pic({name!r}): nothing in out/img/ — run ./process.sh, '
                  f'or see docs/images.md')
    widths = sorted(by_w)
    srcset = ', '.join(f'{u("/assets/img/" + by_w[w][0])} {w}w' for w in widths)
    small = by_w[widths[0]]
    big = by_w[widths[-1]]
    c = f' class="{cls}"' if cls else ''
    load = 'lazy' if lazy else 'eager'
    return (f'<picture{c}><img src="{u("/assets/img/" + small[0])}" srcset="{srcset}" '
            f'sizes="{sizes}" alt="{html.escape(alt)}" width="{big[1]}" height="{big[2]}" '
            f'loading="{load}" decoding="async"{" " + extra if extra else ""}></picture>')


# What a card asks the browser for: one of three across at desktop, two at
# tablet, the full width on a phone.
CARD_SIZES = '(min-width:960px) 33vw, (min-width:640px) 50vw, 100vw'
PAIR_SIZES = '(min-width:640px) 50vw, 100vw'

# A hero runs the full width of the window, but it is never asked to fill more
# than 1,600 CSS px. PLAN.md §9(a): ten of the twelve photographs Wix ever held
# are only ~1,200 px wide, so a 2,560 px laptop asking for 2,560 px of image
# would only be told "the biggest I have is 1,242" — and then stretch it. The
# cap is the honest ceiling until Ephraim's originals arrive.
HERO_SIZES = '(min-width:1600px) 1600px, 100vw'

# Small numbers read better as words in a sentence, and the only numbers this
# site spells out are counts it computed itself.
_WORDS = ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
          'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
          'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty')


def spell(n, cap=False):
    w = _WORDS[n] if 0 <= n < len(_WORDS) else f'{n:,}'
    return w[:1].upper() + w[1:] if cap else w


PRIME = '\u2032'          # the foot mark, kept out of f-strings that nest quotes
TIMES = '\u00d7'


def dims(w, h, size=''):
    """The hook: a wall's measurements, set physically wide.

    Mint touches the prime marks and the times sign and nothing else — one
    accent stays one accent. `size` adds a modifier: dims('sm') on a card.
    """
    cls = 'dims' + (f' dims-{size}' if size else '')
    return (f'<div class="{cls}"><span class="n">{w}</span><span class="f">\u2032</span>'
            f'<span class="x">\u00d7</span><span class="n">{h}</span>'
            f'<span class="f">\u2032</span></div>')


def pcard(p, cls='', sizes=CARD_SIZES):
    """A project card. The card is the link; the figures are the headline."""
    place = f"{p['city']}, {p['state']}"
    alt = f"{p['title']} mural by Open Air Gallery, {place}"
    return f'''<a class="pcard rv {cls}" href="{u('/work/' + p['slug'])}">
  <div class="pcard-img">{pic(p['hero'], alt, sizes)}</div>
  <div class="pcard-body">{dims(p['dim_w'], p['dim_h'], 'sm')}<h3>{p['title']}</h3><span class="place">{place}</span></div>
</a>'''


def check_projects():
    """Refuse to build on a malformed project row.

    The dimensions are the whole design, so a string, a float or a typo has to
    stop the build rather than reach a page. The hero check is a hard assert:
    the images pipeline has landed (docs/images.md) and every one of the twelve
    heroes is on disk, so a missing file now means process.sh has not been run,
    not that the photograph does not exist yet.
    """
    root = os.path.join(SRC, 'out', 'img')
    seen = set()
    for p in PROJECTS:
        slug = p['slug']
        assert slug and slug not in seen, f'projects.py: empty or duplicate slug {slug!r}'
        seen.add(slug)
        for k in ('dim_w', 'dim_h'):
            v = p[k]
            assert isinstance(v, int) and not isinstance(v, bool) and 0 < v < 1000, (
                f'{slug}: {k} must be a whole number of feet, got {v!r}')
        assert p['category'] in CATEGORIES, (
            f"{slug}: category {p['category']!r} is not one of {CATEGORIES}")
        assert p['year'] is None or (isinstance(p['year'], int) and 1900 < p['year'] < 2100), (
            f"{slug}: year is {p['year']!r} — leave it None rather than guess")
        assert p['story'] and p['title'] and p['city'] and p['state'], f'{slug}: missing text'
        for name in [p['hero']] + list(p['gallery']):
            assert os.path.exists(os.path.join(root, name + '.webp')), (
                f'{slug}: out/img/{name}.webp is missing — run ./process.sh '
                f'(see docs/images.md)')
    flagged = {p['slug'] for p in PROJECTS if p['featured']}
    assert flagged == set(FEATURED_ORDER), (
        f'projects.py: featured flags {sorted(flagged)} do not match '
        f'FEATURED_ORDER {sorted(FEATURED_ORDER)}')


check_projects()


ICONS = {
 'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
 'ig': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 'chevL': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
 'chevR': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>',
}

# (label, href). No dropdowns on this site — six pages, all one click away.
NAV = [
  ('Work', '/work'),
  ('Graffiti Removal', '/graffiti-removal'),
  ('Services', '/services'),
  ('About', '/about'),
  ('Contact', '/contact'),
]

COMPANY = [('Services', '/services'), ('Graffiti Removal', '/graffiti-removal'),
           ('About', '/about'), ('Contact', '/contact')]
FOOT_LINE = ('Murals &middot; Banners &middot; Signs &middot; Graffiti removal '
             '&middot; New York and nationwide')


def brand(aria=''):
    """The wordmark: two lines, set wide, the only place the name is drawn."""
    a = f' aria-label="{aria}"' if aria else ''
    return (f'<a class="brand" href="{u("/")}"{a}>'
            f'<span>Open Air</span><span>Gallery</span></a>')


def nav_html():
    items = ''.join(f'<li><a href="{u(href)}">{label}</a></li>' for label, href in NAV)
    return f'''<header class="nav">
  <div class="wrap">
    {brand(f'{SITE_NAME} home')}
    <nav aria-label="Main"><ul class="nav-links" id="nav-links">{items}<li class="nav-cta"><a class="btn btn-mint btn-sm" href="{u('/contact')}">Book a free consult</a></li></ul></nav>
    <button class="nav-toggle" type="button" aria-label="Menu" aria-controls="nav-links" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  </div>
</header>'''


def footer_html():
    work = ''.join(f'<li><a href="{u("/work/" + p["slug"])}">{p["title"]}</a></li>'
                   for p in featured())
    company = ''.join(f'<li><a href="{u(href)}">{label}</a></li>' for label, href in COMPANY)
    return f'''<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        {brand()}
        <p>Murals, banners and large-image work at building scale. Ephraim and the Open Air Gallery crew, out of New York, painting nationwide.</p>
        <ul class="foot-contact">
          <li><a href="mailto:{EMAIL}">{ICONS['mail']}{EMAIL}</a></li>
          <li><a {ext(IG)}>{ICONS['ig']}{IG_HANDLE}</a></li>
        </ul>
      </div>
      <div><h4>Work</h4><ul>{work}<li><a href="{u('/work')}">All twelve walls</a></li></ul></div>
      <div><h4>Company</h4><ul>{company}</ul></div>
    </div>
    <div class="foot-bottom">
      <span>{FOOT_LINE}</span>
      <span>&copy; <span id="year">2026</span> {SITE_NAME}</span>
    </div>
  </div>
</footer>
<script src="{u('/js/site.js')}?v={asset_v("js/site.js")}" defer></script>'''


def asset_v(rel):
    """Short content hash so browsers refetch css/js after every edit."""
    with open(os.path.join(OUT, rel.lstrip('/')), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def page_hero(eyebrow, title, lead, media_slug=None, crumb=None, cls='', media_alt=''):
    """The top of a page: a photograph, a shade over it, and the words.

    The photograph goes through pic() rather than img() so the browser picks a
    rendition instead of always taking the widest one, and it is the page's
    LCP element, so it loads eagerly at high priority. media_alt is the
    description of the mural; leave it empty only when the photograph is
    genuinely decorative, which on this site it never is.
    """
    media = (f'<div class="hero-media">'
             f'{pic(media_slug, media_alt, HERO_SIZES, extra="fetchpriority=\"high\"", lazy=False)}'
             f'</div><div class="hero-shade"></div>') if media_slug else ''
    crumbs = (f'<div class="crumbs"><a href="{u("/")}">Home</a><span>/</span><span>{crumb or title}</span></div>'
              if crumb is not False else '')
    return f'''<section class="page-hero{" " + cls if cls else ""}">{media}
  <div class="wrap"><div class="hero-inner">{crumbs}<div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p class="lead">{lead}</p></div></div></section>'''


def cta(title='Ready when you are.',
        text='Tell us the wall, the city and roughly how big it is. We will come back with a plan and a price.',
        primary=('Book a free consultation', '/contact'),
        secondary=('See the work', '/work')):
    return f'''<section class="cta-wrap"><div class="wrap"><div class="cta rv">
  <h2>{title}</h2><p>{text}</p>
  <div class="btn-row"><a class="btn btn-mint" href="{u(primary[1])}">{primary[0]} {ICONS['arrow']}</a><a class="btn btn-ghost" href="{u(secondary[1])}">{secondary[0]}</a></div>
</div></div></section>'''


# Ephraim's own account of the work, transcribed from the About page of his
# live site (research/wix/about.html, saved 2026-09-18). His three stage names
# and his three paragraphs, verbatim but for one typo — he wrote "how the light
# will affect it's color", which is set as "its" here. Nothing else is changed:
# these are his sentences and they are better than anything written for him.
# Home quotes all three as the process; About runs them at length; Services
# takes the second and third for paint science and preservation.
PROCESS = [
  ('Mural prep',
   'When it comes to mural creations, it starts from a small image and explodes '
   'onto a massive canvas. It takes meticulous prep work to ensure that the scale '
   'of the image is appropriately captured. The ability to scale and project is '
   'what differs an artist and a muralist.'),
  ('Paint analysis',
   'There is a science to paint and an understanding for the preservation of the '
   'environment. We analyze the way the paint will decay over time and how the '
   'light will affect its color. This intensive process allows us to use only what '
   'we need and what will last.'),
  ('Mural preservation',
   'After the completion of the mural, we understand the fears of clients regarding '
   'vandalism and degradation. We take this into account and apply environmentally '
   'friendly coating that will make it easy to clean any future vandalism without '
   'damaging the art work.'),
]


def beats(items, cls=''):
    """His stages as quoted blocks — the stage name, then his own sentences."""
    li = ''.join(
        f'<li class="beat rv{" rv-d" + str(i) if i else ""}">'
        f'<h3>{stage}</h3><blockquote><p>{words}</p></blockquote></li>'
        for i, (stage, words) in enumerate(items))
    return f'<ol class="{("beats " + cls).strip()}">{li}</ol>'


def swipe(slides, label, cls=''):
    """A slide rail you can throw with a finger, a mouse or the arrow keys.

    With JavaScript off it is still a native scroll-snap strip, so the arrows
    and dots are enhancement rather than the only way through the slides.
    """
    items = ''.join(f'<div class="swipe-slide">{s}</div>' for s in slides)
    dots = ''.join(f'<button type="button" class="swipe-dot{" is-on" if i == 0 else ""}" data-dot="{i}" aria-label="Go to slide {i + 1}"></button>' for i in range(len(slides)))
    return f'''<div class="swipe rv {cls}" data-swipe aria-roledescription="carousel" aria-label="{label}">
  <div class="swipe-rail" data-rail tabindex="0">{items}</div>
  <button class="swipe-arw prev" type="button" data-prev aria-label="Previous">{ICONS['chevL']}</button>
  <button class="swipe-arw next" type="button" data-next aria-label="Next">{ICONS['chevR']}</button>
  <div class="swipe-dots" data-dots>{dots}</div>
  <div class="swipe-hint" aria-hidden="true">Drag or swipe</div>
</div>'''


def layout(path, title, desc, body, ld=None, noindex=False):
    canonical = BASE_URL + (path if path != '/index' else '/')
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else ''
    ldjson = f'<script type="application/ld+json">{json.dumps(ld)}</script>' if ld else ''
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(d){{var c=d.documentElement.classList;c.add('js');try{{if(!matchMedia('(prefers-reduced-motion: reduce)').matches)c.add('motion')}}catch(e){{}}}})(document)</script>
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
{robots}
<meta property="og:type" content="website"><meta property="og:site_name" content="{SITE_NAME}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{INK}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{u('/css/site.css')}?v={asset_v("css/site.css")}">
{ldjson}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{nav_html()}
<main id="main">
{body}
</main>
{footer_html()}
</body>
</html>'''


pages = {}

# ---------------------------------------------------------------- HOME
# Every number on this page is computed from projects.py. None of them is
# typed: "Twelve walls. Over 23,000 square feet." is the roster adding itself
# up, so the day a thirteenth wall lands the sentence is already true.
WALLS = len(PROJECTS)
SQ_FT = total_sq_ft()
CITIES = {(p['city'], p['state']) for p in PROJECTS}
TALLEST = max(PROJECTS, key=lambda p: p['dim_h'])
WIDEST = max(PROJECTS, key=lambda p: p['dim_w'])
ROCHESTER = [p for p in PROJECTS if p['category'] == 'civic']


def stat(figure, label, mark=''):
    m = f'<span class="f">{mark}</span>' if mark else ''
    return (f'<li class="stat rv"><span class="stat-n">{figure}{m}</span>'
            f'<span class="stat-l">{label}</span></li>')


pages['/index'] = dict(
  title=f'{SITE_NAME} | Murals at building scale, New York and nationwide',
  desc='Open Air Gallery is a muralist and large-image company led by Ephraim. Gucci in Manhattan at 81 by 80 feet, Crown Royal in Portland at 85 by 90, John Lewis and Malcolm X in Rochester.',
  body=f'''
{page_hero('Muralist and large-image company',
           'Murals that capture the gaze',
           'Open Air Gallery is Ephraim’s studio: eighty-one feet of Gucci on a Manhattan wall, eighty-five feet of Crown Royal in Portland, John Lewis and Malcolm X in Rochester.',
           media_slug='gucci-new-york-hero',
           media_alt='The Gucci mural by Open Air Gallery, eighty-one feet across a New York City wall',
           crumb=False, cls='tall')}

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">The measure of it</div>
  <h2>{spell(WALLS, cap=True)} walls. Over {SQ_FT // 1000:,},000 square feet.</h2>
  <p class="lead">Added up wall by wall, the work so far comes to {SQ_FT:,} square feet of painted surface in {spell(len(CITIES))} cities. The tallest of them stands {TALLEST['dim_h']} feet in {TALLEST['city']}; the widest runs {WIDEST['dim_w']} feet.</p></div>
  <ul class="stats">
    {stat(WALLS, 'walls painted')}
    {stat(f'{SQ_FT:,}', 'square feet of wall')}
    {stat(TALLEST['dim_h'], f'tallest wall, {TALLEST["city"]}', mark='′')}
    {stat(len(CITIES), 'cities, coast to coast')}
  </ul>
</div></section>

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">Selected work</div><h2>{spell(WALLS, cap=True)} walls, measured in feet</h2>
  <p class="lead">Six of them here, all {spell(WALLS)} on the Work page. The number over each photograph is how much wall it took.</p></div>
  <div class="pgrid">{''.join(pcard(p, f'rv-d{i % 3}' if i % 3 else '') for i, p in enumerate(featured()))}
  </div>
  <div class="row-end rv"><a class="btn btn-ghost" href="{u('/work')}">All {spell(WALLS)} walls {ICONS['arrow']}</a></div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">{ROCHESTER[0]['city']}, {ROCHESTER[0]['state']}</div>
  <h2>Two walls in Rochester</h2>
  <p class="lead">{ROCHESTER[0]['title']} and {ROCHESTER[1]['title']}, painted in the same city at the same size: {ROCHESTER[0]['dim_w']} feet wide by {ROCHESTER[0]['dim_h']} feet tall, each of them.</p></div>
  <div class="pgrid pair">{''.join(pcard(p, 'pcard-lg' + (' rv-d1' if i else ''), PAIR_SIZES) for i, p in enumerate(ROCHESTER))}
  </div>
</div></section>

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">How a wall gets painted</div><h2>Prep, paint, preservation</h2>
  <p class="lead">Ephraim’s three stages, in his own words.</p></div>
  {beats(PROCESS)}
</div></section>

<!-- gr_band() lands in step 12 -->

{cta()}''')

# ---------------------------------------------------------------- WORK
# The index is one grid of all twelve with four chips over it. The chips are
# anchors and the filtering is CSS: `#f-civic:target ~ .pgrid .pcard:not(...)`
# hides what does not match. No JavaScript is involved, so the filter works in
# a text browser, in a crawler, and on a page whose script never arrived — and
# with nothing targeted the grid shows everything, which is the right default.
CAT_LABEL = {'brand': 'Brands', 'portrait': 'Portraits', 'civic': 'Civic'}


def work_index():
    chips = [('#f-all', 'All', len(PROJECTS))]
    chips += [(f'#f-{c}', CAT_LABEL[c], sum(1 for p in PROJECTS if p['category'] == c))
              for c in CATEGORIES]
    targets = '<span class="ftarget" id="f-all"></span>' + ''.join(
        f'<span class="ftarget" id="f-{c}"></span>' for c in CATEGORIES)
    bar = ''.join(f'<li><a class="chip" href="{href}">{label}'
                  f'<span class="ct">{n}</span></a></li>' for href, label, n in chips)
    cards = ''.join(pcard(p, f"cat-{p['category']}" + (f' rv-d{i % 3}' if i % 3 else ''))
                    for i, p in enumerate(PROJECTS))
    return f'''<section class="work"><div class="wrap">
  {targets}
  <ul class="filters" aria-label="Filter the work">{bar}</ul>
  <div class="pgrid">{cards}</div>
</div></section>'''


pages['/work'] = dict(
  title=f'Work | {SITE_NAME}',
  desc=f'All {spell(WALLS)} walls Open Air Gallery has painted, with what each one measured — '
       f'{SQ_FT:,} square feet across {spell(len(CITIES))} cities, from Gucci in Manhattan to '
       f'John Lewis and Malcolm X in Rochester.',
  body=f'''
{page_hero('The roster', f'{spell(WALLS, cap=True)} walls',
           f'Every wall Open Air Gallery has painted, with what it measured. '
           f'{SQ_FT:,} square feet in {spell(len(CITIES))} cities — brand walls, painted '
           f'portraits, and the two Rochester commissions.',
           crumb='Work')}
{work_index()}
{cta()}''')


# ---------------------------------------------------------------- PROJECTS
# A six-foot figure, drawn once: 20 units wide by 60 tall, so two feet by six,
# and the aspect ratio is the scale. Step 14 gives her the drag; until then she
# stands at --fx:.12 on the baseline, correctly sized, captioned. On the Gucci
# wall that makes her about a thirtieth of the picture, which is the point.
FIGURE_SVG = ('<svg class="fig-svg" viewBox="0 0 20 60" fill="currentColor" aria-hidden="true" '
              'focusable="false"><circle cx="10" cy="5.5" r="4.4"/>'
              '<path d="M10 11c3.6 0 6.2 2.2 6.6 5.6l1.1 12c.1 1.3-.7 2.2-1.8 2.3-1.1.1-1.9-.6-2-1.8'
              'l-.7-7.1-.5 9.2 2 16.9c.2 1.5-.8 2.6-2.2 2.7-1.3.1-2.3-.8-2.5-2.2l-1-12.4-1 12.4c-.2 '
              '1.4-1.2 2.3-2.5 2.2-1.4-.1-2.4-1.2-2.2-2.7l2-16.9-.5-9.2-.7 7.1c-.1 1.2-.9 1.9-2 1.8'
              '-1.1-.1-1.9-1-1.8-2.3l1.1-12C3.8 13.2 6.4 11 10 11z"/></svg>')


def scale_hero(p):
    """The wall at full bleed, with the scale figure standing on it.

    PLAN.md §4a: the wrapper carries data-scale and the wall's width in feet,
    and the figure is sized (6 / ft) of the picture's width — she is 2 ft wide
    and 6 ft tall, so the CSS gives her 2/ft of the width and an aspect ratio
    of 1:3 and the arithmetic comes out on its own. This is the No-JS state the
    plan describes and it is what ships until step 14: she stands at --fx:.12
    on a mint baseline with a real "6 ft" caption, which is a static scale bar.
    """
    alt = (f"{p['title']} mural by Open Air Gallery in {p['city']}, {p['state']} — "
           f"{p['dim_w']} feet wide by {p['dim_h']} feet tall")
    return f'''<section class="phero"><div class="scale" data-scale data-ft="{p['dim_w']}" style="--ft:{p['dim_w']};--fx:.12">
  <div class="scale-media">{pic(p['hero'], alt, '100vw', extra='fetchpriority="high"', lazy=False)}</div>
  <div class="scale-base"></div>
  <button class="fig" type="button" data-fig aria-label="Drag the figure for scale"><span class="fig-cap">6 ft</span>{FIGURE_SVG}</button>
</div></section>'''


def project_page(p):
    i = PROJECTS.index(p)
    prv, nxt = PROJECTS[i - 1], PROJECTS[(i + 1) % len(PROJECTS)]
    place = f"{p['city']}, {p['state']}"

    # Facts only where there is a fact. No client on a wall that had none, no
    # year anywhere until Ephraim gives them, no credit until he names one.
    meta = ''
    if p['client']:
        meta += f'<div><dt>Client</dt><dd>{p["client"]}</dd></div>'
    meta += f'<div><dt>Location</dt><dd>{place}</dd></div>'
    if p['year']:
        meta += f'<div><dt>Year</dt><dd>{p["year"]}</dd></div>'
    credit = f'<p class="credit">{p["credit"]}</p>' if p['credit'] else ''

    gallery = ''
    if p['gallery']:
        slides = [pic(name, f'{p["title"]} mural by Open Air Gallery, {place}',
                      '(min-width:960px) 76vw, 100vw')
                  for name in [p['hero']] + list(p['gallery'])]
        gallery = f'''<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">The gallery</div><h2>{spell(len(slides), cap=True)} views of the same wall</h2></div>
  {swipe(slides, f'Photographs of the {p["title"]} mural')}
</div></section>'''

    def step(q, side, label, icon):
        figure = f'{q["dim_w"]}{PRIME} {TIMES} {q["dim_h"]}{PRIME}'
        return (f'<a class="pnav-{side}" href="{u("/work/" + q["slug"])}">'
                f'<span class="pnav-k">{ICONS[icon]}{label}</span>'
                f'<span class="pnav-t">{q["title"]}</span>'
                f'<span class="pnav-d">{figure}</span></a>')

    return f'''
{scale_hero(p)}
<section class="pintro"><div class="wrap">
  <div class="crumbs"><a href="{u('/')}">Home</a><span>/</span><a href="{u('/work')}">Work</a><span>/</span><span>{p['title']}</span></div>
  <div class="eyebrow">{place}</div>
  <h1>{p['title']}</h1>
  {dims(p['dim_w'], p['dim_h'])}
  <p class="lead pstory">{p['story']}</p>
  <dl class="pmeta">{meta}</dl>
  {credit}
</div></section>
{gallery}
<section class="pnav-wrap"><div class="wrap">
  <nav class="pnav" aria-label="More projects">{step(prv, 'prev', 'Previous', 'chevL')}{step(nxt, 'next', 'Next', 'chevR')}</nav>
</div></section>
{cta(title='Want one this size?',
     text='Tell us the wall, the city and roughly how big it is. We will come back with a plan and a price.',
     secondary=('All twelve walls', '/work'))}'''


for _p in PROJECTS:
    _place = f"{_p['city']}, {_p['state']}"
    pages[f"/work/{_p['slug']}"] = dict(
      title=f"{_p['title']}, {_place} | {SITE_NAME}",
      desc=_p['story'],
      body=project_page(_p))


# ---------------------------------------------------------------- ABOUT
# Ephraim by name, the crew at work, his three stages at length, and the
# cities the roster has actually put a wall in — counted from projects.py,
# never typed.
#
# The name: CLAUDE.md records that the only surname anywhere on his site is
# in one Wix alt attribute, and that it is unconfirmed. So this page says
# Ephraim and stops there until the owner says otherwise.
#
# Both long paragraphs below are his, transcribed from the live site
# (research/wix/, saved 2026-09-18) and reproduced verbatim — the studio
# paragraph from the About page, the crew paragraph from the home page.
STUDIO = ('At Open Air Gallery, we are driven by our passion for mural creations. '
          'Each project we undertake is a labor of love, and we pour our hearts into '
          'every brushstroke. Our goal is to captivate the imagination of the viewer '
          'and create awe-inspiring murals that last a lifetime. We take great pride '
          'in every project and strive to execute it with the utmost care, quality, '
          'and joy.')

CREW = ('Open Air Gallery is a team of skilled muralists dedicated to turning your '
        'creative vision into a reality. No matter the size of the project, we '
        'carefully consider the space, lighting, and intended purpose to ensure that '
        'the final product meets your expectations. We take pride in our ability to '
        'execute each project with precision and attention to detail, resulting in '
        'stunning works of art. Our goal is to bring art to the world, one mural at '
        'a time.')

# Where the work has been. The rows are the roster grouping itself: most walls
# first, then alphabetical, so the order is a ranking and still never moves on
# its own. Nothing here is a claim about anywhere a wall has not been painted.
CITY_WALLS = {}
for _q in PROJECTS:
    CITY_WALLS.setdefault((_q['city'], _q['state']), []).append(_q)
CITY_ROWS = sorted(CITY_WALLS.items(), key=lambda kv: (-len(kv[1]), kv[0][0]))


def city_tile(place, walls):
    city, state = place
    n = len(walls)
    return (f'<li class="city rv"><b>{city}</b>'
            f'<span>{state} &middot; {spell(n)} wall{"" if n == 1 else "s"}</span></li>')


PORTRAIT_SIZES = '(min-width:960px) 420px, (min-width:640px) 55vw, 100vw'
HALF_SIZES = '(min-width:960px) 640px, 100vw'

pages['/about'] = dict(
  title=f'About | {SITE_NAME}',
  desc='Open Air Gallery is Ephraim’s studio — a muralist and large-image company '
       'painting at building scale, out of New York and nationwide. His crew, his '
       'three stages, and every city the work has reached.',
  body=f'''
{page_hero('About Open Air Gallery', 'Ephraim and the crew',
           f'A muralist and large-image company: murals, banners and signs painted at '
           f'building scale. Ephraim leads it, the crew goes up on the lift, and the '
           f'walls stand in {spell(len(CITIES))} cities so far.',
           crumb='About')}

<section><div class="wrap">
  <div class="duo">
    <div class="portrait rv">{pic('ephraim-portrait', 'Ephraim, the muralist who leads Open Air Gallery', PORTRAIT_SIZES)}</div>
    <div class="rv rv-d1">
      <div class="eyebrow">The muralist</div>
      <h2>Ephraim</h2>
      <p class="lead">Ephraim is the muralist behind Open Air Gallery. The company paints
      brand walls at building scale — Gucci, Crown Royal, Uber — and painted portraits,
      including the two civil-rights walls in Rochester. In his own words:</p>
      <blockquote class="pull"><p>{STUDIO}</p><cite>Ephraim, Open Air Gallery</cite></blockquote>
    </div>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="duo wide">
    <div class="rv">
      <div class="eyebrow">The crew</div>
      <h2>Nobody paints eighty feet alone</h2>
      <blockquote class="pull"><p>{CREW}</p><cite>Ephraim, Open Air Gallery</cite></blockquote>
    </div>
    <figure class="figframe rv rv-d1">{pic('about-team', 'An Open Air Gallery painter working from a lift platform, mask on, part way through a wall', HALF_SIZES)}
      <figcaption class="figcap">On the lift, mid-wall.</figcaption></figure>
  </div>
</div></section>

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">How a wall gets painted</div>
  <h2>Prep, paint, preservation</h2>
  <p class="lead">Ephraim’s three stages, in full and in his own words — the same three
  he has published since the first version of this company’s site.</p></div>
  {beats(PROCESS, 'beats-full')}
</div></section>

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">Where we work</div>
  <h2>New York, and wherever the wall is</h2>
  <p class="lead">Open Air Gallery is based in New York and paints nationwide. The
  {spell(WALLS)} walls on the Work page stand in {spell(len(CITIES))} cities, coast to
  coast — {SQ_FT:,} square feet of painted surface between them.</p></div>
  <ul class="cities">{''.join(city_tile(place, walls) for place, walls in CITY_ROWS)}</ul>
  <div class="row-end rv"><a class="btn btn-ghost" href="{u('/work')}">See all {spell(WALLS)} walls {ICONS['arrow']}</a></div>
</div></section>

<!-- gr_strip() lands in step 12 -->

{cta(title='If you’re ready, we’re ready.',
     text='Tell us the wall, the city and roughly how big it is. We will come back with '
          'a plan and a price.')}''')


# ---------------------------------------------------------------- SERVICES
# What the company sells, in the order it sells it: the walls, the signs, the
# paint itself, and the cleaning side of the business that has its own page.
#
# Every paragraph set as a quotation is Ephraim's, transcribed from the live
# site. The sign roster is his too — the lower half of his Work page is a grid
# of hand-painted signs (wix-sources.json, not_fetched.signs_and_banners). Not
# one of those photographs has been fetched, so this page names the jobs and
# shows no picture: a sign roster with invented artwork would be worse than a
# list. Move an entry into `extras` in wix-sources.json and re-run fetch-wix.py
# the day the photographs are wanted here.
from urllib.parse import quote as _urlq

# The six things a visitor can ask for. The Contact form's <select> is built
# from this same tuple (step 13), so a link that pre-selects a service can
# never name one the form does not offer.
SERVICE_OPTIONS = ('Murals', 'Banners and signs', 'Graffiti removal',
                   'Pressure washing', 'Commercial painting', 'Something else')

SIGN_ROSTER = ('Heineken', 'Jack Daniels', 'Corona', 'Black Crow',
               'House of Pizza & Calzones')


def consult(service=None):
    """A link to the contact form, with the service already chosen."""
    if service is None:
        return u('/contact')
    assert service in SERVICE_OPTIONS, f'consult({service!r}): not in SERVICE_OPTIONS'
    return f"{u('/contact')}?service={_urlq(service)}"


pages['/services'] = dict(
  title=f'Services | {SITE_NAME}',
  desc='Murals at building scale, hand-painted banners and signs, and the paint '
       'science behind both — plus graffiti removal, pressure washing and commercial '
       'painting from the same crew.',
  body=f'''
{page_hero('What we do', 'Murals, banners and signs',
           'Hand-painted work at building scale, by the crew that cleans the wall '
           'afterwards too: murals, banners and signs, graffiti removal — and the paint '
           'science that runs through all of it.',
           media_slug='moncler-wide',
           media_alt='A hand-painted wall advertisement high above a New York street, '
                     'with traffic and pedestrians below it for scale',
           crumb='Services')}

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">Murals</div>
  <h2>A small image, exploded onto a massive canvas</h2>
  <p class="lead">Brand walls, painted portraits and civic commissions, projected and
  painted by hand. {spell(WALLS, cap=True)} of them so far — {SQ_FT:,} square feet in
  {spell(len(CITIES))} cities, the largest {WIDEST['dim_w']} feet across.</p></div>
  <div class="duo wide">
    <div class="rv">
      <blockquote class="pull"><p>{PROCESS[0][1]}</p><cite>Ephraim, Open Air Gallery</cite></blockquote>
      <div class="btn-row" style="margin-top:1.8rem">
        <a class="btn btn-mint" href="{consult('Murals')}">Start a mural {ICONS['arrow']}</a>
        <a class="btn btn-ghost" href="{u('/work')}">See all {spell(WALLS)} walls</a>
      </div>
    </div>
    <ul class="stats rv rv-d1 stats-2">
      {stat(WALLS, 'walls painted')}
      {stat(f'{SQ_FT:,}', 'square feet of wall')}
      {stat(WIDEST['dim_w'], f'widest wall, {WIDEST["city"]}', mark=PRIME)}
      {stat(len(CITIES), 'cities, coast to coast')}
    </ul>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">Banners and signs</div>
  <h2>Hand-painted, at any size</h2>
  <p class="lead">The same brushes on smaller surfaces: storefront signs, hand-painted
  banners and interior lettering. Ephraim’s own line for the company, and it has been
  the line since the first version of this site — murals, banners, art.</p></div>
  <ul class="roster">{''.join(f'<li class="rv">{html.escape(n)}</li>' for n in SIGN_ROSTER)}</ul>
  <div class="row-end rv"><a class="btn btn-ghost" href="{consult('Banners and signs')}">Ask about a sign {ICONS['arrow']}</a></div>
</div></section>

<section><div class="wrap">
  <div class="duo">
    <figure class="figframe rv">{pic('about-preservation', 'Four Open Air Gallery painters on a suspended platform, finishing a painted portrait wall', HALF_SIZES)}
      <figcaption class="figcap">A crew on a suspended platform, finishing a portrait wall.</figcaption></figure>
    <div class="rv rv-d1">
      <div class="eyebrow">Paint science</div>
      <h2>There is a science to paint</h2>
      <p class="lead">Two of Ephraim’s three stages are about what happens to the paint
      after the crew goes home: how it will fade, and how it survives what is thrown at it.</p>
      <h3 class="svc-h">{PROCESS[1][0]}</h3>
      <blockquote class="pull"><p>{PROCESS[1][1]}</p></blockquote>
      <h3 class="svc-h">{PROCESS[2][0]}</h3>
      <blockquote class="pull"><p>{PROCESS[2][1]}</p><cite>Ephraim, Open Air Gallery</cite></blockquote>
    </div>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="gr-panel rv">
    <div class="eyebrow">Also from Open Air</div>
    <h2>We take it off, too.</h2>
    <p class="lead">Open Air Gallery removes unsightly graffiti &amp; stains with industrial
    strength cleaning services, available in NYC — the same crew that paints the wall knows
    what the surface is made of. Send a picture of the space you want cleaned and you get a
    quote and a date back.</p>
    <ul class="tags">
      <li>Graffiti removal</li><li>Pressure washing</li><li>Commercial painting</li>
    </ul>
    <div class="btn-row" style="margin-top:1.8rem">
      <a class="btn btn-mint" href="{u('/graffiti-removal')}">See graffiti removal {ICONS['arrow']}</a>
      <a class="btn btn-ghost" href="{consult('Graffiti removal')}">Send a photo, get a quote</a>
    </div>
  </div>
</div></section>

<!-- gr_strip() lands in step 12 -->

{cta(title='Which one do you need?',
     text='Tell us the wall, the city and roughly how big it is. We will come back with '
          'a plan and a price.')}''')


# ---------------------------------------------------------------- write
os.makedirs(OUT, exist_ok=True)

# Local convenience only: the pages ask for /assets/img/..., which deploy.sh
# rsyncs out of out/img/ (and skips in site/, --exclude 'assets/'). Link the
# two here so `python3 -m http.server -d site` serves a complete site while we
# are building it. Nothing in the deployed tree depends on this.
_img = os.path.join(SRC, 'out', 'img')
_link = os.path.join(OUT, 'assets', 'img')
if os.path.isdir(_img) and not os.path.exists(_link):
    os.makedirs(os.path.dirname(_link), exist_ok=True)
    os.symlink(os.path.relpath(_img, os.path.dirname(_link)), _link)

for path, p in pages.items():
    fn = os.path.join(OUT, path.strip('/') + '.html')
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, 'w') as f:
        f.write(layout(path, p['title'], p['desc'], p['body'], p.get('ld'), p.get('noindex', False)))
    print('wrote', fn)

# sitemap + robots
# A page marked noindex is a working page, not a public one: it must not be
# advertised in the sitemap any more than it should be indexed.
urls = [BASE_URL + ('/' if p == '/index' else p) for p, d in pages.items()
        if p != '/404' and not d.get('noindex')]
with open(os.path.join(OUT, 'sitemap.xml'), 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + ''.join(f'<url><loc>{u_}</loc></url>' for u_ in urls) + '</urlset>\n')
with open(os.path.join(OUT, 'robots.txt'), 'w') as f:
    f.write(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n')
print('wrote', os.path.join(OUT, 'sitemap.xml'), 'and robots.txt')
