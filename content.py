#!/usr/bin/env python3
"""Everything the Mendoza Marketing site says that is a fact rather than a
layout: the business, the six services, and every package Drew sells.

Rule for this file: nothing in it is written for Drew. Names and prices come
from his README (quoted in CLAUDE.md); sentences come from his own pages
(incoming/refs/netorious-pages.txt) and arrive in step 4 of the plan. A field
whose value we do not have is TODO and empty — never a plausible invention.
build.py prints the TODO list at the end of every build so it cannot be
forgotten.
"""

# --------------------------------------------------------------- the business
# TODO (Drew): email, phone and the two social accounts are all still owed.
# The values below are the ones published on his CURRENT site
# (netoriouslabs.com/contact, saved 2026-09-22). They are real and they are his,
# but they carry the old brand — a mendozamarketing.* address may replace the
# email before launch. Confirm both, then delete this note.
SITE = dict(
    name='Mendoza Marketing',
    tagline='Content · Websites · Drones',          # his README, verbatim
    owner='Drew Mendoza',                           # TODO confirm the spelling of his full name
    email='drew@netoriouslabs.com',                 # TODO confirm for the new brand
    phone='716-860-5991',                           # TODO confirm
    phone_href='+17168605991',
    place='Grand Island · Buffalo, NY',
    # (label, icon key in build.ICONS, url). An empty url renders as a drawn,
    # unlinked icon — the footer keeps its shape and nobody clicks a dead link.
    socials=[
        ('Instagram', 'ig', ''),                    # TODO Drew's Instagram URL
        ('Facebook',  'fb', ''),                    # TODO Drew's Facebook URL
    ],
)

# Where the quote form posts. Unset is a supported state, not a broken one:
# site/js/form.js then hands the filled-in brief to the visitor's own mail app,
# addressed to SITE['email'] — and with no script at all the form's own
# action="mailto:..." does the same thing. Nothing is lost while this is empty.
#
# When Drew supplies the id, this becomes the whole Formspree endpoint URL:
#
#     FORM_ENDPOINT = 'https://formspree.io/f/<the id from his dashboard>'
#
# build.py hands it to the page as window.MM.form and form.js POSTs the fields
# to it as JSON. Nothing else in the build changes.
FORM_ENDPOINT = ''                                  # TODO Drew's Formspree id

# Every field above that is still a placeholder, named so the build can say so.
TODO = [
    'SITE email — confirm the address for the Mendoza Marketing brand',
    'SITE phone — confirm 716-860-5991 is still the number to publish',
    'SITE socials — Instagram and Facebook URLs',
    'FORM_ENDPOINT — the Formspree id for the quote form',
    'SERVICES one_line / included — Drones and Lead conversion have no copy '
    'on his current site; both need new copy in his register, for him to approve',
]


# ----------------------------------------------------------------- the prices
# Straight from Drew's README, and nothing else. `amount` is what the card
# prints; `qualifier` is the word in front of it ("from" or nothing); `note` is
# the line under it. price_card() in build.py reads this table rather than
# taking a price as an argument, so a card can never quote a figure this file
# does not know.
#
# NOTE, for Drew: three of these differ from the prices on netoriouslabs.com
# today — the README says web RE-DESIGN $600 (his site says $500) and LOGO $500
# (his site says $750), and the README's Meta ad line is $750 for setup AND
# filming where his site prices management at $500 + the client's daily budget.
# The README is what we have built to. Flagged in CLAUDE.md.
PRICING = {
    'web-design': dict(
        name='Website design', service='websites',
        qualifier='from', amount='$1,250', note=None,
        tier='Websites'),
    'web-redesign': dict(
        name='Website re-design', service='websites',
        qualifier='', amount='$600', note=None,
        tier='Websites'),
    'meta-ads': dict(
        name='Meta ad setup & filming', service='meta-ads',
        qualifier='', amount='$750', note=None,
        tier='Meta ads'),
    'social-emerald': dict(
        name='Social media — Emerald', service='social',
        qualifier='', amount='$500', note=None,
        tier='Emerald'),
    'social-sapphire': dict(
        name='Social media — Sapphire', service='social',
        qualifier='', amount='$1,000', note=None,
        tier='Sapphire'),
    'social-diamond': dict(
        name='Social media — Diamond', service='social',
        qualifier='', amount='$2,000', note=None,
        tier='Diamond'),
    'logo': dict(
        name='Logo design', service='logo',
        qualifier='', amount='$500', note=None,
        tier='Logo'),
    'lead-conversion': dict(
        name='Lead conversion', service='lead-conversion',
        qualifier='', amount='Commission or hourly',
        note='Priced to the need — ask.',
        tier='Leads'),
    'drone-session': dict(
        name='Drone session', service='drones',
        qualifier='', amount='$1,000', note=None,
        tier='Drones'),
}


