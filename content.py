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
    'SERVICES /drones and /lead-conversion — every sentence on those two pages '
    'is NEW COPY written here (both are blank on his current site). Drew has to '
    'read and approve them before launch',
    'PRICING social-emerald / social-sapphire / social-diamond — the three tiers '
    'are priced but what is IN each one is not written down anywhere we hold, so '
    '/social and /pricing show the tiers with their contents marked to confirm',
    'WORK — what was done for Buffalo Holistic Center, Zen Zone, Britt Fitness '
    'and Adam\u2019s Detailing: we hold their logos and nothing else, so each card '
    'says logo and brand work with the details to confirm',
    'WORK — no logo file for Kelly\u2019s Country Store or Gator Jon\u2019s BBQ, both '
    'of which are clients linked from his current site',
    'SERVICES /meta-ads — his page prices MANAGEMENT at $500 plus the client\u2019s '
    'daily budget; the README prices SETUP AND FILMING at $750. The page carries '
    'the README figure and his budget clause. Confirm which service this is',
    'SERVICES /websites — his "Web Design Lessons" block is cut off mid-sentence '
    'in our capture and has no price; left off the page. Does he still sell it?',
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
#   slug            the URL and the page
#   name            the nav label and the page title
#   one_line        one sentence under the name on the Home card. EMPTY, and
#                  deliberately: home.py's HOME_LINES carries the sentence the
#                  owner approved on the mockup, and uses it only while this is
#                  blank. A summary written by us here would silently replace an
#                  approved line with an unapproved one. It gets filled the day
#                  Drew gives us a sentence of his own, and his then wins.
#   hero_title      the page's two-tone <h1>; the <span> is line two, in green
#   lead            his opening paragraph, under the headline
#   intro           the rest of his opening block, paragraph by paragraph
#   breakdown_title his own heading, e.g. "Web Design Breakdown"
#   breakdown_price his price sentence with {amount} interpolated from PRICING,
#                   or None where his page has no price line. The figure is
#                   NEVER typed here — CLAUDE.md rule 6.
#   breakdown       the rest of his bullets under that heading
#   included_title  his own heading over the trio ("What You Can Expect",
#                   "Included In This Service", "Included With This Service",
#                   "Included In Our Service" — they differ, and they are his)
#   included        the trio itself: his headings and sub-lines
#   prices          the PRICING keys whose cards this page shows, in order
#   extra           the second block some of his pages carry (the web re-design
#                   service, "Re-define your brand", "Our services in action")
#   new_copy        True where NOTHING on the page came from him
#
# Everything above is transcribed from his current site
# (incoming/refs/netorious-pages.txt, saved 2026-09-22) with two changes and
# only two: "Netorious Labs" becomes "Mendoza Marketing", and on the web-design
# page "found in his cinematic content" becomes "our" — a first-person slip on
# his own site. Drones and Lead conversion have no page on his site at all;
# every sentence on those two is new, is marked NEW COPY below, and goes to him
# before launch.
#
# NOT transcribed: the "Web Design Lessons" block at the foot of his
# website-design page. Our capture of it is cut off mid-sentence and it carries
# no price, so it is left out rather than guessed at. TODO ask Drew whether he
# still sells it.
SERVICES = [
    dict(slug='websites', name='Website design', price_key='web-design',
         one_line='',      # see the note above SERVICES
         hero_title='Professional<span>web design.</span>',
         # His own first paragraph, with one word changed: his page reads
         # "found in his cinematic content", which is a slip on a first-person
         # site. Same class of fix as Netorious Labs -> Mendoza Marketing.
         lead='We will work with you to design and deliver a professional website '
              'built on WordPress with the same quality and creativity found in our '
              'cinematic content.',
         intro=[
             'Each website is fully responsive across all devices to ensure smooth '
             'performance and crisp visuals. After your site goes live, we can provide '
             'ongoing support so your digital presence stays strong long after launch.',
             'As your brand expands, we can implement new features, pages, SEO, and '
             'enhancements to ensure consistent growth.',
         ],
         breakdown_title='Web Design Breakdown',
         # His sentence; the figure is interpolated from PRICING so the page can
         # never disagree with the price card beside it (CLAUDE.md rule 6).
         breakdown_price='Price starts at {amount}, to increase based on client needs.',
         breakdown=[
             '5+ Custom Content Pages designed for services, about, etc.',
             'Responsive Design across all devices and displays.',
             'Launch support + DNS records management.',
             'SEO integration setup.',
         ],
         included_title='What You Can Expect',
         included=[
             ('SEO Setup', 'Increased exposure across the internet.'),
             ('Optimized Speed', 'Optimized for fast, seamless performance.'),
             ('Mobile Friendly', 'Designed for seamless mobile experiences.'),
         ],
         prices=['web-design'],
         # The second half of his own website-design page.
         extra=dict(
             eyebrow='Web re-design',
             title='Web<span>re-design.</span>',
             paras=[
                 'Our website revamp enhances your existing platform without requiring '
                 'a full rebuild or migration. We refine your current structure, '
                 'modernize the design, and improve usability while preserving the '
                 'tools, integrations, and workflows you already rely on.',
                 'We optimize page speed, improve mobile responsiveness, update layouts, '
                 'and refine calls-to-action so visitors can navigate effortlessly and '
                 'take action with confidence.',
                 'This service also includes content and visual updates to ensure your '
                 'site aligns with your brand today. From refreshed visuals and '
                 'typography to clearer messaging, your website will feel current, '
                 'professional, and built to support growth.',
             ],
             breakdown_title='Web Redesign Breakdown',
             breakdown_price='Price starts at {amount}, to increase based on client needs.',
             breakdown=[
                 'Improved page speed and performance optimization.',
                 'Mobile-friendly and new responsive updates.',
                 'Refreshed visuals, content, and brand consistency.',
             ],
             prices=['web-redesign'],
         )),
    dict(slug='meta-ads', name='Meta ads & filming', price_key='meta-ads',
         one_line='',      # see the note above SERVICES
         hero_title='Professional<span>ad campaigns.</span>',
         lead='We will work with you to plan, launch, and manage high-performing ad '
              'campaigns through Meta Business Suite with the same strategy and '
              'precision used in premium digital marketing.',
         intro=[
             'Each campaign is optimized across Facebook and Instagram to ensure '
             'consistent reach, strong engagement, and clear performance tracking. '
             'After launch, we provide ongoing management so your ad results remain '
             'effective long after activation.',
             'As your business scales, we can refine targeting, creative, budgets, and '
             'reporting to ensure continued growth and measurable returns.',
         ],
         breakdown_title='Ad Campaign Breakdown',
         # His line reads "Price starts at $500 to manage, client covers daily
         # budget." The README prices $750 for SETUP AND FILMING, which is not
         # the same thing — one of the three disagreements CLAUDE.md flags. The
         # clause about the client's budget is his and is kept; the figure comes
         # from PRICING. ASK DREW which of the two this page should describe.
         breakdown_price='Price starts at {amount}. The client covers the daily ad budget.',
         breakdown=[
             'Strategic ad campaign setup through Meta Business Suite.',
             'Creation of custom Ad Creative to use for content.',
             'Ongoing campaign monitoring, testing, and optimization.',
         ],
         included_title='Included In This Service',
         included=[
             ('Campaign Management', 'Full-Service Meta Advertising Management.'),
             ('On-Going Optimization', 'Real-Time Meta Business Ad Optimization.'),
             ('Real Leads', 'Qualified Leads Via Meta Advertising.'),
         ],
         prices=['meta-ads']),
    dict(slug='social', name='Social media', price_key='social-emerald',
         one_line='',      # see the note above SERVICES
         hero_title='Viral content<span>management.</span>',
         lead='We will work with you to plan, create, and deliver professional social '
              'media content with the same quality, creativity, and storytelling found '
              'in our cinematic work.',
         intro=[
             'Each piece of content is optimized for all platforms to ensure strong '
             'performance, clear visuals, and consistent engagement. After your content '
             'goes live, we can provide ongoing management so your online presence '
             'stays active and relevant.',
             'As your brand grows, we can introduce new content formats, campaigns, '
             'trends, and optimizations to support consistent reach, engagement, and '
             'growth.',
         ],
         breakdown_title='Viral Content Breakdown',
         breakdown_price=None,          # his page prices the tiers, not the service
         breakdown=[
             'Weekly custom high-performing short-form reels.',
             'Active engagement with your audience on all pages.',
             'Content planning to keep your page relevant.',
             'Brand-aligned storytelling that showcases your business.',
         ],
         included_title='Included In Our Service',
         included=[
             ('Content Creation', 'Strategic content designed to convert.'),
             ('User Interaction', 'Meaningful engagement that builds trust.'),
             ('Page Growth', 'Consistent growth through strategic optimization.'),
         ],
         prices=['social-emerald', 'social-sapphire', 'social-diamond'],
         extra=dict(
             eyebrow='Our services in action',
             title='Kelly&rsquo;s<span>Country Store.</span>',
             paras=[
                 'Below is one of our clients that is currently enrolled in our Viral '
                 'Content Management services. Each page is actively optimized to '
                 'leverage trends, platform algorithms, and audience behavior for '
                 'maximum reach and growth.',
             ],
             link=('See the work', '/work'))),
    dict(slug='logo', name='Logo design', price_key='logo',
         one_line='',      # see the note above SERVICES
         hero_title='Professional<span>logo design.</span>',
         lead='We will work with you to design and deliver a professional logo that '
              'captures your brand identity with the same level of creativity, '
              'precision, and polish found in cinematic visual work.',
         intro=[
             'Each logo is crafted to scale seamlessly across digital and print use, '
             'ensuring clarity, balance, and impact everywhere it appears. After '
             'delivery, we can provide revisions and brand support so your logo remains '
             'effective long after launch.',
             'As your brand evolves, we can refine, refresh, or expand your logo system '
             'to support growth, consistency, and long-term recognition.',
         ],
         breakdown_title='Logo Design Breakdown',
         breakdown_price='Price starts at {amount}, to increase based on client needs.',
         breakdown=[
             'Multiple final concept options to choose from.',
             'Unlimited revisions to refine and perfect the final design.',
             'Scalable files for web, print, and social media use.',
             'Full copyright and usage rights upon delivery.',
         ],
         included_title='Included With This Service',
         included=[
             ('Logo Copyright', 'Full ownership rights to logo.'),
             ('Social Media Kit', 'Optimized logos for social platforms.'),
             ('Scalable Images', 'Logos that scale flawlessly.'),
         ],
         prices=['logo'],
         extra=dict(
             eyebrow='Re-define',
             title='Re-define<span>your brand.</span>',
             paras=[
                 'Transform your existing logo into a more dynamic, modern, and '
                 'impactful brand asset. We start by understanding what already works '
                 'in your current logo and what needs refinement, ensuring brand '
                 'recognition is preserved.',
                 'We enhance scalability and clarity so your logo looks sharp '
                 'everywhere, from social media sites to physical signage. The result '
                 'is a professional logo that feels refreshed, confident, and built to '
                 'grow with your business.',
             ],
             link=('See a logo we built', '/work'))),

    # ---------------------------------------------------------------------
    # NEW COPY — for Drew to approve
    # Both of these pages are blank on netoriouslabs.com, so every sentence
    # below was written here, in his register (plain, data-driven, confident,
    # the "We will work with you to ... / Each ... / As your ..." shape his
    # other four service pages use). Nothing here came from him. It does not
    # go live until he has read it. CLAUDE.md rule 7.
    # ---------------------------------------------------------------------
    dict(slug='drones', name='Drone sessions', price_key='drone-session',
         new_copy=True,
         one_line='',      # see the note above SERVICES
         hero_title='Professional<span>drone sessions.</span>',   # NEW COPY
         lead='We will work with you to plan and fly a drone session that shows your '  # NEW COPY
              'property, your business, or your event from an angle nobody on the '
              'ground can reach, with the same quality and creativity found in our '
              'cinematic work.',
         intro=[                                             # NEW COPY
             'Each flight is planned around the location, the light, and the shots you '
             'actually need, so the footage comes back usable rather than merely '
             'impressive. You get edited 4K clips cut for Facebook, Instagram, and your '
             'website, plus stills pulled from the same session.',
             'As the property, the build, or the season changes, we can fly it again, '
             'so what people see online is what your business looks like today.',
         ],
         breakdown_title='Drone Session Breakdown',          # NEW COPY
         breakdown_price='Price starts at {amount}, to increase based on client needs.',
         breakdown=[                                         # NEW COPY
             'A planned shoot list for the property, business, or event.',
             'Edited 4K clips cut for social and for your website.',
             'High-resolution stills pulled from the same session.',
             'Licensed for your own advertising, listings, and pages.',
         ],
         included_title='Included In This Service',          # NEW COPY
         included=[                                          # NEW COPY
             ('4K Aerial Film', 'Cinematic clips, cut for social and for your site.'),
             ('Stills Included', 'High-resolution photographs from the same flight.'),
             ('Planned Around You', 'Location, light and shot list scouted before we fly.'),
         ],
         prices=['drone-session']),
    dict(slug='lead-conversion', name='Lead conversion', price_key='lead-conversion',
         new_copy=True,
         one_line='',      # see the note above SERVICES
         hero_title='Professional<span>lead conversion.</span>',   # NEW COPY
         lead='We will work with you to close the leads your campaigns already '  # NEW COPY
              'generate. The ads bring the inquiry in; this service is everything after '
              'that &mdash; calling, qualifying, and booking every lead so the ad spend '
              'turns into customers instead of a full inbox.',
         intro=[                                             # NEW COPY
             'Every lead is worked on a schedule and tracked from first contact to '
             'close, so you can see exactly what came in, what was reached, and what '
             'turned into business.',
             'Pricing is built around the work rather than a package: commission on '
             'what we close, or an hourly rate where that fits the business better. '
             'Tell us what your campaigns are producing and we will price it to the need.',
         ],
         breakdown_title='Lead Conversion Breakdown',        # NEW COPY
         breakdown_price=None,                               # no number on this page
         breakdown=[                                         # NEW COPY
             'Fast follow-up on every lead your campaigns generate.',
             'Qualifying calls that separate real inquiries from the noise.',
             'Appointments and bookings placed straight into your calendar.',
             'Reporting on what came in, what was reached, and what closed.',
         ],
         included_title='Included In This Service',          # NEW COPY
         included=[                                          # NEW COPY
             ('Fast Follow-Up', 'Every lead worked while it is still warm.'),
             ('Qualified, Not Counted', 'Real inquiries separated from the noise.'),
             ('Tracked To The Close', 'What came in, what was reached, what closed.'),
         ],
         prices=['lead-conversion']),
]

