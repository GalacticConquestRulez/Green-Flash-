# Green Flash Advertising

Standalone marketing site for Green Flash Advertising (GFA). Vite + React + Tailwind. Static build, served by nginx on a DigitalOcean Droplet.

## Local

```bash
npm install
npm run dev
```

Production build:

```bash
npm run build
```

Output is in `dist/`.

## Publish on a DigitalOcean Droplet (nginx)

This site runs at `/var/www/greenflash` on an existing Droplet that also
hosts other sites, served by nginx. See [`deploy/`](deploy/) for the actual
scripts; short version:

1. **One-time setup** — add greenflashusa.com as an nginx site alongside
   your others (does not touch `ufw` or any other site's config):
   ```bash
   scp deploy/nginx/green-flash-advertising.conf root@YOUR_DROPLET_IP:/tmp/greenflash.conf
   ssh root@YOUR_DROPLET_IP 'bash -s' < deploy/provision.sh
   ```
2. **Point DNS** — `greenflashusa.com` and `www.greenflashusa.com` A records
   at the droplet's IP.
3. **Deploy the build** — from your machine, whenever you want to ship:
   ```bash
   ./deploy/deploy.sh root@YOUR_DROPLET_IP
   ```
   This runs `npm run build` and rsyncs `dist/` into `/var/www/greenflash`.
4. **Enable HTTPS** (once DNS has propagated):
   ```bash
   ssh root@YOUR_DROPLET_IP 'certbot --nginx -d greenflashusa.com -d www.greenflashusa.com'
   ```

`.do/app.yaml` is also in the repo as an alternative if you ever want to
move this to DigitalOcean App Platform instead — it's unused by the
Droplet path above.

## Contact form

Submissions post to Formspree (`src/components/contact-form.tsx`). Manage the form and see incoming leads at [formspree.io](https://formspree.io/forms) — check the spam filter settings there and confirm the notification email if leads aren't arriving. To switch providers, swap `FORMSPREE_ENDPOINT` for your new endpoint.

## Stack

- React 19, Vite 8, Tailwind 4
- React Router for `/`, `/privacy`, `/terms`
- Lucide icons, Oswald + Manrope fonts
