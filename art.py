#!/usr/bin/env python3
"""The drawings: the six service icons, the little quad, the service marks.

Everything here is inline SVG rather than a file. Three reasons, in order:
the icons take their colour from `currentColor`, so one rule in the stylesheet
lights a whole card; they cost no request, which matters on a page that is
already carrying a film; and they are in the same repository as the design, so
a change to the line weight is a diff rather than a re-export.

**The house line.** Every icon is drawn in a 44×44 box — the size the card
actually renders it at, so nothing is scaled and no stroke lands on a half
pixel — with a 1.6px stroke, round caps and round joins, no fill, and the
geometry snapped to whole or half units. Drew's references (EllesmereUI,
Midnight Marketing) both use exactly this register: thin, geometric, one
weight, no decoration. If a seventh service ever arrives, it is drawn to the
same rules or it does not go on the grid.
"""
import html

# The one set of attributes every icon shares. Written once so a later change
# to the weight is a change to this line.
_A = ('xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44" fill="none" '
      'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
      'stroke-linejoin="round" aria-hidden="true"')


def _svg(body, cls='ico-art'):
    return f'<svg class="{cls}" {_A}>{body}</svg>'


# ------------------------------------------------------------- the six icons
# One drawing per service, in content.py's order. Each one says what the
# service *is* in a single object: a browser, a target, a phone, a nib, a
# quad, a funnel. No two of them share a silhouette, which is the only test
# that matters on a grid where all six are seen at once.
ICONS = {

    # Website design — a browser window: the chrome, the dots, three lines of
    # content. The lines are the same three the first card's demo well draws,
    # so the icon and the demo are the same idea at two sizes.
    'websites': (
        '<rect x="5" y="9" width="34" height="27" rx="3.5"/>'
        '<path d="M5 17h34"/>'
        '<circle cx="10" cy="13" r="1.1"/><circle cx="14" cy="13" r="1.1"/>'
        '<circle cx="18" cy="13" r="1.1"/>'
        '<path d="M11 23h13M11 28h20M11 32.5h8"/>'
    ),

    # Meta ads & filming — a target with the arrow already in flight. The
    # campaign is the aim; the arrow is the money going in.
    'meta-ads': (
        '<circle cx="19" cy="25" r="12.5"/><circle cx="19" cy="25" r="7.5"/>'
        '<circle cx="19" cy="25" r="2.4"/>'
        '<path d="M24 20 37.5 6.5"/>'
        '<path d="M30.5 6.5h7v7"/>'
    ),

    # Social media — a phone held upright with a reel playing on it. Portrait,
    # because everything this service makes is 1080×1920.
    'social': (
        '<rect x="12.5" y="4" width="19" height="36" rx="4"/>'
        '<path d="M19 8.5h6"/>'
        '<path d="M19.5 17.5 28 22.5l-8.5 5z"/>'
    ),

    # Logo design — a pen nib. The mark, the slit and the breather hole: the
    # three shapes every nib has, and the only tool on this grid that draws.
    'logo': (
        '<path d="M22 4.5 32.5 29.5 22 39.5 11.5 29.5z"/>'
        '<path d="M22 4.5v20"/>'
        '<circle cx="22" cy="28.5" r="3"/>'
    ),

    # Drone sessions — the quad seen from above: body, four arms, four rotor
    # discs, and the camera under the nose. Same machine as quad() below.
    'drones': (
        '<rect x="16.5" y="18.5" width="11" height="7" rx="2.5"/>'
        '<path d="M17.5 19.2 11.5 12.5M26.5 19.2l6-6.7'
        'M17.5 24.8l-6 6.7M26.5 24.8l6 6.7"/>'
        '<ellipse cx="10" cy="11" rx="5" ry="2"/>'
        '<ellipse cx="34" cy="11" rx="5" ry="2"/>'
        '<ellipse cx="10" cy="33" rx="5" ry="2"/>'
        '<ellipse cx="34" cy="33" rx="5" ry="2"/>'
        '<path d="M22 25.5v3.5"/>'
    ),

    # Lead conversion — a funnel with one lead coming out of the bottom. The
    # service is the last inch of that drawing: the part where a name that
    # went in at the top leaves as a customer.
    'lead-conversion': (
        '<path d="M7.5 8.5h29L25.5 21.5v13L18.5 38.5v-17z"/>'
        '<path d="M28.5 31.5h8"/><path d="M33 28l3.5 3.5L33 35"/>'
    ),
}