# Defaults, so a page never has to test for a key: the four services that came
# from his site carry no `new_copy` flag and not all of them have a second
# block or a price sentence.
for _s in SERVICES:
    _s.setdefault('new_copy', False)
    _s.setdefault('extra', None)
    _s.setdefault('breakdown_price', None)
    _s.setdefault('prices', [_s['price_key']])


BY_SLUG = {s['slug']: s for s in SERVICES}


# ---------------------------------------------------------- the search result
# What a service page looks like in Google, which is the only place most people
# will ever read it. Two fields:
#
#   head   the phrase after "Mendoza Marketing — " in the <title>. Google
#          prints about 60 characters of a title and drops the rest, so the
#          whole line has to fit inside that; build.seo_title() checks it.
#   meta   the description under it, about 155 characters. Each one is Drew's
#          own opening sentence from `lead` above, shortened to fit — his
#          words, fewer of them. Nothing here says anything his page does not.
#
# Where his page names a place, so does this: Grand Island is where he is,
# Buffalo is the market, and a local search is the whole reason to name either.
SEO = {
    'websites': dict(
        head='Website design in Grand Island, NY',
        meta='We will work with you to design and deliver a professional website '
             'built on WordPress with the same quality and creativity found in our '
             'cinematic content.'),
    'meta-ads': dict(
        head='Meta ads & filming, Grand Island NY',
        meta='We will work with you to plan, launch and manage high-performing ad '
             'campaigns through Meta Business Suite, with the filming that feeds '
             'them.'),
    'social': dict(
        head='Social media management, Buffalo NY',
        meta='We will work with you to plan, create and deliver professional social '
             'media content with the same quality and creativity found in our '
             'cinematic work.'),
    'logo': dict(
        head='Logo design in Grand Island, NY',
        meta='We will work with you to design and deliver a professional logo that '
             'captures your brand identity with creativity, precision and polish.'),
    'drones': dict(
        head='Drone sessions in Buffalo, NY',
        meta='We will work with you to plan and fly a drone session that shows your '
             'property, your business or your event from an angle nobody on the '
             'ground can reach.'),
    'lead-conversion': dict(
        head='Lead conversion for Meta ads',
        meta='The ads bring the inquiry in; this service is everything after that — '
             'calling, qualifying and booking every lead so ad spend turns into '
             'customers.'),
}

