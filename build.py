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
import os, sys, re, html, json, struct, hashlib
from urllib.parse import quote as _urlq
from art import brush_rule_svg, roller_pass_svg, spraycan_pass_svg, can_tipping_svg
from strokes import stroke_svg, highlight_svg

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

# The three colours the HTML itself has to name (a <meta> tag and the inline
# favicon cannot read a CSS custom property). They mirror --ink, --mint and
# --paper in site/css/site.css, and docs/contrast.py fails the build if they
# ever drift.
INK = '#0A0A0B'
MINT = '#71EEB8'
PAPER = '#FFFFFF'

# White ground, ink type, one loud colour and one accent: if those pairs stop
# being readable the design has stopped working, so the build refuses to
# finish. docs/contrast.py reads the tokens straight out of the stylesheet and
# checks the three constants above still match the tokens they mirror.
sys.path.insert(0, os.path.join(SRC, 'docs'))
import contrast
contrast.check(os.path.join(OUT, 'css', 'site.css'),
               {'--ink': INK, '--mint': MINT, '--paper': PAPER})

# One request for four of the five faces (CLAUDE.md, round three: Colossal's
# lesson is "multiple typefaces — four or five", used deliberately). Anton is
# the headline; Archivo ships the width axis the dimension figures and the
# wordmark need (wdth 62..125); Fraunces is the reading face; Inter carries
# the interface and its tabular numerals. The fifth is the marker, and it is
# not here: Permanent Marker is already in the repo, so it is served from
# site/fonts/ and declared in site.css rather than asked of a CDN.
FONTS = ('https://fonts.googleapis.com/css2?'
         'family=Anton'
         '&family=Archivo:wdth,wght@62..125,400..900'
         '&family=Fraunces:opsz,wght@9..144,400..600'
         '&family=Inter:wght@400;600;700&display=swap')

# A drawn mark rather than a file: a mint frame on ink, the wall the work goes
# on. Inline so there is no favicon request to 404 before the images land.
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           f"%3Crect width='64' height='64' fill='{INK.replace('#', '%23')}'/%3E"
           f"%3Crect x='11' y='15' width='42' height='34' fill='none' "
           f"stroke='{MINT.replace('#', '%23')}' stroke-width='6'/%3E%3C/svg%3E")

# The twelve walls. Every project fact on the site comes from here.
from projects import (PROJECTS, FEATURED_ORDER, CATEGORIES, BY_SLUG,
                      featured, measured, total_sq_ft)


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


FEET_NOTE = 'feet to come'


def feet_note(size=''):
    """What stands where the figure would, on a wall we have no feet for.

    The measurements are the hook on this site, so a wall without them cannot
    simply have a hole where the figure goes — the card would stop reading as
    a wall. It gets the promise instead, in his own hand: the feet are coming.
    It is the same thing the public-works section says about the photographs
    it does not have yet, and it is a note rather than a number, so nothing
    counts it, sprays it or rolls it.

    Coral on the white page, at the size .note fixes — CLAUDE.md, round three:
    --pop on --paper is 3.4:1, which is large-text contrast and nothing else.
    Mint on a card, where the scrim is dark and mint is already the colour the
    caption is set in.
    """
    cls = 'feet-note marker' + (f' feet-note-{size}' if size else '')
    return f'<div class="{cls}">{FEET_NOTE}</div>'


def dims(w, h, size=''):
    """The hook: a wall's measurements, set physically wide.

    Mint touches the prime marks and the times sign and nothing else — one
    accent stays one accent. `size` adds a modifier: dims('sm') on a card.

    A wall with no feet gets nothing at all from here: the caller decides what
    stands in its place (feet_note()), and site.js's Live, Stencil and Cure
    bind to the .dims that exist, so a page without one simply has less to do.
    """
    if w is None or h is None:
        return ''
    cls = 'dims' + (f' dims-{size}' if size else '')
    return (f'<div class="{cls}"><span class="n">{w}</span><span class="f">\u2032</span>'
            f'<span class="x">\u00d7</span><span class="n">{h}</span>'
            f'<span class="f">\u2032</span></div>')


def glow():
    """The ambient mint breath behind a section (site.js and site.css, "Live").

    An empty, aria-hidden box the size of its section, in the server HTML on
    purpose: it is then the same document with a script and without one, so
    the no-JS and reduced-motion renders stay identical to each other. It
    paints nothing at all outside html.motion — the light is a radial
    gradient drawn by the stylesheet, brightened as the section centres in
    the viewport and dimmed as it leaves.

    Four places only, staggered so two are never lit on one screen: the
    stats band and the Rochester pair on Home, the closing call to action,
    and the head of the words under a project's wall — which is the foot of
    that page's hero, and the one dark band there is. It never goes over a
    photograph and its core never sits under type.
    """
    return '<div class="glow" data-glow aria-hidden="true"></div>'


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


def roller_sprite():
    """The roller, drawn once a page, for every card on it to borrow.

    art.py's roller_pass_svg() is a detailed piece of kit — a nap drawn fibre
    by fibre — and a page can hold twelve cards, so it goes into the document
    once as a <symbol> and each card carries a <use> of it. The hidden <svg>
    is absolutely positioned and zero-sized (site.css .propdefs), so it can
    never take part in the layout.

    It is also where the cursor comes from: site.js serialises this symbol at
    40 px into a data URI and hangs it on the grid, so the roller the pointer
    wears and the roller riding the card are the same drawing, not two.

    layout() puts it on any page whose body holds a card and on no other, so
    a page with no grid does not carry a roller it will never draw.
    """
    svg = roller_pass_svg('oaroller')
    inner = svg[svg.index('>') + 1:-len('</svg>')]
    return ('<svg class="propdefs" width="0" height="0" aria-hidden="true" focusable="false">'
            f'<symbol id="oa-roller" viewBox="0 0 200 200">{inner}</symbol></svg>')


def pcard(p, cls='', sizes=CARD_SIZES):
    """A project card. The card is the link; the figures are the headline.

    data-live is the scroll-live mark (site.js, "Live"): the card rises into
    place as it comes up the screen and settles back as it leaves, its
    photograph drifts inside the frame with the scroll, and on a desktop it
    tilts a few degrees toward the pointer. The attribute is inert without
    html.motion — with no script it is a card with a photograph in it.

    The track after the photograph is Roll it in: the roller that rides the
    wet edge as the mural is rolled in over its primer, and the sheen it
    leaves just behind the nap. It is one <use> of the page's single roller
    <symbol> (roller_sprite()), it is display:none outside html.motion, and
    it is absolutely positioned inside a box that already clips — so it adds
    nothing to the layout and a page with no script never shows it. The
    second, unprimed copy of the photograph that the wipe reveals is not
    here: site.js clones it, so a crawler is never handed the same mural
    twice and the no-JS document is the document it has always been.
    """
    place = f"{p['city']}, {p['state']}"
    alt = f"{p['title']} mural by Open Air Gallery, {place}"
    return f'''<a class="pcard rv {cls}" data-live href="{u('/work/' + p['slug'])}">
  <div class="pcard-img">{pic(p['hero'], alt, sizes, extra=focus_attr(p))}<span class="pcard-roll" aria-hidden="true"><span class="pcard-wet"></span><span class="pcard-roller"><svg viewBox="0 0 200 200"><use href="#oa-roller"></use></svg></span></span></div>
  <div class="pcard-body">{dims(p['dim_w'], p['dim_h'], 'sm') or feet_note('sm')}<h3>{p['title']}</h3><span class="place">{place}</span></div>
</a>'''


