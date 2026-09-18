#!/bin/bash
# Open Air Gallery image pipeline - after /root/dronegodmax-src/process.sh.
#
# Every assets/<name>.{jpg,jpeg,png} becomes four WebP renditions:
#
#   out/img/<name>.webp        <=2400w  q84   the full-bleed photo
#   out/img/<name>-1600.webp   <=1600w  q82   srcset middle
#   out/img/<name>-800.webp    <= 800w  q80   srcset small / mobile
#   out/img/t/<name>.webp      <= 640w  q76   thumbnails and cards
#
# Aspect ratio is preserved and nothing is ever upscaled: min(N,iw) means a
# 1242px original stays 1242px in the "2400" slot. Re-runs are cheap - a
# rendition is only rebuilt when it is older than its source, so dropping one
# new photo into assets/ reprocesses that photo alone.
#
# The filenames are the contract with build.py. When Ephraim's originals
# arrive they go into assets/ under these same names and nothing else changes.
# See docs/images.md.

set -uo pipefail
shopt -s nullglob

cd "$(dirname "$(readlink -f "$0")")" || exit 1
A=assets
O=out/img

command -v ffmpeg >/dev/null || { echo "process.sh: ffmpeg not found" >&2; exit 1; }
[ -d "$A" ] || { echo "process.sh: no $A/ - run fetch-wix.py first" >&2; exit 1; }

mkdir -p "$O/t"

# assets/Gucci New York Hero.JPG -> gucci-new-york-hero. A no-op on the names
# fetch-wix.py writes; forgiving if a client folder arrives less tidy.
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
  ffmpeg -v error -y -i "$src" \
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

  render "$f" "$O/$s.webp"       2400 84 || fail=$((fail + 1))
  render "$f" "$O/$s-1600.webp"  1600 82 || fail=$((fail + 1))
  render "$f" "$O/$s-800.webp"    800 80 || fail=$((fail + 1))
  render "$f" "$O/t/$s.webp"      640 76 || fail=$((fail + 1))
done

echo "process.sh: $sources sources, $built renditions written, $fail failed"
[ "$fail" -eq 0 ] || exit 1
echo IMAGES DONE
