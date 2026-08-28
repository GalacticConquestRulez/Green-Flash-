/**
 * Per-route JSON-LD, injected at prerender time so every page carries schema
 * specific to what it sells — not one Organization blob repeated site-wide.
 *
 * The template's own <script type="application/ld+json"> keeps the shared
 * Organization + WebSite graph (identity, founders, catalog); this module adds
 * the page layer: WebPage, BreadcrumbList, and the page's own Service/Offer.
 * Breadcrumbs are one of the few schema types Google still renders in the
 * listing itself; the Service/Offer detail is primarily for AI answer engines,
 * which quote prices and scope straight from structured data.
 */

const SITE = "https://greenflashusa.com";
const ORG = `${SITE}/#organization`;
const WEBSITE = `${SITE}/#website`;

const crumb = (items) => ({
  "@type": "BreadcrumbList",
  itemListElement: items.map(([name, path], i) => ({
    "@type": "ListItem",
    position: i + 1,
    name,
    item: `${SITE}${path}`,
  })),
});

const webPage = (meta, extra = {}) => ({
  "@type": "WebPage",
  "@id": `${SITE}${meta.path}#webpage`,
  url: `${SITE}${meta.path === "/" ? "/" : meta.path}`,
  name: meta.title,
  description: meta.description,
  isPartOf: { "@id": WEBSITE },
  about: { "@id": ORG },
  primaryImageOfPage: `${SITE}/og.jpg`,
  inLanguage: "en-US",
  ...extra,
});

/** Route -> extra graph nodes. Routes not listed get WebPage + breadcrumb only. */
export function schemaFor(meta) {
  const graph = [];

  switch (meta.path) {
    case "/":
      // Home's page node; the Organization itself already lives in the template.
      graph.push(webPage(meta));
      break;

    case "/advertising":
      graph.push(
        webPage(meta, { breadcrumb: crumb([["Home", "/"], ["Advertising", "/advertising"]]) }),
        crumb([["Home", "/"], ["Advertising", "/advertising"]]),
        {
          "@type": "Service",
          "@id": `${SITE}/advertising#service`,
          name: "Google & Meta Ads Management",
          serviceType: "Online advertising management",
          provider: { "@id": ORG },
          areaServed: { "@type": "Country", name: "United States" },
          description:
            "Monthly management of Google Ads and Meta (Facebook + Instagram) campaigns: AI-powered optimization, HYROS tracking and attribution, audience research, weekly optimizations, and monthly reporting.",
          offers: {
            "@type": "Offer",
            name: "Business Growth Package",
            url: `${SITE}/advertising#pricing`,
            price: "375",
            priceCurrency: "USD",
            priceSpecification: {
              "@type": "UnitPriceSpecification",
              price: "375",
              priceCurrency: "USD",
              unitText: "MONTH",
            },
            availability: "https://schema.org/InStock",
          },
        },
      );
      break;

    case "/merch":
      graph.push(
        webPage(meta, { breadcrumb: crumb([["Home", "/"], ["Merch", "/merch"]]) }),
        crumb([["Home", "/"], ["Merch", "/merch"]]),
        {
          "@type": "Service",
          "@id": `${SITE}/merch#service`,
          name: "Elite Branding Custom Merch Setup",
          serviceType: "Custom merchandise design and setup",
          provider: { "@id": ORG },
          areaServed: { "@type": "Country", name: "United States" },
          description:
            "One-time setup of a custom branded merchandise line — apparel, accessories, and bedding — with custom design work, print-ready production files, an ordering sheet, and website store integration.",
          offers: {
            "@type": "Offer",
            name: "Elite Branding",
            url: `${SITE}/merch#whats-included`,
            price: "199",
            priceCurrency: "USD",
            availability: "https://schema.org/InStock",
          },
        },
      );
      break;

    case "/websites":
      graph.push(
        webPage(meta, { breadcrumb: crumb([["Home", "/"], ["Websites", "/websites"]]) }),
        crumb([["Home", "/"], ["Websites", "/websites"]]),
        {
          "@type": "Service",
          "@id": `${SITE}/websites#service`,
          name: "Website Design & Care",
          serviceType: "Web design and development",
          provider: { "@id": ORG },
          areaServed: { "@type": "Country", name: "United States" },
          description:
            "Mobile-first business websites: a single landing page for a flat fee, full multi-page sites quoted from a base price, and a monthly care plan covering maintenance, security, and content updates.",
          // "from $975" is a floor, so it is expressed as minPrice — claiming a
          // fixed price that quotes then exceed is what gets schema flagged.
          offers: [
            {
              "@type": "Offer",
              name: "Landing Page",
              url: `${SITE}/websites#pricing`,
              price: "375",
              priceCurrency: "USD",
              availability: "https://schema.org/InStock",
            },
            {
              "@type": "Offer",
              name: "Full Website",
              url: `${SITE}/websites#pricing`,
              priceCurrency: "USD",
              priceSpecification: {
                "@type": "PriceSpecification",
                minPrice: "975",
                priceCurrency: "USD",
              },
              availability: "https://schema.org/InStock",
            },
            {
              "@type": "Offer",
              name: "Website Care Plan",
              url: `${SITE}/websites#pricing`,
              price: "125",
              priceCurrency: "USD",
              priceSpecification: {
                "@type": "UnitPriceSpecification",
                price: "125",
                priceCurrency: "USD",
                unitText: "MONTH",
              },
              availability: "https://schema.org/InStock",
            },
          ],
        },
      );
      break;

    case "/privacy":
    case "/terms":
      graph.push(
        webPage(meta, {
          breadcrumb: crumb([["Home", "/"], [meta.path === "/privacy" ? "Privacy Policy" : "Terms of Service", meta.path]]),
        }),
        crumb([["Home", "/"], [meta.path === "/privacy" ? "Privacy Policy" : "Terms of Service", meta.path]]),
      );
      break;

    default:
      graph.push(webPage(meta));
  }

  return { "@context": "https://schema.org", "@graph": graph };
}
