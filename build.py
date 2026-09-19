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
from urllib.parse import quote as _urlq

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

# Where the contact form posts. Unset is a supported state, not a broken one:
# site.js then hands the filled-in message to the visitor's own mail app,
# addressed to EMAIL, which needs no account and works today. Set it to a
# Formspree or Web3Forms endpoint and the same form POSTs JSON instead.
FORM_ENDPOINT = os.environ.get('FORM_ENDPOINT', '')

# "Save my number" — a vCard the phone opens straight into Contacts. The owner
# asked for the button first and the details later, so every field here is a
# placeholder that is simply omitted when empty: a card with no phone is a
# minor disappointment, a card with a made-up one is a lie. Fill in as Ephraim
# supplies them. vCard 3.0, which Apple, Google and Outlook all read.
CONTACT = dict(
    given='Ephraim', family='',          # surname unconfirmed (CLAUDE.md)
    org=SITE_NAME, title='Muralist',
    phone='',                            # to come
    email=EMAIL,
    url=None,                            # filled in from BASE_URL below
    instagram=IG,
    note='Murals, banners, signs and graffiti removal — New York and nationwide.',
)
VCF_PATH = '/ephraim.vcf'


def _vesc(v):
    # The format's separators must be escaped; values keep their own punctuation.
    return (v.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,')
             .replace('\r\n', '\\n').replace('\n', '\\n'))


def _vfold(line):
    # Lines are at most 75 octets, not characters; a continuation line starts
    # with one space (RFC 2426). Fold on bytes so an em dash is never split.
    b = line.encode('utf-8')
    if len(b) <= 75:
        return line
    out, i, limit = [], 0, 75
    while i < len(b):
        j = min(i + limit, len(b))
        while j < len(b) and (b[j] & 0xC0) == 0x80:  # do not cut a multibyte sequence
            j -= 1
        out.append(('' if i == 0 else ' ') + b[i:j].decode('utf-8'))
        i, limit = j, 74
    return '\r\n'.join(out)


def vcard():
    c = dict(CONTACT); c['url'] = c['url'] or BASE_URL + '/'
    name = ' '.join(x for x in (c['given'], c['family']) if x)
    lines = ['BEGIN:VCARD', 'VERSION:3.0',
             f"N:{_vesc(c['family'])};{_vesc(c['given'])};;;",
             f'FN:{_vesc(name)}',
             f"ORG:{_vesc(c['org'])}"]
    if c['title']:  lines.append(f"TITLE:{_vesc(c['title'])}")
    if c['phone']:  lines.append(f"TEL;TYPE=CELL,VOICE:{_vesc(c['phone'])}")
    if c['email']:  lines.append(f"EMAIL;TYPE=INTERNET:{_vesc(c['email'])}")
    lines.append(f"URL:{_vesc(c['url'])}")
    if c['instagram']: lines.append(f"X-SOCIALPROFILE;TYPE=instagram:{_vesc(c['instagram'])}")
    if c['note']:   lines.append(f"NOTE:{_vesc(c['note'])}")
    lines += ['END:VCARD']
    return '\r\n'.join(_vfold(l) for l in lines) + '\r\n'


def save_number(cls='btn btn-mint'):
    """The button. `download` names the file; the .vcf URL is what makes iOS
    Safari hand it to Contacts rather than Files."""
    return (f'<a class="{cls}" href="{u(VCF_PATH)}" download="ephraim.vcf" '
            f'type="text/vcard">{ICONS["person"]}Save my number</a>')

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


def focus_attr(p):
    """object-position for a photograph whose subject is not in the middle.

    Every crop on the site is object-fit: cover, which takes the centre of the
    frame by default. A portrait-shaped photo of a wall with the mural high up
    (Malcolm X) then shows the street and cuts the mural. `focus` on the
    project row says where the mural is; it rides the <img> as an inline
    style so the card, the large card and the page hero all agree.
    """
    f = p.get('focus')
    return f'style="object-position:{f}"' if f else ''


