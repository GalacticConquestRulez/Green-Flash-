#!/usr/bin/env bash
# One-time setup to add greenflashusa.com as a new nginx site on your
# existing multi-site Droplet. Safe to run alongside your other sites —
# it does not touch ufw or any other site's config.
#
# Run on the droplet itself (as root or with sudo):
#   scp deploy/nginx/green-flash-advertising.conf root@DROPLET_IP:/tmp/greenflash.conf
#   ssh root@DROPLET_IP 'bash -s' < deploy/provision.sh
set -euo pipefail

DOMAIN="greenflashusa.com"
SITE_NAME="greenflash"
WEB_ROOT="/var/www/greenflash"
CONF_SRC="/tmp/greenflash.conf"

command -v nginx >/dev/null || { apt-get update && apt-get install -y nginx; }
command -v certbot >/dev/null || apt-get install -y certbot python3-certbot-nginx

mkdir -p "${WEB_ROOT}"
chown -R www-data:www-data "${WEB_ROOT}"

cp "${CONF_SRC}" "/etc/nginx/sites-available/${SITE_NAME}"
ln -sf "/etc/nginx/sites-available/${SITE_NAME}" "/etc/nginx/sites-enabled/${SITE_NAME}"

nginx -t
systemctl reload nginx

cat <<EOF

nginx is now serving ${DOMAIN} from ${WEB_ROOT}.

Next steps:
1. Point ${DOMAIN} (and www.${DOMAIN}) DNS A records at this droplet's IP,
   if you haven't already.
2. Deploy the built site into ${WEB_ROOT} (see deploy/deploy.sh).
3. Once DNS has propagated, enable HTTPS:
     certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}
EOF
