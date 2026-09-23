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

import art
import re

from content import (SITE, SERVICES, SEO, PRICING, BY_SLUG, CLIENTS, CASE,
                     SITES, REELS, DRONE_CLIPS, ABOUT, BEATS, price, price_text)
from results import (DASH1, DASH2, DASH3, DASH5, CONTENT_TYPES, LEADS,
                     bar_pct, leads_points)


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
        f'<div class="inc-card panel rv rv-d{i + 1}">'
        f'<span class="f-ico">{art.feature(h)}</span><h3>{h}</h3><p>{t}</p></div>'
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


def stat(f):
    """One dashboard tile, from one results.py figure.

    `f['value']` is in the HTML as text, so the page is complete and identical
    with no script and under prefers-reduced-motion. data-count and its
    formatting attributes describe how to get back to that same string by
    arithmetic, which is step 5's hook and nothing more: the count-up cannot
    land on a number the server did not already send.
    """
    attrs = ''
    if f.get('count') is not None:
        attrs = f' data-count="{f["count"]}"'
        for k in ('decimals', 'prefix', 'suffix'):
            if f.get(k):
                attrs += f' data-{k}="{f[k]}"'
    delta = f'<i class="stat-delta">{f["delta"]}</i>' if f.get('delta') else ''
    note = f'<span class="stat-note">{f["note"]}</span>' if f.get('note') else ''
    return (f'<div class="stat panel rv">'
            f'<span class="stat-label">{f["label"]}</span>'
            f'<b class="stat-num"{attrs}>{f["value"]}</b>{delta}{note}</div>')


def stats_row(figs, caption, cls='grid-4'):
    tiles = ''.join(stat(f) for f in figs)
    return (f'<div class="grid {cls} stats">{tiles}</div>'
            f'<p class="fig-cap rv">{caption}</p>')


def bars(caption, rows):
    """A bar row: (name, percent, printed value).

    The width is inline so it is right with no script; data-w repeats it so
    step 5 can run the bars out from zero under html.motion. The percentages
    are computed from the figures by results.bar_pct(), never typed, so the
    shape of the row cannot drift from the numbers printed beside it.
    """
    body = ''.join(
        f'<div class="bar"><span class="bar-name">{n}</span>'
        f'<div class="bar-track"><b style="width:{p}%" data-w="{p}"></b></div>'
        f'<span class="bar-val">{v}</span></div>'
        for n, p, v in rows)
    return (f'<div class="panel figure rv" data-bars>'
            f'<div class="fig-h">{caption}</div>{body}</div>')


def chart(caption, points, label):
    """The daily-leads line, drawn in the markup so a reader with no script
    sees the same shape. data-chart is step 5's hook to draw it on."""
    pts = ' '.join(f'{x},{y}' for x, y in points)
    last_x = points[-1][0]
    return (f'<div class="panel figure rv" data-chart>'
            f'<div class="fig-h">{caption}</div>'
            f'<div class="chart"><svg viewBox="0 0 300 100" preserveAspectRatio="none" '
            f'role="img" aria-label="{html.escape(label)}">'
            f'<polyline class="chart-fill" points="{pts} {last_x},100 0,100"></polyline>'
            f'<polyline class="chart-line" points="{pts}"></polyline>'
            f'</svg></div></div>')


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
        title=B.seo_title(SEO[slug]['head']),
        desc=SEO[slug]['meta'],
        og=f"og-{slug}.png",
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


# ------------------------------------------------------------------ /pricing
def pricing_page():
    B = _b()
    groups = []
    for s in SERVICES:
        keys = [k for k, p in PRICING.items() if p['service'] == s['slug']]
        if not keys:
            continue
        bullets = {k: TBC for k in keys} if s['slug'] == 'social' else None
        words = 'prices-words' if s['slug'] == 'lead-conversion' else ''
        about = (f'<a class="btn btn-ghost" href="{B.u("/" + s["slug"])}">'
                 f'About this service</a>')
        groups.append(
            '<div class="pg-group">'
            + sec_head(s['name'], two_tone(s['name'], 1), aside=about)
            + price_row(keys, bullets=bullets, cls=words)
            + '</div>')
    return dict(
        title=B.seo_title('Pricing for every package'),
        desc='Every Mendoza Marketing package and what it costs: website design and '
             're-design, Meta ads and filming, social media, logo design and drone '
             'sessions.',
        body='\n'.join([
            B.page_hero('Pricing', 'Every package.<span>Every price.</span>',
                        'What each service costs, up front. Where a job is bigger '
                        'than the package, the price moves with it &mdash; and you '
                        'are told before anything starts.',
                        crumb='Pricing'),
            section('\n'.join(groups)),
            B.cta(title='Not sure which one you need?',
                  text='Tell Drew what the business is and what you want it to do. '
                       'You get a plan and a price back.',
                  primary=('Get a quote', '/contact'),
                  secondary=('See the results', '/results')),
        ]))


