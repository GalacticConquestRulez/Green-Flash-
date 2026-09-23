#!/bin/bash
# Rebuild the Mendoza Marketing site and publish it to /var/www/drew
# (drew.greenflashusa.com). Same shape as /root/openairgallery-src/deploy.sh.
#
# Not run until the owner says go: the subdomain, the DNS record and the
# certificate are step 9 of the plan.
set -e
cd "$(dirname "$0")"
BASE_URL="${BASE_URL:-https://mendozamarketing.com}" python3 build.py

# assets/ is synced separately: --delete over the images and films would leave
# the live site empty while it re-copied them.
rsync -a --delete --exclude 'assets/' site/ /var/www/drew/
mkdir -p /var/www/drew/assets
[ -d out/img ] && rsync -a out/img/ /var/www/drew/assets/img/
[ -d out/video ] && rsync -a out/video/ /var/www/drew/assets/video/
chown -R www-data:www-data /var/www/drew
nginx -t && systemctl reload nginx
echo "Deployed (canonical ${BASE_URL:-https://mendozamarketing.com})"
