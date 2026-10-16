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
import os

import art
import campaign
import results
import re

from content import (LOGO_CASES, WEB_FEATURES, price_range,
                     SITE, SERVICES, SEO, PRICING, BY_SLUG, CLIENTS, CASE,
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


def campaign_results():
    """Previous campaign results on /meta-ads (Drew, 2026-10-11: "Highlight
    1,996 incoming leads over 90 days (July 9 – October 9) … make this section
    visually engaging with subtle animated statistics or charts").

    The headline counts up on its rolling wheels and the 90 days fill in under
    it; beside it, his daily-leads chart draws itself. That chart is dash-6,
    an earlier window than the headline, and says so in its caption — the
    Jul 9 – Oct 9 daily series is in the screenshots he sent, which did not
    arrive. When they do, results.py gets that series and the caption changes.
    Converted leads and conversion rates are left out on his instruction.
    """
    lead, daily = results.DASH7
    s = results.LEADS['series']
    months = ''.join(f'<span>{m}</span>' for m in ('Jul 9', 'Aug', 'Sep', 'Oct 9'))
    big = (f'<div class="cr-big panel rv">'
           f'<span class="stat-label">{lead["label"]}</span>'
           f'<b class="cr-num stat-num" data-count="{lead["count"]}">{lead["value"]}</b>'
           f'<span class="cr-when">{lead["note"]} &middot; Meta Leads Center</span>'
           f'<div class="cr-span" aria-hidden="true"><i></i></div>'
           f'<div class="cr-months mono" aria-hidden="true">{months}</div>'
           f'<div class="cr-sub"><b class="mono" data-count="{daily["count"]}">'
           f'{daily["value"]}</b><span>{daily["label"].lower()} &middot; '
           f'{daily["note"]}</span></div></div>')
    graph = chart(f'{results.LEADS["label"]} &middot; {results.LEADS["range"]}',
                  results.leads_points(),
                  f'{results.LEADS["label"]}, {results.LEADS["range"]}: between '
                  f'{min(s)} and {max(s)} a day')
    note = (f'<p class="fig-cap rv">From Meta&rsquo;s Leads Center, on campaigns '
            f'Mendoza Marketing manages. The daily chart is an earlier window: '
            f'{results.LEADS["range"]}, between {min(s)} and {max(s)} new leads a '
            f'day.</p>')
    return section(
        sec_head('Campaign results', 'Real campaigns.<span>Real leads.</span>')
        + f'<div class="cr">{big}{graph}</div>{note}', cls='cr-sec')


def logo_cases():
    """Before and after, one row per transformation (content.LOGO_CASES).

    A row needs both files on disk; have() lists the missing one at the end of
    the build (CLAUDE.md rule 10) and the row is left out until it lands. No
    rows, no section. Both logos sit on the same light plate, because a
    client's mark is drawn for white and the comparison has to be fair.
    """
    B = _b()
    rows = ''
    for c in LOGO_CASES:
        if not (B.have(f'img/{c["before"]}.webp') and B.have(f'img/{c["after"]}.webp')):
            continue
        side = lambda slug, k, alt: (
            f'<figure class="ba-side ba-{k.lower()}"><span class="ba-k mono">{k}</span>'
            f'<div class="ba-plate">{B.pic(slug, alt, "(min-width:960px) 480px, 90vw")}'
            f'</div></figure>')
        rows += (f'<div class="ba rv">'
                 + side(c['before'], 'Before', f'The old {c["name"]} logo')
                 + f'<span class="ba-arrow" aria-hidden="true">{B.ICONS["arrow"]}</span>'
                 + side(c['after'], 'After', f'The new {c["name"]} logo')
                 + f'<p class="ba-cap"><b>{c["name"]}</b> &middot; {c["what"]}</p></div>')
    if not rows:
        return ''
    return section(sec_head('Before &amp; after', 'Old mark.<span>New brand.</span>',
                            aside='<p class="sec-note">Logos we have redrawn, '
                                  'side by side.</p>')
                   + f'<div class="ba-list">{rows}</div>', sid='before-after')


def brand_tie_in():
    """After the logo, the brand (Drew, 2026-10-12: "Similar to Max's page, add
    a section encouraging customers to build their brand after getting their
    logo. Mainly promote Website Design with a button linking to that
    service"). Max's is a closing strip pairing a logo with a website build;
    this is the same move, with the website package's own card — its price
    and its four features read off PRICING, so nothing here can drift from
    /websites. The sentence on the left is NEW COPY, for Drew to approve."""
    B = _b()
    feats = ''.join(f'<li><span><b>{t}</b> &ndash; {d}</span></li>' for t, d in WEB_FEATURES)
    card = (f'<div class="tie-card panel rv">'
            f'<div class="tie-top"><span class="ico">{art.icon("websites")}</span>'
            f'<span class="tie-price mono">{price_text("web-design")}</span></div>'
            f'<h3>Website design</h3><ul>{feats}</ul>'
            f'<div class="btn-row"><a class="btn" href="{B.u("/websites")}">'
            f'Explore website design {B.ICONS["arrow"]}</a></div></div>')
    also = (f'<p class="tie-also">Also pairs well with '
            f'<a href="{B.u("/social")}">social media</a> and '
            f'<a href="{B.u("/meta-ads")}">performance marketing</a>.</p>')
    words = (f'<div class="tie-words rv"><p class="lead">A great logo needs '
             f'somewhere to live. Put yours to work on a website built around it '
             f'&mdash; the same colours, the same polish, designed to turn visitors '
             f'into customers.</p><p class="sec-note">Starting with a logo? Ask for '
             f'the website in the same quote and we will plan the two together.</p>'
             f'{also}</div>')
    return section(sec_head('Build the brand',
                            'Your logo is the start.<span>Build the brand around it.</span>')
                   + f'<div class="tie">{words}{card}</div>', cls='band-alt tie-sec')


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

    hero_price = (price_range(s['prices']) if s.get('hero_price') == 'range'
                  else price_text(s['price_key']))
    proof = ''
    if s.get('hero_proof'):
        # Drew's own results, as text: on a desktop they float in the hero
        # beside the words, on a phone they sit under the buttons.
        proof = ('<ul class="hero-proof">'
                 + ''.join(f'<li class="mono rv rv-d{i + 1}"><i></i>{t}</li>'
                           for i, t in enumerate(s['hero_proof']))
                 + '</ul>')
    out.append(B.page_hero(
        name, s['hero_title'], s['lead'], crumb=name,
        backdrop=s.get('hero_backdrop'),
        extra=(f'<div class="hero-price mono">{hero_price}</div>'
               f'<div class="btn-row">'
               f'<a class="btn" href="{quote}">Get a quote {B.ICONS["arrow"]}</a>'
               f'<a class="btn btn-ghost" href="#pricing">See the pricing</a>'
               f'</div>{proof}')))

    link = ''
    if s.get('intro_link'):
        label, href = s['intro_link']
        link = (f'<div class="btn-row rv"><a class="btn btn-ghost" '
                f'href="{B.u(href)}">{label} {B.ICONS["arrow"]}</a></div>')
    out.append(section(
        f'<div class="split"><div>{prose(s["intro"])}{link}</div>'
        f'{bd_panel(s["breakdown_title"], s["breakdown"], s["breakdown_price"], s["price_key"])}'
        f'</div>'))

    out.append(section(
        sec_head('Included', two_tone(s['included_title'])) + inc_cards(s['included']),
        cls='band-alt'))

    if slug == 'social':
        out.append(kelly_dashboard())

    if slug == 'drones':
        out.append(drone_arsenal())
        out.append(drone_film())
        out.append(drone_rail())

    if slug == 'lead-conversion':
        out.append(lead_hub())

    if slug == 'meta-ads':
        out.append(campaign_results())
        mgmt = (f'Management is {price_text("meta-ads").replace("/", " a ")}'
                f', on top.')
        out.append(section(campaign.section(
            sec_head('Campaign preview', 'Set a budget.<span>See the reach.</span>',
                     aside='<p class="sec-note">Move the dials to see what a '
                           'campaign could look like before it starts.</p>'),
            mgmt), cls='band-alt', sid='preview'))

    if slug == 'logo':
        out.append(logo_cases())

    ex = s.get('extra')
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

    if slug == 'lead-conversion':
        out.append(lead_quote())
    else:
        out.append(section(
            sec_head('Pricing', 'What it<span>costs.</span>',
                     aside=f'<a class="btn btn-ghost" href="{B.u("/pricing")}">Every package</a>')
            + price_row(s['prices']),
            sid='pricing'))

    if slug == 'logo':
        out.append(brand_tie_in())

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


# ------------------------------------------------------- /social: Kelly's
def kelly_dashboard():
    """Kelly's Country Store as an analytics dashboard (Drew, 2026-10-15).

    The tiles are dash-2, Kelly's own 28-day Insights, counting up on their
    wheels like every dashboard figure on the site. The follower-growth chart
    is drawn only from results.KELLY['growth'] — his numbers from the start
    through the first year, which he is sending; until then it is absent, not
    sketched. The two highlights are his own statements, set as words with no
    invented figures behind them; the package is read off PRICING.
    """
    B = _b()
    k = results.KELLY
    views, _pay, eng, fol = DASH2
    tiles = ''.join(stat(f) for f in (views, eng, fol))

    growth = ''
    if k.get('growth'):
        pts = k['growth']
        top = max(n for _, n in pts)
        step = 300 / (len(pts) - 1)
        line = [(round(i * step, 1), round(96 - n / top * 88, 1)) for i, (_, n) in enumerate(pts)]
        growth = chart(f'Followers · {pts[0][0]} – {pts[-1][0]}', line,
                       f'Kelly’s followers from {pts[0][1]:,} to {pts[-1][1]:,}')

    em = PRICING['social-emerald']
    per = f'/{em["per"]}' if em.get('per') else ''
    links = (f'<a class="kd-link" href="{k["instagram"]}" target="_blank" rel="noopener">'
             f'{B.ICONS["ig"]}<span>Instagram</span></a>'
             f'<a class="kd-link" href="{k["facebook"]}" target="_blank" rel="noopener">'
             f'{B.ICONS["fb"]}<span>Facebook</span></a>')
    high = (
        '<div class="kd-hl rv rv-d1"><span class="kd-k mono">Reels</span>'
        '<b class="kd-big mono">100K+</b>'
        '<p>Multiple reels past 100,000 views, every one filmed on-site at the store.</p></div>'
        '<div class="kd-hl rv rv-d2"><span class="kd-k mono">Fall Fest</span>'
        '<b class="kd-big">Biggest turnout</b>'
        '<p>Their biggest Fall Fest crowd since we started working together.</p></div>'
        f'<a class="kd-hl kd-pkg rv rv-d3" href="#pricing"><span class="kd-k mono">Their package · {em["tier"]}</span>'
        f'<b class="kd-big mono">{em["amount"]}{per}</b>'
        f'<p>Kelly&rsquo;s runs on our {em["tier"]} package &mdash; our most affordable, '
        f'best-value package.</p><span class="kd-go">See {em["tier"]} {B.ICONS["arrow"]}</span></a>')
    return section(
        sec_head('Our services in action', 'Kelly&rsquo;s<span>Country Store.</span>',
                 aside=f'<div class="kd-links">{links}</div>')
        + prose(['Below is one of our clients that is currently enrolled in our Viral '
                 'Content Management services. Each page is actively optimized to '
                 'leverage trends, platform algorithms, and audience behavior for '
                 'maximum reach and growth.'])
        + f'<div class="kd panel rv">'
          f'<div class="kd-top"><span class="kd-live"><i></i>Kelly&rsquo;s Country Store</span>'
          f'<span class="kd-src mono">Facebook &amp; Instagram · Insights</span></div>'
          f'<div class="grid grid-3 stats kd-stats">{tiles}</div>'
          f'{growth}'
          f'<div class="kd-hls">{high}</div>'
          f'<p class="fig-cap">Tiles: Kelly&rsquo;s Country Store · last 28 days, against '
          f'the 28 before it, read off their own dashboard.</p></div>',
        cls='band-alt')


# ------------------------------------------------------- /drones: arsenal
# Drew, 2026-10-15: "showcasing the professional drone equipment we use …
# DJI Neo, DJI Mini 5 Pro". The descriptions and spec chips are NEW COPY,
# for Drew to confirm. A photo of his own drone at out/img/<slug>.webp takes
# the drawing's place by itself.
ARSENAL = [
    dict(slug='drone-neo', name='DJI Neo', role='The close-up camera', art='neo',
         text='Palm-sized with full prop guards, the Neo flies safely through '
              'doorways, down hallways and close to people &mdash; smooth interior '
              'walkthroughs and follow shots no larger drone can get.',
         chips=['4K video', 'Full prop guards', 'Indoor &amp; walkthroughs']),
    dict(slug='drone-mini-5-pro', name='DJI Mini 5 Pro', role='The cinematic camera', art='mini',
         text='A 1-inch sensor on a gimbal that turns for true vertical: cinematic 4K '
              'with real detail in shadow and at golden hour, shot native for '
              'websites, reels and Stories.',
         chips=['1-inch sensor', '4K HDR', 'True vertical']),
]


def drone_arsenal():
    B = _b()
    cards = []
    for i, d in enumerate(ARSENAL):
        # Optional, so os.path rather than have(): the drawing is a finished
        # card, not a gap waiting for a file.
        if os.path.exists(os.path.join(B.SRC, 'out', 'img', f'{d["slug"]}.webp')):
            media = B.pic(d['slug'], d['name'], '(min-width:960px) 40vw, 90vw')
        else:
            media = getattr(art, d['art'])()
        chips = ''.join(f'<li class="mono">{c}</li>' for c in d['chips'])
        cards.append(
            f'<article class="ars-card panel rv rv-d{i + 1}">'
            f'<div class="ars-stage">{media}<i class="ars-shadow"></i></div>'
            f'<div class="ars-body"><span class="eyebrow">{d["role"]}</span>'
            f'<h3>{d["name"]}</h3><p>{d["text"]}</p><ul class="ars-chips">{chips}</ul></div>'
            f'</article>')
    return section(
        sec_head('Our arsenal', 'The drones<span>we fly.</span>',
                 aside='<p class="sec-note">Two aircraft, one for the tight spaces '
                       'and one for the big picture.</p>')
        + f'<div class="grid grid-2 ars">{"".join(cards)}</div>')


# ------------------------------------------------------- /drones: the film
# Drew, 2026-10-15: "a featured video section showcasing our actual drone
# footage … in a cinematic video player". A lite embed: the poster and a play
# button, and YouTube's player only once someone presses it (site.js swaps in
# the youtube-nocookie iframe). Without a script the button is a plain link
# to the film on YouTube. The poster is YouTube's own frame, saved once to
# out/img/drone-film.webp; until it is there the card uses YouTube's URL.
FILM = dict(id='kVI5MWz1cC8', title='5133 East River Road, Grand Island',
            sub='Live walkthrough · Isle de Grande')


def drone_film():
    B = _b()
    f = FILM
    if os.path.exists(os.path.join(B.SRC, 'out', 'img', 'drone-film.webp')):
        poster = B.u('/assets/img/drone-film.webp')
    else:
        poster = f'https://i.ytimg.com/vi/{f["id"]}/maxresdefault.jpg'
    return section(
        sec_head('Our drone work', 'Featured<span>film.</span>',
                 aside='<p class="sec-note">Our own footage, flown and edited for the '
                       'listing. Press play.</p>')
        + f'<figure class="film rv">'
          f'<a class="film-frame" href="https://www.youtube.com/watch?v={f["id"]}" '
          f'data-yt="{f["id"]}" target="_blank" rel="noopener" '
          f'aria-label="Play: {f["title"]}">'
          f'<img src="{poster}" alt="" loading="lazy" decoding="async">'
          f'<span class="film-shade"></span>'
          f'<span class="film-play">{B.ICONS["play"]}</span>'
          f'<span class="film-meta"><b>{f["title"]}</b>'
          f'<span class="mono">{f["sub"]}</span></span></a></figure>',
        cls='band-alt film-sec')


# ------------------------------------------------- /lead-conversion: the hub
# Drew, 2026-10-15: "a small animated section showing leads from multiple
# platforms being organized into one dashboard through third-party
# integrations". An illustration, and labelled one: the rows say where a lead
# came from and where it is, never whose it is, and carry no figures. The
# sentence beside it is NEW COPY for Drew to approve.
HUB_SOURCES = [('fb', 'Facebook'), ('ig', 'Instagram'), ('g', 'Google'),
               ('mail', 'Website form'), ('phone', 'Calls &amp; texts')]
HUB_ROWS = [('Facebook', 'Lead form', 'New'), ('Website form', 'Quote request', 'Contacted'),
            ('Instagram', 'Message', 'Qualified'), ('Google', 'Call', 'Booked'),
            ('Calls &amp; texts', 'Missed call', 'Contacted')]
G_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
          'stroke-linecap="round"><path d="M20 12a8 8 0 11-2.4-5.7M20 12h-7"/></svg>')


