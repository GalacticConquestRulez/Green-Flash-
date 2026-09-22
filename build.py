#!/usr/bin/env python3
"""Static site builder for Mendoza Marketing — drew.greenflashusa.com.

Renders site/*.html from the `pages` dict at the bottom of this file. Copied
and stripped from /root/dronegodmax-src/build.py the way
/root/openairgallery-src/build.py was: one dict of pages, one write loop, a
sitemap and robots.txt written from the same dict, and content hashes on the
css and js so a browser never serves a stale stylesheet. Everything specific to
DroneGodMax — the shop, the Mavic, the flight deck, the Green Flash cross-sell
band — is gone; what is left is the frame, in Drew's palette and type.

Two environment variables move the whole site:

    BASE_URL   absolute origin for canonical/OG URLs and the sitemap
    PREFIX     path the site is served under, e.g. /p/<slug> on the preview

Every root-absolute link goes through u() and every image through img()/pic(),
so the same build runs at the domain root and under a preview prefix.

Media (out/img, out/video) is produced by a separate pipeline. Until it lands,
a missing file is a WARNING, not a failed build: the scaffold has to be
reviewable before the photographs and the films exist. Every warning is
collected and printed at the end, so nothing goes quiet.

    python3 build.py                        → site/ at the domain root
    PREFIX=/p/test python3 build.py         → site/ under a preview prefix
"""
import os, html, json, hashlib, struct, datetime

from content import (SITE, SERVICES, SEO, PRICING, BY_SLUG, TODO,
                     FORM_ENDPOINT, price)

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, 'site')

BASE_URL = os.environ.get('BASE_URL', 'https://drew.greenflashusa.com').rstrip('/')
PREFIX = os.environ.get('PREFIX', '').rstrip('/')

SITE_NAME = SITE['name']

# The three colours the HTML itself has to name — a <meta> tag and an inline
# favicon cannot read a CSS custom property. They mirror --bg, --green and
# --ink in site/css/site.css; the contrast block at the top of that file is
# where the arithmetic lives.
BG = '#050A0A'
GREEN = '#2de8b5'
INK = '#f0ffff'

# One request, three faces, the weights the stylesheet actually declares:
# Space Grotesk 500/700 for display, Inter 400/600 for body, JetBrains Mono
# 400/600 for labels and figures. display=swap so the words are readable
# while the faces are still in flight.
FONTS = ('https://fonts.googleapis.com/css2?'
         'family=Inter:wght@400;600'
         '&family=JetBrains+Mono:wght@400;600'
         '&family=Space+Grotesk:wght@500;700'
         '&display=swap')

# The icon set and the share card, all cut from Drew's own logo by
# tools/make-og.py and written into out/img/ with the rest of the media. A page
# that names no card of its own gets OG_DEFAULT; the six service pages name
# their own, which has the service on it.
FAVICONS = ('favicon.ico', 'favicon-32.png', 'favicon.svg', 'apple-touch-icon.png')
OG_DEFAULT = 'og.png'

# The wordmark. The media pipeline writes out/img/logo.webp — Drew's mark and
# name on black. The transparent PNG and the vector arrive from him in a day or
# two; when they do, the same slug is rebuilt and nothing here changes.
LOGO = 'logo'


# ------------------------------------------------------------------ warnings
# Asset asserts are soft while the media is being made in parallel. Anything
# the pages ask for and out/ does not have yet lands here and is printed once.
MISSING = []


def have(rel):
    """Is out/<rel> on disk? Records the miss rather than raising."""
    path = os.path.join(SRC, 'out', rel)
    if os.path.exists(path):
        return True
    if rel not in MISSING:
        MISSING.append(rel)
    return False


# ------------------------------------------------------------------- helpers
def u(path):
    """A root-absolute link, prefixed so the preview works under /p/<slug>/."""
    return PREFIX + path


def ext(href):
    """Attributes for an off-site link."""
    return f'href="{href}" target="_blank" rel="noopener"'


# A search result prints roughly 60 characters of a title and 155 of a
# description, and truncates the rest mid-word. Both limits are asserted rather
# than trusted: the write loop checks every description, and this checks every
# title as it is built, so a line that has grown too long fails the build
# instead of arriving in Google with an ellipsis through it.
TITLE_MAX = 60
DESC_MAX = 155


