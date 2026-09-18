# Open Air Gallery at ephraim.greenflashusa.com. Site body: snippets/openair-site.conf.
# Wix keeps serving openairgallery.art; when Ephraim points the real domain
# here, this block becomes a 301 to it (see deploy/go-live.md).
server {
    server_name ephraim.greenflashusa.com;
    include snippets/openair-site.conf;

    listen [::]:443 ssl;
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/ephraim.greenflashusa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ephraim.greenflashusa.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
server {
    listen 80;
    listen [::]:80;
    server_name ephraim.greenflashusa.com;
    return 301 https://$host$request_uri;
}