# Every price row points at a service that exists, and every service at a price
# row that exists. Cheap to check, and it is the kind of typo that reaches the
# page as a wrong number rather than as a crash.
for _k, _p in PRICING.items():
    assert _p['service'] in BY_SLUG, f'PRICING[{_k!r}].service is not a service slug'
for _s in SERVICES:
    assert _s['price_key'] in PRICING, f'SERVICES {_s["slug"]!r}: no PRICING row'
    assert _s['slug'] in SEO, f'SERVICES {_s["slug"]!r}: no SEO row'


def price(key):
    """One row of PRICING, by key. KeyError here is the point: a page that asks
    for a package we do not sell should stop the build, not print blank."""
    return PRICING[key]


def price_text(key):
    """'from $1,250' / '$750' / 'Commission or hourly' — the figure as a
    sentence, for a card that has no room for the full price block."""
    p = PRICING[key]
    return f"{p['qualifier']} {p['amount']}".strip()


# ------------------------------------------------------------------- the work
# What we can show, and only what we can show. CLAUDE.md rule 8: this list is
# the files Drew happened to send us, not the size of his business — /work says
# so in as many words and never counts them.
#
# The four brands below are the logo files in assets/: we hold the mark and
# nothing else, so the card says what kind of work it was and marks the detail
# as unconfirmed rather than inventing a brief. Isle de Grande came with two
# renders, which makes it the one case study we can actually show.
CLIENTS = [
    dict(slug='client-buffalo-holistic', name='Buffalo Holistic Center',
         work='Logo and brand work', detail=None),
    dict(slug='client-zen-zone', name='Zen Zone Property Maintenance LLC',
         work='Logo and brand work', detail=None),
    dict(slug='client-britt-fitness', name='Britt Fitness LLC',
         work='Logo and brand work', detail=None),
    dict(slug='client-adams-detailing', name='Adam&rsquo;s Detailing &amp; Coatings',
         work='Logo and brand work', detail=None),
]

