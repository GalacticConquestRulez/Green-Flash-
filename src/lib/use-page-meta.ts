import { useEffect } from "react";

const SITE_URL = "https://greenflashusa.com";

function setMeta(selector: string, attr: string, value: string) {
  let el = document.head.querySelector<HTMLMetaElement | HTMLLinkElement>(selector);
  if (!el) return;
  el.setAttribute(attr, value);
}

export function usePageMeta({
  title,
  description,
  path,
  noindex = false,
}: {
  title: string;
  description: string;
  path: string;
  noindex?: boolean;
}) {
  useEffect(() => {
    document.title = title;
    setMeta('meta[name="description"]', "content", description);
    setMeta('meta[property="og:title"]', "content", title);
    setMeta('meta[property="og:description"]', "content", description);
    setMeta('meta[property="og:url"]', "content", `${SITE_URL}${path}`);
    setMeta('meta[name="twitter:title"]', "content", title);
    setMeta('meta[name="twitter:description"]', "content", description);
    setMeta('link[rel="canonical"]', "href", `${SITE_URL}${path}`);
    setMeta('meta[name="robots"]', "content", noindex ? "noindex, follow" : "index, follow");
  }, [title, description, path, noindex]);
}