def icon(slug):
    """The service's icon, at the size the card draws it.

    KeyError is deliberate: a service with no drawing should stop the build
    rather than leave a hole in the middle of the grid.
    """
    return _svg(ICONS[slug])


# ----------------------------------------------------------- the little quad
def quad(cls='quad'):
    """The quad on its own, wide and small — the mark that flies across the
    drone card's demo well when step 5 gives it a track to fly along.

    It is drawn here, in the server HTML, and parked at the left of the well:
    the no-JS page shows a quad sitting on a strip of sky, which is a picture
    of the service; the script only moves it. A mark that exists only once the
    script runs would leave that well empty in exactly the renders CLAUDE.md
    rule 4 says have to be complete.
    """
    return (f'<svg class="{cls}" xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 46 26" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">'
            f'<rect x="17" y="10" width="12" height="6" rx="2.5"/>'
            f'<path d="M18 10.5 12.5 6M28 10.5 33.5 6'
            f'M18 15.5 12.5 20M28 15.5 33.5 20"/>'
            f'<ellipse cx="10" cy="5" rx="5.5" ry="2"/>'
            f'<ellipse cx="36" cy="5" rx="5.5" ry="2"/>'
            f'<ellipse cx="10" cy="21" rx="5.5" ry="2"/>'
            f'<ellipse cx="36" cy="21" rx="5.5" ry="2"/>'
            f'<path d="M23 16v2.5"/></svg>')


# ------------------------------------------------------- the service marks
# Drew's README: "per-service marks = the Mendoza logo with the text changed".
#
# We cannot do that yet, and this is the honest version of why. What he sent
# is a 2000×2000 JPEG of the finished lockup on black — the mark, MENDOZA
# MARKETING, and CONTENT | WEBSITES | DRONES, all baked into pixels. Swapping
# the third line for "WEBSITE DESIGN" means setting that line in his typeface
# at his tracking and compositing it into his mark, which needs the vector
# file (or at minimum the transparent PNG plus the name of the face). Both are
# on his list of things still owed; CLAUDE.md records it.
#
# So until the vector lands, a service mark is his logo with the service named
# underneath it in the site's own mono — the same information, plainly set,
# rather than a forgery of his artwork in the wrong typeface. When the vector
# arrives this function changes and no page that calls it does.
def _builder():
    """build.py, whichever name it is running under.

    home.py, pages.py and this file are pages of build.py rather than
    libraries it uses: they need u() and img() and build.py needs them, which
    is a cycle if either side imports the other at the top. Resolving it here,
    at call time, out of the modules already loaded, means build.py keeps one
    plain import line and is never executed twice — which is what `from build
    import img` would do to a build.py that is running as __main__.
    """
    import sys
    for name in ('build', '__main__'):
        m = sys.modules.get(name)
        if m is not None and hasattr(m, 'img'):
            return m
    raise RuntimeError('art.py is part of build.py and must be called from it')


def service_mark(slug, name=None, cls='mark'):
    """Drew's mark with the service named under it. See the note above.

    `name` defaults to the service's own name from content.py, so a caller
    that has the row does not have to pass it and a caller that has only the
    slug does not have to look it up.
    """
    b = _builder()
    if name is None:
        from content import BY_SLUG
        name = BY_SLUG[slug]['name']
    return (f'<div class="{cls}" data-mark="{html.escape(slug)}">'
            f'{b.img("logo", "Mendoza Marketing", extra=b.img_dims("logo"))}'
            f'<div class="mark-cap mono">{html.escape(name)}</div></div>')