# The logo-design case: his mark for Grand Island's news page, in both renders
# he sent. The line under the name is his own, from netoriouslabs.com.
CASE = dict(
    name='Isle de Grande', work='Logo design',
    blurb='Grand Island&rsquo;s #1 news source.',
    renders=[('isle-de-grande', 'The Isle de Grande logo'),
             ('isle-de-grande-profile', 'The Isle de Grande profile mark')],
)

# The three businesses his own portfolio page lists under "Websites", with his
# own description of each. No logo files for these, and no URLs in our capture,
# so they are named and described rather than linked.
SITES = [
    dict(name='Kelly&rsquo;s Country Store',
         work='Website · Viral content management · Meta ads',
         blurb='Grand Island&rsquo;s hidden gem since 1962. Candy, Chocolate, '
               'Nostalgic gifts and so much more!'),
    dict(name='Slick &amp; Shine Detailing', work='Website',
         blurb='Premier auto detailing shop located in Orchard Park, NY. Offering '
               'full detailing, paint correction and ceramic coatings.'),
    dict(name='Gator Jon&rsquo;s BBQ', work='Website',
         blurb='The best BBQ on Grand Island! Located in the Kelly&rsquo;s Country '
               'Store lot, smoked BBQ to perfection.'),
]

# The three Kelly's reels the pipeline cuts. The captions describe the film;
# "Santa at Kelly's" is his own title for the first one, from his portfolio.
REELS = [
    ('reel-santa', 'Santa at Kelly&rsquo;s', 'The Santa event ad'),
    ('reel-pretzels', 'Chocolate pretzels', 'Packing the boxes'),
    ('reel-rice-krispies', 'Rice Krispie treats', 'Sprinkles going on'),
]