def pcard(p, cls='', sizes=CARD_SIZES):
    """A project card. The card is the link; the figures are the headline."""
    place = f"{p['city']}, {p['state']}"
    alt = f"{p['title']} mural by Open Air Gallery, {place}"
    return f'''<a class="pcard rv {cls}" href="{u('/work/' + p['slug'])}">
  <div class="pcard-img">{pic(p['hero'], alt, sizes, extra=focus_attr(p))}</div>
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
 'person': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/></svg>',
 'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
 'ig': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 'chevL': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
 'chevR': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>',
 'clock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.2 2"/></svg>',
 'pin': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-5.6 7-11a7 7 0 10-14 0c0 5.4 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/></svg>',
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


def page_hero(eyebrow, title, lead, media_slug=None, crumb=None, cls='', media_alt='', video=None):
    """The top of a page: a photograph, a shade over it, and the words.

    The photograph goes through pic() rather than img() so the browser picks a
    rendition instead of always taking the widest one, and it is the page's
    LCP element, so it loads eagerly at high priority. media_alt is the
    description of the mural; leave it empty only when the photograph is
    genuinely decorative, which on this site it never is.

    video names a clip in out/video/ (<name>.mp4 + <name>.webp poster). It
    plays muted, looped, inline, on top of the photograph: the photograph is
    still the LCP element and the still every crawler, reader mode and
    reduced-motion visitor gets; the clip is the motion. site.js pauses it
    under prefers-reduced-motion and data-saver, and the CSS hides it there
    too, so the page never depends on the clip having arrived.
    """
    clip = ''
    if video:
        assert os.path.exists(f'out/video/{video}.mp4') and os.path.exists(f'out/video/{video}.webp'), \
            f'hero video {video}: out/video/{video}.mp4 and .webp must exist'
        clip = (f'<video class="hero-video" data-autoplay autoplay muted loop playsinline preload="metadata" '
                f'poster="{u("/assets/video/" + video + ".webp")}" aria-hidden="true" tabindex="-1">'
                f'<source src="{u("/assets/video/" + video + ".mp4")}" type="video/mp4"></video>')
    media = (f'<div class="hero-media">'
             f'{pic(media_slug, media_alt, HERO_SIZES, extra="fetchpriority=\"high\"", lazy=False)}{clip}'
             f'</div><div class="hero-shade"></div>') if media_slug else ''
    crumbs = (f'<div class="crumbs"><a href="{u("/")}">Home</a><span>/</span><span>{crumb or title}</span></div>'
              if crumb is not False else '')
    return f'''<section class="page-hero{" " + cls if cls else ""}">{media}
  <div class="wrap"><div class="hero-inner">{crumbs}<div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p class="lead">{lead}</p></div></div></section>'''


# The six things a visitor can ask for. The Contact form's <select> is built
# from this same tuple, so a link that pre-selects a service can never name one
# the form does not offer.
SERVICE_OPTIONS = ('Murals', 'Banners and signs', 'Graffiti removal',
                   'Pressure washing', 'Commercial painting', 'Something else')


def consult_path(service=None):
    """The contact-form path, with the service already chosen — unprefixed.

    cta() puts its two hrefs through u(), so it needs the bare path; every
    other caller wants the finished link and uses consult().
    """
    if service is None:
        return '/contact'
    assert service in SERVICE_OPTIONS, f'consult({service!r}): not in SERVICE_OPTIONS'
    return f'/contact?service={_urlq(service)}'


def consult(service=None):
    """A link to the contact form, with the service already chosen."""
    return u(consult_path(service))


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


def beats(items, cls='', quoted=True):
    """A row of stages: the stage name, then the sentences under it.

    `quoted` is not decoration. Where the words are Ephraim's they are set in
    a <blockquote>, because that is what they are; where they are ours — the
    four beats of a graffiti job, who the service is for — they are ordinary
    paragraphs. Marking our own prose as a quotation of his would be the one
    kind of lie this site cannot afford.
    """
    body = ('<blockquote><p>{0}</p></blockquote>' if quoted else '<p>{0}</p>')
    li = ''.join(
        f'<li class="beat rv{" rv-d" + str(i) if i else ""}">'
        f'<h3>{stage}</h3>{body.format(words)}</li>'
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


def ld_json(ld):
    """A JSON-LD block that cannot end its own <script> element.

    Nothing on this site puts a '<' in structured data today, but the tag is
    written once and the content comes from projects.py, so the escape is
    cheaper than the assumption. json.dumps already escapes the rest.
    """
    if not ld:
        return ''
    if isinstance(ld, list):
        ld = {'@context': 'https://schema.org', '@graph': ld}
    else:
        ld = {'@context': 'https://schema.org', **ld}
    body = json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c')
    return f'<script type="application/ld+json">{body}</script>'


def layout(path, title, desc, body, ld=None, noindex=False, wash=False, og=None,
           splat=False):
    """The document around a page body.

    `wash` carries the two Wash assets — css/wash.css and js/wash.js — and it
    is opt-in per page on purpose (wall.py's docstring says so): only Home and
    /graffiti-removal hold a drawn wall, and on every other page the pair
    would be two requests for a file that binds nothing.

    `splat` writes `data-splat` on <body>. Splat is the one mechanic a visitor
    sets off on purpose — a mint burst out of the click point on a button —
    and the owner asked for it on the home page, so the attribute is the whole
    of its scope: site.js binds nothing on a page that does not carry it.
    """
    canonical = BASE_URL + (path if path != '/index' else '/')
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else ''
    ldjson = ld_json(ld)
    # The card a link to this page draws. og:image wants an absolute URL, and
    # the width and height stop a scraper guessing at the crop.
    ogimg = ''
    if og:
        src, w, h = abs_img(og)
        ogimg = (f'<meta property="og:image" content="{src}">'
                 f'<meta property="og:image:width" content="{w}">'
                 f'<meta property="og:image:height" content="{h}">'
                 f'<meta property="og:image:alt" content="{html.escape(title)}">')
    washer = (f'<link rel="stylesheet" href="{u("/css/wash.css")}?v={asset_v("css/wash.css")}">'
              f'\n<script src="{u("/js/wash.js")}?v={asset_v("js/wash.js")}" defer></script>'
              if wash else '')
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
{ogimg}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{INK}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{u('/css/site.css')}?v={asset_v("css/site.css")}">
{washer}
{ldjson}
</head>
<body{' data-splat' if splat else ''}>
<a class="skip" href="#main">Skip to content</a>
{nav_html()}
<main id="main">
{body}
</main>
{footer_html()}
</body>
</html>'''


