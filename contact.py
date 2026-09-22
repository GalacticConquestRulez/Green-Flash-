#!/usr/bin/env python3
"""The /contact page: the quote form, and the other ways to reach Drew.

His README asks for "a quote form". This is it, built the way Open Air
Gallery's is (`/root/openairgallery-src/build.py`'s /contact and the form block
in its site.js), because that form already works in the three states this one
has to work in:

    endpoint set      site/js/form.js POSTs the fields to Formspree as JSON and
                      says so inline. content.py's FORM_ENDPOINT is where the
                      id goes; it is empty today.
    endpoint unset    form.js hands the filled-in brief to the visitor's own
                      mail app, addressed to Drew. This is today's state and it
                      needs no account anywhere.
    no script at all  the <form> itself is `action="mailto:…" method="post"
                      enctype="text/plain"`, so the button still produces an
                      email. (method="get" is useless for a mailto: the fields
                      would replace the query string and take the subject with
                      them. OAG's form is the model here.)

Nothing on the page is hidden from a visitor with no JavaScript: every field,
every option, both selects and the note under the button are in the server
HTML. What form.js adds on top is the `?service=` prefill and the two nicer
endings.

`?service=<slug>` arrives from every price card and service CTA
(`price_card()` builds `/contact?service={service}`). form.js reads it and
selects that option. A static site has no server to read a query string with,
so the select is also plain and complete: with no script the six services are
all there and the visitor picks one — the URL is a convenience, never the only
way the field gets filled.

This module is a *page of* build.py in the same way home.py is: it reaches back
for u(), ICONS and the rest at call time, so build.py's side stays one import
line and is never executed twice.
"""
import html
from urllib.parse import quote

from content import SITE, SERVICES


# --------------------------------------------------------------------- glue
def _b():
    """build.py, whichever name it is running under. Same reason as home.py:
    this file needs u() and build.py needs contact_page(), which is a cycle if
    either side imports the other at the top."""
    import sys
    for name in ('build', '__main__'):
        m = sys.modules.get(name)
        if m is not None and hasattr(m, 'page_hero'):
            return m
    raise RuntimeError('contact.py is part of build.py and must be called from it')


# ------------------------------------------------------------------ the copy
# The bands a visitor picks from. Ranges rather than a number: this is the
# field that tells Drew whether the enquiry is a $600 re-design or a $2,000
# social package before he writes the quote, and nobody types a real budget
# into a box. They bracket his own price list (content.py PRICING: $500 at the
# bottom, $2,000 at the top) with room above it for a project that combines
# several packages.
BUDGETS = [
    'Under $1,000',
    '$1,000–2,500',
    '$2,500–5,000',
    '$5,000+',
    'Not sure',
]

# What the visitor's mail app puts in the subject line when there is no
# endpoint and no script. form.js writes a more specific one (the service and
# the name) when it is running; this is the fallback, and it has to be a
# constant because no-JS has nothing to build a string with.
SUBJECT = f'Quote request — {SITE["name"]}'

# The seventh option. Five of the six services are a package with a price; the
# sixth (lead conversion) is priced to the need. Somebody whose job is none of
# those still has to be able to send the form, and "Other / not sure" is a
# truthful answer rather than a wrong one — the alternative is that the first
# service in the list gets selected by accident and Drew quotes the wrong work.
OTHER = 'Other / not sure'


def _mailto(subject, extra=''):
    """A mailto: for Drew with the subject already written."""
    return f'mailto:{SITE["email"]}?subject={quote(subject)}{extra}'


# --------------------------------------------------------------------- form
def _field(name, label, control, hint=''):
    h = f'<span class="hint">{hint}</span>' if hint else ''
    return (f'<div class="field"><label for="{name}">{label}</label>'
            f'{control}{h}</div>')


def _select(name, label, options, placeholder):
    """A select with a neutral first option.

    The placeholder is not decoration. A select's default is its first option,
    so a list that opens on "Website design" tells Drew the visitor asked for a
    website when all they did was not touch the field. The empty option is what
    "they did not say" looks like in the email he gets.
    """
    opts = [f'<option value="" selected>{html.escape(placeholder)}</option>']
    for value, slug in options:
        attr = f' data-slug="{slug}"' if slug else ''
        opts.append(f'<option value="{html.escape(value)}"{attr}>{html.escape(value)}</option>')
    control = (f'<span class="sel"><select id="{name}" name="{name}">'
               f'{"".join(opts)}</select></span>')
    return _field(name, label, control)