# --------------------------------------------------------------- the services
# Six cards on Home, six pages, six entries in the nav's Services menu. The
# order here is the order everywhere.
#
#   slug        the URL and the page
#   name        the nav label and the page title
#   one_line    one sentence under the name — HIS sentence, from his current
#               site, in step 4. Empty until then.
#   price_key   which row of PRICING the card's "from $x" reads
#   included    the trio the service page lists. Where his current site already
#               has an "Included in this service" block, these are his own
#               headings and sub-lines, transcribed verbatim
#               (incoming/refs/netorious-pages.txt, saved 2026-09-22). Drones
#               and Lead conversion have no page on his site at all: empty here,
#               and flagged for him to approve new copy.
SERVICES = [
    dict(slug='websites', name='Website design', price_key='web-design',
         one_line='',
         included=[
             ('SEO Setup', 'Increased exposure across the internet.'),
             ('Optimized Speed', 'Optimized for fast, seamless performance.'),
             ('Mobile Friendly', 'Designed for seamless mobile experiences.'),
         ]),
    dict(slug='meta-ads', name='Meta ads & filming', price_key='meta-ads',
         one_line='',
         included=[
             ('Campaign Management', 'Full-Service Meta Advertising Management.'),
             ('On-Going Optimization', 'Real-Time Meta Business Ad Optimization.'),
             ('Real Leads', 'Qualified Leads Via Meta Advertising.'),
         ]),
    dict(slug='social', name='Social media', price_key='social-emerald',
         one_line='',
         included=[
             ('Content Creation', 'Strategic content designed to convert.'),
             ('User Interaction', 'Meaningful engagement that builds trust.'),
             ('Page Growth', 'Consistent growth through strategic optimization.'),
         ]),
    dict(slug='logo', name='Logo design', price_key='logo',
         one_line='',
         included=[
             ('Logo Copyright', 'Full ownership rights to logo.'),
             ('Social Media Kit', 'Optimized logos for social platforms.'),
             ('Scalable Images', 'Logos that scale flawlessly.'),
         ]),
    dict(slug='drones', name='Drone sessions', price_key='drone-session',
         one_line='',
         included=[]),          # TODO — new copy, for Drew to approve
    dict(slug='lead-conversion', name='Lead conversion', price_key='lead-conversion',
         one_line='',
         included=[]),          # TODO — new copy, for Drew to approve
]

BY_SLUG = {s['slug']: s for s in SERVICES}

# Every price row points at a service that exists, and every service at a price
# row that exists. Cheap to check, and it is the kind of typo that reaches the
# page as a wrong number rather than as a crash.
for _k, _p in PRICING.items():
    assert _p['service'] in BY_SLUG, f'PRICING[{_k!r}].service is not a service slug'
for _s in SERVICES:
    assert _s['price_key'] in PRICING, f'SERVICES {_s["slug"]!r}: no PRICING row'


def price(key):
    """One row of PRICING, by key. KeyError here is the point: a page that asks
    for a package we do not sell should stop the build, not print blank."""
    return PRICING[key]


def price_text(key):
    """'from $1,250' / '$750' / 'Commission or hourly' — the figure as a
    sentence, for a card that has no room for the full price block."""
    p = PRICING[key]
    return f"{p['qualifier']} {p['amount']}".strip()