def lead_hub():
    B = _b()
    src = ''.join(
        f'<li class="hub-src rv rv-d{i % 3 + 1}" style="--i:{i}">'
        f'<span class="hub-ico">{G_ICON if k == "g" else B.ICONS[k]}</span>{n}<i></i></li>'
        for i, (k, n) in enumerate(HUB_SOURCES))
    rows = ''.join(
        f'<li class="hub-row" style="--i:{i}"><span class="hub-dot"></span>'
        f'<span class="hub-what"><b>{what}</b><span class="mono">{s}</span></span>'
        f'<span class="hub-st hub-{st.lower()} mono">{st}</span></li>'
        for i, (s, what, st) in enumerate(HUB_ROWS))
    return section(
        sec_head('Lead centralization', 'Every platform.<span>One dashboard.</span>',
                 aside='<p class="sec-note">Leads from Facebook, Instagram, Google, your '
                       'website and your phone land in one dashboard through third-party '
                       'integrations, so every lead is followed up from one place and '
                       'nothing slips through.</p>')
        + f'<div class="hub rv"><ul class="hub-srcs">{src}</ul>'
          f'<div class="hub-flow" aria-hidden="true"><i></i><i></i><i></i></div>'
          f'<div class="hub-dash panel"><div class="hub-top"><b>All leads</b>'
          f'<span class="hub-tag mono">Illustration</span></div>'
          f'<ul class="hub-rows">{rows}</ul></div></div>',
        cls='band-alt')