pages = {}

# --------------------------------------------- THE OTHER HALF OF THE BUSINESS
# Open Air Gallery paints walls and it cleans them, and the second half has to
# be advertised on the first half's pages the way DroneGodMax advertises Green
# Flash (build.py gf_band()/gf_strip(), which are the shape these two take).
#
# gr_band() is the one scrubbed-clean block on a dark site: a --wall panel with
# near-black type and a faint diagonal ghost of overpaint fading out across the
# top-left corner, which is the pitch in one image. Its visual is the same
# drawn wall as /graffiti-removal, in auto mode — the compact loop, no pointer
# handling, no sound, no washer head — so Home carries wash.css and wash.js too.
#
# The palette rule from PLAN.md §2 is what shapes it: mint never sits on
# --wall. So on this panel the accent appears the only way it is allowed to,
# as ink on mint — the eyebrow is a mint pill and the primary button is a mint
# button — and every piece of type is ink or the muted ink beside it.
from wall import wall_html, brick_svg

# His own pitch, in his own words, verbatim from the Wix graffiti page
# (research/wix/graffiti-removal.html). The clause after the em dash is ours
# and reads as ours.
GR_PITCH = ('Open Air Gallery removes unsightly graffiti &amp; stains with industrial '
            'strength cleaning services, available in NYC &mdash; the same crew that paints '
            'the wall knows what the surface is made of. Send a picture of the space you '
            'want cleaned and you get a quote and a date back.')

GR_CHIPS = ('Graffiti removal', 'Pressure washing', 'Commercial painting')


def gr_band():
    """The graffiti-removal band. Home only, after the process, before the CTA."""
    chips = ''.join(f'<li>{c}</li>' for c in GR_CHIPS)
    return f'''<section class="gr-band-wrap"><div class="wrap">
  <div class="gr-band rv">
    <div class="gr-band-words">
      <div class="eyebrow">Also from Open Air</div>
      <h2>We take it off, too.</h2>
      <p class="lead">{GR_PITCH}</p>
      <ul class="tags">{chips}</ul>
      <div class="btn-row">
        <a class="btn btn-mint" href="{u('/graffiti-removal')}">See graffiti removal {ICONS['arrow']}</a>
        <a class="btn btn-ghost" href="{consult('Graffiti removal')}">Send a photo, get a quote</a>
      </div>
    </div>
    <div class="gr-band-wall">{wall_html(mode='auto', id_prefix='washhome')}</div>
  </div>
</div></section>'''


