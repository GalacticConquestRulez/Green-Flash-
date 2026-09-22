#!/usr/bin/env python3
"""Drew's client dashboards, as data.

The site redraws these dashboards in his own UI and in his own colours — it
never shows the screenshots. So every figure the pages print lives here, once,
with the screenshot it was read off named beside it. A number typed into a page
body is a bug (CLAUDE.md rule 6 says it for prices; the same goes for these,
and for the same reason: the day Drew sends a newer dashboard, one file
changes).

The six screenshots are in his drop of 2026-09-22, under
`incoming/Drew's stretched hole/_client dashboards/client dashboards/`, and are
built to `out/img/dash-1..6.webp` by process.sh as *reference renditions* —
they are on disk so a figure below can be checked against a picture instead of
against a memory, and nothing on the site links to them.

    dash-1  IMG_5024.jpeg     Analytics, 28 days (one client page)
    dash-2  IMG_7436.PNG      Kelly's Country Store, 28 days
    dash-3  IMG_8145.PNG      Instagram Insights, all content, 90 days
    dash-4  IMG_8146.PNG      Views by content type
    dash-5  Screenshot_220.png  Leads Center performance
    dash-6  Screenshot_221.png  Daily new leads, the chart

CLAUDE.md rule 8 applies to every sentence written around these: they are the
pages Drew happens to have sent us a screenshot of, not the size of his
business. Label them "one client page", never "our clients".
"""

# --------------------------------------------------------------- the sources
# Where each figure was read. `file` is relative to the drop folder named in
# the docstring; `slug` is the rendition process.sh builds from it.
SOURCES = {
    'dash-1': dict(slug='dash-1', file='IMG_5024.jpeg',
                   what='Analytics, 28 days, one client page'),
    'dash-2': dict(slug='dash-2', file='IMG_7436.PNG',
                   what="Kelly's Country Store page, 28 days"),
    'dash-3': dict(slug='dash-3', file='IMG_8145.PNG',
                   what='Instagram Insights, all content, 90 days'),
    'dash-4': dict(slug='dash-4', file='IMG_8146.PNG',
                   what='Views by content type'),
    'dash-5': dict(slug='dash-5', file='Screenshot_220.png',
                   what='Leads Center performance'),
    'dash-6': dict(slug='dash-6', file='Screenshot_221.png',
                   what='Daily new leads, Jun 23 onward'),
}


def fig(key, source, label, value, delta=None, note=None,
        count=None, prefix='', suffix='', decimals=0):
    """One printed figure.

    `value` is the string the page renders and is the only thing a visitor
    sees. `count`/`prefix`/`suffix`/`decimals` are for step 5's count-up: they
    describe how to get back to `value` by arithmetic, so the animation can
    never land on a number the server HTML does not already say.
    """
    return dict(key=key, source=source, label=label, value=value, delta=delta,
                note=note, count=count, prefix=prefix, suffix=suffix,
                decimals=decimals)


# ------------------------------------------------------- every figure we hold
# dash-1 — Analytics, 28 days. One client page, and the page is not named on
# the screenshot, so the site does not name it either.
DASH1 = [
    fig('d1-views', 'dash-1', 'Views · 28 days', '344,880', '↑ 11×',
        'one client page', count=344880),
    fig('d1-earnings', 'dash-1', 'Earnings · 28 days', '$42.15', '↑ 802%',
        'approximate, same page', count=42.15, prefix='$', decimals=2),
    fig('d1-engagement', 'dash-1', 'Engagement · 28 days', '14,164', '↑ 646%',
        'same page', count=14164),
    fig('d1-followers', 'dash-1', 'Net followers · 28 days', '511', '↑ 30×',
        'same page', count=511),
]

# dash-2 — Kelly's Country Store, 28 days. The one client the screenshot names
# itself, and the client whose reels are on the Home page.
DASH2 = [
    fig('d2-views', 'dash-2', 'Views · 28 days', '413,311', '↑ 211%',
        "Kelly's Country Store", count=413311),
    fig('d2-earnings', 'dash-2', 'Earnings · 28 days', '$104.56', '↑ 621%',
        "Kelly's Country Store", count=104.56, prefix='$', decimals=2),
    # NOTE the engagement rise here is 61%, not dash-1's 646%. Two different
    # pages; the numbers are not interchangeable.
    fig('d2-engagement', 'dash-2', 'Engagement · 28 days', '20,983', '↑ 61%',
        "Kelly's Country Store", count=20983),
    fig('d2-followers', 'dash-2', 'Net followers · 28 days', '1,380', '↑ 190%',
        "Kelly's Country Store", count=1380),
]

# dash-3 — Instagram Insights, all content, 90 days.
#
# The third tile is CUT OFF by the edge of the screenshot: it reads
# "Interact…  22,8…". So 22.8K is a partial reading, not a figure we have —
# it is carried here for the record, marked partial, and it is not to be
# printed as a headline number anywhere. Only a fresh screenshot from Drew
# promotes it.
DASH3 = [
    fig('d3-views', 'dash-3', 'Views · 90 days', '569,027', '+904 followers',
        '87.6% new audience', count=569027),
    fig('d3-followers', 'dash-3', 'Net followers · 90 days', '+904', None,
        'same period', count=904, prefix='+'),
    dict(fig('d3-interactions', 'dash-3', 'Interactions · 90 days', '22.8K',
             None, 'same period', count=22.8, suffix='K', decimals=1),
         partial=True),      # cropped — see the note above; never a headline
    fig('d3-split', 'dash-3', 'Reached · 90 days', '87.6%', None,
        'non-followers · 12.4% followers', count=87.6, suffix='%', decimals=1),
]