def check_projects():
    """Refuse to build on a malformed project row.

    The dimensions are the whole design, so a string, a float or a typo has to
    stop the build rather than reach a page. The hero check is a hard assert:
    the images pipeline has landed (docs/images.md) and every hero is on disk,
    so a missing file now means process.sh has not been run, not that the
    photograph does not exist yet.

    Feet may be missing, and then they are missing in pairs. Both None is a
    wall Ephraim has not measured for us and the page says so; one None is a
    typo, and a half-measured wall would print "81 x None" on the hook.
    """
    root = os.path.join(SRC, 'out', 'img')
    seen = set()
    for p in PROJECTS:
        slug = p['slug']
        assert slug and slug not in seen, f'projects.py: empty or duplicate slug {slug!r}'
        seen.add(slug)
        assert (p['dim_w'] is None) == (p['dim_h'] is None), (
            f"{slug}: dimensions are both or neither — got "
            f"{p['dim_w']!r} x {p['dim_h']!r}")
        for k in ('dim_w', 'dim_h'):
            v = p[k]
            assert v is None or (isinstance(v, int) and not isinstance(v, bool)
                                 and 0 < v < 1000), (
                f'{slug}: {k} must be a whole number of feet or None, got {v!r}')
        assert p['category'] in CATEGORIES, (
            f"{slug}: category {p['category']!r} is not one of {CATEGORIES}")
        assert p['year'] is None or (isinstance(p['year'], int) and 1900 < p['year'] < 2100), (
            f"{slug}: year is {p['year']!r} — leave it None rather than guess")
        assert p['story'] and p['title'] and p['city'] and p['state'], f'{slug}: missing text'
        # A film with no words over it would be a rectangle in the middle of a
        # page. The band is only built for a row that brought both.
        assert not p.get('film') or (p.get('film_eyebrow') and p.get('film_line')), (
            f'{slug}: film= needs film_eyebrow and film_line beside it')
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
    """The menu across the top of the screen, at every width.

    Ephraim's reference is Overall Murals and the owner wrote down what he
    took from it (CLAUDE.md, round three): "the menu runs across the top of
    the screen, not tucked on the right — a full horizontal nav beside the
    wordmark, visible at every width (no hamburger)." So the hamburger is
    gone, and with it the panel and the JavaScript that opened it: the
    wordmark is on the left, the five links run across the middle, the
    consult button is on the right, and on a phone the row of links stays
    where it is and scrolls sideways. Nothing here is ever hidden behind a
    control, which is the whole of the reference.

    The consult button is outside the list rather than the last item in it:
    it is not one of the five pages, and the list has to be able to centre
    itself between two things that are not the same width.
    """
    items = ''.join(f'<li><a href="{u(href)}">{label}</a></li>' for label, href in NAV)
    return f'''<header class="nav">
  <div class="wrap">
    {brand(f'{SITE_NAME} home')}
    <nav class="nav-bar" aria-label="Main"><ul class="nav-links">{items}</ul></nav>
    <a class="btn btn-mint btn-sm nav-cta" href="{u('/contact')}">Book a free consult</a>
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
      <div><h4>Work</h4><ul>{work}<li><a href="{u('/work')}">All the work</a></li></ul></div>
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


def _uid(text):
    """A stroke's name, out of the words it is painted behind.

    Lower case, letters and digits, hyphens for everything else: the seed a
    stroke is generated from has to be stable across builds, and a heading is
    the only thing on hand that is both stable and unique to its page.
    """
    out = ''.join(c if c.isalnum() else '-' for c in text.lower())
    return '-'.join(p for p in out.split('-') if p)[:48] or 'stroke'


# The one-line script that goes after a <video> with two renditions. It calls
# the picker the head bootstrap defined, while the parser is still standing
# where the element is — see clip_sources().
PICK = '<script>oagPick()</script>'


def clip_sources(name):
    """(poster, the source the HTML names, the source a big screen swaps in).

    Every clip in out/video/ is built twice (make-*-clip.sh): the cut at the
    camera's own size and rate, and a 1920-wide companion of the same cut.

    **The server HTML names the companion.** That is the file a phone should
    be given, and it is the only file a visitor with no script or with reduced
    motion should ever be asked to fetch — for both of them the clip is
    display:none and there is nothing on screen to justify the download.

    The big one is named on data-hi, and PICK — one call, in the body, right
    after the element — swaps it in while the parser is still there, before
    the browser has begun choosing a resource. That is why it is not a line in
    site.js: site.js is deferred, and by the time a deferred script runs the
    1080 file is already on the wire, so swapping it there would spend a
    request to save a download. Here nothing is requested twice.
    """
    for suffix in ('.mp4', '-1080.mp4', '.webp'):
        assert os.path.exists(f'out/video/{name}{suffix}'), (
            f'clip {name}: out/video/{name}{suffix} is missing — '
            f'run the make-*.sh that builds it')
    return (u(f'/assets/video/{name}.webp'),
            u(f'/assets/video/{name}-1080.mp4'),
            u(f'/assets/video/{name}.mp4'))


def page_hero(eyebrow, title, lead, media_slug=None, crumb=None, cls='', media_alt='',
              video=None, wall=False, extra='', tip=False, hl=''):
    """The top of a page: a photograph, a shade over it, and the words.

    The photograph goes through pic() rather than img() so the browser picks a
    rendition instead of always taking the widest one, and it is the page's
    LCP element, so it loads eagerly at high priority. media_alt is the
    description of the mural; leave it empty only when the photograph is
    genuinely decorative, which on this site it never is.

    video names a clip in out/video/. Two renditions of it exist — the cut at
    the camera's own size and a 1920-wide companion — and clip_sources() says
    which one the HTML names and which one a wide screen swaps in before the
    browser has asked for anything. It
    plays muted, looped, inline, on top of the photograph: the photograph is
    still the LCP element and the still every crawler, reader mode and
    reduced-motion visitor gets; the clip is the motion. site.js pauses it
    under prefers-reduced-motion and data-saver, and the CSS hides it there
    too, so the page never depends on the clip having arrived.

    wall marks this hero as a blank wall the visitor can paint (site.js,
    "Wall"). It is one attribute and nothing else: the canvas, the strokes and
    the sound toggle are all built by the script under html.motion, so the
    no-JS and reduced-motion renders are the hero exactly as it is today. It
    only belongs on a hero with no photograph — there is nothing blank about
    a wall with a mural already on it.

    extra is markup dropped inside the hero's words, under the lead: the 404's
    two ways back, and nothing else so far.

    hl is a second line of the headline, painted on a stroke of mint the way
    Home's is (highlight(), strokes.py) — the option, on every page that
    wants it. The words on the paint are ink, which is the only thing mint
    may carry; the stroke is seeded from the words themselves, so it is the
    same stroke on every build and a different one on every page.

    tip stands a paint tin on the floor of the hero's text column ("Tip",
    tip_can()). Unlike wall, it is not one inert attribute: the tin is drawn
    in the server HTML and is there in every render, so the hero carries
    .has-tip and the stylesheet reserves the tin its room in all three. The
    tipping, the pour, the pool and the rule below are site.js's, under
    html.motion.
    """
    clip = ''
    if video:
        poster, src, hi = clip_sources(video)
        clip = (f'<video class="hero-video" data-autoplay data-hi="{hi}" autoplay muted loop '
                f'playsinline preload="metadata" poster="{poster}" aria-hidden="true" tabindex="-1">'
                f'<source src="{src}" type="video/mp4"></video>{PICK}')
    media = (f'<div class="hero-media">'
             f'{pic(media_slug, media_alt, HERO_SIZES, extra="fetchpriority=\"high\"", lazy=False)}{clip}'
             f'</div><div class="hero-shade"></div>') if media_slug else ''
    crumbs = (f'<div class="crumbs"><a href="{u("/")}">Home</a><span>/</span><span>{crumb or title}</span></div>'
              if crumb is not False else '')
    # Home's hero is the headline and nothing else (the mockup): the sentence
    # that used to stand under it is the shouted lead of the band below, so
    # the paragraph is left out rather than left empty.
    lead_html = f'<p class="lead">{lead}</p>' if lead else ''
    assert not (wall and media_slug), 'page_hero: a wall to paint is a hero with no photograph'
    cls = (cls + ' has-tip').strip() if tip else cls
    # A hero with a photograph is one of the three black bands — the words on
    # it are light. A hero without one is the white page, and its words are
    # ink. The class says which, so no rule has to guess.
    cls = (cls + ' has-media').strip() if media_slug else cls
    if hl:
        title = f'{title}<br>{highlight(hl, "hl-" + _uid(hl))}'
    return f'''<section class="page-hero{" " + cls if cls else ""}"{' data-wall' if wall else ''}>{media}
  <div class="wrap"><div class="hero-inner">{crumbs}<div class="eyebrow">{eyebrow}</div><h1>{title}</h1>{lead_html}{extra}{tip_can() if tip else ''}</div></div></section>'''


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


def stroke_band(inner, uid, cls='', h=720, before=''):
    """A section whose background is one swept stroke of mint (strokes.py).

    Owner, 2026-09-19: "Maybe make the teal a brush stroke — so it looks like
    he painted on the screen." So this is the only way a mint band happens on
    this site. `inner` is the words; `uid` names the stroke, which is also its
    seed — the same name is the same stroke on every build, and two bands on
    one page are two different strokes because they are two different names.

    The stroke is behind the words and aria-hidden, the words are in the
    ordinary .wrap, and the drawing is stretched over the section with
    preserveAspectRatio="none": a stroke over a taller section is a wider
    brush, which is the right answer. Nothing here is gated on motion — a
    painted band is not an animation, it is the page.

    `before` is a slot outside the words and beside the stroke, for the one
    thing that has to be the size of the section rather than the size of
    the paragraph: the closing call to action's ambient glow.
    """
    return f'''<section class="band{" " + cls if cls else ""}">{before}
  <div class="stroke-wrap">{stroke_svg(uid, h=h)}</div>
  <div class="wrap">{inner}</div>