# The six clips from one real-estate shoot, in the order the house is revealed
# rather than in DJI filename order (make-clips.sh sets the same order).
DRONE_CLIPS = [
    ('drone-1', 'Elevated orbit &mdash; pool, lake and roofline'),
    ('drone-2', 'Push-in reveal from the seawall'),
    ('drone-3', 'Up the lawn, in to the window wall'),
    ('drone-4', 'The pass along the garden front'),
    ('drone-5', 'Inside: the sunroom, then the dining room'),
    ('drone-6', 'Inside: the living room and the water view'),
]


# ------------------------------------------------------------------ about Drew
# His own About page, word for word, with "Netorious Labs" replaced by the new
# name and nothing else changed. The three beats are his too; the only edit is
# sentence case and the spelling of "stand out", which his page runs together.
ABOUT = dict(
    hero_title='Welcome to<span>Mendoza Marketing.</span>',
    lead='At Mendoza Marketing, our mission is to help small and mid-sized '
         'businesses grow and compete online. We deliver data-driven digital '
         'marketing solutions designed to strengthen brand visibility and drive '
         'measurable results.',
    specialize_title='We specialize in:',
    specialize=[
        'WordPress Website Design',
        'Brand &amp; Logo Development',
        'Data-driven Meta Business Suite Advertising Campaigns',
        'High-quality Social Media Content Creation',
        'Aerial Drone Content Creation',
    ],
    together_title='Let&rsquo;s Build Something Great Together',
    together='Mendoza Marketing is a digital marketing agency offering a full suite '
             'of data-driven web marketing services. We help businesses scale by '
             'building online strategies designed for measurable growth.',
    # The four photographs he sent. The alt text describes the picture and
    # claims nothing about him that he has not told us.
    photo_lead=('drew-headshot', 'Drew Mendoza'),
    photos=[
        ('drew-suit', 'Drew Mendoza outdoors in autumn'),
        ('drew-detailing', 'Drew Mendoza filming at a detailing shop'),
        ('drew-mt-bank', 'Drew Mendoza downtown, in black and white'),
    ],
)

# Design · Launch · Grow — his three beats, from the same page.
BEATS = [
    ('01', 'Design', 'We create clean visuals that stand out.'),
    ('02', 'Launch', 'We build, test and deploy your vision.'),
    ('03', 'Grow', 'We turn traffic into paying customers.'),
]
