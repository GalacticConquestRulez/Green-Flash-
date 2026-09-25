#!/usr/bin/env python3
"""The walls — the single source of truth for every project on the site.

Nothing about a project is typed twice. The Work index, the project
pages, the featured row on Home, the footer column, the square-foot total and
the JSON-LD all read this list, and build.py refuses to finish if a row is
malformed or its photograph is not on disk.

Where the facts come from
-------------------------
Client, title, city and the dimensions are Ephraim's own, transcribed from the
Work page of the live Wix site (saved in research/wix/work.html on 2026-09-18)
and cross-checked against the "Recent Projects" block on his home page. The
photographs are the Wix renditions pulled by fetch-wix.py — placeholders until
his originals arrive; see docs/images.md.

Three rules held while writing this file:

* **Years are not on his site, so `year` is None.** An invented date on a
  civil-rights mural is worse than no date. Fill them in when Ephraim says.
* **`dim_w` and `dim_h` may both be None**, and then neither may be guessed.
  A wall Ephraim has photographed but never measured for us is still a wall;
  it is the *figures* we do not have, and the site says so in his own hand
  rather than printing a number nobody gave it. Both or neither: a width with
  no height is a typo, and build.py's check_projects() refuses it.
* **`story` says only what is known.** His site carries no project write-ups
  at all, so each story is the short factual line PLAN.md asks for — client,
  city, size — plus anything his own pages actually state. No anecdotes, no
  imagined briefs, no invented collaborators. When he sends real stories they
  replace these, one commit, nothing else changes.

`credit` is None for every row for the same reason: the live site credits no
photographer or collaborator, and we are not going to guess at one.

Fields
------
slug      URL segment, /work/<slug>            title    as his site names it
client    the brand, or None for a wall with no commercial client
city, state                                     dim_w, dim_h  feet, or both None
year      None until Ephraim confirms          category 'brand'|'portrait'|'civic'
hero      out/img/<hero>.webp and friends      gallery  extra image names
video     out/video/<video>.{mp4,webp}, laid over the hero photograph
progress  out/video/<progress>.{mp4,webp}, the portrait reel under the story
film      out/video/<film>.{mp4,webp}, the whole film behind the play button,
          with film_eyebrow and film_line as the words over it
story     one paragraph                        credit   None until supplied
featured  on the Home row and in the footer
"""

# 'civic' is the two Rochester commissions, which PLAN.md and the design notes
# name explicitly and which the site treats as their own beat. 'portrait' holds
# I Am A Man — a painted portrait, not a brand wall, and not one of the two
# Rochester pieces. That last call is ours, not Ephraim's: worth confirming
# with him when he reviews the preview.
CATEGORIES = ('brand', 'portrait', 'civic')