</section>'''


def highlight(text, uid):
    """Words on a stroke of mint — the hero's second line, and its like.

    The stroke is drawn behind the letters rather than under them: it sits at
    z-index -1 inside the span's own stacking context, a little larger than
    the words in both directions, so the paint runs past the ends of the line
    the way a highlight laid with a brush does. The type on it is ink, which
    is the only thing mint may carry (13.8:1).
    """
    return (f'<span class="hl">{highlight_svg(uid)}'
            f'<em>{text}</em></span>')


def cta(title="Let&rsquo;s paint it",
        eyebrow='got a wall?',
        text='Tell us the wall, the city and roughly how big it is. We will come back with a plan and a price.',
        primary=('Book a free consult', '/contact'),
        secondary=('See the work', '/work'),
        uid='lets-paint-it'):
    """The last thing on every page, and the second band painted in mint.

    The mockup's closing section: the marker asking "got a wall?", the
    headline at the size of a hoarding, and a coral button on the paint. It
    keeps the second link the live site had — a visitor who is not ready to
    write still has somewhere to go — and it keeps the ambient glow, which
    is one of the four places the Live verb is allowed to light (CLAUDE.md).
    The glow is a sibling of the stroke rather than a child of the words, so
    it is the section that breathes and not the paragraph.

    The primary button is coral rather than mint for the obvious reason: a
    mint button on a mint stroke is a button nobody can see.
    """
    return stroke_band(f"""<div class="cta rv">
    <span class="eyebrow">{eyebrow}</span>
    <h2>{title}</h2>
    <p class="serif">{text}</p>
    <div class="btn-row"><a class="btn btn-pop" href="{u(primary[1])}">{primary[0]} {ICONS['arrow']}</a><a class="btn btn-ghost" href="{u(secondary[1])}">{secondary[0]}</a></div>
  </div>""", uid, cls='cta-wrap', h=640, before=glow())


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


def beats(items, cls='', quoted=True, rule=False):
    """A row of stages: the stage name, then the sentences under it.

    `quoted` is not decoration. Where the words are Ephraim's they are set in
    a <blockquote>, because that is what they are; where they are ours — the
    four beats of a graffiti job, who the service is for — they are ordinary
    paragraphs. Marking our own prose as a quotation of his would be the one
    kind of lie this site cannot afford.

    `rule` is Brush: the mint rule the stages sit on is painted in by a brush
    as the visitor scrolls, and un-painted as they scroll back up. It is on
    his three stages and nowhere else — the Home row and the About column,
    which are the same three sentences twice.
    """
    body = ('<blockquote><p>{0}</p></blockquote>' if quoted else '<p>{0}</p>')
    li = ''.join(
        f'<li class="beat rv{" rv-d" + str(i) if i else ""}">'
        f'<h3>{stage}</h3>{body.format(words)}</li>'
        for i, (stage, words) in enumerate(items))
    ol = f'<ol class="{("beats " + cls).strip()}">{li}</ol>'
    return brush_rule(ol) if rule else ol


def brush_rule(stages):
    """The rule the stages sit on, and the brush that paints it (Brush).

    All of it is in the server HTML, because the page has to be finished
    without a script: the track is an absolutely positioned box with the mint
    line on its bottom edge, laid over the top hairline of the stage list, so
    it adds nothing to the layout and a page with no JavaScript — or a
    visitor who asked for reduced motion, who never gets html.motion — simply
    reads a rule that is already painted. The brush and the wet edge are here
    too, and are display:none outside html.motion: markup a crawler can see
    and nobody else can. site.js writes one number, --paint, and the
    stylesheet does the rest.
    """
    return (f'<div class="beatrule" data-brush>'
            f'<div class="beatrule-track" aria-hidden="true">'
            f'<span class="beatrule-line"></span>'
            f'<span class="beatrule-pos"><span class="beatrule-wet"></span>'
            f'<span class="beatrule-brush">{brush_rule_svg()}</span></span>'
            f'</div>{stages}</div>')


def spray_band(text='Open Air / Gallery', cls=''):
    """A full-width band with a word sprayed across it (site.js, "Spray").

    Owner, 2026-09-19: "Is there any way to have a can of spray paint spray
    'Open Air Gallery' underneath the hero as a section builder?" So this is
    the section builder: give it a word and it gives you a band, the word set
    in the wordmark's own face at the size of a headline. `text` is split on
    a slash into the lines it stacks as, which is what the wordmark does in
    the nav and in the footer; anything else is one line.

    The word is real text in the server HTML and is the only thing that gives
    the band its height. The can is here too — art.py's spraycan_pass_svg(),
    one drawing, once — and it is display:none outside html.motion, the way
    Brush's brush is: markup a crawler can see and nobody else can. The halo,
    the drips and the mask are site.js's, built under html.motion and nowhere
    else, so a page with no script and a visitor who asked for reduced motion
    both get the wordmark as plain text, with no can over it.

    Nothing in it can move a box. The track is absolutely positioned inside a
    stage that shrink-wraps the word, the band clips what leaves it, and the
    mask that hides the letters before the can reaches them changes no
    metric of the text at all.
    """
    lines = ''.join(f'<span>{t.strip()}</span>' for t in text.split('/'))
    return f'''<section class="spray-band{" " + cls if cls else ""}" data-spray>
  <div class="wrap"><div class="spray-stage">
    <p class="spray-word">{lines}</p>
    <span class="spray-track" aria-hidden="true"><span class="spray-pos"><span class="spray-mist"></span><span class="spray-can">{spraycan_pass_svg()}</span></span></span>
  </div></div>
</section>'''


def tip_can():
    """The paint tin on the hero's floor, and nothing else (site.js, "Tip").

    Owner, 2026-09-19: "Maybe a paint bucket you click and it spills." So a
    tin sits on the baseline of the hero's text column and, clicked or dragged
    over, tips and empties itself down the hero.

    Everything here is in the server HTML and everything here is upright: the
    tin is art.py's can_tipping_svg(), which is can_svg()'s drawing with the
    paint in the rim in a group of its own, and with no script — or for a
    visitor who asked for reduced motion, who never gets html.motion — it is
    simply a drawn tin standing beside the headline, as still as the
    photograph behind it. It is not a <button> in that document either: a
    control that does nothing is worse than a picture, so site.js is what
    gives it a role, a tab stop and a name, under html.motion and nowhere
    else. The sheet of paint, the pool at the hero's foot and the run onto
    the section below are all site.js's too, and none of them exists here.

    Nothing in it can move a box: .tip is absolutely positioned in the
    bottom-left corner of the hero's words, in room the stylesheet has
    already reserved for it in every render — page_hero(tip=True) puts
    .has-tip on the hero, and .has-tip's padding is the tin's own height.
    """
    return (f'<div class="tip" data-tip>'
            f'<span class="tip-can" data-tip-can>{can_tipping_svg()}</span></div>')


def tip_rule():
    """The mint rule the paint becomes when it drips through (site.js, "Tip").

    The rule is real, it is mint, and it is finished in the server HTML — a
    hairline across the top of the section the way Brush's rule sits across
    the top of the stage list. Only the motion is gated: under html.motion it
    waits at scaleX(0) and is filled outward from the point the pool drips
    through, and then it takes the Cure sheen.

    The bail-out is the other way round from the rest of this file. Everything
    else hidden under html.motion reveals itself after 2.8s in case the script
    never arrives; a rule that did that would be painted before the visitor
    had touched the tin, which is the whole mechanic given away. So the 2.8s
    self-reveal is here — a page whose site.js never lands still ends up with
    its rule — and site.js calls it off the moment it binds (html.tipready),
    exactly as Roll it in calls off the primer's.
    """
    return ('<div class="tiprule" data-tip-rule>'
            '<span class="tiprule-line" aria-hidden="true"></span></div>')


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


def layout(path, title, desc, body, ld=None, noindex=False, wash=False, og=None):
    """The document around a page body.

    `wash` carries the two Wash assets — css/wash.css and js/wash.js — and it
    is opt-in per page on purpose (wall.py's docstring says so): only Home and
    /graffiti-removal hold a drawn wall, and on every other page the pair
    would be two requests for a file that binds nothing.

    Splat used to be opt-in here too, as a `data-splat` attribute on Home's
    <body>. It is sitewide now — every button splats and every nav, wordmark
    and footer link paints its page transition — so there is nothing per-page
    left to mark: site.js binds it everywhere, under html.motion.
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
    # The roller sprite rides along on any page that has a card to roll in,
    # and on no other: one <symbol> the cards and the cursor both borrow.
    props = roller_sprite() if 'class="pcard' in body else ''
    washer = (f'<link rel="stylesheet" href="{u("/css/wash.css")}?v={asset_v("css/wash.css")}">'
              if wash else '')
    # wash.js goes after site.js, not in the head with its stylesheet. Both
    # are deferred, so they run in document order, and wash.js asks site.js
    # for the shared Sound module the moment it binds — one AudioContext for
    # the page, one persisted mute state, whichever mechanic asked for it.
    washer_js = (f'\n<script src="{u("/js/wash.js")}?v={asset_v("js/wash.js")}" defer></script>'
                 if wash else '')
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(d){{var c=d.documentElement.classList;c.add('js');try{{if(!matchMedia('(prefers-reduced-motion: reduce)').matches)c.add('motion')}}catch(e){{}}var hi=false;try{{hi=c.contains('motion')&&matchMedia('(min-width: 900px)').matches}}catch(e){{}}window.oagPick=function(){{var s=d.currentScript,v=s&&s.previousElementSibling,q;if(!hi||!v||!v.dataset||!v.dataset.hi)return;q=v.querySelector('source');if(q)q.src=v.dataset.hi}}}})(document)</script>
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
{robots}
<meta property="og:type" content="website"><meta property="og:site_name" content="{SITE_NAME}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{canonical}">
{ogimg}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{PAPER}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{u('/css/site.css')}?v={asset_v("css/site.css")}">
{washer}
{ldjson}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{props}{nav_html()}
<main id="main">
{body}
</main>
{footer_html()}{washer_js}
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


MARQUEE = ('Always hand painted', 'Murals', 'Banners &amp; signs', 'Graffiti removal')


def marquee(items=MARQUEE, times=3):
    """The strip that runs between two bands (Colossal, CLAUDE.md round three).

    One of the three black bands the white canvas keeps, and the only one
    that is type and nothing else: the four things the company does, set in
    the headline face, divided by a coral bar, running off both edges of the
    screen because a strip that fits is a list. It does not move — the motion
    on this site is the paint verbs, and every one of them is written down.
    """
    row = ''.join(f'<span>{t}</span><b aria-hidden="true">|</b>' for t in items)
    return (f'<div class="mq" aria-label="What Open Air Gallery does">'
            f'{row * times}</div>')


def row(slug, alt, words, flip=False, sizes=PAIR_SIZES):
    """A photograph down one half of the page and the words down the other.

    The mockup's spine: Roots, Vision and Public works are all this, and the
    only difference between them is which side the wall is on. `flip` puts
    the words first, which is also the order they stack in on a phone — the
    one place the two disagree, and the mockup's own answer.
    """
    media = f'<div class="rows-media">{pic(slug, alt, sizes)}</div>'
    body = f'<div class="rows-words rv">{words}</div>'
    inner = (body + media) if flip else (media + body)
    return f'<section class="rows{" flip" if flip else ''}">{inner}</section>'

# ------------------------------------------------------------- PAINTED FOR
# The logo wall, and the strand of faces beside it. CLAUDE.md, round three:
# Colossal shows who it has painted for, so Ephraim's site does too — "in each
# brand's actual colours", which is why every mark here is the brand's own
# file and not a drawing of it.
#
# brands.py holds the roster, the source URL and the licence for each mark;
# process-brands.sh does the downloading. This is only the rendering: a ruled
# five-by-three grid on white, two columns on a phone, every mark at the same
# optical height rather than the same box height, each cell a real <img> with
# its own width and height so the wall never reflows as the logos land.
from brands import BRANDS, intrinsic


def brand_mark(b):
    """One mark: the brand's own SVG, or type in the brand's own colour."""
    if b['mark'] == 'svg':
        w, h = intrinsic(b['slug'])
        return (f'<img class="bmark" src="{u("/assets/img/brands/" + b["slug"] + ".svg")}" '
                f'alt="{html.escape(b["name"])}" width="{w:g}" height="{h:g}" '
                f'style="--bh:{b["h"]}px;--bhm:{b["hm"]}px" loading="lazy" decoding="async">')
    # No free file for this one yet. Type, in the brand's own colour, and the
    # name is the content — a screen reader hears the same thing either way.
    return (f'<span class="bword {b["face"]}" style="color:{b["colour"]}">'
            f'{html.escape(b["name"])}</span>')


def brand_wall(eyebrow='painted for', title='The brands', cls=''):
    """The "Painted for" wall — fifteen marks, ruled, on white."""
    cells = ''.join(f'<li class="bcell">{brand_mark(b)}</li>' for b in BRANDS)
    sect = ('brandwall ' + cls).strip()
    return f'''<section class="{sect}"><div class="wrap">
  <div class="bhead rv"><span class="marker">{eyebrow}</span><h2 class="tall">{title}</h2></div>
  <ul class="bgrid rv" aria-label="Brands Open Air Gallery has painted for">{cells}</ul>
