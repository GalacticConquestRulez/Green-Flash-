#!/usr/bin/env python3
"""Every inner page of the Mendoza Marketing site: the six service pages,
/pricing, /work, /results and /about.

build.py owns the frame — layout(), the nav, the footer, page_hero(), cta(),
swipe(), price_card() — and this file owns what goes between. It is a separate
module for one reason: Home and the inner pages were built at the same time by
two people, and two people editing one 1,500-line generator is how a block goes
missing in a merge. build.py calls inner_pages() once, from the bottom, and
that is the only line of it this file touches.

Nothing here holds a fact. Every sentence comes from content.py (which holds
Drew's own words, from his current site) and every figure from FIGURES below,
which is the temporary local copy of what results.py will own.

    /websites /meta-ads /social /logo /drones /lead-conversion
    /pricing /work /results /about
"""
import html
import re

from content import (SITE, SERVICES, PRICING, BY_SLUG, CLIENTS, CASE, SITES,
                     REELS, DRONE_CLIPS, ABOUT, BEATS, price, price_text)


# --------------------------------------------------------------- the builder
def _b():
    """The build module that is running us.

    build.py imports this file from its own bottom, so `import build` here
    would load and execute the whole generator a second time — a second write
    loop, a second sitemap, and every page rendered twice. The module object we
    want is already in sys.modules under the name the process started it with,
    which is '__main__' when someone runs `python3 build.py`. Falling through
    to a real import is for the case where this file is imported on its own,
    from a test or a shell, and build.py is not the program.
    """
    import sys
    for name in ('build', '__main__'):
        m = sys.modules.get(name)
        if m is not None and hasattr(m, 'page_hero'):
            return m
    import build as m
    return m


# --------------------------------------------------------------- small parts
def txt(s):
    """Markup down to the sentence inside it, for a <meta> description."""
    return html.unescape(re.sub(r'<[^>]+>', ' ', s)).replace('  ', ' ').strip()


def two_tone(title, words=1):
    """His heading, with its last word (or two) wrapped for the green line.

    The two-tone headline is the one move Drew picked out of Ellesmere by
    name, so every heading on the site does it; splitting the last word off
    his own heading does it without writing him a new one.
    """
    parts = title.split(' ')
    if len(parts) <= words:
        return f'<span>{title}</span>'
    return ' '.join(parts[:-words]) + f'<span>{" ".join(parts[-words:])}</span>'


def section(inner, cls='', sid=''):
    c = f' class="{cls}"' if cls else ''
    i = f' id="{sid}"' if sid else ''
    return f'<section{c}{i}><div class="wrap">{inner}</div></section>'


def sec_head(eyebrow, title, aside=''):
    """Mockup's section head: eyebrow over a two-tone h2, something on the
    right at desktop width, stacked under it on a phone."""
    a = f'<div class="sec-aside">{aside}</div>' if aside else ''
    return (f'<div class="sec-head rv"><div><div class="eyebrow">{eyebrow}</div>'
            f'<h2>{title}</h2></div>{a}</div>')


def prose(paras):
    return '<div class="prose rv">' + ''.join(f'<p>{p}</p>' for p in paras) + '</div>'


def bd_panel(title, bullets, price_line=None, price_key=None):
    """His "… Breakdown" block, as the panel card beside the prose.

    The price sentence is his; the figure in it is interpolated from PRICING,
    so this panel and the price card below it cannot drift apart and no number
    is typed into a page body (CLAUDE.md rule 6).
    """
    items = []
    if price_line and price_key:
        line = price_line.format(amount=price(price_key)['amount'])
        items.append(f'<li class="bd-price">{line}</li>')
    items += [f'<li>{b}</li>' for b in bullets]
    return (f'<aside class="bd panel rv"><h3 class="bd-h">{title}</h3>'
            f'<ul>{"".join(items)}</ul></aside>')


def inc_cards(trio):
    return '<div class="grid grid-3 inc">' + ''.join(
        f'<div class="inc-card panel rv rv-d{i + 1}"><h3>{h}</h3><p>{t}</p></div>'
        for i, (h, t) in enumerate(trio)) + '</div>'


def price_row(keys, bullets=None, featured=None, cls=''):
    """A row of price cards, each one reading its own row of PRICING."""
    B = _b()
    bullets = bullets or {}
    cards = ''.join(B.price_card(k, bullets=bullets.get(k, ()),
                                 featured=(k == featured)) for k in keys)
    cols = min(len(keys), 3)
    return f'<div class="grid grid-{cols} prices prices-{len(keys)} {cls}">{cards}</div>'


