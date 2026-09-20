#!/bin/bash
# Publish the Open Air Gallery build to the Green Flash preview host, at a
# fixed unguessable slug, with robots noindex — the link Ephraim reviews.
#
#   ./publish-preview.sh            → https://preview.greenflashusa.com/p/<SLUG>/
#
# Mirrors what the site-builder bot's publisher.py does (copy into a staging
# dir, harden, rename into place) without the bot. SLUG is fixed so republishes
# keep the same link alive; it was generated once with secrets.token_urlsafe(16).
set -e
cd "$(dirname "$0")"

SLUG="oag-9vL2xQm7Kp4RtW8sNfHb"
ROOT="/srv/sitebuilder/p"
TARGET="$ROOT/$SLUG"
STAGING="$ROOT/.staging-$SLUG"
RETIRING="$ROOT/.retiring-$SLUG"

PREFIX="/p/$SLUG" BASE_URL="https://preview.greenflashusa.com/p/$SLUG" python3 build.py

rm -rf "$STAGING"
mkdir -p "$STAGING/assets"
rsync -a --exclude 'assets/' site/ "$STAGING/"
rsync -a out/img/ "$STAGING/assets/img/"
# The films, the same way deploy.sh syncs them. site/assets/video is a symlink
# into out/, and the rsync above excludes assets/ wholesale, so without this
# line a republish would leave the preview with three <video> elements and no
# files behind them - and the publish renames a fresh directory into place, so
# the copies the last publish left there would go with it.
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