</div></section>'''


# The second strand. CLAUDE.md, round three: the owner asked to "add in Kylie
# or mentioned models" — so beside the brands there are the people, and they
# appear the one way this site will show a person: as a wall Ephraim painted
# of them, never as a stock photograph of the person themselves.
#
# Four of the five have a wall on this site and each name is the link to it.
# Kylie Jenner is the fifth and she links nowhere, because no photograph of
# that wall has reached us — a name with no picture behind it is honest, and a
# name linked to somebody else's wall would not be. She is a line in CLAUDE.md
# under what Ephraim still owes, and the day the photograph lands `slug` is
# filled in and nothing else on this page changes.
#
# `+ the campaign models` is a marker aside and not a name, because Ephraim has
# not named them yet. It says there are more without inventing who.
FACES = [
  dict(name='Kylie Jenner', slug=None,
       where='the mural project \u2014 no photograph of the wall yet'),
  dict(name='John Lewis', slug='john-lewis-rochester'),
  dict(name='Malcolm X', slug='malcolm-x-rochester'),
  dict(name='Antwuan', slug='uber-san-francisco'),
  dict(name='Dexter', slug='showtime-dexter-boston'),
]
FACES_MORE = '+ the campaign models'

_BY_SLUG = {p['slug']: p for p in PROJECTS}
for _f in FACES:
    assert _f['slug'] is None or _f['slug'] in _BY_SLUG, \
        f"faces: {_f['name']} points at {_f['slug']!r}, which is not a project"


def faces_strand(eyebrow='and the faces', title='Painted portraits', cls=''):
    """The faces row: five names set as the serif they deserve, four of them links."""
    items = []
    for f in FACES:
        if f['slug']:
            q = _BY_SLUG[f['slug']]
            label = f"{f['name']} \u2014 the {q['title']} wall, {q['city']}, {q['state']}"
            items.append(f'<a class="face" href="{u("/work/" + f["slug"])}" '
                         f'aria-label="{html.escape(label)}">{html.escape(f["name"])}</a>')
        else:
            items.append(f'<span class="face face-unlinked">{html.escape(f["name"])}</span>')
    items.append(f'<span class="face-more marker">{html.escape(FACES_MORE)}</span>')
    sect = ('faces ' + cls).strip()
    return f'''<section class="{sect}"><div class="wrap">
  <div class="bhead rv"><span class="marker">{eyebrow}</span><h2 class="tall">{title}</h2></div>
  <p class="faces-lead serif rv">The people on the walls, painted at building scale &mdash;
  John Lewis and Malcolm X in Rochester, Antwuan on the Uber wall in San Francisco, Dexter on
  the Showtime wall in Boston. Each name goes to its wall.</p>
  <div class="frow rv">{''.join(items)}</div>
</div></section>'''


# ------------------------------------------------------------ PUBLIC WORKS
# The strand the owner asked for in his own words (CLAUDE.md, round three):
# "he has more not on there, and wants to show more of his public works like
# Colossal did; he's been to Mexico, Brazil, teen empowerment and more, so
# don't limit."
#
# So this block exists to be open-ended. It names the places he has worked and
# the kinds of work — community walls, civil-rights portraits, teen-empowerment
# murals — and it says out loud, in marker, that more is coming as the
# photographs arrive. It does not count anything, it does not present the
# roster as complete, and it does not invent a project that has no photograph.
#
# The picture is about-team, the crew on the lift, because that photograph is
# about the people doing the work rather than about one brand's wall — it is
# the right placeholder for this strand and it is labelled as the crew, not as
# a public commission. A real public-works photograph replaces it in one line.
PW_PLACES = ('Mexico', 'Brazil', 'Rochester', 'New York')
PW_MARKER = 'more coming as the photos arrive'


# The community wall the strand leads with. It is a project row like any other,
# read from projects.py, so the day its feet or a better photograph arrive this
# section changes with the rest of the site and not on its own.
FLOWER_CITY = BY_SLUG['flower-city-arts-center-rochester']


def public_works(cls=''):
    """Public works — the community strand, framed for the work we do not have yet.

    The photograph is the Flower City wall itself now, rather than the crew on a
    lift: the section is about community walls and there is finally one of them
    on the site to show. The copy names it and links to it, and still says what
    it has always said — that what we have photographs of is not the extent of
    the work.
    """
    places = ' &middot; '.join(PW_PLACES)
    sect = ('pw ' + cls).strip()
    return f'''<section class="{sect}"><div class="pw-grid">
  <figure class="pw-media rv">{pic(FLOWER_CITY['hero'],
      'The Flower City Arts Center wall in Rochester, New York — painted storefronts '
      'and portraits along a concrete underpass, with the crew still on the lifts',
      PAIR_SIZES)}</figure>
  <div class="pw-words rv rv-d1">
    <h2 class="tall">Public <em class="pop">works</em></h2>
    <p class="pw-places wide">{places}</p>
    <p class="serif">Beyond the brands: community walls, civil-rights portraits and
    teen-empowerment murals &mdash; painted with the people who live beside them, in
    Mexico, Brazil and at home in Rochester and New York.</p>
    <p class="serif">Three Rochester walls are the ones we have photographs of so far:
    the <a href="{u('/work/' + FLOWER_CITY['slug'])}">{FLOWER_CITY['title']}</a> wall on the
    underpass by the ballpark, and the two civil-rights portraits across town. They are not
    the extent of the work, and this page has room for the rest.</p>
    <p class="pw-note marker">{PW_MARKER}</p>
    <div class="row-end"><a class="btn btn-ghost" href="{u('/work')}#f-civic">See the public works {ICONS['arrow']}</a></div>
  </div>