TBC = ('<span class="tbc">Tier contents &mdash; to confirm with Drew</span>',)


# ------------------------------------------------------------ service pages
def service_page(s):
    """One of the six. Hero, his opening block beside his breakdown, his
    "Included" trio, the second block where his page has one, the price
    card(s), and a quote CTA that arrives at /contact with the service already
    chosen."""
    B = _b()
    slug, name = s['slug'], s['name']
    quote = B.u(f'/contact?service={slug}')
    out = []

    out.append(B.page_hero(
        name, s['hero_title'], s['lead'], crumb=name,
        extra=(f'<div class="hero-price mono">{price_text(s["price_key"])}</div>'
               f'<div class="btn-row">'
               f'<a class="btn" href="{quote}">Get a quote {B.ICONS["arrow"]}</a>'
               f'<a class="btn btn-ghost" href="#pricing">See the pricing</a>'
               f'</div>')))

    out.append(section(
        f'<div class="split">{prose(s["intro"])}'
        f'{bd_panel(s["breakdown_title"], s["breakdown"], s["breakdown_price"], s["price_key"])}'
        f'</div>'))

    out.append(section(
        sec_head('Included', two_tone(s['included_title'])) + inc_cards(s['included']),
        cls='band-alt'))

    if slug == 'drones':
        out.append(drone_rail())

    ex = s['extra']
    if ex:
        inner = [sec_head(ex['eyebrow'], ex['title'])]
        if ex.get('breakdown'):
            inner.append(f'<div class="split">{prose(ex["paras"])}'
                         f'{bd_panel(ex["breakdown_title"], ex["breakdown"], ex.get("breakdown_price"), ex["prices"][0])}'
                         f'</div>')
        else:
            inner.append(prose(ex['paras']))
        if ex.get('prices'):
            inner.append(price_row(ex['prices']))
        if ex.get('link'):
            label, href = ex['link']
            inner.append(f'<div class="btn-row rv"><a class="btn btn-ghost" '
                         f'href="{B.u(href)}">{label}</a></div>')
        out.append(section(''.join(inner), cls='band-alt' if slug == 'social' else ''))

    bullets = {k: TBC for k in s['prices']} if slug == 'social' else None
    words = ' prices-words' if slug == 'lead-conversion' else ''
    out.append(section(
        sec_head('Pricing', 'What it<span>costs.</span>',
                 aside=f'<a class="btn btn-ghost" href="{B.u("/pricing")}">Every package</a>')
        + price_row(s['prices'], bullets=bullets, cls=words.strip()),
        sid='pricing'))

    out.append(B.cta(
        title=f'Ready to start on {name.lower()}?',
        text='Tell Drew what the business is and what you want it to do. '
             'You get a plan and a price back.',
        primary=('Get a quote', f'/contact?service={slug}'),
        secondary=('See the results', '/results')))

    return dict(
        title=f'{name} | {SITE["name"]}',
        desc=txt(s['lead'])[:300],
        og='logo',
        body='\n'.join(out))


def drone_rail():
    """The six clips from one real-estate shoot.

    controls + preload="none" + a poster: the rail costs a poster image until
    somebody presses play, nothing plays by itself, and nothing makes a sound
    unasked. The rail is a native scroll-snap strip with no script at all.
    """
    B = _b()
    slides = []
    for i, (name, caption) in enumerate(DRONE_CLIPS, 1):
        poster, src = B.clip(name)
        slides.append(
            f'<figure class="clip-card">'
            f'<video controls preload="none" playsinline poster="{poster}">'
            f'<source src="{src}" type="video/mp4"></video>'
            f'<figcaption><span class="mono">Clip {i}</span>{caption}</figcaption>'
            f'</figure>')
    return section(
        sec_head('The footage', 'One shoot,<span>outside in.</span>',
                 aside='<p class="sec-note">A real-estate session, in the order the '
                       'house is revealed. Press play on any of them.</p>')
        + B.swipe(slides, 'Clips from a drone session', cls='clip-rail'),
        cls='band-alt')


# ---------------------------------------------------------------------- all
def inner_pages():
    """Every page in this file, keyed the way build.py's write loop wants it."""
    out = {}
    for s in SERVICES:
        out['/' + s['slug']] = service_page(s)
    return out