def gr_strip(text=None):
    """The slim one-liner, for the pages that are not Home (PLAN.md §3a).

    Same offer, one line of it: Work, Services and About each end on it, so a
    visitor who came for the murals leaves knowing the crew cleans as well.
    """
    text = text or ('Graffiti removal, pressure washing and commercial painting in NYC, '
                    'from the crew that knows what the surface is made of.')
    return f'''<section class="gr-strip-wrap"><div class="wrap">
  <div class="gr-strip rv">
    <p><b>We take it off, too.</b> {text}</p>
    <div class="gr-strip-links">
      <a class="btn btn-mint btn-sm" href="{u('/graffiti-removal')}">See graffiti removal</a>
      <a class="btn btn-ghost btn-sm" href="{consult('Graffiti removal')}">Send a photo, get a quote {ICONS['arrow']}</a>
    </div>
  </div>
</div></section>'''


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
  wash=True,
  splat=True,
  title=f'{SITE_NAME} | Murals at building scale, New York and nationwide',
  desc='Open Air Gallery is a muralist and large-image company led by Ephraim. Gucci in Manhattan at 81 by 80 feet, Crown Royal in Portland at 85 by 90, John Lewis and Malcolm X in Rochester.',
  body=f'''
{page_hero('Muralist and large-image company',
           'Murals that capture the gaze',
           'Open Air Gallery is Ephraim’s studio: eighty-one feet of Gucci on a Manhattan wall, eighty-five feet of Crown Royal in Portland, John Lewis and Malcolm X in Rochester.',
           media_slug='gucci-new-york-hero',
           media_alt='The Gucci mural by Open Air Gallery, eighty-one feet across a New York City wall',
           video='hero-johnnie-walker',
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

{gr_band()}

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
{gr_strip('Graffiti removal, pressure washing and commercial painting in NYC. The '
          'crew that painted these walls cleans them too.')}
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
    plan describes and it is still exactly what a visitor with no JavaScript
    gets: she stands at --fx:.12 on a mint baseline with a real "6 ft"
    caption, which is a static scale bar and needs nothing else to be true.

    site.js gives her the drag on top of that. The hint is aria-hidden and
    display:none outside html.motion, because "Drag me" is an instruction for
    something only the script can do — it is not content.
    """
    alt = (f"{p['title']} mural by Open Air Gallery in {p['city']}, {p['state']} — "
           f"{p['dim_w']} feet wide by {p['dim_h']} feet tall")
    return f'''<section class="phero"><div class="scale" data-scale data-ft="{p['dim_w']}" style="--ft:{p['dim_w']};--fx:.12">
  <div class="scale-media">{pic(p['hero'], alt, '100vw', extra=('fetchpriority="high" ' + focus_attr(p)).strip(), lazy=False)}</div>
  <div class="scale-base"></div>
  <button class="fig" type="button" data-fig aria-label="Drag the figure for scale"><span class="fig-cap">6 ft</span>{FIGURE_SVG}</button>
  <span class="scale-hint" aria-hidden="true">Drag me</span>
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
    <div class="portrait rv">{pic('ephraim-portrait', 'Ephraim, the muralist who leads Open Air Gallery', PORTRAIT_SIZES)}
      <div class="portrait-cta">{save_number()}</div></div>
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

{gr_strip()}

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
SIGN_ROSTER = ('Heineken', 'Jack Daniels', 'Corona', 'Black Crow',
               'House of Pizza & Calzones')


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

{gr_strip('Graffiti removal, pressure washing and commercial painting in NYC. The '
          'fourth thing the company sells, and it has a page of its own.')}