</div></section>'''


# --------------------------------------------------------- THE DIAMOND BOARD
# The Services page. Overall Murals' *idea* — cards as negative space over a
# deep, parallaxing mural layer that hands over seamlessly — in Ephraim's own
# form. The owner, 2026-09-19: "Maybe we switch ours up and use some sort of
# diamond concept, add his teal and a few other colours as splatter on the
# crisp white cards before we add the text — let's not copy."
#
# So the grid is turned forty-five degrees. The white diamonds are the cards
# and the gaps between them are the windows: one strip of his walls laid end
# to end behind the whole board, each wall feathered into the next with a mask
# gradient so there is never a seam to see, moving slower than the page so the
# wall sits behind it rather than on it.
#
# Every card is splattered first and lettered after (splatter.py): two or three
# clusters of the drop-cloth palette thrown at the diamond's points, where the
# type never goes, each with a rim, a gloss and a drip. Seeded per card, so no
# two match and every build is byte for byte the last one.
from splatter import splatter_svg

# The drop-cloth palette. The same four hexes are declared as tokens in the
# stylesheet's PAGES block; splatter.py needs real values rather than var()
# names, so they are written once here and once there and nowhere else.
DROP_PALETTE = ('#71EEB8', '#FF4F2E', '#FFD23F', '#7B5CFF')

# The strip behind the board: five of his walls, in the order they hand over.
DEEP_WALLS = ('gucci-new-york-hero', 'crown-royal-trail-blazers-hero',
              'john-lewis-rochester-hero', 'uber-san-francisco-hero',
              'malcolm-x-rochester-hero')

# Six services, and the lattice they sit on: three across, then two on the
# half step, then one. `l` and `t` are per cent of the board.
BOARD = [
  ('01', 'Murals', '20%', '5%',
   'It starts from a small image and explodes onto a massive canvas &mdash; brand '
   'walls, portraits and public works, painted by hand at building scale.',
   'See the walls', '/work'),
  ('02', 'Banners &amp; signs', '50%', '5%',
   'Hand-lettered signage and painted banners for storefronts and campaigns, '
   'done with the same brush as the walls.',
   'See the signs', consult_path('Banners and signs')),
  ('03', 'Graffiti removal', '80%', '5%',
   'Industrial-strength cleaning for tags, stains and overspray in NYC. Send a '
   'picture; we send back a quote and a date.',
   'Send a photo', consult_path('Graffiti removal')),
  ('04', 'Public works', '35%', '40%',
   'Community walls, civil-rights portraits and teen-empowerment murals in '
   'Mexico, Brazil, Rochester and New York.',
   'See the public works', '/work#f-civic'),
  ('05', 'Paint science', '65%', '40%',
   'We analyze how the paint will decay and how the light will affect its '
   'colour, so we use only what we need and what will last.',
   'How a wall is preserved', '/about'),
  ('06', 'Commercial painting', '50%', '75%',
   'Facades, interiors and the coating that keeps a finished wall easy to '
   'clean &mdash; the crew that paints it knows how to keep it.',
   'Book a consult', consult_path('Commercial painting')),
]


# The four cells that complete the lattice are brand cards (owner, 2026-09-19:
# "if you need more cards, add brand cards mixed in that he's worked with, just
# a large logo on the blanks"): a splattered white diamond carrying one big
# mark from the brand wall — Gucci, Sprite, Ford, Heineken, the four with the
# strongest real logos on file.
BOARD_BRANDS = ('gucci', 'sprite', 'ford', 'heineken')


def _brand_diamond(i, slug):
    b = next(x for x in BRANDS if x['slug'] == slug)
    cols = [DROP_PALETTE[0], DROP_PALETTE[1 + i % 3], DROP_PALETTE[1 + (i + 1) % 3]]
    spat = splatter_svg(f'd{i}', cols, 4100 + i * 137)
    return (f'<div class="dia brand"><div class="sq">{spat}'
            f'<div class="tx"><div class="bigmark">{brand_mark(b)}</div></div></div></div>')


def _diamond(i, row):
    if isinstance(row, str):
        return _brand_diamond(i, row)

    # The lattice positions are not here. They are per breakpoint — three
    # across at desktop, two on a tablet, one on a phone — and a position in
    # the markup would be an inline style that no media query could move.
    num, name, _l, _t, words, more, href = row
    # A different pair of the palette on every card, rotated so the teal he
    # asked for is on all of them and the other three take turns beside it.
    cols = [DROP_PALETTE[0], DROP_PALETTE[1 + i % 3], DROP_PALETTE[1 + (i + 1) % 3]]
    spat = splatter_svg(f'd{i}', cols, 4100 + i * 137)
    return (f'<div class="dia"><div class="sq">{spat}'
            f'<div class="tx"><span class="num marker">{num}</span>'
            f'<span class="rule" aria-hidden="true"></span>'
            f'<h3 class="tall">{name}</h3><p class="serif">{words}</p>'
            f'<a class="more tall" href="{u(href)}">{more} '
            f'<span aria-hidden="true">&rarr;</span></a></div></div></div>')


def services_board(eyebrow='our services',
                   title=('There&rsquo;s a wall for everyone<br>when you choose '
                          '<em class="pop">hand-painted</em> murals.')):
    """The board: one deep strip of walls under a packed diamond lattice.

    The strip is the only thing that moves, it moves at about half the page's
    speed, and it moves through a CSS scroll timeline rather than through a
    scroll handler of its own — so there is no second rAF loop on this page,
    nothing to run on a browser that has no scroll timelines, and reduced
    motion and no-script both get the strip standing still at its first
    position, which is the state the design is drawn for. It carries
    data-deep and data-deep-rate so site.js can take it over from the Live
    loop later; the stylesheet stands the CSS animation down the moment
    <html> gains .deep-js, so the two can never both be driving.
    """
    walls = ''.join(
        f'<div class="dwall" style="background-image:url('
        f'{u("/assets/img/" + w + "-1600.webp")})"></div>' for w in DEEP_WALLS)
    # Ten cells in lattice order: three across, then a row on the half step
    # with fillers at the edges, then the last card between two fillers. The
    # positions live in the stylesheet by nth-child, per breakpoint.
    b = BOARD_BRANDS
    order = [BOARD[0], BOARD[1], BOARD[2], b[0], BOARD[3], BOARD[4], b[1],
             b[2], BOARD[5], b[3]]
    dias = ''.join(_diamond(i, row) for i, row in enumerate(order))
    return (f'<section class="sboard-head"><div class="wrap">'
            f'<p class="marker">{eyebrow}</p><h2 class="tall">{title}</h2>'
            f'</div></section>\n'
            f'<section class="sboard-wrap">'
            f'<div class="deep" data-deep data-deep-rate="0.5" aria-hidden="true">{walls}</div>'
            f'<div class="sboard">{dias}</div></section>')


# ---------------------------------------------------------------- HOME
# Every number on this page is computed from projects.py. None of them is
# typed: "Twelve walls. Over 23,000 square feet." is the roster adding itself
# up, so the day a thirteenth wall lands the sentence is already true.
WALLS = len(PROJECTS)
SQ_FT = total_sq_ft()
CITIES = {(p['city'], p['state']) for p in PROJECTS}
# Every figure on the site is computed from the walls we have the feet for.
# A wall Ephraim has photographed but never measured for us is not a small
# wall and must never be counted as one — it is simply not in the sum, and
# the sentence around the sum says what the sum is of.
MEASURED = measured()
TALLEST = max(MEASURED, key=lambda p: p['dim_h'])
WIDEST = max(MEASURED, key=lambda p: p['dim_w'])
# The Rochester pair is a pair because the two walls are the same size to the
# foot, and that is what the band and the row on Home both say. It is not
# "the civic category" — Flower City Arts Center is civic and in Rochester too,
# and dropping it into a band headed "Two walls in Rochester" would make the
# heading a lie the day it joined. So: the civic walls in Rochester we have the
# feet for, and an assert, because the copy below counts them out loud.
ROCHESTER = [p for p in PROJECTS if p['category'] == 'civic'
             and p['city'] == 'Rochester' and p['dim_w'] is not None]
assert len(ROCHESTER) == 2, (
    'the Rochester band and the Vision row on Home both say "two": '
    f'{[q["slug"] for q in ROCHESTER]}')


def stat(figure, label, mark=''):
    m = f'<span class="f">{mark}</span>' if mark else ''
    return (f'<li class="stat rv"><span class="stat-n">{figure}{m}</span>'
            f'<span class="stat-l">{label}</span></li>')


CITY_LIST = []
for _p in PROJECTS:
    if _p['city'] not in CITY_LIST:
        CITY_LIST.append(_p['city'])


def and_list(names):
    """A, B and C — the roster read out loud rather than counted.

    Never a count: "he has more not on there ... so don't limit" (owner,
    2026-09-19). The names are what we have photographs of; the sentence
    they land in is the one that says the work does not stop there.
    """
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]


CROWN = BY_SLUG['crown-royal-trail-blazers']

pages['/index'] = dict(
  wash=True,
  title=f'{SITE_NAME} | Murals at building scale, New York and nationwide',
  desc='Open Air Gallery is a muralist and large-image company led by Ephraim. Gucci in Manhattan at 81 by 80 feet, Crown Royal in Portland at 85 by 90, John Lewis and Malcolm X in Rochester.',
  body=f'''
{page_hero('est. New York &middot; painted by hand',
           f'Murals that<br>{highlight("capture the gaze", "home-hero")}',
           '',
           media_slug='gucci-new-york-hero',
           media_alt='The Gucci mural by Open Air Gallery, eighty-one feet across a New York City wall',
           video='hero-johnnie-walker',
           crumb=False, cls='tall hero-mid')}

