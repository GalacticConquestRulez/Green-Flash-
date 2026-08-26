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

You can also import [`.do/app.yaml`](.do/app.yaml) — replace `YOUR_GITHUB_USER/green-flash-advertising` first.

## Contact form

The form currently saves inquiries in the visitor’s browser (`localStorage`) so the UI works out of the box. To receive real emails, wire the submit handler in `src/components/contact-form.tsx` to Formspree, Basin, a serverless function, or your CRM.

## Stack

- React 19, Vite 8, Tailwind 4
- React Router for `/`, `/privacy`, `/terms`
- Lucide icons, Oswald + Manrope fonts