# dash-5 — Leads Center. The Meta leads the ad campaigns brought in, which is
# the number the lead-conversion service is about.
DASH5 = [
    fig('d5-leads', 'dash-5', 'Leads Center', '614', '↑ 27.4%',
        'intake leads', count=614),
]

# dash-4 — views by content type. A bar row rather than four tiles: the shape
# (reels dwarf everything else) is the point, and it is the argument for the
# social-media service.
CONTENT_TYPES = dict(
    source='dash-4',
    label='Views by content type',
    total=fig('d4-viewers', 'dash-4', 'Viewers', '226,373', None, None,
              count=226373),
    rows=[
        # (label, the string printed, the number the bar is drawn from)
        ('Reels',   '365K',  365000),
        ('Stories', '32K',    32000),
        ('Posts',   '1.7K',    1700),
        ('Live',    '0',          0),
    ],
)


def bar_pct(value, rows=None):
    """A bar's width, as a percentage of the biggest bar in its row set.

    Drawn from the numbers rather than typed, so the shape cannot drift from
    the figures beside it. Meta's own screenshot scales the same way.
    """
    rows = rows or CONTENT_TYPES['rows']
    top = max(v for _, _, v in rows) or 1
    return round(value / top * 100, 1)


# dash-6 — the daily-new-leads chart, Jun 23 onward, 90 points.
#
# HOW THIS SERIES WAS MADE, because it matters: the screenshot is a picture of
# a line, not a table, so the line was read back off the pixels — the axis
# gridlines (0 and 40) give the vertical scale, the five date labels give the
# horizontal one, and the value at each of the 90 day positions was taken from
# the centre of the stroke, with the peaks and troughs read off the stroke's
# outer edge. Every value lands within 0.15 of a whole lead, the maximum comes
# back as 37 and the minimum as 8, which is what the chart shows. Call it
# ±1 lead: it is Drew's shape and Drew's peaks, not a drawing of a trend.
#
# The last date label on his chart is Sep 11; the line runs nine days past it,
# so the series is Jun 23 → Sep 20 — ninety days, the same window as dash-3.
#
# The total of this series is NOT dash-5's 614: the Leads Center counts intake
# leads and this chart counts every new lead. Two figures, two labels, never
# added together.
LEADS = dict(
    source='dash-6',
    label='Daily new leads',
    range='Jun 23 – Sep 20',
    series=[19, 12, 11, 16, 13, 15, 20, 28, 10, 15,
            21, 16, 25, 23, 23, 16, 23, 21, 23, 18,
            22, 22, 14, 22, 20, 22, 27, 26, 22, 21,
            15, 23, 19, 21, 28, 23, 11, 18, 25, 23,
            27, 19, 15, 24, 17, 16, 10, 14, 14, 18,
            13, 16, 16, 18, 14, 16, 14,  9, 11, 17,
            15, 21, 16,  8, 13, 21, 19, 31, 24, 20,
            16, 29, 19, 19, 18, 20, 28, 13, 31, 25,
            24, 20, 22, 30, 25, 26, 23, 13, 23, 37],
)


def leads_points(w=300.0, h=100.0, pad=6.0, series=None):
    """The chart's polyline, in a 0 0 w h viewBox.

    The baseline is zero leads, not the smallest day: a chart whose floor is
    the minimum exaggerates its own slope, and this one does not need the
    help. `pad` keeps the 37-lead spike and the 2px stroke inside the box.
    """
    s = series or LEADS['series']
    top = max(s) or 1
    step = w / (len(s) - 1)
    return [(round(i * step, 2), round(h - pad - (v / top) * (h - pad), 2))
            for i, v in enumerate(s)]


# The four tiles the Home page shows, in the mockup's order: the reach, the
# money, the ninety-day view, the leads. The other figures above are for
# /results, which shows all six dashboards in full.
HOME_STATS = [DASH1[0], DASH1[1], DASH3[0], DASH5[0]]

# Every figure this file knows, for the build's own sake: the verification
# script asserts each string below appears in the page that prints it, so a
# figure can never drift between this file and the HTML.
ALL = DASH1 + DASH2 + DASH3 + DASH5 + [CONTENT_TYPES['total']]

for _f in ALL:
    assert _f['source'] in SOURCES, f'{_f["key"]}: unknown source {_f["source"]}'
for _f in HOME_STATS:
    assert not _f.get('partial'), (
        f'{_f["key"]} was read off a cropped screenshot and cannot be a '
        f'headline tile — see the dash-3 note')
assert LEADS['source'] in SOURCES and CONTENT_TYPES['source'] in SOURCES
assert len(LEADS['series']) == 90, 'the leads chart is ninety days'