{spray_band()}

{stroke_band(f"""<h2>Always hand painted</h2>
    <p class="band-lead wide">Open Air Gallery is the New York muralist and large-image company behind eighty-one feet of Gucci in Manhattan, eighty-five feet of Crown Royal in Portland, and John Lewis and Malcolm X in Rochester.</p>
    <p class="band-copy serif">It starts from a small image and explodes onto a massive canvas. The ability to scale and project is what differs an artist and a muralist.</p>""",
             'always-hand-painted')}

{row('crown-royal-trail-blazers-hero',
     f'{CROWN["title"]} mural by Open Air Gallery, {CROWN["city"]}, {CROWN["state"]}',
     f"""<h2>Roots</h2>
     {dims(CROWN['dim_w'], CROWN['dim_h'], 'row')}
     <p class="serif">{CROWN['title']}, {CROWN['city']}. Walls in {and_list(CITY_LIST)} &mdash; and in Mexico and Brazil &mdash; the tallest of them {spell(TALLEST['dim_h'])} feet.</p>
     <p class="serif">There is a science to paint. We analyze the way the paint will decay over time and how the light will affect its color, so we use only what we need and what will last.</p>""")}

{row('john-lewis-rochester-hero',
     f'{ROCHESTER[0]["title"]} mural by Open Air Gallery, {ROCHESTER[0]["city"]}, {ROCHESTER[0]["state"]}',
     f"""<h2><span class="shout">Vision</span></h2>
     {dims(ROCHESTER[0]['dim_w'], ROCHESTER[0]['dim_h'], 'row')}
     <p class="serif">{ROCHESTER[0]['title']}, and {ROCHESTER[1]['title']} &mdash; two civil-rights walls in {ROCHESTER[0]['city']} at the same size to the foot.</p>
     <p class="serif">Each project is a labor of love, and we pour our hearts into every brushstroke.</p>""",
     flip=True)}

{brand_wall()}
{faces_strand()}

{marquee()}

