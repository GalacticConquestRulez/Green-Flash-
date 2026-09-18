#!/bin/bash
# Rebuild the Open Air Gallery site and publish it to /var/www/ephraim
# (ephraim.greenflashusa.com). Same shape as /root/dronegodmax-src/deploy.sh.
set -e
cd "$(dirname "$0")"
BASE_URL="${BASE_URL:-https://ephraim.greenflashusa.com}" python3 build.py

# assets/ is synced separately: --delete over the images would leave the live
# site imageless while it re-copied them.
rsync -a --delete --exclude 'assets/' site/ /var/www/ephraim/
mkdir -p /var/www/ephraim/assets
rsync -a out/img/ /var/www/ephraim/assets/img/
chown -R www-data:www-data /var/www/ephraim
nginx -t && systemctl reload nginx
echo "Deployed (canonical ${BASE_URL:-https://ephraim.greenflashusa.com})"
