#!/bin/bash
# Publish the Mendoza Marketing build to the Green Flash preview host, at a
# fixed unguessable slug, with robots noindex — the link Drew reviews.
#
#   ./publish-preview.sh            → https://preview.greenflashusa.com/p/<SLUG>/
#
# The same shape as /root/openairgallery-src/publish-preview.sh, which mirrors
# what the site-builder bot's publisher.py does: build under the prefix, copy
# into a staging directory, harden it, then rename it into place so the link is
# never half-published. SLUG is fixed so every republish keeps the same link
# alive; it was generated once with secrets.token_urlsafe(16).
set -e
cd "$(dirname "$0")"

SLUG="FpneVVmTCTqRO_sI7peZHg"
ROOT="/srv/sitebuilder/p"
TARGET="$ROOT/$SLUG"
STAGING="$ROOT/.staging-$SLUG"
RETIRING="$ROOT/.retiring-$SLUG"

PREFIX="/p/$SLUG" BASE_URL="https://preview.greenflashusa.com/p/$SLUG" python3 build.py

rm -rf "$STAGING"
mkdir -p "$STAGING/assets"
# site/assets is a pair of symlinks into out/ for the local http.server; the
# real copies follow, so exclude it here rather than following the links.
rsync -a --exclude 'assets/' site/ "$STAGING/"
[ -d out/img ] && rsync -a out/img/ "$STAGING/assets/img/"
[ -d out/video ] && rsync -a out/video/ "$STAGING/assets/video/"
# The preview must never be indexed, whatever build.py wrote.
printf 'User-agent: *\nDisallow: /\n' > "$STAGING/robots.txt"
rm -f "$STAGING/sitemap.xml"
find "$STAGING" -type d -exec chmod 755 {} +
find "$STAGING" -type f -exec chmod 644 {} +

rm -rf "$RETIRING"
[ -e "$TARGET" ] && mv "$TARGET" "$RETIRING"
mv "$STAGING" "$TARGET"
rm -rf "$RETIRING"
echo "Preview: https://preview.greenflashusa.com/p/$SLUG/"