def quote_form():
    """The brief. Complete with no script, better with one."""
    b = _b()
    services = [(s['name'], s['slug']) for s in SERVICES] + [(OTHER, '')]
    return f'''<form id="quote-form" class="form" action="{_mailto(SUBJECT)}"
        method="post" enctype="text/plain">
  <div class="row">
    {_field('name', 'Name', '<input id="name" name="name" required autocomplete="name" placeholder="Your name">')}
    {_field('email', 'Email', '<input id="email" name="email" type="email" required autocomplete="email" placeholder="you@business.com">')}
  </div>
  <div class="row">
    {_field('phone', 'Phone', '<input id="phone" name="phone" type="tel" autocomplete="tel" placeholder="Optional">')}
    {_field('business', 'Business', '<input id="business" name="business" autocomplete="organization" placeholder="Optional">')}
  </div>
  <div class="row">
    {_select('service', 'Service', services, 'Choose a service')}
    {_select('budget', 'Budget', [(x, '') for x in BUDGETS], 'Choose a range')}
  </div>
  {_field('message', 'Message',
          '<textarea id="message" name="message" required '
          'placeholder="What is the business, what do you want it to do, and when do you need it?"></textarea>')}
  <div class="gotcha" aria-hidden="true">
    <label for="_gotcha">Leave this field empty</label>
    <input id="_gotcha" name="_gotcha" type="text" tabindex="-1" autocomplete="off">
  </div>
  <div class="btn-row"><button class="btn" type="submit">Send the brief {b.ICONS['arrow']}</button></div>
  <div class="form-status" role="status"></div>
  <p class="form-note">Sending opens a pre-filled email from your own mail app.
    You can also write to <a href="mailto:{SITE['email']}">{SITE['email']}</a>
    or call <a href="tel:{SITE['phone_href']}">{SITE['phone']}</a> directly.</p>
</form>'''


# ------------------------------------------------------------------ sidebar
def _card(icon, title, value, href=None, cls=''):
    inner = (f'<div class="ic">{icon}</div>'
             f'<div><b>{title}</b><span>{value}</span></div>')
    c = f'side-card{" " + cls if cls else ""}'
    if href:
        return f'<a class="{c}" href="{href}">{inner}</a>'
    return f'<div class="{c}">{inner}</div>'


def sidebar():
    """The other ways in — and the one card that is a promise, not a link.

    Email and phone are content.py's, which still carries the values published
    on netoriouslabs.com today: the address names the old brand and CLAUDE.md
    asks Drew to confirm it. They are rendered exactly as that file holds them
    rather than tidied here.

    The social icons are drawn and not linked, the same way footer_html() does
    it, because we have neither URL. Nobody clicks a dead link and the column
    keeps its shape for the day they arrive.
    """
    b = _b()
    book = _mailto(f'Booking a call — {SITE["name"]}')
    return f'''<aside class="contact-side">
  <div class="eyebrow">Or reach out</div>
  {_card(b.ICONS['mail'], 'Email', SITE['email'], f'mailto:{SITE["email"]}')}
  {_card(b.ICONS['phone'], 'Phone', SITE['phone'], f'tel:{SITE["phone_href"]}')}
  {_card(b.ICONS['pin'], 'Where Drew works', SITE['place'])}
  <div class="side-card side-social">
    <div><b>Follow along</b><span>Instagram and Facebook &mdash; links to come.</span>
    {b.socials_html()}</div>
  </div>
  <div class="side-card book">
    <div class="eyebrow">Book a call</div>
    <h3>Twenty minutes, no pitch deck.</h3>
    <p>We&rsquo;ll talk through what you need and what it costs.</p>
    <a class="btn btn-ghost" href="{book}">Book a call {b.ICONS['arrow']}</a>
  </div>
</aside>'''


# --------------------------------------------------------------------- page
def contact_page():
    """The page, as build.py's `pages` dict wants it.

    `extra_scripts` is why layout() takes that argument: form.js is the only
    script on the site that one page needs and the other pages must not pay
    for. It loads after site.js (both deferred, so both run in order) and does
    nothing at all on a page with no #quote-form.
    """
    b = _b()
    hero = b.page_hero(
        'Get a quote',
        'Tell us what you&rsquo;re building.<span>Priced to the package.</span>',
        'Tell Drew what the business is and what you want it to do. A quote '
        'comes back within a business day, priced to the package.',
        crumb='Contact', cls='contact-hero')
    body = f'''{hero}
<section class="contact-sec"><div class="wrap">
  <div class="contact-grid">
    <div class="quote panel rv">
      <div class="eyebrow">The brief</div>
      <h2>What are we building?</h2>
      {quote_form()}
    </div>
    <div class="rv rv-d1">{sidebar()}</div>
  </div>
</div></section>'''
    return dict(
        title=b.seo_title('Get a quote, Grand Island NY'),
        desc=f'Get a quote from {b.SITE_NAME} — websites, Meta ads and filming, '
             f'social media, logo design, drone sessions and lead conversion in '
             f'Buffalo, NY.',
        body=body,
        extra_scripts=f'<script src="{b.u("/js/form.js")}?v='
                      f'{b.asset_v("js/form.js")}" defer></script>')
