import { Link } from "react-router-dom";
import { SiteChrome } from "@/components/chrome";
import { Button } from "@/components/ui/button";
import { usePageMeta } from "@/lib/use-page-meta";

export function NotFoundPage() {
  usePageMeta({
    title: "Page Not Found | Green Flash Advertising",
    description: "The page you're looking for doesn't exist.",
    path: "/",
    noindex: true,
  });
  return (
    <SiteChrome>
      <main id="main" className="mx-auto flex w-full max-w-3xl flex-col items-start px-4 py-24 sm:px-6">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">404</p>
        <h1 className="mt-3 font-display text-5xl tracking-wide text-foreground">Page not found</h1>
        <p className="mt-4 max-w-md text-base leading-relaxed text-muted">
          That page doesn’t exist or may have moved. Head back home to find what you were
          looking for.
        </p>
        <Button asChild className="mt-8">
          <Link to="/">Back to home</Link>
        </Button>
      </main>
    </SiteChrome>
  );
}