{cta(title='Which one do you need?',
     text='Tell us the wall, the city and roughly how big it is. We will come back with '
          'a plan and a price.')}''')


# ---------------------------------------------------------------- GRAFFITI REMOVAL
# The other half of the business, and the page the owner asked to look awesome.
#
# The mechanic is the hero. Not a photograph with a widget under it: the thing
# a visitor meets at the top of this page is a tagged brick wall that comes
# clean under their own hand (wall.py, css/wash.css, js/wash.js). Everything
# else on the page is the argument for why they should not have to do it
# themselves.
#
# Every paragraph set as a quotation below is Ephraim's, transcribed from
# research/wix/graffiti-removal.html (saved 2026-09-18) and reproduced
# verbatim — his three reasons, his three services, his three-step booking
# ladder. The four beats of the job and the three audiences are ours and are
# set as plain prose, not as quotations of him: beats(quoted=False) is that
# distinction, and it matters.

# His three reasons, from the line under his headline.
GR_REASONS = ('Attract more customers', 'Increase safety', 'Beat the competition')

# His three services, each with his own paragraph, exactly as he wrote them
# (including "services analyzes", "Whether its wood" and "techniques creates" —
# they are his sentences and they are not ours to tidy).
GR_SERVICES = [
  ('Graffiti removal',
   'Our graffiti removal services analyzes the surface material that the graffiti '
   'is on and utilizes the proper paint stripping techniques to remove all graffiti '
   'on the designated area. With industrial strength processes, we make the space '
   'look like new. Send us a picture of the space you want cleaned and we&rsquo;ll send '
   'you a no hassle quote and date of completion.'),
  ('Pressure washing',
   'Our pressure washing services not only serve as a technique for graffiti removal, '
   'but it also serves as a technique for stain removal. Remove stains, moss, and dirt '
   'from various surfaces with professional pressure washing. We clean sidewalks, '
   'stairs, windows, and the exterior of buildings. Whether its wood, concrete, or '
   'metal, we will clean it.'),
  ('Commercial painting',
   'Once the graffiti is removed or the surface is cleaned, you may need a fresh coat '
   'of paint. With a team of professional muralists, we will apply a fresh coat of '
   'paint that not only brings your space to life but maintains its vibrancy over '
   'time from various environmental effects. Our proprietary techniques creates paint '
   'mixtures that can weather the storm.'),
]

# The booking ladder he already publishes. His headings, his sentences.
GR_LADDER = [
  ('Take a picture',
   'Take a picture of the areas that you want us to come and remove graffiti, clean, '
   'or paint.'),
  ('Send us an email',
   'Send us a text message with the images of the spaces that need graffiti removal, '
   'cleaning, or painting.'),
  ('Pay a 50% deposit',
   'We will reply to your message with a date that we can come and complete the job '
   'and a quote for the cost of the job. You will only need to pay a 50% deposit to '
   'secure your spot.'),
]

# What happens at the wall once the date is booked — the four beats PLAN.md §3
# asks for. Ours, so plain prose, and every claim in them is one his own copy
# already makes: surface analysis and the proper stripping technique are from
# the graffiti page, the environmentally friendly coating from his mural
# process (PROCESS[2]).
GR_PROCESS = [
  ('Assessment',
   'The job starts with the surface, not with the tag. What the paint is sitting on '
   'decides what will take it off without taking the wall with it, so the material is '
   'read first &mdash; brick, block, stone, render, timber or metal &mdash; and everything '
   'after that follows from it.'),
  ('Removal matched to the substrate',
   'Then the proper stripping technique for that material, at industrial strength: '
   'chemical stripping where the surface will take it, pressure washing where it will '
   'not, and a fresh coat from the same crew where removal alone would leave a shadow '
   'of the piece behind.'),
  ('Anti-graffiti coating',
   'The same environmentally friendly coating the murals get. Ephraim&rsquo;s third stage '
   'is written for a painted wall, and it is exactly what a cleaned one wants: a '
   'finish that makes the next tag wipe off instead of soak in.'),
  ('Maintenance',
   'A wall that has been hit once tends to be hit again. Once it is coated the next '
   'one comes off without another strip &mdash; send a picture when it happens and the '
   'same crew comes back.'),
]

# Who the service is for. Three audiences, described as audiences: none of
# these is a claim that a particular client has been served.
GR_WHO = [
  ('Property managers',
   'Storefronts, lobbies, loading bays, roller shutters and the back of the building. '
   'One picture gets a quote and a date, and the crew works around the tenants.'),
  ('Brands and franchises',
   'A location that has to look the same in every city. The team that paints brand '
   'walls at building scale is the team cleaning this one, so the repaint matches '
   'rather than patches.'),
  ('Cities and BIDs',
   'Business improvement districts, civic property and the blocks in between. Larger '
   'runs, scheduled, with the coating that keeps the next round cheaper than this one.'),
]

def ba_layer(kind, label, uid):
    """One half of the before/after: a drawn wall and the word for it."""
    return (f'<div class="ba-layer ba-{kind}">{brick_svg(kind == "before", uid)}'
            f'<span class="ba-lab">{label}</span></div>')


def before_after():
    """The before/after presentation (PLAN.md §3).

    With no script it is what it says: two pictures side by side, each of them
    labelled, both of them real content in the server HTML. With the script it
    becomes one picture under a mint divider you drag across it — the same two
    layers, stacked instead of paired.

    The pictures are the drawn wall from wall.py, both layers of it, because
    Ephraim has not sent a real before-and-after yet. When he does, this is the
    one function that changes: two pic() calls in place of the two brick_svg()
    calls, and nothing else on the page or in the stylesheet moves.
    """
    return f"""<figure class="ba rv" data-ba>
  <div class="ba-stage" data-ba-stage>
    {ba_layer('after', 'After', 'ba-a')}
    {ba_layer('before', 'Before', 'ba-b')}
    <button class="ba-handle" type="button" data-ba-handle
            aria-label="Drag to compare the wall before and after"><span class="ba-grip" aria-hidden="true">{ICONS['chevL']}{ICONS['chevR']}</span></button>
  </div>
  <figcaption class="ba-cap">The same brick, tagged and cleaned.<span class="ba-hint"> Drag the divider across it.</span></figcaption>
</figure>"""


pages['/graffiti-removal'] = dict(
  wash=True,
  title=f'Commercial graffiti removal, New York | {SITE_NAME}',
  desc='Graffiti removal, pressure washing and commercial painting in NYC from Open Air '
       'Gallery — the muralists who know what the surface is made of. Send a picture of '
       'the space and get a quote and a date back.',
  body=f'''
<section class="page-hero gr-hero">
  <div class="wrap"><div class="gr-hero-grid">
    <div class="hero-inner">
      <div class="crumbs"><a href="{u('/')}">Home</a><span>/</span><span>Graffiti removal</span></div>
      <div class="eyebrow">Commercial</div>
      <h1>Graffiti removal</h1>
      <p class="lead">{' &middot; '.join(GR_REASONS)}.</p>
      <div class="btn-row"><a class="btn btn-mint" href="{consult('Graffiti removal')}">Send a photo, get a quote {ICONS['arrow']}</a><a class="btn btn-ghost" href="#gr-services">The three services</a></div>
    </div>
    <div class="gr-hero-wall">{wall_html(mode='interactive', id_prefix='wash')}</div>
  </div></div>
