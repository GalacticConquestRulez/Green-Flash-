# Green Flash Advertising

Standalone marketing site for Green Flash Advertising (GFA). Vite + React + Tailwind. Static build — ready for DigitalOcean App Platform.

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

## Publish on DigitalOcean App Platform

1. Create a GitHub repo and push this folder (the files next to this README, not a nested extra folder).
2. In DigitalOcean: **Create → App Platform → GitHub**, pick the repo.
3. Choose **Static Site**.
   - Build command: `npm ci && npm run build`
   - Output directory: `dist`
   - Catch-all / index: `index.html`
   - Node version: **22**
4. Deploy. Then **Settings → Domains** and add `greenflashads.com` (or whatever you own). Point the domain’s DNS to DigitalOcean as they show you.

You can also import [`.do/app.yaml`](.do/app.yaml) directly.

## Contact form

Submissions post to Formspree (`src/components/contact-form.tsx`). Manage the form and see incoming leads at [formspree.io](https://formspree.io/forms) — check the spam filter settings there and confirm the notification email if leads aren't arriving. To switch providers, swap `FORMSPREE_ENDPOINT` for your new endpoint.

## Stack

- React 19, Vite 8, Tailwind 4
- React Router for `/`, `/privacy`, `/terms`
- Lucide icons, Oswald + Manrope fonts