# --------------------------------------------------------------------- /work
def work_page():
    B = _b()
    logos = ''.join(
        f'<div class="logo-card panel rv rv-d{i % 3 + 1}">'
        f'<div class="logo-shot">{B.pic(c["slug"], c["name"] + " logo", B.CARD_SIZES)}</div>'
        f'<h3>{c["name"]}</h3>'
        f'<p class="mono logo-work">{c["work"]}</p>'
        f'<p class="logo-note">{c["detail"] or "Details to confirm with Drew."}</p>'
        f'</div>' for i, c in enumerate(CLIENTS))

    renders = ''.join(
        f'<figure class="case-shot rv">{B.pic(slug, alt, "(min-width:960px) 45vw, 100vw")}'
        f'<figcaption>{alt}</figcaption></figure>' for slug, alt in CASE['renders'])

    sites = ''.join(
        f'<div class="site-card panel rv rv-d{i % 3 + 1}"><h3>{s["name"]}</h3>'
        f'<p class="mono logo-work">{s["work"]}</p><p>{s["blurb"]}</p></div>'
        for i, s in enumerate(SITES))

    reels = ''.join(reel_card(slug, title, sub) for slug, title, sub in REELS)

    return dict(
        title=B.seo_title('Work, brands and client reels'),
        desc='Brands, websites and content by Mendoza Marketing: logo and brand '
             'work, the Isle de Grande logo, and reels running on client pages '
             'around Buffalo, NY.',
        body='\n'.join([
            B.page_hero('Work', 'The marks.<span>The films.</span>',
                        'A selection of what Drew has built &mdash; the logos, the '
                        'websites and the content. There is more of it than fits on '
                        'one page: ask him what he has done in your line of business.',
                        crumb='Work'),
            section(sec_head('Brands', 'Logo and<span>brand work.</span>')
                    + f'<div class="grid grid-4 logos">{logos}</div>'),
            section(sec_head(CASE['work'],
                             f'{CASE["name"]}<span>{CASE["blurb"]}</span>',
                             aside=f'<a class="btn btn-ghost" href="{B.u("/logo")}">'
                                   f'About logo design</a>')
                    + f'<div class="grid grid-2 case">{renders}</div>',
                    cls='band-alt'),
            section(sec_head('Websites', 'Built and<span>launched.</span>')
                    + f'<div class="grid grid-3 sites">{sites}</div>'),
            section(sec_head('Content in action', 'Made for the feed.<span>Filmed for the client.</span>',
                             aside='<p class="sec-note">Kelly&rsquo;s Country Store &mdash; '
                                   'viral content management and Meta ad campaigns.</p>')
                    + f'<div class="grid grid-3 reels">{reels}</div>',
                    cls='band-alt'),
            B.cta(primary=('Get a quote', '/contact'),
                  secondary=('See the results', '/results')),
        ]))


def reel_card(slug, title, sub):
    """One vertical reel in a phone frame. Sound is part of the work, so these
    are never autoplayed and never muted-by-default: the visitor presses play."""
    B = _b()
    poster, src = B.clip(slug)
    return (f'<figure class="reel rv">'
            f'<div class="phone"><video controls preload="none" playsinline '
            f'poster="{poster}"><source src="{src}" type="video/mp4"></video></div>'
            f'<figcaption><b>{title}</b><span class="mono">{sub}</span></figcaption>'
            f'</figure>')