</section>

<section id="gr-services"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">In his own words</div>
  <h2>Graffiti removal &amp; cleaning services</h2>
  <p class="lead">{GR_PITCH}</p></div>
  {beats(GR_SERVICES)}
  <div class="row-end rv btn-row">
    <a class="btn btn-mint" href="{consult('Graffiti removal')}">Send a photo, get a quote {ICONS['arrow']}</a>
    <a class="btn btn-ghost" href="{consult('Pressure washing')}">Ask about pressure washing</a>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">Before and after</div>
  <h2>What comes off</h2>
  <p class="lead">Ephraim&rsquo;s own before-and-after photographs go here the day he sends
  them. Until then this is the wall at the top of the page, drawn, with every tag on
  it and then none of them.</p></div>
  {before_after()}
</div></section>

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">His three step process</div>
  <h2>Take a picture. Send us an email. Pay a 50% deposit.</h2>
  <p class="lead">The booking ladder Open Air Gallery has published since the first
  version of this site, unchanged.</p></div>
  {beats(GR_LADDER)}
</div></section>

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">At the wall</div>
  <h2>Four beats, once the date is set</h2>
  <p class="lead">What the crew actually does between the deposit and the wall you get
  back.</p></div>
  {beats(GR_PROCESS, 'beats-4', quoted=False)}
</div></section>

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">Who it&rsquo;s for</div>
  <h2>Whose wall this is</h2></div>
  {beats(GR_WHO, quoted=False)}
</div></section>

{cta(title='Send a photo, get a quote',
     text='A picture of the space is enough to start. You get a no hassle quote and a '
          'date of completion back &mdash; and the deposit is half.',
     primary=('Send a photo, get a quote', consult_path('Graffiti removal')),
     secondary=('See the murals', '/work'))}''')


# ---------------------------------------------------------------- CONTACT
# The consultation request. The fields are the ones his own Wix form asks for,
# minus the ones it asked for twice: first/last name become one name, "position"
# and "type of organization" go, and the address field keeps his own helper
# sentence because it says exactly what he wants to know.
#
# The form works with no endpoint and no JavaScript, in that order:
#
#   * FORM_ENDPOINT set    — site.js POSTs the fields as JSON and says so.
#   * FORM_ENDPOINT unset  — site.js hands the message to the visitor's own
#                            mail app, addressed to EMAIL. Nothing is lost and
#                            no account is needed. This is today's state.
#   * no JavaScript at all — every field, label and option is in the server
#                            HTML, and the note under the button gives the
#                            address to write to directly.
#
# _gotcha is the honeypot Formspree and Web3Forms both read: off-screen, out of
# the tab order, and dropped before anything is sent.
BUDGET_BANDS = ('Not sure yet', 'Under $5,000', '$5,000 – $10,000', '$10,000 – $25,000',
                '$25,000 – $50,000', '$50,000 and up')


def _options(values):
    return ''.join(f'<option value="{html.escape(v)}">{html.escape(v)}</option>'
                   for v in values)


pages['/contact'] = dict(
  title=f'Contact | {SITE_NAME}',
  desc=f'Book a free consultation with Open Air Gallery. Tell us the wall, the city and '
       f'roughly how big it is, or email {EMAIL} directly.',
  body=f'''
{page_hero('Book a free consultation', 'Let’s get to work',
           'Fill out the form and we’ll connect with you shortly. Tell us the wall, the '
           'city and roughly how big it is, and you get a plan and a price back.',
           media_slug='contact-band',
           media_alt='Three Open Air Gallery painters flat on a lift platform, rolling out '
                     'a wall by hand',
           crumb='Contact')}

