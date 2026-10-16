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
# The phone is the one published on his old site (netoriouslabs.com/contact,
# saved 2026-09-22). The email is the new brand's: drew@mendozamarketing.com
# replaced drew@netoriouslabs.com on the owner's word, 2026-10-15.
SITE = dict(
    name='Mendoza Marketing',
    tagline='Content · Websites · Drones',          # his README, verbatim
    owner='Drew Pitts',                             # confirmed by the owner, 2026-09-25
    email='drew@mendozamarketing.com',              # the owner, 2026-10-15
    phone='716-860-5991',                           # TODO confirm
    phone_href='+17168605991',
    place='Grand Island · Buffalo, NY',
    # (label, icon key in build.ICONS, url). An empty url renders as a drawn,
    # unlinked icon — the footer keeps its shape and nobody clicks a dead link.
    # Both URLs from Drew, 2026-10-03.
    socials=[
        ('Instagram', 'ig', 'https://www.instagram.com/mendozamarketinggroup/'),
        ('Facebook',  'fb', 'https://www.facebook.com/mendozamarketinggroup'),
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
    'FORM_ENDPOINT — the Formspree id for the quote form',
    'SERVICES /drones and /lead-conversion — the heroes, the lead-conversion '
    'paragraphs and both package lists are his (2026-10-15); the rest is NEW '
    'COPY written here: the drones intro and Included trio, the arsenal cards '
    '(pages.ARSENAL), the lead Included trio and the hub sentence. Drew to approve',
    'SERVICES /social — the three Included sentences are NEW COPY (his headings)',
    'RESULTS Kelly\u2019s follower growth, start through the first year — '
    'results.KELLY["growth"]; the dashboard draws the chart once it is filled',
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
# NOTE: the README and netoriouslabs.com used to disagree on two of these.
# Drew settled both himself — performance marketing at $750 a month
# (2026-10-11) and logo design from $500 (2026-10-12).
#
# There is no re-design package. Drew, 2026-10-10: "I've decided to focus
# exclusively on full website builds rather than redesigns." The row, its
# section on /websites and its line on Home all went together.
#
# `features` is a package's own list of what is in it, as (title, detail),
# printed on its price card wherever the card appears. `image` names a
# rendition in out/img/ shown at the top of that card — only once the file
# is there, so a missing graphic warns in the build and never ships a broken
# image (CLAUDE.md rule 10).
WEB_FEATURES = [
    # Drew's own list, 2026-10-10, word for word.
    ('5+ Custom Content Pages', 'Services, About, etc.'),
    ('Responsive Design', 'Optimized for all devices.'),
    ('Launch Support', 'Domain setup and DNS management.'),
    ('SEO Integration', 'Initial SEO setup for search visibility.'),
]

LOGO_FEATURES = [
    # Drew's own list, 2026-10-12, word for word.
    ('Multiple Concepts', 'Final design options to choose from.'),
    ('Unlimited Revisions', 'Refine the design until it’s right.'),
    ('Scalable Files', 'Ready for web, print, and social media.'),
    ('Full Ownership', 'Copyright and usage rights upon delivery.'),
]

# The three social tiers, Drew 2026-10-15, word for word. A feature that is a
# plain string prints as one line; a (title, detail) pair prints as above.
EMERALD_FEATURES = [
    '2 scheduled 1.5-hour on-site video shoots monthly (every 2 weeks).',
    '1 cinematic custom reel weekly (15–30 seconds), approximately every 7–10 days.',
    '2 custom story posts weekly using filmed content to drive website traffic.',
    'Weekly page management and community engagement.',
    'Recurring monthly billing.',
]
SAPPHIRE_FEATURES = [
    '1 scheduled 2-hour on-site shoot weekly (8 hours monthly).',
    '1–2 cinematic custom reels weekly (15–30 seconds), approximately every 5–7 days.',
    'Drone and Meta Glasses footage for dynamic angles and POV content.',
    'Daily page management and community engagement.',
    'Weekly multi-platform story content.',
]
DIAMOND_FEATURES = [
    '2 scheduled 2-hour on-site shoots weekly (16 hours monthly).',
    '5–7 custom reels weekly (15–30 seconds).',
    'Priority support and on-site visits.',
    'Full social media page management and community engagement.',
]

DRONE_FEATURES = [
    # Drew, 2026-10-15, word for word.
    '2-hour professional aerial photography or video filming session.',
    'Horizontal and vertical 4K filming for websites, social media, and '
    'promotional content.',
    'Professionally edited final creative, ready for digital use.',
]

LEAD_FEATURES = [
    # Drew, 2026-10-15, word for word.
    'Lead Follow-Up &amp; Outreach',
    'Lead Qualification &amp; Sales Conversion',
    'Appointment Scheduling &amp; Booking',
    'Conversion Tracking &amp; Optimization',
]

PRICING = {
    'web-design': dict(
        name='Website design', service='websites',
        qualifier='from', amount='$1,250', note=None,
        tier='Websites', features=WEB_FEATURES,
        # His "Website Design graphic", sent 2026-10-10 as the placeholder for
        # this package. Not received yet: drop it in as out/img/pkg-web-design.webp
        image='pkg-web-design'),
    # Performance marketing (Drew, 2026-10-11: "Update to $750/month"). `per`
    # is the billing period, printed after the figure wherever it appears
    # ("$750/month") and carried into the graph as a monthly price.
    'meta-ads': dict(
        name='Performance Marketing', service='meta-ads',
        qualifier='', amount='$750', per='month', note=None,
        tier='Performance',
        # His "Performance Marketing graphic", sent 2026-10-11 as the product
        # image. Not received yet: drop it in as out/img/pkg-meta-ads.webp
        image='pkg-meta-ads'),
    # Drew, 2026-10-15: Emerald $1,000 / Sapphire $1,500 / Diamond $2,000 a
    # month, each with its own contents. (His hero line said "$500–$2,000";
    # the owner chose the range the three rows actually make.)
    'social-emerald': dict(
        name='Social media — Emerald', service='social',
        qualifier='', amount='$1,000', per='month', note=None,
        tier='Emerald', features=EMERALD_FEATURES),
    'social-sapphire': dict(
        name='Social media — Sapphire', service='social',
        qualifier='', amount='$1,500', per='month', note=None,
        tier='Sapphire', features=SAPPHIRE_FEATURES),
    'social-diamond': dict(
        name='Social media — Diamond', service='social',
        qualifier='', amount='$2,000', per='month', note=None,
        tier='Diamond', features=DIAMOND_FEATURES),
    # Drew, 2026-10-12: "Starting at $500 … Pricing varies by project needs",
    # and the four features below, his words. The README/netoriouslabs
    # disagreement ($500 vs $750) is settled by this: $500, as a floor.
    'logo': dict(
        name='Logo design', service='logo',
        qualifier='from', amount='$500', note='Pricing varies by project needs.',
        tier='Logo', features=LOGO_FEATURES,
        # His product graphic, sent 2026-10-12 — not received yet: drop it in
        # as out/img/pkg-logo.webp and the card picks it up.
        image='pkg-logo'),
    'lead-conversion': dict(
        name='Lead conversion', service='lead-conversion',
        # Drew, 2026-10-15: "an hourly rate plus commission on closed deals",
        # and a custom quote rather than a package.
        qualifier='', amount='Hourly + commission',
        note='A custom quote for every business.',
        tier='Leads', features=LEAD_FEATURES),
    'drone-session': dict(
        name='Drone session', service='drones',
        qualifier='', amount='$1,000', note=None,
        tier='Drones', features=DRONE_FEATURES),
}


# ------------------------------------------------------- logo before & after
# The logo transformations on /logo (Drew, 2026-10-12: "Add a before-and-after
# section showcasing logo transformations. I'm attaching the old and new Isle
# De Grande logos as an example"). Each case names two renditions in
# out/img/; a case shows only when BOTH files are there, and the section only
# when at least one case does — a "before" we have not got is never faked and
# never shown as a gap. More cases are more rows here.
#
# Isle de Grande's "after" we have held since his first drop (the transparent
# master, on a light plate). The "before" — the old logo — did not arrive with
# his message: save it as out/img/isle-de-grande-before.webp.
LOGO_CASES = [
    dict(name='Isle de Grande', what='Grand Island&rsquo;s #1 news source',
         before='isle-de-grande-before', after='isle-de-grande'),
]


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
#   intro_link      (label, path) — a button under the intro, where he asked
#                   for one ("View Our Work" on /websites)
#   hero_backdrop   what moves behind the hero: 'sky' (clouds and wind, on
#                   /websites) or 'sketch' (a logo being drawn, on /logo)
#   extra           the second block some of his pages carry ("Re-define your
#                   brand", "Our services in action")
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
         # The package's own list (Drew, 2026-10-10), so the breakdown beside
         # the intro and the price card further down say the same four things.
         breakdown=[f'{t} &ndash; {d}' for t, d in WEB_FEATURES],
         intro_link=('View our work', '/work'),
         hero_backdrop='sky',
         included_title='What You Can Expect',
         # Drew, 2026-10-10: "expand the descriptions slightly to focus on
         # customer benefits rather than 1 line generic statements". The
         # headings are his; the sentences under them are NEW COPY, written in
         # his register, for him to approve.
         included=[
             ('SEO Setup', 'Your site is built to be found from day one &mdash; '
              'clean page titles, descriptions and a sitemap search engines can '
              'read &mdash; so the customers searching for what you do land on '
              'you, not a competitor.'),
             ('Optimized Speed', 'Pages that load fast on any connection, so '
              'visitors stay instead of bouncing, and the traffic your ads and '
              'posts send actually gets to see what you offer.'),
             ('Mobile Friendly', 'Most customers meet you on a phone first. Every '
              'page is designed for a small screen from the start, with menus, '
              'buttons and forms that are easy to use with one thumb.'),
         ],
         prices=['web-design'],
         extra=None),
    # Renamed from "Meta ads & filming" (Drew, 2026-10-11: "Rename … to
    # 'Performance Marketing' throughout the page, … the submenu in the header
    # & the footer"). The slug, and so the URL, stays /meta-ads: renaming it
    # would break every link already out there for no gain a visitor can see.
    dict(slug='meta-ads', name='Performance Marketing', price_key='meta-ads',
         one_line='',      # see the note above SERVICES
         hero_title='Performance<span>marketing.</span>',
         # His two paragraphs, 2026-10-11, word for word: the first under the
         # headline, the second beside the breakdown.
         lead='Our professionally managed Meta campaigns combine targeted local '
              'advertising with high-quality video production to reach potential '
              'customers. From filming content to launching and managing campaigns, '
              'we handle the entire process.',
         intro=[
             'Getting views is one thing. Turning them into customers is another. '
             'Through strategic targeting, engaging ad creatives, and ongoing '
             'optimization, we focus on generating real engagement, qualified leads, '
             'and measurable results.',
         ],
         breakdown_title='Performance Marketing Breakdown',
         # His old line was "Price starts at $500 to manage, client covers daily
         # budget." The figure is now $750 a month (PRICING); the clause about
         # the client's own ad budget is his and is kept — the campaign preview
         # on this page says the same thing about the spend it adds up.
         breakdown_price='{amount} a month. The client covers the daily ad budget.',
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
         # Drew, 2026-10-15: the heading in initial caps, this paragraph word for
         # word, the price as the range his three tiers make, and his two
         # results floating in the hero (`hero_proof`).
         hero_title='Viral Content<span>Management.</span>',
         lead='Elevate your social media presence with strategic planning, creative '
              'storytelling, and professional content production designed to showcase '
              'your brand, engage your audience, and take your online presence to the '
              'next level.',
         hero_backdrop='social',
         hero_price='range',
         hero_proof=['1.5M+ views on a single reel',
                     'Consistent 300K&ndash;400K monthly views'],
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
         # His headings; the sentences under them are NEW COPY (Drew,
         # 2026-10-15: "expand the descriptions … emphasize that we personally
         # film and produce content on-site"). For Drew to approve.
         included=[
             ('Content Creation',
              'We come to you. Every reel is filmed on-site at your business by us '
              '&mdash; your space, your people, your products &mdash; then edited '
              'in-house and cut for each platform. No stock footage, nothing '
              'outsourced.'),
             ('User Interaction',
              'We stay active on your pages between posts: answering comments and '
              'messages, replying to tags and joining the conversation in your '
              'voice, so the people who find you get a real response and a reason '
              'to come back.'),
             ('Page Growth',
              'We track how every post performs and plan the next shoot around what '
              'worked, adjusting formats, timing and trends month to month for '
              'steady growth rather than one lucky post.'),
         ],
         prices=['social-emerald', 'social-sapphire', 'social-diamond'],
         # The Kelly's section is its own dashboard now: pages.kelly_dashboard().
         ),
    dict(slug='logo', name='Logo design', price_key='logo',
         one_line='',      # see the note above SERVICES
         hero_title='Professional<span>logo design.</span>',
         hero_backdrop='sketch',
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
         # The package's own list (Drew, 2026-10-12), as on /websites.
         breakdown=[f'{t} &ndash; {d}' for t, d in LOGO_FEATURES],
         included_title='Included With This Service',
         # Drew, 2026-10-12: "Expand the descriptions slightly to sound more
         # professional and explain the benefits." His headings; the sentences
         # are NEW COPY for him to approve.
         included=[
             ('Logo Copyright', 'You own your logo outright. Full copyright and '
              'usage rights pass to you on delivery, so it is yours to print, '
              'register and use anywhere &mdash; no licensing fees, no permission '
              'needed.'),
             ('Social Media Kit', 'Versions of your logo sized and cropped for each '
              'profile &mdash; Facebook, Instagram, Google and more &mdash; so your '
              'brand looks sharp and consistent everywhere customers find you.'),
             ('Scalable Images', 'Vector and high-resolution files that stay crisp '
              'at any size, from a website icon to a storefront sign, a vehicle '
              'wrap or a printed banner.'),
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
         # Drew, 2026-10-15: the heading in initial caps and this paragraph,
         # word for word — the hero is his now; the rest below is still ours.
         hero_title='Professional Drone<span>Sessions.</span>',
         lead='Our professional drone services deliver stunning aerial perspectives of '
              'your property, business, or event. Combining expert flight planning, '
              'precision, and cinematic creativity, we capture high-quality visuals '
              'that showcase every detail from a perspective beyond the ground.',
         hero_backdrop='peaks',
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
         breakdown=DRONE_FEATURES,                           # his, 2026-10-15
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
         # Drew, 2026-10-15: heading, lead and the two paragraphs, word for word.
         hero_title='Professional Lead<span>Conversion.</span>',
         lead='Turn more leads into paying customers and maximize your advertising '
              'investment. Through professional follow-ups, lead qualification, and '
              'appointment booking, we turn interested prospects into real customers '
              'and help drive more revenue.',
         hero_backdrop='growth',
         intro=[
             'We create targeted campaigns to generate qualified leads. Pricing is '
             'based on an hourly rate plus commission on closed deals.',
             'We also help close initial leads to offset costs while training your '
             'team to confidently handle future leads.',
         ],
         breakdown_title='Lead Conversion Breakdown',        # NEW COPY
         breakdown_price=None,                               # no number on this page
         breakdown=LEAD_FEATURES,                            # his, 2026-10-15
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
        head='Performance Marketing, Grand Island NY',
        meta='Professionally managed Meta campaigns that pair targeted local '
             'advertising with high-quality video, from filming to launch and '
             'ongoing management.'),
    'social': dict(
        head='Viral Content Management, Buffalo NY',
        meta='Strategic planning, creative storytelling and professional content '
             'production, filmed on-site, to showcase your brand and engage your '
             'audience.'),
    'logo': dict(
        head='Logo design in Grand Island, NY',
        meta='We will work with you to design and deliver a professional logo that '
             'captures your brand identity with creativity, precision and polish.'),
    'drones': dict(
        head='Drone sessions in Buffalo, NY',
        meta='Stunning aerial perspectives of your property, business or event: '
             'expert flight planning, precision and cinematic 4K, from a perspective '
             'beyond the ground.'),
    'lead-conversion': dict(
        head='Lead conversion for Meta ads',
        meta='Turn more leads into paying customers: professional follow-ups, lead '
             'qualification and appointment booking that get more from your '
             'advertising.'),
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
    """'from $1,250' / '$750/month' / 'Hourly + commission' — the figure as a
    sentence, for a card that has no room for the full price block."""
    p = PRICING[key]
    per = f"/{p['per']}" if p.get('per') else ''
    return f"{p['qualifier']} {p['amount']}{per}".strip()


def price_range(keys):
    """'$1,000–$2,000/month' — the lowest and highest of a set of rows, so a
    hero that quotes a range can never disagree with the cards under it."""
    rows = sorted((PRICING[k] for k in keys),
                  key=lambda p: float(p['amount'].strip('$').replace(',', '')))
    lo, hi = rows[0], rows[-1]
    per = f"/{hi['per']}" if hi.get('per') else ''
    return f"{lo['amount']}&ndash;{hi['amount']}{per}"


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
    # Drew, 2026-10-15: these four, his own mark included. Adam's Detailing and
    # Britt Fitness are off: "I didn't design these two logos, so they
    # shouldn't be included in our portfolio." (Both still sit in Home's
    # Trusted By strip, which is about clients rather than design work.)
    dict(slug='client-buffalo-holistic', name='Buffalo Holistic Center',
         work='Logo design', detail=None),
    dict(slug='client-zen-zone', name='Zen Zone Property Maintenance',
         work='Logo design', detail=None),
    dict(slug='isle-de-grande', name='Isle de Grande',
         work='Logo design', detail=None, light=True),
    dict(slug='logo', name='Mendoza Marketing',
         work='Logo design · our own', detail=None, contain=True),
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
    # Drew, 2026-10-15: "our completed $1,250 WordPress websites", these six,
    # in his order. The previews are screenshots of the live sites taken by
    # tools/shoot-sites.mjs into out/img/site-<slug>.webp (re-run it when a
    # site changes); a missing one warns and the card shows the address alone.
    dict(slug='sourdough-by-amanda', name='Sourdough by Amanda',
         url='https://sourdoughbyamanda.com/'),
    dict(slug='gator-jons-bbq', name='Gator Jon&rsquo;s BBQ',
         url='https://gatorjonsbbq.com/'),
    dict(slug='buffalo-benefits', name='Buffalo Benefits',
         url='https://buffalobenefits.com/'),
    dict(slug='britt-fitness', name='Britt Fitness',
         url='https://brittfitness716.com/'),
    dict(slug='slick-and-shine', name='Slick &amp; Shine Detailing',
         url='https://www.slickandshine716.com/'),
    dict(slug='zen-zone', name='Zen Zone Property Maintenance',
         url='https://zenzonepropertymaintenance.net/'),
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
    photo_lead=('drew-headshot', 'Drew Pitts'),
    photos=[
        ('drew-suit', 'Drew Pitts outdoors in autumn'),
        ('drew-detailing', 'Drew Pitts filming at a detailing shop'),
        ('drew-mt-bank', 'Drew Pitts downtown, in black and white'),
    ],
)

# Design · Launch · Grow — his three beats, from the same page.
BEATS = [
    ('01', 'Design', 'We create clean visuals that stand out.'),
    ('02', 'Launch', 'We build, test and deploy your vision.'),
    ('03', 'Grow', 'We turn traffic into paying customers.'),
]