# Order = the order the Work index lists them, which is the order his own
# Work page uses, read left to right.
PROJECTS = [
  dict(slug='gucci-new-york', title='Gucci', client='Gucci',
       city='New York', state='NY', dim_w=81, dim_h=80, year=None,
       category='brand', hero='gucci-new-york-hero', gallery=[],
       story='Gucci, on a wall in New York City — 81 feet wide by 80 feet tall, '
             'and the first project on Ephraim’s own Work page.',
       credit=None, featured=True),

  dict(slug='crown-royal-trail-blazers', title='Crown Royal × Trail Blazers',
       client='Crown Royal × Trail Blazers',
       city='Portland', state='OR', dim_w=85, dim_h=90, year=None,
       category='brand', hero='crown-royal-trail-blazers-hero', gallery=[],
       story='Crown Royal with the Portland Trail Blazers — 85 feet wide by 90 feet '
             'tall in Portland, Oregon. Ninety feet is the tallest wall in the roster.',
       credit=None, featured=True),

  dict(slug='uber-san-francisco', title='Uber', client='Uber',
       city='San Francisco', state='CA', dim_w=62, dim_h=23, year=None,
       category='brand', hero='uber-san-francisco-hero', gallery=[],
       story='Uber, in San Francisco — a long horizontal run, 62 feet wide by '
             '23 feet tall.',
       credit=None, featured=True),

  dict(slug='victorias-secret-austin', title='Victoria’s Secret',
       client='Victoria’s Secret',
       city='Austin', state='TX', dim_w=36, dim_h=8, year=None,
       category='brand', hero='victorias-secret-austin-hero', gallery=[],
       story='Victoria’s Secret in Austin, Texas — 36 feet wide by 8 feet tall. '
             'His Work page files it as Victoria Secret; the same wall appears on his '
             'home page under Pink, the brand’s line.',
       credit=None, featured=False),

  dict(slug='vitamin-water-new-york', title='Vitamin Water', client='Vitamin Water',
       city='New York', state='NY', dim_w=9, dim_h=20, year=None,
       category='brand', hero='vitamin-water-new-york-hero', gallery=[],
       story='Vitamin Water, New York City — 9 feet wide by 20 feet tall: a tall '
             'narrow wall rather than a broad one.',
       credit=None, featured=False),

  dict(slug='sprite-new-york', title='Sprite', client='Sprite',
       city='New York', state='NY', dim_w=11, dim_h=16, year=None,
       category='brand', hero='sprite-new-york-hero', gallery=[],
       story='Sprite, New York City — 11 feet wide by 16 feet tall. Sprite is also '
             'slide 02 on the home page of his current site.',
       credit=None, featured=False),

  dict(slug='ford-mustang-chicago', title='Ford Mustang', client='Ford Mustang',
       city='Chicago', state='IL', dim_w=23, dim_h=36, year=None,
       category='brand', hero='ford-mustang-chicago-hero', gallery=[],
       story='Ford Mustang, Chicago — 23 feet wide by 36 feet tall. His current home '
             'page lists it among recent projects as Mustang, 23′ × 36′, '
             'Chicago, IL.',
       credit=None, featured=False),

  # PLAN.md fixes the slug as showtime-dexter-boston. His own site says only
  # "Showtime", so that is all the page says until he confirms the title.
  dict(slug='showtime-dexter-boston', title='Showtime', client='Showtime',
       city='Boston', state='MA', dim_w=18, dim_h=9, year=None,
       category='brand', hero='showtime-dexter-boston-hero', gallery=[],
       story='Showtime, Boston — 18 feet wide by 9 feet tall, and the smallest '
             'surface on this page by area.',
       credit=None, featured=False),

  dict(slug='upendo-los-angeles', title='Upendo', client='Upendo',
       city='Los Angeles', state='CA', dim_w=18, dim_h=18, year=None,
       category='brand', hero='upendo-los-angeles-hero', gallery=[],
       story='Upendo, Los Angeles — 18 feet by 18 feet, square. His current home page '
             'lists it among recent projects at that size and city.',
       credit=None, featured=True),

  dict(slug='i-am-a-man-chicago', title='I Am A Man', client=None,
       city='Chicago', state='IL', dim_w=15, dim_h=32, year=None,
       category='portrait', hero='i-am-a-man-chicago-hero', gallery=[],
       story='I Am A Man, Chicago — 15 feet wide by 32 feet tall: a portrait painted '
             'above the lettering that gives the wall its name.',
       credit=None, featured=False),

  dict(slug='john-lewis-rochester', title='I Am Speaking: John Lewis', client=None,
       city='Rochester', state='NY', dim_w=53, dim_h=50, year=None,
       category='civic', hero='john-lewis-rochester-hero',
       gallery=['john-lewis-rochester-1'],
       story='I Am Speaking: John Lewis, in Rochester, New York — 53 feet wide by '
             '50 feet tall. One of two civil-rights walls Open Air Gallery painted in '
             'the same city, at the same size.',
       credit=None, featured=True),

  dict(slug='malcolm-x-rochester', title='Malcolm X', client=None,
       city='Rochester', state='NY', dim_w=53, dim_h=50, year=None,
       category='civic', hero='malcolm-x-rochester-hero', gallery=[],
       # The photograph is portrait and the mural fills its top half; a centred
       # crop shows the lift and the windows and cuts the faces (owner, 2026-09-19).
       focus='50% 0%',
       story='Malcolm X, in Rochester, New York — 53 feet wide by 50 feet tall, the '
             'companion to the John Lewis wall and the same size to the foot.',
       credit=None, featured=True),

  # Ephraim's own drop, 2026-09-20 (docs/ephraim-drop-2026-09-20.md): a wall
  # that was never on his Wix Work page, so it joins at the end of the order
  # that page set rather than being slotted into the middle of it. The films
  # and the photographs came with the drop; the feet came from the owner on
  # 2026-09-21 — "15x15 on rains" — written wide by tall like every other row
  # in this file. The year is the year he posted the film (the owner,
  # 2026-09-20), not a date read off the wall.
  dict(slug='rains-new-york', title='Rains', client='AMC × Angel Media Co.',
       city='New York', state='NY', dim_w=15, dim_h=15, year=2024,
       category='brand', hero='rains-new-york-hero', video='hero-rains',
       progress='rains-progress', film='film-rains',
       film_eyebrow='with the sound on',
       film_line='Ephraim\u2019s own edit of the job \u2014 the same flight the top of '
                 'this page is cut from, at full size and with its sound.',
       gallery=['rains-new-york-1', 'rains-new-york-2', 'rains-new-york-3',
                'rains-new-york-4'],
       story='Three faces and the word RAINS, painted on a Manhattan wall for '
             'AMC — Angel Media Co., whose placard sits under it. It went up by '
             'hand from a boom lift, 15 feet wide by 15 feet tall.',
       credit=None, featured=True),

  # The second wall out of the same drop. A community wall under the bridge by
  # the ballpark, filmed by Max (@omgmaxgod) — the only project on the site
  # with a credit on it, because it is the only one where somebody other than
  # Ephraim's own camera is the source. The feet came from the owner on
  # 2026-09-21 — "25x50 on flower city" — and the year from the post date (the
  # owner, 2026-09-20). Its photographs are frames pulled from the film. It is
  # the one wall on the roster that is taller than it is wide, which is what a
  # wall under a bridge abutment is.
  dict(slug='flower-city-arts-center-rochester', title='Flower City Arts Center',
       client='Flower City Arts Center',
       city='Rochester', state='NY', dim_w=25, dim_h=50, year=2023,
       category='civic', hero='flower-city-arts-center-rochester-hero',
       video='hero-flower-city', film='film-flower-city',
       film_eyebrow='with the sound on',
       film_line='Max\u2019s film of the wall, start to finish: the crew, the lifts, '
                 'and the people it was painted with.',
       gallery=['flower-city-arts-center-rochester-1',
                'flower-city-arts-center-rochester-2',
                'flower-city-arts-center-rochester-3'],
       story='A community wall with Flower City Arts Center, on the underpass by the '
             'ballpark in Rochester — a block of storefronts and portraits, painted '
             'from lifts along the concrete, 25 feet wide by 50 feet tall.',
       credit='Film by Max — @omgmaxgod', featured=False),
  # Ephraim's drop, 2026-09-25 (docs/ephraim-drop-2026-09-25.md): four New
  # York walls that arrived as films and nothing else. Every one of them is a
  # wall his Wix Work page never carried, so they join at the end of the order
  # that page set, the way Rains and Flower City did.
  #
  # NO YEAR AND NO FEET on any of the four. Nobody has given us either, and
  # neither is guessed: dim_w/dim_h are None, so the card and the page carry
  # feet_note() where the figure goes, and year is None, so the Year row is
  # simply not written. The one date-shaped thing in the whole drop is the
  # copyright line on the end card of the Fords Gin film (2025 Brown-Forman),
  # which is a notice on a video and not a statement about when a wall was
  # painted — so it is in the drop doc as a question for Ephraim and nowhere
  # near this file.
  #
  # video= and film= name THE SAME FILE on all four, which is the point: there
  # is one encode of each (make-drop-films.sh), it plays whole and muted in a
  # loop behind the words at the top of the page, and the play button under it
  # unmutes that same element and starts it again from the front, with its
  # sound. Nothing is cut and nothing is fetched twice.
  # The photographs are frames pulled from the films at the camera's own size
  # (make-drop-stills.sh), because no photographs of these four walls exist
  # here.

  dict(slug='moncler-new-york', title='Moncler', client='Moncler',
       city='New York', state='NY', dim_w=None, dim_h=None, year=None,
       category='brand', hero='moncler-new-york-hero',
       video='film-moncler', film='film-moncler',
       film_eyebrow='with the sound on',
       film_line='The wall from the first bucket of paint to the drone pulling away '
                 'from the finished block \u2014 whole, at full size, with its sound.',
       gallery=['moncler-new-york-1', 'moncler-new-york-2', 'moncler-new-york-3',
                'moncler-new-york-4'],
       story='A woman in a green mask, painted for Moncler on a brick wall at Grand '
             'and Centre in lower Manhattan, with \u201cWhere Dreams Are Made Of\u201d '
             'lettered under her. MONCLER GENIUS is tagged in yellow on the brick '
             'beside it. It went up by hand from a boom lift.',
       credit=None, featured=False),

  dict(slug='asap-rocky-ray-ban-new-york', title='A$AP Rocky \u00d7 Ray-Ban',
       client='Ray-Ban \u00d7 A$AP Rocky',
       city='New York', state='NY', dim_w=None, dim_h=None, year=None,
       category='brand', hero='asap-rocky-ray-ban-new-york-hero',
       video='film-asap-rocky-ray-ban', film='film-asap-rocky-ray-ban',
       film_eyebrow='with the sound on',
       film_line='Ephraim\u2019s film of the job \u2014 the lift, the street and the '
                 'block from the air, whole and with its sound.',
       gallery=['asap-rocky-ray-ban-new-york-1', 'asap-rocky-ray-ban-new-york-2',
                'asap-rocky-ray-ban-new-york-3', 'asap-rocky-ray-ban-new-york-4'],
       story='A$AP Rocky in Ray-Bans, painted over a New York street on a pale blue '
             'ground, with a second portrait beside him and the Ray-Ban roundel that '
             'names the campaign \u2014 AWGE set around its rim. Painted by hand from '
             'a boom lift, in the middle of the traffic.',
       credit=None, featured=False),

  dict(slug='fords-gin-new-york', title='Fords Gin', client='Fords Gin',
       city='New York', state='NY', dim_w=None, dim_h=None, year=None,
       category='brand', hero='fords-gin-new-york-hero',
       video='film-fords-gin', film='film-fords-gin',
       film_eyebrow='with the sound on',
       film_line='Shot vertically, so it plays the shape he shot it \u2014 the whole '
                 'film, at full size, with its sound.',
       gallery=['fords-gin-new-york-1', 'fords-gin-new-york-2',
                'fords-gin-new-york-3', 'fords-gin-new-york-4'],
       story='\u201cNew York, thank you for the Martini. Sincerely, Fords Gin\u201d '
             '\u2014 a painted advertisement on a lower Manhattan wall, glass, olives '
             'and every letter of it laid on by hand from a lift. Ephraim filmed this '
             'one portrait, and the page plays it the shape he shot it.',
       credit=None, featured=False),

  dict(slug='louboutin-shun-sudo-new-york',
       title='Christian Louboutin \u00d7 Shun Sudo',
       client='Christian Louboutin \u00d7 Shun Sudo',
       city='New York', state='NY', dim_w=None, dim_h=None, year=None,
       category='brand', hero='louboutin-shun-sudo-new-york-hero',
       video='film-louboutin-shun-sudo', film='film-louboutin-shun-sudo',
       film_eyebrow='with the sound on',
       film_line='A short one, shot portrait: the wall from the street and from the '
                 'air, whole and with its sound.',
       gallery=['louboutin-shun-sudo-new-york-1', 'louboutin-shun-sudo-new-york-2',
                'louboutin-shun-sudo-new-york-3', 'louboutin-shun-sudo-new-york-4'],
       story='Christian Louboutin with the painter Shun Sudo \u2014 crossed legs and '
             'red soles over his blossoms, four storeys up a Manhattan wall, with '
             'christianlouboutin.com along the foot of it. Shun Sudo is in the film, '
             'watching it from the street.',
       credit=None, featured=False),
]