<section class="alt stats-band">{glow()}<div class="wrap">
  <div class="section-head rv"><div class="eyebrow">the measure of it</div>
  <h2>Over {SQ_FT // 1000:,},000 square feet, and counting.</h2>
  <p class="lead serif">Added up wall by wall, the walls we have the feet for come to {SQ_FT:,} square feet of painted surface in {spell(len(CITIES))} cities &mdash; with more walls in Mexico, Brazil and beyond. The tallest of them stands {TALLEST['dim_h']} feet in {TALLEST['city']}; the widest runs {WIDEST['dim_w']} feet.</p></div>
  <ul class="stats">
    {stat(f'{SQ_FT:,}', 'square feet, and counting')}
    {stat(TALLEST['dim_h'], f'tallest wall, {TALLEST["city"]}', mark='&#8242;')}
    {stat(len(CITIES), 'cities, coast to coast')}
  </ul>
</div></section>

<section class="walls-band"><div class="wrap">
  <div class="section-head rv"><h2>The walls</h2>
  <p class="sub">measured in feet</p>
  <p class="lead serif">A first look here, the rest on the Work page. The figure over each photograph is how much wall it took &mdash; where he has given us the feet.</p></div>
  <div class="pgrid">{''.join(pcard(p, f'rv-d{i % 3}' if i % 3 else '') for i, p in enumerate(featured()))}
  </div>
  <div class="row-end rv"><a class="btn btn-ghost" href="{u('/work')}">See the work {ICONS['arrow']}</a></div>
</div></section>

<section class="alt pair-band">{glow()}<div class="wrap">
  <div class="section-head rv"><div class="eyebrow">{ROCHESTER[0]['city']}, {ROCHESTER[0]['state']}</div>
  <h2>Two walls in Rochester</h2>
  <p class="lead serif">{ROCHESTER[0]['title']} and {ROCHESTER[1]['title']}, painted in the same city at the same size: {ROCHESTER[0]['dim_w']} feet wide by {ROCHESTER[0]['dim_h']} feet tall, each of them.</p></div>
  <div class="pgrid pair">{''.join(pcard(p, 'pcard-lg' + (' rv-d1' if i else ''), PAIR_SIZES) for i, p in enumerate(ROCHESTER))}
  </div>
</div></section>

{row('about-team',
     'Ephraim and the Open Air Gallery crew painting a wall from a lift',
     """<h2>Public <span class="shout">works</span></h2>
     <p class="places wide">Mexico &middot; Brazil &middot; Rochester &middot; New York</p>
     <p class="serif">Beyond the brands: community walls, civil-rights portraits and teen-empowerment murals &mdash; painted with the people who live beside them, in Mexico, Brazil and at home.</p>
     <p class="marker note">more coming as the photos arrive</p>""")}

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow">how a wall gets painted</div><h2>Prep, paint, preservation</h2>
  <p class="lead serif">Ephraim&rsquo;s three stages, in his own words.</p></div>
  {beats(PROCESS, rule=True)}
</div></section>

{gr_band()}

{cta()}''')

# ---------------------------------------------------------------- WORK
# The index is one grid of all twelve with four chips over it. The chips are
# anchors and the filtering is CSS: `#f-civic:target ~ .pgrid .pcard:not(...)`
# hides what does not match. No JavaScript is involved, so the filter works in
# a text browser, in a crawler, and on a page whose script never arrived — and
# with nothing targeted the grid shows everything, which is the right default.
# The third chip says "Public works", not "Civic". CLAUDE.md, round three:
# Ephraim wants the community side shown the way Colossal shows its public
# art, and the two Rochester commissions are what we have photographs of
# today — so the chip is named for the strand and filters on the category we
# already have. Mexico, Brazil and the teen-empowerment murals join it as
# their photographs arrive, and the label does not have to change again.
#
# The chips carry no counts. A number beside "All" is a wall count, and this
# site does not state one (CLAUDE.md: "Don't say 12 walls — he has more not
# on there"). The filter is a filter; it is not a tally of his career.
CAT_LABEL = {'brand': 'Brands', 'portrait': 'Portraits', 'civic': 'Public works'}


def work_index():
    chips = [('#f-all', 'All')]
    chips += [(f'#f-{c}', CAT_LABEL[c]) for c in CATEGORIES]
    targets = '<span class="ftarget" id="f-all"></span>' + ''.join(
        f'<span class="ftarget" id="f-{c}"></span>' for c in CATEGORIES)
    bar = ''.join(f'<li><a class="chip" href="{href}">{label}</a></li>'
                  for href, label in chips)
    cards = ''.join(pcard(p, f"cat-{p['category']}" + (f' rv-d{i % 3}' if i % 3 else ''))
                    for i, p in enumerate(PROJECTS))
    return f'''<section class="work"><div class="wrap">
  {targets}
  <ul class="filters" aria-label="Filter the work">{bar}</ul>
  <div class="pgrid">{cards}</div>
</div></section>'''


pages['/work'] = dict(
  title=f'Work | {SITE_NAME}',
  desc=f'Walls Open Air Gallery has painted, with what each one measured — '
       f'{SQ_FT:,} square feet and counting, in {spell(len(CITIES))} cities, from Gucci in '
       f'Manhattan to John Lewis and Malcolm X in Rochester, and public works beyond them.',
  body=f'''
{page_hero('<span class="marker">measured in feet</span>', 'The walls',
           f'The walls we have photographs of, with what each one measured. '
           f'{SQ_FT:,} square feet and counting, in {spell(len(CITIES))} cities — brand walls, '
           f'painted portraits and public works, with more of both on the way.',
           crumb='Work')}
{work_index()}
{public_works()}
{faces_strand()}
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


def film_hero(p):
    """The top of a project page that has no feet to hang a figure on.

    scale_hero() is the hook: the wall at full bleed with a six-foot figure
    standing on it, sized from the wall's own width. With no width there is
    nothing to size her against, and a figure drawn to a guessed scale would
    be a lie told in pixels. So a wall we have no measurements for opens the
    way every other page on the site opens — the photograph, the shade and
    the words — and the film, where there is one, lies over the photograph
    exactly as Home's does: same element, same poster, same reduced-motion,
    data-saver and no-script behaviour, because it is the same function.

    The crumbs stay in the words below, where every project page has always
    kept them: page_hero's crumb is two levels and a project is three.
    """
    alt = f"{p['title']} mural by Open Air Gallery in {p['city']}, {p['state']}"
    return page_hero(f'<span class="marker">{p["city"]}, {p["state"]}</span>',
                     p['title'], '', media_slug=p['hero'], media_alt=alt,
                     video=p.get('video'), crumb=False, cls='tall')


def film_band(p):
    """The whole film, with its sound, behind a button.

    The hero clip is a cut with no sound, built to sit behind a headline. This
    is the film itself, at the size and the bitrate it was delivered in, with
    its audio, because a visitor who presses "watch the film" has asked for the
    film and not for a version of it. It is a big file and that is what the
    button is for: the element is preload="none", so nothing at all is fetched
    until somebody clicks, and nginx serves /assets/video/ with ranges, so what
    is fetched is the part being watched.

    The <video> is in the server HTML with its controls and its poster, so with
    no script — and under reduced motion — this is already a film a visitor can
    play, with the browser's own control. What site.js adds under html.motion is
    the one thing the native control cannot be: a button the size of the
    picture, in the site's own type. It is built there and nowhere else,
    because a button that cannot do anything is worse than no button (which is
    what the paint tin taught us). Splat never sees it either: the click
    mechanic acts on a[href] and on a form's submit, and this is neither.

    Nothing here can move a box: the frame is aspect-ratio 16/9 in every state,
    and the poster, the paused film and the playing film are the same shape.
    """
    film = p['film']
    for suffix in ('.mp4', '.webp'):
        assert os.path.exists(f'out/video/{film}{suffix}'), (
            f'film {film}: out/video/{film}{suffix} is missing — run ./make-films.sh')
    credit = f'<p class="credit">{p["credit"]}</p>' if p['credit'] else ''
    return f'''<section class="film"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow"><span class="marker">{p['film_eyebrow']}</span></div>
  <h2 class="tall">Watch the <em class="pop">film</em></h2>
  <p class="lead serif">{p['film_line']}</p></div>
  <figure class="film-frame rv" data-film>
    <video class="film-video" controls playsinline preload="none" width="3840" height="2160"
           poster="{u("/assets/video/" + film + ".webp")}">
      <source src="{u("/assets/video/" + film + ".mp4")}" type="video/mp4">
    </video>
  </figure>
  {credit}
</div></section>'''


def progress_band(p):
    """The wall going up: Ephraim's own portrait reel, in a phone-shaped frame.

    He shot the job vertically as well, and that reel is the one thing on this
    page that is about the *painting* rather than the painted wall: the artwork
    it was worked from, then the lift crossing the wall, filmed from the air.
    It is his edit and it is left whole.

    The clip is muted, loops, and plays only while it is on screen — one more
    contract on the Live observer rather than an observer of its own. Without
    html.motion there is no script to start it, so the server HTML gives the
    visitor a real control instead: the element carries `controls` and the
    poster, and site.js takes the controls away only once it knows it can play
    it. Reduced motion and no-script are therefore the same document, and it is
    a document where the reel can still be watched, on purpose.

    Nothing here can move a box: the frame is an aspect-ratio 9/16 well, the
    clip carries its own intrinsic 720x1280, and the poster is the same shape.

    The sentence is this reel's: a second progress reel would need its own.
    """
    poster, src, hi = clip_sources(p['progress'])
    return f'''<section class="progress"><div class="wrap">
  <div class="progress-grid">
    <figure class="progress-phone rv">
      <video class="progress-video" data-inview data-hi="{hi}" width="1080" height="1920" controls
             muted loop playsinline preload="metadata" poster="{poster}">
        <source src="{src}" type="video/mp4">
      </video>{PICK}
    </figure>
    <div class="progress-words rv rv-d1">
      <h2 class="tall">The wall <em class="pop">going up</em></h2>
      <p class="serif">Ephraim&rsquo;s own reel from the job: the artwork it was painted
      from, then the lift working its way across the wall, filmed from the air.</p>
    </div>
  </div>
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
  <div class="section-head rv"><div class="eyebrow"><span class="marker">The gallery</span></div><h2 class="tall">{spell(len(slides), cap=True)} views of the same wall</h2></div>
  {swipe(slides, f'Photographs of the {p["title"]} mural')}
</div></section>'''

    def step(q, side, label, icon):
        ft = q['dim_w'] is not None
        figure = f'{q["dim_w"]}{PRIME} {TIMES} {q["dim_h"]}{PRIME}' if ft else FEET_NOTE
        return (f'<a class="pnav-{side}" href="{u("/work/" + q["slug"])}">'
                f'<span class="pnav-k">{ICONS[icon]}{label}</span>'
                f'<span class="pnav-t">{q["title"]}</span>'
                f'<span class="pnav-d{"" if ft else " marker"}">{figure}</span></a>')

    # A wall with feet leads with the figure standing on the photograph, and
    # the words under it carry the title. A wall without them has no figure to
    # stand, so the title is in the hero with the film and the words pick up
    # at the note that says the feet are coming — the heading is not said twice.
    ft = p['dim_w'] is not None
    head = (f'''<div class="eyebrow"><span class="marker">{place}</span></div>
  <h1 class="tall">{p['title']}</h1>
  {dims(p['dim_w'], p['dim_h'])}''' if ft else feet_note())

    return f'''
{scale_hero(p) if ft else film_hero(p)}
<section class="pintro">{glow()}<div class="wrap">
  <div class="crumbs"><a href="{u('/')}">Home</a><span>/</span><a href="{u('/work')}">Work</a><span>/</span><span>{p['title']}</span></div>
  {head}
  <p class="lead pstory serif">{p['story']}</p>
  <dl class="pmeta">{meta}</dl>
  {credit}
</div></section>
{progress_band(p) if p.get('progress') else ''}
{film_band(p) if p.get('film') else ''}
{gallery}
<section class="pnav-wrap"><div class="wrap">
  <nav class="pnav" aria-label="More projects">{step(prv, 'prev', 'Previous', 'chevL')}{step(nxt, 'next', 'Next', 'chevR')}</nav>
</div></section>
{cta(title='Want one this size?',
     text='Tell us the wall, the city and roughly how big it is. We will come back with a plan and a price.',
     secondary=('See the work', '/work'))}'''


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
{page_hero('<span class="marker">the studio</span>', 'Ephraim and the crew',
           f'A muralist and large-image company: murals, banners and signs painted at '
           f'building scale. Ephraim leads it, the crew goes up on the lift, and the '
           f'walls stand in {spell(len(CITIES))} cities so far.',
           crumb='About', wall=True)}

<section><div class="wrap">
  <div class="duo">
    <div class="portrait rv">{pic('ephraim-portrait', 'Ephraim, the muralist who leads Open Air Gallery', PORTRAIT_SIZES)}
      <div class="portrait-cta">{save_number()}</div></div>
    <div class="rv rv-d1">
      <div class="eyebrow"><span class="marker">The muralist</span></div>
      <h2 class="tall">Ephraim</h2>
      <p class="lead serif">Ephraim is the muralist behind Open Air Gallery. The company paints
      brand walls at building scale — Gucci, Crown Royal, Uber — and painted portraits,
      including the two civil-rights walls in Rochester. In his own words:</p>
      <blockquote class="pull serif"><p>{STUDIO}</p><cite>Ephraim, Open Air Gallery</cite></blockquote>
    </div>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="duo duo-wide">
    <div class="rv">
      <div class="eyebrow"><span class="marker">The crew</span></div>
      <h2 class="tall">Nobody paints eighty feet alone</h2>
      <blockquote class="pull serif"><p>{CREW}</p><cite>Ephraim, Open Air Gallery</cite></blockquote>
    </div>
    <figure class="figframe rv rv-d1">{pic('about-team', 'An Open Air Gallery painter working from a lift platform, mask on, part way through a wall', HALF_SIZES)}
      <figcaption class="figcap">On the lift, mid-wall.</figcaption></figure>
  </div>
</div></section>

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow"><span class="marker">How a wall gets painted</span></div>
  <h2 class="tall">Prep, paint, preservation</h2>
  <p class="lead serif">Ephraim’s three stages, in full and in his own words — the same three
  he has published since the first version of this company’s site.</p></div>
  {beats(PROCESS, 'beats-full', rule=True)}
</div></section>

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow"><span class="marker">Where we work</span></div>
  <h2 class="tall">New York, and wherever the wall is</h2>
  <p class="lead serif">Open Air Gallery is based in New York and paints nationwide. The
  The walls on the Work page stand in {spell(len(CITIES))} cities, coast to
  coast — {SQ_FT:,} square feet of painted surface between them.</p></div>
  <ul class="cities">{''.join(city_tile(place, walls) for place, walls in CITY_ROWS)}</ul>
  <div class="row-end rv"><a class="btn btn-ghost" href="{u('/work')}">See the work {ICONS['arrow']}</a></div>
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
#
# The hero also carries the paint tin ("Tip", tip_can()) and the first section
# under it carries the rule the tin's paint becomes (tip_rule()). Both are
# drawn in the server HTML and both are finished there — an upright tin and a
# mint rule — so this page reads the same with no script as it does with one.
SIGN_ROSTER = ('Heineken', 'Jack Daniels', 'Corona', 'Black Crow',
               'House of Pizza & Calzones')


pages['/services'] = dict(
  title=f'Services | {SITE_NAME}',
  desc='Murals at building scale, hand-painted banners and signs, and the paint '
       'science behind both — plus graffiti removal, pressure washing and commercial '
       'painting from the same crew.',
  body=f'''
{page_hero('<span class="marker">what we do</span>', 'Murals, banners and signs',
           'Hand-painted work at building scale, by the crew that cleans the wall '
           'afterwards too: murals, banners and signs, graffiti removal — and the paint '
           'science that runs through all of it.',
           media_slug='moncler-wide',
           media_alt='A hand-painted wall advertisement high above a New York street, '
                     'with traffic and pedestrians below it for scale',
           crumb='Services', tip=True)}

<section class="svc-rule"><div class="wrap">
  {tip_rule()}
  <ul class="stats rv stats-3">
    {stat(f'{SQ_FT:,}', 'square feet, and counting')}
    {stat(WIDEST['dim_w'], f'widest wall, {WIDEST["city"]}', mark=PRIME)}
    {stat(len(CITIES), 'cities, coast to coast')}
  </ul>
</div></section>

{services_board()}

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow"><span class="marker">in his own words</span></div>
  <h2 class="tall">There is a science to paint</h2>
  <p class="lead serif">Two of Ephraim&rsquo;s three stages are about what happens to the paint
  after the crew goes home: how it will fade, and how it survives what is thrown at it.</p></div>
  {beats(PROCESS, 'beats-gr', rule=True)}
  <ul class="roster rv">{''.join(f'<li>{html.escape(n)}</li>' for n in SIGN_ROSTER)}</ul>
  <div class="row-end rv"><a class="btn btn-ghost" href="{consult('Banners and signs')}">Ask about a sign {ICONS['arrow']}</a></div>
</div></section>

{brand_wall()}

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
      <div class="eyebrow"><span class="marker">Commercial</span></div>
      <h1 class="tall">Graffiti removal</h1>
      <p class="lead serif">{' &middot; '.join(GR_REASONS)}.</p>
      <div class="btn-row"><a class="btn btn-mint" href="{consult('Graffiti removal')}">Send a photo, get a quote {ICONS['arrow']}</a><a class="btn btn-ghost" href="#gr-services">The three services</a></div>
    </div>
    <div class="gr-hero-wall">{wall_html(mode='interactive', id_prefix='wash')}</div>
  </div></div>
</section>

<section id="gr-services"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow"><span class="marker">In his own words</span></div>
  <h2 class="tall">Graffiti removal &amp; cleaning services</h2>
  <p class="lead serif">{GR_PITCH}</p></div>
  {beats(GR_SERVICES, 'beats-gr')}
  <div class="row-end rv btn-row">
    <a class="btn btn-mint" href="{consult('Graffiti removal')}">Send a photo, get a quote {ICONS['arrow']}</a>
    <a class="btn btn-ghost" href="{consult('Pressure washing')}">Ask about pressure washing</a>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow"><span class="marker">Before and after</span></div>
  <h2 class="tall">What comes off</h2>
  <p class="lead serif">Ephraim&rsquo;s own before-and-after photographs go here the day he sends
  them. Until then this is the wall at the top of the page, drawn, with every tag on
  it and then none of them.</p></div>
  {before_after()}
</div></section>

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow"><span class="marker">His three step process</span></div>
  <h2 class="tall">Take a picture. Send us an email. Pay a 50% deposit.</h2>
  <p class="lead serif">The booking ladder Open Air Gallery has published since the first
  version of this site, unchanged.</p></div>
  {beats(GR_LADDER, 'beats-gr')}
</div></section>

<section class="alt"><div class="wrap">
  <div class="section-head rv"><div class="eyebrow"><span class="marker">At the wall</span></div>
  <h2 class="tall">Four beats, once the date is set</h2>
  <p class="lead serif">What the crew actually does between the deposit and the wall you get
  back.</p></div>
  {beats(GR_PROCESS, 'beats-4', quoted=False)}
</div></section>

<section><div class="wrap">
  <div class="section-head rv"><div class="eyebrow"><span class="marker">Who it&rsquo;s for</span></div>
  <h2 class="tall">Whose wall this is</h2></div>
  {beats(GR_WHO, 'beats-gr', quoted=False)}
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
{page_hero('<span class="marker">book a free consultation</span>', 'Let’s get to work',
           'Fill out the form and we’ll connect with you shortly. Tell us the wall, the '
           'city and roughly how big it is, and you get a plan and a price back.',
           media_slug='contact-band',
           media_alt='Three Open Air Gallery painters flat on a lift platform, rolling out '
                     'a wall by hand',
           crumb='Contact')}

<section><div class="wrap">
  <div class="contact-grid">
    <div class="rv">
      <div class="eyebrow"><span class="marker">the brief</span></div>
      <h2 class="tall">Tell us about the wall</h2>
      <p class="contact-aside marker">a photo of the wall is enough to start</p>
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
        <div><b>Where we work</b><span>New York and nationwide — Manhattan to Los Angeles,
        and walls abroad in Mexico and Brazil.</span></div></div>
    </div>
  </div>
</div></section>
<script>window.OAG={{form:{json.dumps(FORM_ENDPOINT)},email:{json.dumps(EMAIL)}}}</script>
''')


# ------------------------------------------------------------------- 404
# nginx serves this for anything it cannot find (`error_page 404 /404.html`
# in deploy/nginx/openair-site.conf), so it is a real page of the site that
# is never linked from it: noindex, kept out of the sitemap by the write
# loop, and carrying the two ways back a visitor who mistyped a URL wants.
#
# It is also the second blank wall. The hero has no photograph, which on a
# dark site is a wall with nothing on it, and the copy says so — so the Wall
# mechanic is not decoration here, it is the page's one joke, and the page
# reads exactly the same with no script at all.
pages['/404'] = dict(
  noindex=True,
  title=f'Page not found | {SITE_NAME}',
  desc='That page is not here. Head back to the work, or to the front.',
  body=f'''
{page_hero('<span class="marker">404</span>', 'Nothing on this wall yet.',
           'Paint something, or head back.',
           crumb=False, cls='blank', wall=True,
           extra=f'''<div class="btn-row"><a class="btn btn-mint" href="{u('/')}">Home {ICONS['arrow']}</a>'''
                 f'''<a class="btn btn-ghost" href="{u('/work')}">Work</a></div>''')}''')


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
      'image': abs_img(p['hero'])[0],
      'genre': {'brand': 'Brand mural', 'portrait': 'Painted portrait',
                'civic': 'Civic mural'}[p['category']],
    }
    # A measurement nobody gave us is left out of the graph rather than
    # guessed into it: a QuantitativeValue of null is worse than silence.
    if p['dim_w'] is not None:
        ld['width'] = feet(p['dim_w'])
        ld['height'] = feet(p['dim_h'])
    if p['client']:
        ld['sponsor'] = {'@type': 'Organization', 'name': p['client']}
    if p['year']:
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
  '/404': 'gucci-new-york-hero',
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