def seo_title(head):
    """The brand, an em dash, and what this page is: 'Mendoza Marketing —
    Website design in Grand Island, NY'. Brand first because it is the thing
    Drew wants recognised, and because every page of a six-page marketing site
    otherwise reads as an orphan in a results list."""
    t = f'{SITE_NAME} — {head}'
    assert len(t) <= TITLE_MAX, f'title is {len(t)} characters, over {TITLE_MAX}: {t}'
    return t


CSS_PARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site', 'css', 'parts')

def concat_css():
    """site/css/site.css is built from site/css/parts/*.css in name order, so
    parallel builders each own a part file and never merge-conflict on one
    stylesheet (the DGM merge that swallowed a whole block is the lesson)."""
    parts = sorted(f for f in os.listdir(CSS_PARTS) if f.endswith('.css'))
    out = []
    for f in parts:
        with open(os.path.join(CSS_PARTS, f)) as fh:
            out.append(f'/* ==== {f} ==== */\n' + fh.read().rstrip() + '\n')
    with open(os.path.join(OUT, 'css', 'site.css'), 'w') as fh:
        fh.write('\n'.join(out))
    return parts


def asset_v(rel):
    """Short content hash so browsers refetch css/js after every edit."""
    with open(os.path.join(OUT, rel.lstrip('/')), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def img(slug, alt='', thumb=False, cls='', extra='', lazy=True):
    """One <img> at one rendition. out/img/<slug>.webp, or t/<slug>.webp."""
    rel = f"img/{'t/' if thumb else ''}{slug}.webp"
    have(rel)
    src = u('/assets/' + rel)
    c = f' class="{cls}"' if cls else ''
    load = 'lazy' if lazy else 'eager'
    return (f'<img src="{src}" alt="{html.escape(alt)}" loading="{load}" '
            f'decoding="async"{c}{" " + extra if extra else ""}>')


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


def png_size(path):
    """(width, height) out of a PNG's IHDR. Same reason as webp_size(): the
    share-card tags say how big the card is, and the number is read off the
    file rather than repeated from the script that made it."""
    with open(path, 'rb') as f:
        h = f.read(24)
    if h[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path}: not a PNG')
    return struct.unpack('>II', h[16:24])


def pic(name, alt, sizes, cls='', extra='', lazy=True):
    """<picture> over whichever renditions the pipeline actually produced.

    The width descriptors are read off the files rather than assumed, so the
    browser is never told a rendition is wider than it is, and identical widths
    collapse to one entry. With nothing on disk yet it degrades to a single
    <img> at the base name and records the miss — the markup is right, the file
    simply is not there yet.
    """
    root = os.path.join(SRC, 'out', 'img')
    by_w = {}
    for rel in (f't/{name}.webp', f'{name}-800.webp', f'{name}-1600.webp', f'{name}.webp'):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            continue
        w, h = webp_size(path)
        by_w.setdefault(w, (rel, w, h))     # first one wins: the smaller file
    if not by_w:
        have(f'img/{name}.webp')
        return img(name, alt, cls=cls, extra=extra, lazy=lazy)
    widths = sorted(by_w)
    srcset = ', '.join(f'{u("/assets/img/" + by_w[w][0])} {w}w' for w in widths)
    small, big = by_w[widths[0]], by_w[widths[-1]]
    c = f' class="{cls}"' if cls else ''
    load = 'lazy' if lazy else 'eager'
    return (f'<picture{c}><img src="{u("/assets/img/" + small[0])}" srcset="{srcset}" '
            f'sizes="{sizes}" alt="{html.escape(alt)}" width="{big[1]}" height="{big[2]}" '
            f'loading="{load}" decoding="async"{" " + extra if extra else ""}></picture>')


def clip(name):
    """(poster, mp4) for out/video/<name>.mp4 — soft while the films are cut."""
    have(f'video/{name}.mp4')
    have(f'video/{name}.webp')
    return u(f'/assets/video/{name}.webp'), u(f'/assets/video/{name}.mp4')


CARD_SIZES = '(min-width:960px) 33vw, (min-width:640px) 50vw, 100vw'
HERO_SIZES = '(min-width:1600px) 1600px, 100vw'


ICONS = {
 'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 'chev':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg>',
 'chevL': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>',
 'chevR': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>',
 'play':  '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>',
 'mail':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
 'phone': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 3h3l1.5 4.5-2 1.5a12 12 0 006 6l1.5-2L21 14.5v3a2 2 0 01-2.2 2A16.5 16.5 0 014 5.2 2 2 0 016 3z"/></svg>',
 'pin':   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 22s7-6.2 7-12a7 7 0 10-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>',
 'ig':    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 'fb':    '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 22v-8h2.7l.4-3.1h-3.1V8.9c0-.9.25-1.5 1.55-1.5H16.7V4.6A21 21 0 0014.3 4.5c-2.4 0-4 1.45-4 4.1v2.3H7.6V14h2.7v8z"/></svg>',
}


# --------------------------------------------------------------- the top bar
# Services ▾ is built from SERVICES, so the menu can never offer a page the
# site does not build, and the six are always in the one order content.py sets.
SERVICE_MENU = [(u('/' + s['slug']), s['name'], '') for s in SERVICES]

NAV = [
    ('Services', None, SERVICE_MENU),
    ('Work', '/work', None),
    ('Results', '/results', None),
    ('About', '/about', None),
    ('Pricing', '/pricing', None),
    ('Contact', '/contact', None),
]


def img_dims(slug):
    """width/height attributes read off the file, so the browser reserves the
    right box and the nav does not jump when the logo arrives. Empty while the
    rendition is still being made."""
    path = os.path.join(SRC, 'out', 'img', f'{slug}.webp')
    if not os.path.exists(path):
        return ''
    w, h = webp_size(path)
    return f'width="{w}" height="{h}"'


def wordmark(cls='brand', aria=None):
    """Drew's logo, on black, as the name of the site.

    An image rather than set type: the mark and the wordmark are one file he
    designed, and the per-service marks later on are that same file with the
    text changed. The alt text is the business name — this is what a screen
    reader hears at the top of every page, not decoration.

    The lockup he sent is square and stacked (mark over MENDOZA MARKETING over
    CONTENT | WEBSITES | DRONES), so the stylesheet gives it most of the height
    of the bar rather than the 44px a horizontal lockup would take. CLAUDE.md
    asks him for a horizontal version with the transparent PNG.
    """
    a = f' aria-label="{html.escape(aria)}"' if aria else ''
    return (f'<a class="{cls}" href="{u("/")}"{a}>'
            f'{img(LOGO, SITE_NAME, extra=img_dims(LOGO), lazy=False)}</a>')


def nav_html():
    """The glass bar: wordmark, the links, the green quote pill, the hamburger.

    Max's nav, with his dropdown and his toggle, in Drew's palette. The quote
    pill is a list item so the phone sheet can stack it full-width under the
    links; on a desktop the same markup sits at the end of the row.
    """
    items = []
    for label, href, sub in NAV:
        if sub:
            subs = ''.join(
                (f'<li><a {ext(h)}>{t}{f"<small>{d}</small>" if d else ""}</a></li>'
                 if h.startswith('http') else
                 f'<li><a href="{h}">{t}{f"<small>{d}</small>" if d else ""}</a></li>')
                for h, t, d in sub)
            items.append(f'<li class="has-menu"><button type="button" aria-haspopup="true" '
                         f'aria-expanded="false">{label}{ICONS["chev"]}</button>'
                         f'<ul class="submenu">{subs}</ul></li>')
        else:
            items.append(f'<li><a href="{u(href)}">{label}</a></li>')
    items.append(f'<li class="nav-cta"><a class="btn btn-sm" href="{u("/contact")}">Get a quote</a></li>')
    return f'''<header class="nav">
  <div class="wrap">
    {wordmark(aria=f'{SITE_NAME} home')}
    <nav aria-label="Main"><ul class="nav-links">{''.join(items)}</ul></nav>
    <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  </div>
</header>'''


def socials_html():
    """The row of social icons. An account Drew has not given us yet is drawn
    and not linked — the footer keeps its shape and nobody clicks a dead
    link. content.py's TODO list is what gets these filled in."""
    out = []
    for label, key, url in SITE['socials']:
        if url:
            out.append(f'<a {ext(url)} aria-label="{label}">{ICONS[key]}</a>')
        else:
            out.append(f'<span aria-label="{label} — link to come" title="{label} — link to come">{ICONS[key]}</span>')
    return f'<div class="socials">{"".join(out)}</div>'


# The pages that are not services, for the footer's Explore column.
EXPLORE = [('Work', '/work'), ('Results', '/results'), ('About Drew', '/about'),
           ('Pricing', '/pricing'), ('Contact', '/contact')]

GF = 'https://greenflashusa.com'


def footer_html():
    """Max's footer, in Drew's colours — the shape he asked for.

    Brand and tagline and socials on the left, then Services, Explore and
    Contact, then the bottom rule with the year and the Green Flash line.
    """
    services = ''.join(f'<li><a href="{u("/" + s["slug"])}">{s["name"]}</a></li>'
                       for s in SERVICES)
    explore = ''.join(f'<li><a href="{u(href)}">{label}</a></li>' for label, href in EXPLORE)
    mail = (f'<li><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>'
            if SITE['email'] else '')
    tel = (f'<li><a href="tel:{SITE["phone_href"]}">{SITE["phone"]}</a></li>'
           if SITE['phone'] else '')
    return f'''<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        {wordmark(cls='brand')}
        <div class="foot-tag">{SITE['tagline']}</div>
        <p>Data-driven marketing out of Grand Island, New York: websites, Meta ad campaigns, social content and aerial film.</p>
        {socials_html()}
      </div>
      <div><h4>Services</h4><ul>{services}</ul></div>
      <div><h4>Explore</h4><ul>{explore}</ul></div>
      <div><h4>Contact</h4><ul>{mail}{tel}<li><span>{SITE['place']}</span></li></ul></div>
    </div>
    <div class="foot-bottom">
      <span>&copy; <span id="year">2026</span> {SITE_NAME}. All rights reserved.</span>
      <span>Built by <a {ext(GF)}>Green Flash</a></span>
    </div>
  </div>
</footer>'''


# -------------------------------------------------------------- page pieces
def page_hero(eyebrow, title, lead, media_slug=None, crumb=None, video=None,
              cls='', media_alt='', extra=''):
    """The top of a page: an optional photograph or film, a shade, the words.

    `title` is passed through as markup so a two-tone headline can be written
    as 'Content. Websites.<span>Drones.</span>' — line one ink, line two green,
    which is the Ellesmere move Drew picked out. Add class "h-two" via `cls` on
    the hero for it.

    The film is decoration on top of the poster, never instead of it: the
    poster is the LCP element and the still that a crawler, reader mode and a
    reduced-motion visitor all get.
    """
    media = ''
    if video:
        poster, src = clip(video)
        media = (f'<div class="hero-media"><video data-autoplay muted loop playsinline '
                 f'preload="none" poster="{poster}" aria-hidden="true" tabindex="-1">'
                 f'<source src="{src}" type="video/mp4"></video></div>')
    elif media_slug:
        media = (f'<div class="hero-media">'
                 f'{pic(media_slug, media_alt, HERO_SIZES, extra="fetchpriority=\"high\"", lazy=False)}'
                 f'</div>')
    shade = '<div class="hero-shade"></div>' if media else ''
    crumbs = (f'<div class="crumbs"><a href="{u("/")}">Home</a><span>/</span>'
              f'<span>{crumb or eyebrow}</span></div>') if crumb is not False else ''
    lead_html = f'<p class="lead">{lead}</p>' if lead else ''
    return f'''<section class="page-hero{" " + cls if cls else ""}">{media}{shade}
  <div class="wrap"><div class="hero-inner rv">{crumbs}<div class="eyebrow">{eyebrow}</div><h1>{title}</h1>{lead_html}{extra}</div></div></section>'''


def cta(title='Ready to get started?',
        text='Tell Drew what the business is and what you want it to do. You get a plan and a price back.',
        primary=('Get a quote', '/contact'),
        secondary=('See the pricing', '/pricing')):
    """The last thing on every page."""
    return f'''<section class="cta-wrap"><div class="wrap"><div class="cta rv">
  <h2>{title}</h2><p>{text}</p>
  <div class="btn-row"><a class="btn" href="{u(primary[1])}">{primary[0]} {ICONS['arrow']}</a><a class="btn btn-ghost" href="{u(secondary[1])}">{secondary[0]}</a></div>
</div></div></section>'''


def swipe(slides, label, cls=''):
    """A slide rail you can throw with a finger, a mouse or the arrow keys.

    With JavaScript off it is still a native scroll-snap strip, so the arrows
    and the dots are enhancement rather than the only way through the slides.
    """
    items = ''.join(f'<div class="swipe-slide">{s}</div>' for s in slides)
    dots = ''.join(f'<button type="button" class="swipe-dot{" is-on" if i == 0 else ""}" '
                   f'data-dot="{i}" aria-label="Go to slide {i + 1}"></button>'
                   for i in range(len(slides)))
    return f'''<div class="swipe rv {cls}" data-swipe aria-roledescription="carousel" aria-label="{label}">
  <div class="swipe-rail" data-rail tabindex="0">{items}</div>
  <button class="swipe-arw prev" type="button" data-prev aria-label="Previous">{ICONS['chevL']}</button>
  <button class="swipe-arw next" type="button" data-next aria-label="Next">{ICONS['chevR']}</button>
  <div class="swipe-dots" data-dots>{dots}</div>
  <div class="swipe-hint" aria-hidden="true">Drag or swipe</div>
</div>'''


def price_card(key, bullets=(), featured=False, badge=None, cta_label='Get a quote'):
    """One package, priced from content.py and nowhere else.

    DGM's price_card() takes the figure as an argument and asserts it against
    the shop table; here the card simply cannot be given a figure — it is
    handed a key and reads the row. A card that quotes a price PRICING does not
    know is then impossible rather than merely caught.
    """
    p = price(key)
    qual = f'<span class="qual">{p["qualifier"]}</span>' if p['qualifier'] else ''
    note = f'<small>{p["note"]}</small>' if p['note'] else ''
    b = ''.join(f'<li>{x}</li>' for x in bullets)
    href = u(f'/contact?service={p["service"]}')
    return f'''<div class="price{' featured' if featured else ''} rv">
  {f'<span class="badge">{badge}</span>' if badge else ''}
  <span class="tier">{p['tier']}</span>
  <h3>{p['name']}</h3>
  <div class="amount">{qual}{' ' if qual else ''}{p['amount']}{note}</div>
  {f'<ul>{b}</ul>' if b else ''}
  <a class="btn" href="{href}">{cta_label}</a>
</div>'''


# ------------------------------------------------------------------- layout
def ld_json(ld):
    """A JSON-LD block that cannot end its own <script> element."""
    if not ld:
        return ''
    if isinstance(ld, list):
        ld = {'@context': 'https://schema.org', '@graph': ld}
    else:
        ld = {'@context': 'https://schema.org', **ld}
    return ('<script type="application/ld+json">'
            + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c')
            + '</script>')


def layout(path, title, desc, body, ld=None, noindex=False, og=None,
           extra_scripts=''):
    """The document around a page body.

    `extra_scripts` is markup appended after site.js — the hook for a script
    that belongs to exactly one page and that every other page should not have
    to download. /contact's form.js is the only one today. It defaults to empty,
    so a page dict that says nothing about scripts gets the document it always
    got.
    """
    canonical = BASE_URL + (path if path != '/index' else '/')
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else ''
    # An absolute URL built from BASE_URL and a bare path, never through u():
    # on the preview BASE_URL already ends in /p/<slug>, so prefixing it a
    # second time writes the slug twice and every share card 404s.
    og = og or OG_DEFAULT
    ogimg = f'<meta property="og:image" content="{BASE_URL}/assets/img/{og}">'
    if have(f'img/{og}'):
        w, h = png_size(os.path.join(SRC, 'out', 'img', og))
        ogimg += (f'<meta property="og:image:width" content="{w}">'
                  f'<meta property="og:image:height" content="{h}">')
    ogimg += f'<meta property="og:image:alt" content="{html.escape(title)}">'
    for f in FAVICONS:
        have(f'img/{f}')
    icons = (f'<link rel="icon" href="{u("/assets/img/favicon.ico")}" sizes="32x32">'
             f'<link rel="icon" href="{u("/assets/img/favicon.svg")}" type="image/svg+xml">'
             f'<link rel="icon" href="{u("/assets/img/favicon-32.png")}" type="image/png" sizes="32x32">'
             f'<link rel="apple-touch-icon" href="{u("/assets/img/apple-touch-icon.png")}">')
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(d){{var c=d.documentElement.classList;c.add('js');try{{if(!matchMedia('(prefers-reduced-motion: reduce)').matches)c.add('motion')}}catch(e){{}}var wide=false;try{{wide=matchMedia('(min-width: 900px)').matches}}catch(e){{}}var save=false;try{{var n=navigator.connection;save=!!(n&&n.saveData)}}catch(e){{}}window.mmPick=function(v){{if(!v||v.tagName!=='VIDEO'||!v.dataset.hi||!c.contains('motion')||save)return;if(wide)v.src=v.dataset.hi;v.preload='metadata';if(v.hasAttribute('data-autoplay'))v.setAttribute('autoplay','')}}}})(document)</script>
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
{robots}
<meta property="og:type" content="website"><meta property="og:site_name" content="{SITE_NAME}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{canonical}">
{ogimg}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{BG}">
{icons}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{u('/css/site.css')}?v={asset_v('css/site.css')}">
{ld_json(ld)}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{nav_html()}
<main id="main">
{body}
</main>
{footer_html()}
<div class="lb" role="dialog" aria-modal="true" aria-label="Media viewer"><div><div class="lb-inner"></div><div class="lb-cap"></div></div></div>
<script>window.MM={{form:{json.dumps(FORM_ENDPOINT)}}}</script>
<script src="{u('/js/site.js')}?v={asset_v('js/site.js')}" defer></script>{extra_scripts}
</body>
</html>'''


# ========================================================================
#  THE PAGES
#  A page long enough to have sections of its own lives in its own module and
#  is imported here: home.py is Home, section by section. Those modules are
#  pages of this file rather than libraries it uses — they reach back for u(),
#  pic() and the rest at call time, so this import stays one way and this file
#  is never executed twice. The six service pages, /work, /results, /about,
#  /pricing and /contact arrive in steps 4 and 6.
# ========================================================================
from home import home_page
from contact import contact_page

pages = {}

pages['/index'] = dict(
    title=seo_title(f"{SITE['tagline']}, Buffalo NY"),
    desc='Mendoza Marketing builds websites, runs Meta ad campaigns, films content '
         'and flies drones for businesses in Grand Island and Buffalo, New York.',
    body=home_page())

pages['/404'] = dict(
    title=seo_title('Page not found'),
    desc='That page is not here.',
    noindex=True,
    body=f'''