# The Home row and the footer column, in the order PLAN.md §3 names them —
# which is not the Work index order. check_projects() in build.py asserts this
# list and the featured flags above agree, so neither can drift alone.
FEATURED_ORDER = ('gucci-new-york', 'rains-new-york', 'crown-royal-trail-blazers',
                  'john-lewis-rochester', 'uber-san-francisco', 'malcolm-x-rochester',
                  'upendo-los-angeles')

BY_SLUG = {p['slug']: p for p in PROJECTS}


def featured():
    """The walls Home and the footer lead with, in PLAN.md's order.

    Not a count and never phrased as one: the row is a lead-in to the Work
    page, not a statement about how many walls Ephraim has painted.
    """
    return [BY_SLUG[s] for s in FEATURED_ORDER]


def measured():
    """The walls we have the feet for — the only ones any figure may count.

    A wall with no dimensions is not a smaller wall, it is a wall nobody has
    given us a tape measure on. So it is left out of every sum rather than
    counted as zero, and the copy around the sum says what the sum is of.
    """
    return [p for p in PROJECTS if p['dim_w'] is not None]


def total_sq_ft():
    """The measured walls added up, so the scale statement is never typed.

    23,294 square feet as the roster stands. PLAN.md §3 wrote "over 19,000"
    from a rougher count; the number this returns is the one that goes on the
    page — and it is the walls with feet on them, not the whole roster.
    """
    return sum(p['dim_w'] * p['dim_h'] for p in measured())