def lead_quote():
    """Drew, 2026-10-15: "Focus on requesting a custom quote rather than fixed
    packages. CTA: Let's Build a Plan for Your Business", with his four lines
    as what the plan covers."""
    B = _b()
    p = PRICING['lead-conversion']
    tick = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
            'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></svg>')
    items = ''.join(f'<li class="rv rv-d{i % 3 + 1}">{tick}<span>{t}</span></li>'
                    for i, t in enumerate(p['features']))
    return section(
        sec_head('Pricing', 'A plan built<span>for your business.</span>',
                 aside=f'<a class="btn btn-ghost" href="{B.u("/pricing")}">Every package</a>')
        + f'<div class="lq panel rv"><div class="lq-words">'
          f'<span class="tier">{p["tier"]}</span>'
          f'<div class="lq-amount mono">{p["amount"]}</div>'
          f'<p>No fixed packages. Pricing is based on an hourly rate plus commission on '
          f'closed deals, set around your campaigns and your goals.</p>'
          f'<a class="btn" href="{B.u("/contact?service=lead-conversion")}">'
          f'Let&rsquo;s Build a Plan for Your Business {B.ICONS["arrow"]}</a></div>'
          f'<ul class="lq-list">{items}</ul></div>',
        sid='pricing')


# ------------------------------------------------------------------ /pricing
def pricing_page():
    B = _b()
    groups = []
    for s in SERVICES:
        keys = [k for k, p in PRICING.items() if p['service'] == s['slug']]
        if not keys:
            continue
        bullets = None
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
        desc='Every Mendoza Marketing package and what it costs: website design, '
             'performance marketing, social media, logo design and drone sessions.',
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
        f'<div class="logo-shot{" is-light" if c.get("light") else ""}{" is-contain" if c.get("contain") else ""}">'
        f'{B.pic(c["slug"], c["name"] + " logo", B.CARD_SIZES)}</div>'
        f'<h3>{c["name"]}</h3>'
        f'<p class="mono logo-work">{c["work"]}</p>'
        + (f'<p class="logo-note">{c["detail"]}</p>' if c['detail'] else '')
        + '</div>' for i, c in enumerate(CLIENTS))

    renders = ''.join(
        f'<figure class="case-shot rv">{B.pic(slug, alt, "(min-width:960px) 45vw, 100vw")}'
        f'<figcaption>{alt}</figcaption></figure>' for slug, alt in CASE['renders'])

    sites = site_gallery()

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
            section(sec_head('Websites', 'Built and<span>launched.</span>',
                             aside='<p class="sec-note">Completed '
                                   f'{PRICING["web-design"]["amount"]} WordPress '
                                   'websites, live today. Tap one to visit it.</p>')
                    + sites),
            section(sec_head('Content in action', 'Made for the feed.<span>Filmed for the client.</span>',
                             aside='<p class="sec-note">Kelly&rsquo;s Country Store &mdash; '
                                   'viral content management and Meta ad campaigns.</p>')
                    + f'<div class="grid grid-3 reels">{reels}</div>',
                    cls='band-alt'),
            B.cta(primary=('Get a quote', '/contact'),
                  secondary=('See the results', '/results')),
        ]))


