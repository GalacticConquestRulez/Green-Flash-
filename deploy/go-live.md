# Going live on the subdomain

Run once, in order, after the owner's and Ephraim's review of the preview:

    gd-dns add ephraim --ip 142.93.198.162
    dig +short ephraim.greenflashusa.com @1.1.1.1        # until it answers
    certbot certonly --nginx -d ephraim.greenflashusa.com
    mkdir -p /var/www/ephraim && chown www-data:www-data /var/www/ephraim
    cp deploy/nginx/openair-site.conf /etc/nginx/snippets/openair-site.conf
    cp deploy/nginx/ephraim.greenflashusa.com /etc/nginx/sites-available/
    ln -s /etc/nginx/sites-available/ephraim.greenflashusa.com /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    ./deploy.sh

Nothing here touches Wix or openairgallery.art. The real domain moves later,
by Ephraim, at Wix: an A record to 142.93.198.162 and a www CNAME, then
`certbot certonly --nginx -d openairgallery.art -d www.openairgallery.art`,
a server block for the real names including the same snippet, a redeploy
with `BASE_URL=https://openairgallery.art`, and the subdomain block above
becomes a path-preserving 301 the way max.greenflashusa.com did.
