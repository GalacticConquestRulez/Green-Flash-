#!/usr/bin/env bash
# Deploy links.greenflashusa.com. Safe to re-run.
#
# Run from the repo root on the droplet:  sudo bash deploy/deploy-links.sh
#
# The nginx conf is installed only the first time. After certbot runs it
# rewrites that file in place to add the SSL block, so overwriting it on a
# later deploy would silently delete HTTPS — hence the "already installed,
# leaving it alone" branch below.
set -euo pipefail

ROOT=/var/www/gfa-links
AVAIL=/etc/nginx/sites-available/links.greenflashusa.com
ENABLED=/etc/nginx/sites-enabled/links.greenflashusa.com
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/links"

[ -f "$SRC/index.html" ] || { echo "error: $SRC/index.html not found — run this from the repo"; exit 1; }

echo "==> syncing files to $ROOT"
mkdir -p "$ROOT"
cp "$SRC/index.html" "$SRC"/*.jpg "$SRC"/*.png "$SRC"/*.mp4 "$ROOT/"
chown -R www-data:www-data "$ROOT"
find "$ROOT" -type f -exec chmod 644 {} +

if [ -f "$AVAIL" ]; then
  echo "==> $AVAIL already installed, leaving it alone (certbot may own it now)"
else
  echo "==> installing nginx conf"
  cp "$(dirname "$SRC")/deploy/nginx/links.greenflashusa.com.conf" "$AVAIL"
  ln -sfn "$AVAIL" "$ENABLED"
fi

echo "==> testing nginx config"
nginx -t

echo "==> reloading nginx"
systemctl reload nginx

echo
echo "Done. Files in $ROOT:"
ls -la "$ROOT"
echo
echo "If this was the first run, get the certificate next:"
echo "  certbot --nginx -d links.greenflashusa.com"