# No wall count, anywhere, ever. CLAUDE.md, round three, in the owner's own
# words: "Don't say 12 walls — he has more not on there, and wants to show more
# of his public works like Colossal did; he's been to Mexico, Brazil, teen
# empowerment and more, so don't limit." The twelve rows in projects.py are the
# walls we have photographs of; they are not the size of his career, and a
# number computed from our data file must never become a claim about him.
#
# That rule is easy to keep by hand and easy to lose by accident — one
# `spell(len(PROJECTS))` put back in a lead, one chip that counts what it
# filters — so it is checked on the rendered page rather than trusted in the
# source. These patterns run over every page's final HTML and the build stops
# on a hit. A count of *cities* is fine and always has been: "eight cities" is
# where he has worked, not a ceiling on how much he has done.
WALL_COUNT_BAN = [
    # the word itself, in any case, however it is phrased around
    (re.compile(r'\btwelve\b', re.I), 'the word "twelve"'),
    # a figure standing next to walls, in either order, across markup
    (re.compile(r'\b12\b(?:(?!</?(?:section|h[1-6])\b).){0,40}?\bwalls?\b',
                re.I | re.S), '"12" beside "walls"'),
    (re.compile(r'\bwalls?\b(?:(?!</?(?:section|h[1-6])\b).){0,24}?\b12\b',
                re.I | re.S), '"walls" beside "12"'),
    (re.compile(r'\ba dozen\b', re.I), '"a dozen"'),
]


def check_no_wall_count(path, doc):
    for rx, what in WALL_COUNT_BAN:
        m = rx.search(doc)
        if m:
            start = max(0, m.start() - 70)
            raise SystemExit(
                f'build: {path} states a wall count — {what}.\n'
                f'  ...{doc[start:m.end() + 70]}...\n'
                f'  CLAUDE.md, round three: the roster is what we have photographs '
                f'of, never a claim about how much work Ephraim has done.')


for path, p in pages.items():
    fn = os.path.join(OUT, path.strip('/') + '.html')
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    doc = layout(path, p['title'], p['desc'], p['body'], p.get('ld'),
                 p.get('noindex', False), p.get('wash', False), p.get('og'))
    check_no_wall_count(path, doc)
    with open(fn, 'w') as f:
        f.write(doc)
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
