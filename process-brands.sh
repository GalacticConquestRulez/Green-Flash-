#!/bin/bash
# The "Painted for" wall's logos - the download half of process.sh.
#
# Every mark on the wall is the brand's own logo, fetched byte for byte from
# Wikimedia Commons; not one of them is traced or redrawn (CLAUDE.md, round
# three). The list of what to fetch and where from lives in brands.py and
# nowhere else - this script asks for it:
#
#     assets/brands/<slug>.svg     the download, untouched
#     out/img/brands/<slug>.svg    the copy the site serves, at
#                                  /assets/img/brands/<slug>.svg
#
# assets/ and out/ are both gitignored, the way every other image on this site
# is, so this script plus brands.py IS the record: re-running it on a clean
# clone rebuilds the wall exactly. A file already on disk is left alone, so
# re-runs are free and a mark Ephraim supplies by hand is never overwritten by
# Commons - delete it to go back to the download.
#
# Commons asks for a User-Agent that identifies the client and a way to reach
# whoever is running it. That is the -A below; it is not a disguise.

set -uo pipefail
cd "$(dirname "$(readlink -f "$0")")" || exit 1

UA='OpenAirGallerySiteBuild/1.0 (https://ephraim.greenflashusa.com; hello@openairgallery.art)'
A=assets/brands
O=out/img/brands

mkdir -p "$A" "$O"

got=0; had=0; fail=0
while IFS=$'\t' read -r slug url; do
  [ -n "$slug" ] || continue
  dest="$A/$slug.svg"
  if [ -s "$dest" ]; then
    had=$((had + 1))
  else
    if curl -fsSL --retry 2 -A "$UA" -o "$dest.part" "$url" && [ -s "$dest.part" ]; then
      # A Commons error page is HTML, not SVG, and would fail silently as a
      # broken image on the wall. Check before it is allowed to become one.
      if head -c 400 "$dest.part" | grep -qi '<svg'; then
        mv "$dest.part" "$dest"; got=$((got + 1))
      else
        echo "process-brands.sh: $slug: not an SVG at $url" >&2
        rm -f "$dest.part"; fail=$((fail + 1)); continue
      fi
    else
      echo "process-brands.sh: $slug: download failed - $url" >&2
      rm -f "$dest.part"; fail=$((fail + 1)); continue
    fi
  fi
  cp -p "$dest" "$O/$slug.svg"
done < <(python3 brands.py)

echo "process-brands.sh: $got downloaded, $had already on disk, $fail failed"
[ "$fail" -eq 0 ] || exit 1
echo BRANDS DONE
