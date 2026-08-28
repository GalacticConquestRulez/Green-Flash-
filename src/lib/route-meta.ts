export type RouteMeta = {
  title: string;
  description: string;
  path: string;
  noindex?: boolean;
};

const DESCRIPTION =
  "Affordable AI-powered Google and Meta ads for small businesses. Business Growth Package $375/month, no long-term contract. You provide the content — we run the ads.";

/**
 * Single source of truth for per-page metadata. Consumed at runtime by
 * usePageMeta and at build time by scripts/prerender.mjs, so the static HTML
 * and the client stay in sync.
 */
export const ROUTE_META = {
  "/": {
    title: "Green Flash Advertising | Affordable Google & Meta Ads for Local Businesses",
    description: DESCRIPTION,
    path: "/",
  },
  "/merch": {
    title: "Custom Merch Setup | Green Flash Advertising",
    description:
      "Custom branded apparel, accessories, and bedding for your business. $199 one-time Elite Branding setup fee — print-ready files, ordering sheet, and website integration included.",
    path: "/merch",
  },
  "/websites": {
    title: "Website Design & Care Plan | Green Flash Advertising",
    description:
      "Single landing pages from $375 and full multi-page websites from $975, built mobile-first. Add the $125/month care plan for maintenance, security, and monthly content updates.",
    path: "/websites",
  },
  "/privacy": {
    title: "Privacy Policy | Green Flash Advertising",
    description:
      "How Green Flash Advertising collects, uses, and retains information from this site and from client inquiries.",
    path: "/privacy",
  },
  "/terms": {
    title: "Terms of Service | Green Flash Advertising",
    description:
      "Terms covering the Business Growth Package, ad spend, licensing of your content, and liability for Green Flash Advertising campaigns.",
    path: "/terms",
  },
} as const satisfies Record<string, RouteMeta>;

/** Routes that get prerendered to their own static HTML file. */
export const PRERENDER_ROUTES = Object.keys(ROUTE_META) as (keyof typeof ROUTE_META)[];

export const NOT_FOUND_META: RouteMeta = {
  title: "Page Not Found | Green Flash Advertising",
  description: "The page you're looking for doesn't exist.",
  path: "/",
  noindex: true,
};
