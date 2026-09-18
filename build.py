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
import os, html, json, hashlib

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


def nav_html():
    items = ''.join(f'<li><a href="{u(href)}">{label}</a></li>' for label, href in NAV)
    return f'''<header class="nav">
  <div class="wrap">
    <a class="brand" href="{u('/')}" aria-label="{SITE_NAME} home"><span>Open Air</span><b>Gallery</b></a>
    <nav aria-label="Main"><ul class="nav-links">{items}</ul></nav>
    <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  </div>
</header>'''


def footer_html():
    return f'''<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <a class="brand" href="{u('/')}"><span>Open Air</span><b>Gallery</b></a>
        <p>Murals, banners and large-image work at building scale. New York and nationwide.</p>
        <div class="socials">
          <a {ext(IG)} aria-label="Instagram">{ICONS['ig']}</a>
          <a href="mailto:{EMAIL}" aria-label="Email">{ICONS['mail']}</a>
        </div>
      </div>
      <div><h4>Company</h4><ul>
        {''.join(f'<li><a href="{u(href)}">{label}</a></li>' for label, href in NAV)}</ul></div>
      <div><h4>Contact</h4><ul>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a {ext(IG)}>{IG_HANDLE}</a></li></ul></div>
    </div>
    <div class="foot-bottom">
      <span>&copy; <span id="year">2026</span> {SITE_NAME}. All rights reserved.</span>
    </div>
  </div>
</footer>
<script src="{u('/js/site.js')}?v={asset_v("js/site.js")}" defer></script>'''


def asset_v(rel):
    """Short content hash so browsers refetch css/js after every edit."""
    with open(os.path.join(OUT, rel.lstrip('/')), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def page_hero(eyebrow, title, lead, media_slug=None, crumb=None):
    media = f'<div class="hero-media">{img(media_slug, "", extra="fetchpriority=high")}</div>' if media_slug else ''
    crumbs = (f'<div class="crumbs"><a href="{u("/")}">Home</a><span>/</span><span>{crumb or title}</span></div>'
              if crumb is not False else '')
    return f'''<section class="page-hero">{media}<div class="hero-shade"></div>
  <div class="wrap"><div class="hero-inner">{crumbs}<div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p class="lead">{lead}</p></div></div></section>'''


def cta(title='Ready when you are.',
        text='Tell us the wall, the city and roughly how big it is. We will come back with a plan and a price.',
        primary=('Book a free consultation', '/contact'),
        secondary=('See the work', '/work')):
    return f'''<section class="cta-wrap"><div class="wrap"><div class="cta rv">
  <h2>{title}</h2><p>{text}</p>
  <div class="btn-row"><a class="btn btn-mint" href="{u(primary[1])}">{primary[0]} {ICONS['arrow']}</a><a class="btn btn-ghost" href="{u(secondary[1])}">{secondary[0]}</a></div>
</div></div></section>'''


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
pages['/index'] = dict(
  title=f'{SITE_NAME} | Murals at building scale, New York and nationwide',
  desc='Open Air Gallery is a muralist and large-image company led by Ephraim. Gucci in Manhattan at 81 by 80 feet, Crown Royal in Portland at 85 by 90, John Lewis and Malcolm X in Rochester.',
  body=f'''
{page_hero('Muralist and large-image company',
           'Murals that capture the gaze',
           'Open Air Gallery is Ephraim’s studio: eighty-one feet of Gucci on a Manhattan wall, eighty-five feet of Crown Royal in Portland, John Lewis and Malcolm X in Rochester.',
           crumb=False)}
<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">What this is</div><h2>Twelve walls, measured in feet</h2>
  <p class="lead">The scaffold is up. Sections land one commit at a time: the work, the Rochester civic beat, the process, graffiti removal, and the consultation.</p></div>
</div></section>
{cta()}''')

# ---------------------------------------------------------------- write
os.makedirs(OUT, exist_ok=True)
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
