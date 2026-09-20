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
]

# The Home row and the footer column, in the order PLAN.md §3 names them —
# which is not the Work index order. check_projects() in build.py asserts this
# list and the featured flags above agree, so neither can drift alone.
FEATURED_ORDER = ('gucci-new-york', 'crown-royal-trail-blazers', 'john-lewis-rochester',
                  'uber-san-francisco', 'malcolm-x-rochester', 'upendo-los-angeles')

BY_SLUG = {p['slug']: p for p in PROJECTS}


def featured():
    """The six walls Home and the footer lead with, in PLAN.md's order."""
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
