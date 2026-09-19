#!/usr/bin/env python3
"""The "Painted for" wall — the brands Ephraim has painted, in their own colours.

CLAUDE.md, round three: *"A logo section, like Colossal's … a 'Painted for' wall
of the brands he has painted … in each brand's actual colours … Source each mark
as the brand's real logo from its press kit or a Wikimedia Commons SVG (record
the source URL in `brands.py`); where none is available yet, a typographic
wordmark set in the brand's own colours. Never trace or redraw a logo by hand."*

So there are exactly two kinds of row in this file and no third:

* ``mark='svg'``  — the brand's own logo, downloaded byte for byte from
  Wikimedia Commons by ``process-brands.sh`` into ``assets/brands/<slug>.svg``
  and copied to ``out/img/brands/``. ``commons``/``source_url``/``download``
  record where it came from and ``licence`` records what Commons says about it.
  Nothing in the file is edited: the mark on the page is the mark Commons holds.

* ``mark='type'`` — no usable free SVG exists, so the cell is set as type, in
  the brand's own colour, with ``colour_note`` saying where that colour comes
  from and how sure we are of it. Four brands are in this state today (Crown
  Royal, Vitamin Water, Monkey 47, Jack Daniel's) and each one is a line in
  CLAUDE.md's "needed from Ephraim" list: the day he sends the brand asset the
  row changes kind and nothing else on the page moves.

Every logo here is Public Domain on Commons — a wordmark below the threshold of
originality — and every one of them is also a **trademark**. They are used the
one way a contractor may use a client's mark: nominatively, to say whose wall he
painted, at one size, unaltered, and not as an endorsement.

Optical height
--------------
A logo is not its bounding box. Gucci's wordmark is all cap height and fills its
box; Corona's is two lines with air around them; Ford's is a containing oval.
Rendering them all at one CSS height would make Gucci look twice the size of
Corona. ``h`` is therefore the rendered height in CSS pixels of *that file's box*
chosen so the marks read at the same optical weight in the grid, tuned by eye
against pages-brands-1440.png. ``hm`` is the same number for a phone.
"""
import os
import re

SRC = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.join(SRC, 'assets', 'brands')

# Everything Commons serves comes from the same host; the path is the file's.
UPLOAD = 'https://upload.wikimedia.org/wikipedia/commons/'
PAGE = 'https://commons.wikimedia.org/wiki/'

# The Commons licence line, once. Every mark below carries it, because every
# one of them is tagged the same way: a wordmark is not copyrightable, and the
# trademark is the owner's and stays the owner's.
PD_TEXTLOGO = ('Public domain on Wikimedia Commons (PD-textlogo: below the '
               'threshold of originality). Trademarked — used nominatively, '
               'to name a client.')


def _b(slug, name, **kw):
    return dict(slug=slug, name=name, **kw)


