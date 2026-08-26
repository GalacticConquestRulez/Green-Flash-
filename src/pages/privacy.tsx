import { Link } from "react-router-dom";
import { SiteChrome } from "@/components/chrome";
import { ROUTE_META } from "@/lib/route-meta";
import { usePageMeta } from "@/lib/use-page-meta";

export function PrivacyPage() {
  usePageMeta(ROUTE_META["/privacy"]);
  return (
    <SiteChrome>
      <main id="main" className="mx-auto w-full max-w-3xl px-4 py-16 sm:px-6">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">Legal</p>
        <h1 className="mt-3 font-display text-5xl tracking-wide">Privacy Policy</h1>
        <p className="mt-4 text-sm text-muted">Last updated August 25, 2026</p>
        <div className="mt-10 space-y-8 text-sm leading-relaxed text-chrome">
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">Who we are</h2>
            <p className="mt-2">
              Green Flash Advertising (“GFA,” “we,” “us”) is an advertising management company. This
              policy explains how we handle information when you use this website or contact us.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">What we collect</h2>
            <p className="mt-2">
              If you submit the contact form, we collect your name, email address, business type, and
              the message you write. If you email us, we keep the contents of that correspondence.
              This site may also store basic technical logs (browser type, pages visited) needed to
              keep the site running.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">How we use it</h2>
            <p className="mt-2">
              We use contact details to reply to inquiries, book strategy calls, and — if you become
              a client — to manage your campaigns. We do not sell your personal information.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">Ads platforms</h2>
            <p className="mt-2">
              Client campaigns run on Meta and Google. Those platforms have their own privacy
              policies. Tracking tools such as HYROS process conversion data according to their
              terms and your ad-account settings.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">Retention</h2>
            <p className="mt-2">
              Inquiry records are kept as long as needed to respond and for ordinary business
              records. You can ask us to delete a request by emailing{" "}
              <a className="text-flash hover:underline" href="mailto:hello@greenflashusa.com">
                hello@greenflashusa.com
              </a>
              .
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">Contact</h2>
            <p className="mt-2">
              Questions about this policy:{" "}
              <a className="text-flash hover:underline" href="mailto:hello@greenflashusa.com">
                hello@greenflashusa.com
              </a>
              .
            </p>
          </section>
        </div>
        <Link to="/" className="mt-12 inline-block text-sm text-flash hover:underline">
          ← Back to home
        </Link>
      </main>
    </SiteChrome>
  );
}