<section class="nf"><div class="wrap"><div class="hero-inner rv">
  <div class="mono">Error 404</div>
  <h1 class="h-two">Nothing here.<span>Let&rsquo;s go back.</span></h1>
  <p class="lead">The page you asked for does not exist, or it moved.</p>
  <div class="btn-row"><a class="btn" href="{u('/')}">Back to the home page {ICONS['arrow']}</a><a class="btn btn-ghost" href="{u('/contact')}">Get a quote</a></div>
</div></div></section>''')

from pages import inner_pages; pages.update(inner_pages())
# The quote form his README asks for, and the ways to reach him that are not a
# form. It carries its own script (site/js/form.js) rather than adding one to
# every page of the site — layout()'s `extra_scripts` is the hook.
pages['/contact'] = contact_page()


# ================================================================== the graph
#  What a machine reads instead of the page. Two rules run through all of it.
#
#  First, the business is described once, at a stable @id, and every other
#  block points at that id rather than repeating the name and the address — a
#  Service that re-states the business is a second business as far as a crawler
#  is concerned, and two Mendoza Marketings is worse than none.
#
#  Second, nothing in here is a fact the site does not already print. No street
#  address (Drew has not published one), no opening hours, no aggregate rating,
#  no founding date. `sameAs` is the socials from content.py, which today is an
#  empty list, and an empty list is what it stays until he sends the URLs: a
#  guessed profile link is a wrong answer given confidently.
# ============================================================================
BUSINESS_ID = f'{BASE_URL}/#business'
OG_URL = f'{BASE_URL}/assets/img/{OG_DEFAULT}'


def city(name):
    """A named place a crawler can match against a searcher's location."""
    return {'@type': 'City', 'name': name,
            'address': {'@type': 'PostalAddress', 'addressLocality': name,
                        'addressRegion': 'NY', 'addressCountry': 'US'}}


# Where he works, from the narrowest out: the island he is on, the city whose
# market he sells into, and the region both sit in.
AREA = [city('Grand Island'), city('Buffalo'),
        {'@type': 'AdministrativeArea', 'name': 'Western New York'}]

BUSINESS = {
  '@type': 'LocalBusiness',
  '@id': BUSINESS_ID,
  'name': SITE_NAME,
  'url': BASE_URL + '/',
  'description': pages['/index']['desc'],
  'slogan': SITE['tagline'],
  'email': SITE['email'],
  # The E.164 form of the same number the footer prints — content.py holds
  # both, and this is the one a machine can dial.
  'telephone': SITE['phone_href'],
  'image': OG_URL,
  'logo': OG_URL,
  'address': {'@type': 'PostalAddress', 'addressLocality': 'Grand Island',
              'addressRegion': 'NY', 'addressCountry': 'US'},
  'areaServed': AREA,
  'founder': {'@type': 'Person', 'name': SITE['owner']},
  'sameAs': [url for _label, _icon, url in SITE['socials'] if url],
  'knowsAbout': [s['name'] for s in SERVICES],
}


def money(amount):
    """'$1,250' -> '1250'. 'Commission or hourly' -> None, because a price
    nobody has set is not a number and must not be rendered as one."""
    n = amount.replace('$', '').replace(',', '').strip()
    return n if n.replace('.', '', 1).isdigit() else None


def offer(key):
    """One row of PRICING as an Offer. The figure comes from the same table the
    price card reads (rule 6), so the graph can never quote a price the page
    does not print."""
    row = PRICING[key]
    o = {'@type': 'Offer',
         'name': row['name'],
         'url': f'{BASE_URL}/pricing',
         'itemOffered': {'@type': 'Service', 'name': row['name'],
                         'provider': {'@id': BUSINESS_ID}}}
    amount = money(row['amount'])
    if amount is None:
        # Lead conversion: commission or hourly, and Drew has not set either.
        # The offer stays in the graph — he does sell it — with his own
        # sentence in place of a figure.
        o['description'] = f"{row['amount']}. {row['note'] or ''}".strip()
        return o
    o['price'] = amount
    o['priceCurrency'] = 'USD'
    o['availability'] = 'https://schema.org/InStock'
    if row['qualifier'] == 'from':
        # "from $1,250" is a floor, not a price. minPrice says exactly that.
        o['priceSpecification'] = {'@type': 'PriceSpecification',
                                   'priceCurrency': 'USD', 'minPrice': amount}
    return o


def service_prices(s):
    """Every package the service page actually prints, in page order — its own
    and any its `extra` block carries (/websites shows re-design under the
    fold). The graph offers exactly what the page offers, no more."""
    keys = list(s['prices'])
    keys += [k for k in (s.get('extra') or {}).get('prices', []) if k not in keys]
    return keys


def service_ld(s):
    """One service page as a Service, offered by the one business."""
    path = '/' + s['slug']
    return {
      '@type': 'Service',
      '@id': f'{BASE_URL}{path}#service',
      'name': s['name'],
      'serviceType': s['name'],
      'url': BASE_URL + path,
      'description': SEO[s['slug']]['meta'],
      'provider': {'@id': BUSINESS_ID},
      'areaServed': AREA,
      'offers': [offer(k) for k in service_prices(s)],
    }


CATALOG = {
  '@type': 'OfferCatalog',
  '@id': f'{BASE_URL}/pricing#catalog',
  'name': f'{SITE_NAME} packages',
  'url': f'{BASE_URL}/pricing',
  'provider': {'@id': BUSINESS_ID},
  'itemListElement': [offer(k) for k in PRICING],
}

PERSON = {
  '@type': 'Person',
  '@id': f'{BASE_URL}/about#drew',
  'name': SITE['owner'],
  'jobTitle': 'Founder',
  'worksFor': {'@id': BUSINESS_ID},
  'url': f'{BASE_URL}/about',
  'description': pages['/about']['desc'],
}
if have('img/drew-headshot.webp'):
    PERSON['image'] = f'{BASE_URL}/assets/img/drew-headshot.webp'

CONTACT_LD = {
  '@type': 'ContactPage',
  '@id': f'{BASE_URL}/contact#page',
  'url': f'{BASE_URL}/contact',
  'name': f'Contact {SITE_NAME}',
  'about': {'@id': BUSINESS_ID},
  'mainEntity': {'@id': BUSINESS_ID},
}

# Every public page carries the business; a page that is also something in its
# own right carries that too, in one @graph. /404 carries nothing: it is
# noindex, and there is no sense describing a page we ask not to be read.
for _path in pages:
    if _path != '/404':
        pages[_path]['ld'] = BUSINESS
for _s in SERVICES:
    pages['/' + _s['slug']]['ld'] = [BUSINESS, service_ld(_s)]
pages['/pricing']['ld'] = [BUSINESS, CATALOG]
pages['/about']['ld'] = [BUSINESS, PERSON]
pages['/contact']['ld'] = [BUSINESS, CONTACT_LD]


# --------------------------------------------------------------------- write
os.makedirs(OUT, exist_ok=True)

# Local convenience only: the pages ask for /assets/img and /assets/video,
# which deploy.sh rsyncs out of out/. Link them here so
# `python3 -m http.server -d site` serves a complete site while we are
# building. Nothing in the deployed tree depends on these links.
for kind in ('img', 'video'):
    src_dir = os.path.join(SRC, 'out', kind)
    link = os.path.join(OUT, 'assets', kind)
    if os.path.isdir(src_dir) and not os.path.exists(link):
        os.makedirs(os.path.dirname(link), exist_ok=True)
        os.symlink(os.path.relpath(src_dir, os.path.dirname(link)), link)

_titles = [p['title'] for p in pages.values()]
assert len(set(_titles)) == len(_titles), 'two pages share a title'
# seo_title() has already checked every title's length; this is the other half
# of the same rule. A description over DESC_MAX is cut mid-word in the result,
# which reads as carelessness on a page whose whole job is to look professional.
for _path, _p in pages.items():
    assert len(_p['desc']) <= DESC_MAX, \
        f"{_path}: description is {len(_p['desc'])} characters, over {DESC_MAX}"

concat_css()

for path, p in pages.items():
    fn = os.path.join(OUT, path.strip('/') + '.html')
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, 'w') as f:
        f.write(layout(path, p['title'], p['desc'], p['body'], p.get('ld'),
                       p.get('noindex', False), p.get('og'),
                       p.get('extra_scripts', '')))
    print('wrote', fn)

# sitemap + robots. A page marked noindex is a working page, not a public one:
# it must not be advertised in the sitemap any more than it should be indexed.
#
# lastmod is the build date. The site is generated from this repo in one pass,
# so every page is exactly as old as the build that made it — a per-page date
# would have to come from git, and a date that is a guess is worse than a date
# that is honest about being the whole site's.
LASTMOD = datetime.date.today().isoformat()
urls = [BASE_URL + ('/' if p == '/index' else p) for p, d in pages.items()
        if p != '/404' and not d.get('noindex')]
with open(os.path.join(OUT, 'sitemap.xml'), 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + ''.join(f'<url><loc>{x}</loc><lastmod>{LASTMOD}</lastmod></url>'
                      for x in urls) + '</urlset>\n')

# Under a PREFIX the build is a preview, and a preview is never indexed.
# publish-preview.sh already overwrites robots.txt in its staging copy AFTER
# rsyncing site/ into it, and deletes the sitemap, so the published preview is
# closed whatever this writes — but a build under a prefix that leaves an
# "Allow: /" robots lying in site/ is a trap waiting for the day somebody
# copies that directory somewhere else by hand. It says Disallow instead, and
# names no sitemap, so the two agree.
with open(os.path.join(OUT, 'robots.txt'), 'w') as f:
    if PREFIX:
        f.write('User-agent: *\nDisallow: /\n')
    else:
        f.write(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n')
print('wrote', os.path.join(OUT, 'sitemap.xml'), 'and robots.txt')

# Soft asserts, printed rather than raised — the media is being made in
# parallel and the scaffold has to be reviewable before it lands.
if MISSING:
    print(f'\n! {len(MISSING)} asset(s) the pages ask for and out/ does not have yet:')
    for rel in MISSING:
        print(f'    out/{rel}')
    print('  (the media pipeline writes these; the markup is already correct)')
if TODO:
    print(f'\n? {len(TODO)} thing(s) still owed by Drew (content.py):')
    for t in TODO:
        print(f'    {t}')