# ------------------------------------------------------------------ /results
def results_page():
    """The six dashboards in full, each block captioned with whose page it is
    and over what window. Every figure comes from results.py; this file knows
    none of them."""
    B = _b()
    # The bar widths are computed from the numbers, and the split's other half
    # is arithmetic on his own figure rather than a second typed percentage.
    content_rows = [(name, bar_pct(value), shown)
                    for name, shown, value in CONTENT_TYPES['rows']]
    split = DASH3[3]                       # 87.6% of the reach were not followers
    followers = round(100 - split['count'], 1)
    audience_rows = [('Non-followers', split['count'], split['value']),
                     ('Followers', followers, f'{followers}%')]
    return dict(
        title=B.seo_title('Client results and dashboards'),
        desc='The client dashboards in full: 344,880 views in 28 days, 569,027 over '
             '90, and 614 leads through the Meta Leads Center.',
        body='\n'.join([
            B.page_hero('Results', 'Real dashboards.<span>Real numbers.</span>',
                        'Every figure on this page is read off a client\u2019s own '
                        'dashboard. Nothing is modelled, projected or rounded up.',
                        crumb='Results'),
            section(
                sec_head('28 days', 'One page,<span>four weeks.</span>')
                + stats_row(DASH1,
                            'A client page under Mendoza Marketing management · '
                            'last 28 days, against the 28 before it. The screenshot '
                            'does not name the page, so neither does this one.')),
            section(
                sec_head('Kelly&rsquo;s Country Store', 'The same month,<span>a busier page.</span>')
                + stats_row(DASH2,
                            'Kelly&rsquo;s Country Store · last 28 days, against the '
                            '28 before it. Viral content management and Meta ads.'),
                cls='band-alt'),
            section(
                sec_head('90 days', 'A quarter of<span>the same work.</span>')
                + stats_row(DASH3[:2],
                            f'The same client page · last 90 days. {split["value"]} '
                            'of the people who watched were not following the page '
                            'when they did.', cls='grid-2')
                + f'<div class="grid grid-2 figures">'
                + bars('Who watched · 90 days', audience_rows)
                + bars(f'{CONTENT_TYPES["label"]} · '
                       f'{CONTENT_TYPES["total"]["value"]} viewers reached',
                       content_rows)
                + '</div>'),
            section(
                sec_head('Meta Leads Center', 'Leads in,<span>day after day.</span>')
                + '<div class="grid grid-2 figures">'
                + f'<div class="grid stats stats-1">{stat(DASH5[0])}</div>'
                + chart(f'{LEADS["label"]} · {LEADS["range"]}', leads_points(),
                        'Daily new leads over ninety days, from about twelve a day '
                        'to a peak of thirty-seven')
                + '</div>'
                + '<p class="fig-cap rv">Meta Leads Center · intake leads over the '
                  'reporting window, up 27.4% on the window before it. The daily '
                  'chart counts every new lead, which is not the same number.</p>',
                cls='band-alt'),
            B.cta(title='Want numbers like these?',
                  text='This is what a page looks like after a few months of content '
                       'and campaigns. Tell Drew where yours is now.',
                  primary=('Get a quote', '/contact'),
                  secondary=('See the pricing', '/pricing')),
        ]))


# -------------------------------------------------------------------- /about
def about_page():
    B = _b()
    lead_slug, lead_alt = ABOUT['photo_lead']
    # The class carries the crop: these are phone photographs of very
    # different shapes, and the one in the leaves is a noisy full-figure frame
    # that wants cropping in to him rather than showing every leaf.
    photos = ''.join(
        f'<figure class="ph ph-{slug} rv rv-d{i + 1}">'
        f'{B.pic(slug, alt, "(min-width:960px) 33vw, 50vw")}</figure>'
        for i, (slug, alt) in enumerate(ABOUT['photos']))
    spec = ''.join(f'<li>{x}</li>' for x in ABOUT['specialize'])
    beats = ''.join(
        f'<div class="beat rv rv-d{i + 1}"><span class="f-ico">{art.feature(t)}</span>'
        f'<div class="mono">{n} · {t}</div>'
        f'<h3>{line}</h3></div>' for i, (n, t, line) in enumerate(BEATS))

    return dict(
        title=B.seo_title('About Drew Mendoza, Grand Island NY'),
        desc='At Mendoza Marketing, our mission is to help small and mid-sized '
             'businesses grow and compete online with data-driven marketing and '
             'measurable results.',
        body='\n'.join([
            B.page_hero('About', ABOUT['hero_title'], ABOUT['lead'], crumb='About Drew'),
            section(
                '<div class="bio">'
                f'<figure class="bio-shot rv">'
                f'{B.pic(lead_slug, lead_alt, "(min-width:960px) 420px, 100vw")}'
                f'<figcaption>{lead_alt}</figcaption></figure>'
                '<div class="bio-copy rv">'
                f'<div class="eyebrow">{ABOUT["specialize_title"]}</div>'
                f'<ul class="spec">{spec}</ul>'
                f'<h2>{two_tone(ABOUT["together_title"], 2)}</h2>'
                f'<p class="lead">{ABOUT["together"]}</p>'
                f'<div class="btn-row"><a class="btn" href="{B.u("/contact")}">'
                f'Get a quote {B.ICONS["arrow"]}</a>'
                f'<a class="btn btn-ghost" href="{B.u("/work")}">See the work</a></div>'
                '</div></div>'),
            section(f'<div class="grid grid-3 photos">{photos}</div>', cls='band-alt'),
            section(sec_head('How it goes', 'Design.<span>Launch. Grow.</span>')
                    + f'<div class="grid grid-3 beats">{beats}</div>'),
            B.cta(title='Let&rsquo;s build something great together.',
                  text='Tell Drew what the business is and what you want it to do. '
                       'You get a plan and a price back.',
                  primary=('Get a quote', '/contact'),
                  secondary=('See the pricing', '/pricing')),
        ]))


# ---------------------------------------------------------------------- all
def inner_pages():
    """Every page in this file, keyed the way build.py's write loop wants it."""
    out = {}
    for s in SERVICES:
        out['/' + s['slug']] = service_page(s)
    out['/pricing'] = pricing_page()
    out['/work'] = work_page()
    out['/results'] = results_page()
    out['/about'] = about_page()
    return out