<section><div class="wrap">
  <div class="contact-grid">
    <div class="rv">
      <div class="eyebrow">The brief</div>
      <h2>Tell us about the wall</h2>
      <form id="contact-form" class="form" method="post">
        <div class="row">
          <div class="field"><label for="name">Name</label>
            <input id="name" name="name" required autocomplete="name" placeholder="Your name"></div>
          <div class="field"><label for="email">Email</label>
            <input id="email" name="email" type="email" required autocomplete="email" placeholder="you@company.com"></div>
        </div>
        <div class="row">
          <div class="field"><label for="phone">Phone</label>
            <input id="phone" name="phone" type="tel" autocomplete="tel" placeholder="Optional"></div>
          <div class="field"><label for="company">Company</label>
            <input id="company" name="company" autocomplete="organization" placeholder="Optional"></div>
        </div>
        <div class="field"><label for="location">Location</label>
          <input id="location" name="location" placeholder="City and state, or the address of the wall">
          <span class="hint">Please tell us your company location or the location of the potential mural/graphic.</span></div>
        <div class="row">
          <div class="field"><label for="service">Service</label>
            <span class="sel"><select id="service" name="service">{_options(SERVICE_OPTIONS)}</select></span></div>
          <div class="field"><label for="budget">Budget</label>
            <span class="sel"><select id="budget" name="budget">{_options(BUDGET_BANDS)}</select></span></div>
        </div>
        <div class="field"><label for="message">Message</label>
          <textarea id="message" name="message" required placeholder="What is the wall, how big is it, and when do you need it?"></textarea></div>
        <div class="gotcha" aria-hidden="true">
          <label for="_gotcha">Leave this field empty</label>
          <input id="_gotcha" name="_gotcha" tabindex="-1" autocomplete="off"></div>
        <div class="btn-row"><button class="btn btn-mint" type="submit">Send the brief {ICONS['arrow']}</button></div>
        <div class="form-status" role="status"></div>
        <p class="form-note">Sending opens a pre-filled email from your own mail app. You can
        also write to <a href="mailto:{EMAIL}">{EMAIL}</a> directly, or send a DM to
        <a {ext(IG)}>{IG_HANDLE}</a>.</p>
      </form>
    </div>

    <div class="contact-side rv rv-d1">
      <div class="contact-card contact-card-cta"><div class="ic">{ICONS['person']}</div>
        <div><b>Save my number</b><span>One tap adds Ephraim to your contacts.</span>
        <div class="mt">{save_number()}</div></div></div>
      <a class="contact-card" href="mailto:{EMAIL}"><div class="ic">{ICONS['mail']}</div>
        <div><b>Email</b><span>{EMAIL}</span></div></a>
      <a class="contact-card" {ext(IG)}><div class="ic">{ICONS['ig']}</div>
        <div><b>Instagram</b><span>{IG_HANDLE} — the walls as they go up</span></div></a>
      <div class="contact-card"><div class="ic">{ICONS['clock']}</div>
        <div><b>What happens next</b><span>Fill out the form and we’ll connect with you
        shortly. For graffiti removal, a picture is enough to start: send us a picture of the
        space you want cleaned and we’ll send you a no hassle quote and date of completion.</span></div></div>
      <div class="contact-card"><div class="ic">{ICONS['pin']}</div>
        <div><b>Where we work</b><span>New York and nationwide. {spell(WALLS, cap=True)} walls
        in {spell(len(CITIES))} cities so far, from Manhattan to Los Angeles.</span></div></div>
    </div>
  </div>