def site_gallery():
    """Drew's completed websites (2026-10-15: "a scrolling gallery showcasing
    our completed $1,250 WordPress websites … website previews with clickable
    links"). Each card is a browser window around a screenshot of the live
    site (tools/shoot-sites.mjs), and opens the site itself in a new tab.

    The server sends one plain row of cards: a native scroll-snap strip on a
    phone, with no script, and under reduced motion. On a wider screen under
    html.motion site.js copies the row once (aria-hidden, inert) and the pair
    drifts left in a loop, pausing whenever a pointer or focus is on it.
    """
    B = _b()
    amount = PRICING['web-design']['amount']
    cards = []
    for s in SITES:
        host = s['url'].split('//', 1)[1].rstrip('/').removeprefix('www.')
        cards.append(
            f'<a class="ss" href="{s["url"]}" target="_blank" rel="noopener">'
            f'<span class="ss-bar" aria-hidden="true"><i></i><i></i><i></i>'
            f'<span class="mono">{host}</span></span>'
            f'<span class="ss-img">{B.pic("site-" + s["slug"], s["name"] + " home page", "(min-width:960px) 460px, 82vw")}</span>'
            f'<span class="ss-cap"><b>{s["name"]}</b>'
            f'<span class="mono">WordPress · {amount} package</span>{B.ICONS["arrow"]}</span></a>')
    return (f'<div class="ss-gallery rv" data-marquee>'
            f'<div class="ss-track">{"".join(cards)}</div></div>')


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
        title=B.seo_title('About Drew Pitts, Grand Island NY'),
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