BRANDS = [
  _b('gucci', 'Gucci', mark='svg', h=24, hm=19,
     commons='File:Gucci Logo.svg',
     source_url=PAGE + 'File:Gucci_Logo.svg',
     download=UPLOAD + '2/2e/Gucci_Logo.svg',
     licence=PD_TEXTLOGO,
     note='The GUCCI wordmark, black, as the house sets it.'),

  _b('crown-royal', 'Crown Royal', mark='type', face='wide', colour='#52247F',
     colour_note='Crown Royal purple, read off the brand’s own bag and '
                 'bottle livery. Approximate until Ephraim sends the brand asset.',
     note='No free SVG on Wikimedia Commons — nothing under "Crown Royal" '
          'but photographs. Typographic wordmark for now.'),

  _b('uber', 'Uber', mark='svg', h=34, hm=26,
     commons='File:Uber logo 2018.svg',
     source_url=PAGE + 'File:Uber_logo_2018.svg',
     download=UPLOAD + '5/58/Uber_logo_2018.svg',
     licence=PD_TEXTLOGO,
     note='The 2018 wordmark, black, which is the mark on the wall Antwuan is '
          'painted on.'),

  _b('victorias-secret', 'Victoria’s Secret', mark='svg', h=44, hm=34,
     commons='File:Victoria\'s Secret.svg',
     source_url=PAGE + 'File:Victoria%27s_Secret.svg',
     download=UPLOAD + 'c/cd/Victoria%27s_Secret.svg',
     licence=PD_TEXTLOGO,
     note='The two-line wordmark in the house pink (#f1396d in the file).'),

  _b('vitamin-water', 'Vitamin Water', mark='type', face='wide', colour='#E0007A',
     colour_note='The vitaminwater magenta from the brand’s packaging. '
                 'Approximate — the mark is flavour-coloured and the master '
                 'brand asset has not been supplied.',
     note='No free SVG on Wikimedia Commons under vitaminwater or glacéau.'),

  _b('sprite', 'Sprite', mark='svg', h=44, hm=32,
     commons='File:Sprite 2022.svg',
     source_url=PAGE + 'File:Sprite_2022.svg',
     download=UPLOAD + 'a/ae/Sprite_2022.svg',
     licence=PD_TEXTLOGO,
     note='The 2022 script in Sprite green (#00a84e in the file).'),

  _b('ford', 'Ford', mark='svg', h=50, hm=38,
     commons='File:Ford logo flat.svg',
     source_url=PAGE + 'File:Ford_logo_flat.svg',
     download=UPLOAD + '3/3e/Ford_logo_flat.svg',
     licence=PD_TEXTLOGO,
     note='The blue oval, flat rather than the gradient rendering — it holds '
          'up at 50px and it is a quarter of the weight.'),

  _b('showtime', 'Showtime', mark='svg', h=40, hm=30,
     commons='File:Showtime.svg',
     source_url=PAGE + 'File:Showtime.svg',
     download=UPLOAD + '2/22/Showtime.svg',
     licence=PD_TEXTLOGO,
     note='The SHO roundel and wordmark in Showtime red (#ff1f2c in the file).'),

  _b('moncler', 'Moncler', mark='svg', h=38, hm=28,
     commons='File:Logo Moncler Group.svg',
     source_url=PAGE + 'File:Logo_Moncler_Group.svg',
     download=UPLOAD + 'f/f7/Logo_Moncler_Group.svg',
     licence=PD_TEXTLOGO,
     note='Commons holds the Moncler Group lockup and not the bare MONCLER '
          'wordmark, so the cell reads MONCLER with GROUP under it. Replace it '
          'the day Ephraim sends the brand asset.'),

  _b('red-bull', 'Red Bull', mark='svg', h=32, hm=24,
     commons='File:Logo of Red bull.svg',
     source_url=PAGE + 'File:Logo_of_Red_bull.svg',
     download=UPLOAD + '9/91/Logo_of_Red_bull.svg',
     licence=PD_TEXTLOGO,
     note='The wordmark in Red Bull red. Commons has no free version of the '
          'two-bulls-and-sun device, which is a drawing and not a wordmark.'),

  _b('monkey-47', 'Monkey 47', mark='type', face='serif', colour='#1A1A1A',
     colour_note='The Schwarzwald label is black on white; the cell is ink.',
     note='Commons holds only a CC BY-SA photograph-derived PNG, which carries '
          'a share-alike obligation we are not going to put on a client site. '
          'Typographic wordmark for now.'),

  _b('johnnie-walker', 'Johnnie Walker', mark='svg', h=17, hm=13,
     commons='File:Johnnie Walker wordmark.svg',
     source_url=PAGE + 'File:Johnnie_Walker_wordmark.svg',
     download=UPLOAD + '4/49/Johnnie_Walker_wordmark.svg',
     licence=PD_TEXTLOGO,
     note='The wordmark, black. The Striding Man is a drawing and is not on '
          'Commons free.'),

  _b('heineken', 'Heineken', mark='svg', h=22, hm=17,
     commons='File:Heineken logo.svg',
     source_url=PAGE + 'File:Heineken_logo.svg',
     download=UPLOAD + '2/24/Heineken_logo.svg',
     licence=PD_TEXTLOGO,
     note='The red star and the green wordmark — both brand colours in the '
          'one file.'),

  _b('jack-daniels', 'Jack Daniel’s', mark='type', face='serif', colour='#111111',
     colour_note='Old No. 7 is black and white; the cell is ink.',
     note='No free SVG on Wikimedia Commons — the Old No. 7 label is a '
          'drawing and everything filed under the name is a photograph.'),

  _b('corona', 'Corona', mark='svg', h=44, hm=34,
     commons='File:Corona Extra text logo.svg',
     source_url=PAGE + 'File:Corona_Extra_text_logo.svg',
     download=UPLOAD + 'b/ba/Corona_Extra_text_logo.svg',
     licence=PD_TEXTLOGO,
     note='The Corona Extra text logo in Corona blue (#005a9c in the file).'),
]

# The order CLAUDE.md lists them in, which is the order on the wall: five
# across, three down. A row added here changes the grid and nothing else.
assert len(BRANDS) == 15, 'the wall is five across and three down'
assert len({b['slug'] for b in BRANDS}) == 15, 'duplicate brand slug'
for _b_ in BRANDS:
    assert _b_['mark'] in ('svg', 'type'), _b_['slug']
    if _b_['mark'] == 'svg':
        assert _b_['download'].startswith(UPLOAD), _b_['slug']
    else:
        assert _b_['face'] in ('tall', 'wide', 'serif'), _b_['slug']


def manifest():
    """`slug<TAB>url` for every downloadable mark — what process-brands.sh reads.

    The URL table lives here and only here: the shell script is a downloader
    with no list in it, so a source can never drift from what the page records.
    """
    return '\n'.join(f"{b['slug']}\t{b['download']}"
                     for b in BRANDS if b['mark'] == 'svg')


_VIEWBOX = re.compile(r'viewBox\s*=\s*"([-\d.eE]+)[,\s]+([-\d.eE]+)[,\s]+'
                      r'([-\d.eE]+)[,\s]+([-\d.eE]+)"')
_WH = re.compile(r'\b(width|height)\s*=\s*"([\d.]+)(?:px)?"')


def intrinsic(slug):
    """(width, height) of a mark's own box, read out of the file.

    An <img> with no width and height is a layout shift waiting to happen, and
    guessing the aspect ratio of somebody else's logo is how a wordmark ends up
    stretched. Both numbers come off the SVG itself: the viewBox where there is
    one, the width/height attributes otherwise.
    """
    path = os.path.join(BRAND_DIR, slug + '.svg')
    assert os.path.exists(path), (
        f'brands: {path} is missing — run ./process-brands.sh')
    with open(path, encoding='utf-8', errors='replace') as f:
        head = f.read(4000)
    m = _VIEWBOX.search(head)
    if m:
        w, h = float(m.group(3)), float(m.group(4))
        if w > 0 and h > 0:
            return w, h
    wh = dict(_WH.findall(head))
    assert 'width' in wh and 'height' in wh, f'brands: {path} has no usable size'
    return float(wh['width']), float(wh['height'])


if __name__ == '__main__':
    print(manifest())
