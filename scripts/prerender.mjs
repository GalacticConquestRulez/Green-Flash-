/**
 * Bakes each route's markup and metadata into its own static HTML file, so
 * crawlers that don't execute JavaScript (Bing, social scrapers, AI answer
 * engines) see real content instead of an empty <div id="root">.
 *
 * Uses React's own server renderer — no headless browser — to keep the build
 * runnable on a small droplet. React then hydrates the markup on the client.
 */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { schemaFor } from "./schema.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");
const SITE_URL = "https://greenflashusa.com";

const { render, ROUTE_META, PRERENDER_ROUTES, NOT_FOUND_META } = await import(
  join(root, "dist-ssr", "entry-server.js")
);

const template = readFileSync(join(dist, "index.html"), "utf8");

/** Replace an existing tag's attribute value in the HTML template. */
function replaceAttr(html, tagPattern, attr, value) {
  return html.replace(tagPattern, (tag) =>
    tag.replace(new RegExp(`${attr}="[^"]*"`), `${attr}="${escapeAttr(value)}"`),
  );
}

function escapeAttr(s) {
  return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * Each entry renders `route` and writes to `out`. The 404 entry renders an
 * unmatched URL so its markup matches what the client router produces for any
 * unknown path — otherwise React would throw a hydration mismatch.
 */
const targets = [
  ...PRERENDER_ROUTES.map((route) => ({ route, meta: ROUTE_META[route], out: route })),
  { route: "/__not_found__", meta: NOT_FOUND_META, out: "404" },
];

for (const { route, meta, out } of targets) {
  const url = `${SITE_URL}${meta.path === "/" ? "/" : meta.path}`;

  const appHtml = render(route);

  let html = template;
  if (meta.noindex) {
    html = replaceAttr(html, /<meta\s+name="robots"[^>]*>/, "content", "noindex, follow");
    // Drop the canonical entirely rather than let it point elsewhere: a
    // noindex page canonicalising to a different URL is a contradictory
    // signal, and Google may honour the canonical over the noindex.
    html = html.replace(/\s*<link\s+rel="canonical"[^>]*>/, "");
  }
  html = html.replace(/<title>[\s\S]*?<\/title>/, `<title>${escapeHtml(meta.title)}</title>`);
  html = replaceAttr(html, /<meta\s+name="description"[^>]*>/, "content", meta.description);
  html = replaceAttr(html, /<meta\s+property="og:title"[^>]*>/, "content", meta.title);
  html = replaceAttr(html, /<meta\s+property="og:description"[^>]*>/, "content", meta.description);
  html = replaceAttr(html, /<meta\s+property="og:url"[^>]*>/, "content", url);
  html = replaceAttr(html, /<meta\s+name="twitter:title"[^>]*>/, "content", meta.title);
  html = replaceAttr(html, /<meta\s+name="twitter:description"[^>]*>/, "content", meta.description);
  html = replaceAttr(html, /<link\s+rel="canonical"[^>]*>/, "href", url);
  // Page-level JSON-LD (WebPage, breadcrumbs, this page's Service/Offer) rides
  // alongside the template's shared Organization graph. The 404 gets none — a
  // noindex page has no business describing itself to crawlers.
  if (!meta.noindex) {
    const ld = JSON.stringify(schemaFor(meta));
    html = html.replace("</head>", `    <script type="application/ld+json">${ld}</script>\n  </head>`);
  }
  html = html.replace('<div id="root"></div>', `<div id="root">${appHtml}</div>`);

  // "/" -> dist/index.html, "/privacy" -> dist/privacy/index.html, "404" -> dist/404.html
  const outPath =
    out === "/"
      ? join(dist, "index.html")
      : out === "404"
        ? join(dist, "404.html")
        : join(dist, out.slice(1), "index.html");
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, html);
  console.log(`prerendered ${out} -> ${outPath.replace(dist, "dist")} (${(html.length / 1024).toFixed(1)}KB)`);
}

// Generate the sitemap from the same route list, so it can't drift from what
// actually got prerendered or go stale on lastmod.
const PRIORITY = { "/": "1.0", "/advertising": "0.9", "/merch": "0.9", "/websites": "0.9" };
const CHANGEFREQ = { "/": "weekly", "/advertising": "weekly", "/merch": "monthly", "/websites": "monthly" };
const today = new Date().toISOString().slice(0, 10);

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${PRERENDER_ROUTES.map(
  (route) => `  <url>
    <loc>${SITE_URL}${route === "/" ? "/" : route}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${CHANGEFREQ[route] ?? "yearly"}</changefreq>
    <priority>${PRIORITY[route] ?? "0.3"}</priority>
  </url>`,
).join("\n")}
</urlset>
`;
writeFileSync(join(dist, "sitemap.xml"), sitemap);
console.log(`generated sitemap.xml (${PRERENDER_ROUTES.length} urls, lastmod ${today})`);

// llms.txt: the emerging convention AI crawlers read for a site orientation.
// Built from the same ROUTE_META, so page list and descriptions stay in sync.
const llms = `# Green Flash USA (Green Flash Advertising)

> One team for the whole growth stack: AI-powered Google & Meta ads management
> ($375/month), custom branded merch (from a $199 one-time setup), and
> mobile-first websites (landing pages $375, full sites from $975, optional
> $125/month care plan). Online-only, serving businesses across the United
> States. No long-term contracts. Founded by Max Glaser and Tanner Lodini
> (Wright). Contact: greenflashusa@gmail.com

## Pages

${PRERENDER_ROUTES.map((r) => `- [${ROUTE_META[r].title}](${SITE_URL}${r === "/" ? "/" : r}): ${ROUTE_META[r].description}`).join("\n")}

## Related

- [Links hub](https://links.greenflashusa.com): client merch stores, campaign videos, and booking links.
`;
writeFileSync(join(dist, "llms.txt"), llms);
console.log("generated llms.txt");