</div></section>
<script>window.OAG={{form:{json.dumps(FORM_ENDPOINT)},email:{json.dumps(EMAIL)}}}</script>
''')


# ---------------------------------------------------------------------- SEO
# What a machine reads: one business, described once, and every page saying
# which part of it this page is.
#
# Rules, and they are the same rules the copy follows. Nothing is asserted
# that is not on the site or in projects.py: no street address (Ephraim has
# not published one), no telephone, no opening hours, no founding date, no
# surname on the founder (CLAUDE.md: the only surname anywhere is one
# unconfirmed Wix alt attribute), and no dateCreated on a wall whose year we
# do not know — which today is all twelve. A civil-rights mural with an
# invented date on it would be worse than one with no date at all.
#
# The business gets a stable @id so the project pages, the Service and the
# OfferCatalog can point at it instead of repeating it.
BUSINESS_ID = f'{BASE_URL}/#business'
NYC = {'@type': 'City', 'name': 'New York', 'addressRegion': 'NY',
       'address': {'@type': 'PostalAddress', 'addressLocality': 'New York',
                   'addressRegion': 'NY', 'addressCountry': 'US'}}
USA = {'@type': 'Country', 'name': 'United States'}


def abs_img(name):
    """The absolute URL of the largest rendition of an image, for og:image.

    Same rule as pic(): the widths are read off the files rather than
    assumed, so the tag never advertises a size that is not on disk.

    Not u(): an absolute URL is built the way layout() builds `canonical`,
    from BASE_URL and a bare path. On the preview BASE_URL already ends in
    /p/<slug>, so putting the path through u() as well writes the prefix
    twice and every social card 404s.
    """
    root = os.path.join(SRC, 'out', 'img')
    best = None
    for rel in (f'{name}.webp', f'{name}-1600.webp', f'{name}-800.webp'):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            continue
        w, h = webp_size(path)
        if best is None or w > best[1]:
            best = (rel, w, h)
    assert best, f'abs_img({name!r}): nothing in out/img/ — run ./process.sh'
    return f'{BASE_URL}/assets/img/{best[0]}', best[1], best[2]


BUSINESS = {
  '@type': 'LocalBusiness',
  '@id': BUSINESS_ID,
  'name': SITE_NAME,
  'url': BASE_URL + '/',
  'email': EMAIL,
  'description': ('A muralist and large-image company led by Ephraim: murals, '
                  'banners and signs painted at building scale, plus graffiti '
                  'removal, pressure washing and commercial painting.'),
  'image': abs_img('gucci-new-york-hero')[0],
  'areaServed': [NYC, USA],
  'sameAs': [IG],
  'founder': {'@type': 'Person', 'name': 'Ephraim'},
  'knowsAbout': ['Mural painting', 'Hand-painted signs and banners',
                 'Graffiti removal', 'Pressure washing', 'Commercial painting'],
}


def feet(n):
    """A measurement a machine can compare. UN/CEFACT FOT is the foot."""
    return {'@type': 'QuantitativeValue', 'value': n, 'unitCode': 'FOT',
            'unitText': 'feet'}


def project_ld(p):
    """One wall as a CreativeWork, measured, placed and attributed."""
    path = f"/work/{p['slug']}"
    ld = {
      '@type': 'CreativeWork',
      '@id': f'{BASE_URL}{path}#work',
      'name': p['title'],
      'url': BASE_URL + path,
      'description': p['story'],
      'creator': {'@id': BUSINESS_ID},
      'locationCreated': {'@type': 'Place', 'name': f"{p['city']}, {p['state']}"},
      'width': feet(p['dim_w']),
      'height': feet(p['dim_h']),
      'image': abs_img(p['hero'])[0],
      'genre': {'brand': 'Brand mural', 'portrait': 'Painted portrait',
                'civic': 'Civic mural'}[p['category']],
    }
    if p['client']:
        ld['sponsor'] = {'@type': 'Organization', 'name': p['client']}
    if p['year']:                 # None on all twelve today, and left out
        ld['dateCreated'] = str(p['year'])
    return ld


GR_SERVICE_LD = {
  '@type': 'Service',
  '@id': f'{BASE_URL}/graffiti-removal#service',
  'serviceType': 'Graffiti removal',
  'name': 'Commercial graffiti removal',
  'url': f'{BASE_URL}/graffiti-removal',
  'description': ('Graffiti removal, pressure washing and commercial painting '
                  'in New York City. The surface material decides the stripping '
                  'technique; an anti-graffiti coating keeps the next one cheap.'),
  'provider': {'@id': BUSINESS_ID},
  'areaServed': NYC,
}

# The catalogue is SERVICE_OPTIONS without "Something else", which is a way
# of asking rather than a thing to buy — so the form and the catalogue can
# never fall out of step with one another.
SERVICES_LD = {
  '@type': 'OfferCatalog',
  '@id': f'{BASE_URL}/services#catalog',
  'name': f'{SITE_NAME} services',
  'url': f'{BASE_URL}/services',
  'itemListElement': [
    {'@type': 'Offer',
     'itemOffered': {'@type': 'Service', 'name': s, 'provider': {'@id': BUSINESS_ID}}}
    for s in SERVICE_OPTIONS if s != 'Something else'],
}

# Every page carries the business; the pages that are also something in their
# own right carry that too, in one @graph.
pages['/index']['ld'] = BUSINESS
pages['/graffiti-removal']['ld'] = [BUSINESS, GR_SERVICE_LD]
pages['/services']['ld'] = [BUSINESS, SERVICES_LD]
pages['/work']['ld'] = BUSINESS
pages['/about']['ld'] = BUSINESS
pages['/contact']['ld'] = BUSINESS
for _p in PROJECTS:
    pages[f"/work/{_p['slug']}"]['ld'] = [BUSINESS, project_ld(_p)]

# og:image, one per page and never a guess: a project shows its own wall, and
# every other page shows the photograph it is actually about.
OG = {
  '/index': 'gucci-new-york-hero',
  '/work': 'crown-royal-trail-blazers-hero',
  '/about': 'about-team',
  '/services': 'moncler-wide',
  '/graffiti-removal': 'moncler-wide',
  '/contact': 'contact-band',
}
for _path, _name in OG.items():
    pages[_path]['og'] = _name
for _p in PROJECTS:
    pages[f"/work/{_p['slug']}"]['og'] = _p['hero']

# Nothing may ship without the three things a result page is made of.
for _path, _d in pages.items():
    assert _d.get('title') and _d.get('desc'), f'{_path}: no title or description'
    assert _d.get('og'), f'{_path}: no og:image'
_titles = [d['title'] for d in pages.values()]
assert len(set(_titles)) == len(_titles), 'two pages share a title'


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
        f.write(layout(path, p['title'], p['desc'], p['body'], p.get('ld'),
                       p.get('noindex', False), p.get('wash', False), p.get('og'),
                       p.get('splat', False)))
    print('wrote', fn)

# the vCard behind "Save my number"
with open(os.path.join(OUT, VCF_PATH.lstrip('/')), 'w', newline='') as f:
    f.write(vcard())

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
