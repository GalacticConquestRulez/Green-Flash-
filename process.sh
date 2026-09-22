#!/bin/bash
# Mendoza Marketing image pipeline - after /root/openairgallery-src/process.sh,
# which is after /root/dronegodmax-src/process.sh.
#
# Every assets/<slug>.{jpg,jpeg,png} becomes three WebP renditions:
#
#   out/img/<slug>.webp        <=1600w  q82   the full-size image
#   out/img/<slug>-800.webp    <= 800w  q80   srcset small / mobile
#   out/img/t/<slug>.webp      <= 640w  q76   thumbnails, cards, the logo strip
#
# Aspect ratio is preserved and nothing is ever upscaled: min(N,iw) means the
# 212px-wide dashboard crop stays 212px in the "1600" slot. Re-runs are cheap -
# a rendition is only rebuilt when it is older than its source, so dropping one
# new file into assets/ reprocesses that file alone.
#
# assets/ is gitignored and only the TOP level of it is a source directory;
# assets/source/ holds the films make-clips.sh works from and is skipped here.
# The filenames are the contract with build.py - it asks for out/img/<slug>.webp
# by these slugs and nothing else. assets/_sources.json maps each slug back to
# the original file inside incoming/ so a replacement can be dropped in by hand.
#
# The slugs, and what each one is (all from the owner's drop, 2026-09-22):
#
#   logo                      the Mendoza mark + wordmark on black, 2000x2000.
#                             The transparent PNG and the vector are still owed;
#                             when they arrive they replace assets/logo.png and
#                             nothing else changes.
#   logo-mockup               the same mark on an office wall, 2722x1646.
#   client-buffalo-holistic   Buffalo Holistic Center - navy bison roundel on
#   client-zen-zone           Zen Zone Property Maintenance LLC - gold on navy
#   client-britt-fitness      Britt Fitness, LLC - black and white dumbbells
#   client-adams-detailing    Adam's Detailing & Coatings - red/white on black
#                             (the four client logos, identified by eye; the
#                             source filenames are camera-roll noise)
#   isle-de-grande            the Isle de Grande lighthouse logo Drew designed,
#                             7337x7473 with a TRANSPARENT background - the
#                             alpha survives into the WebP, so the page must put
#                             it on a light card, not on #050A0A.
#   isle-de-grande-profile    the same logo as delivered for Facebook, 1251x1251
#                             (a CMYK JPEG; ffmpeg reads it correctly).
#   drew-headshot             Drew in a navy suit, studio, 1170x1535
#   drew-suit                 Drew in a suit in autumn leaves, 749x1280
#   drew-detailing            Drew filming at a detailing shop, 789x1280
#   drew-mt-bank              Drew outside M&T Bank, black and white, 750x750
#   dash-1 .. dash-6          the six client dashboards, REFERENCE ONLY: the
#                             site redraws these figures in its own UI from
#                             results.py and never shows the screenshots. They
#                             are processed so the numbers can be checked
#                             against a rendition instead of the drop, and the
#                             thumbnails are the only size that matters.
#                               dash-1  Analytics 28d: 344,880 views (11x),
#                                       $42.15 (802%), 14,164 engagement (646%),
#                                       511 net followers (30x)
#                               dash-2  Kelly's Country Store: 413,311 views
#                                       (211%), $104.56 (621%), 20,983
#                                       engagement (61%), 1,380 followers (190%)
#                               dash-3  IG Insights 90d: 569,027 views, +904
#                                       followers, 22.8K interactions,
#                                       12.4% followers / 87.6% non-followers
#                               dash-4  Views by content type: 226,373 viewers;
#                                       Reels 365K, Stories 32K, Posts 1.7K,
#                                       Live 0
#                               dash-5  Leads Center: 614 intake leads (27.4%)
#                               dash-6  daily new leads, Jun 23 - Sep 11
#
# The films are not built here - see make-clips.sh.

set -uo pipefail
shopt -s nullglob

cd "$(dirname "$(readlink -f "$0")")" || exit 1
A=assets
O=out/img

command -v ffmpeg >/dev/null || { echo "process.sh: ffmpeg not found" >&2; exit 1; }
[ -d "$A" ] || { echo "process.sh: no $A/ - see assets/_sources.json" >&2; exit 1; }

mkdir -p "$O/t"

# assets/Drew Headshot.JPG -> drew-headshot. A no-op on the names already in
# assets/; forgiving if a replacement arrives less tidy.
slug() {
  basename "$1" | sed -E 's/\.[^.]+$//' \
    | tr 'A-Z' 'a-z' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g'
}

# render <src> <dest> <max-width> <quality>; skips when dest is newer than src
render() {
  local src=$1 dest=$2 w=$3 q=$4
  if [ -f "$dest" ] && [ "$dest" -nt "$src" ]; then
    return 0
  fi
  nice -n 15 ffmpeg -v error -y -i "$src" \
    -vf "scale='min($w,iw)':-2" \
    -c:v libwebp -quality "$q" -compression_level 6 \
    "$dest" || { echo "process.sh: FAILED $dest" >&2; return 1; }
  built=$((built + 1))
}

declare -A seen=()
built=0
sources=0
fail=0

for f in "$A"/*.jpg "$A"/*.jpeg "$A"/*.png; do
  s=$(slug "$f")
  if [ -n "${seen[$s]:-}" ]; then
    echo "process.sh: WARNING '$s' already built from ${seen[$s]}; skipping $f" >&2
    continue
  fi
  seen[$s]=$f
  sources=$((sources + 1))

  render "$f" "$O/$s.webp"      1600 82 || fail=$((fail + 1))
  render "$f" "$O/$s-800.webp"   800 80 || fail=$((fail + 1))
  render "$f" "$O/t/$s.webp"     640 76 || fail=$((fail + 1))
done

echo "process.sh: $sources sources, $built renditions written, $fail failed"
[ "$fail" -eq 0 ] || exit 1
echo IMAGES DONE
