#!/usr/bin/env bash
# One-time setup for a fresh Ubuntu DigitalOcean Droplet.
# Run as root (or with sudo) on the droplet itself:
#   scp -r deploy root@DROPLET_IP:/root/deploy
#   ssh root@DROPLET_IP 'bash /root/deploy/provision.sh yourdomain.com'
set -euo pipefail

DOMAIN="${1:?Usage: provision.sh yourdomain.com}"
APP_NAME="green-flash-advertising"
WEB_ROOT="/var/www/${APP_NAME}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

apt-get update
apt-get install -y nginx certbot python3-certbot-nginx ufw

mkdir -p "${WEB_ROOT}"
chown -R www-data:www-data "${WEB_ROOT}"

cp "${SCRIPT_DIR}/nginx/${APP_NAME}.conf" "/etc/nginx/sites-available/${APP_NAME}"
sed -i "s/greenflashads\.com/${DOMAIN}/g" "/etc/nginx/sites-available/${APP_NAME}"
ln -sf "/etc/nginx/sites-available/${APP_NAME}" "/etc/nginx/sites-enabled/${APP_NAME}"
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl enable nginx
systemctl reload nginx

ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

cat <<EOF

Nginx is configured for ${DOMAIN} and ${WEB_ROOT} is ready.

Next steps:
1. Point ${DOMAIN} (and www.${DOMAIN}) DNS A records at this droplet's IP.
2. Deploy the site from your machine:
     ./deploy/deploy.sh root@$(curl -s ifconfig.me || echo DROPLET_IP)
3. Once DNS has propagated, enable HTTPS:
     certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}
EOF
