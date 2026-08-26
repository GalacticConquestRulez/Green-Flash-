import { Link } from "react-router-dom";
import { SiteChrome } from "@/components/chrome";

export function TermsPage() {
  return (
    <SiteChrome>
      <main id="main" className="mx-auto w-full max-w-3xl px-4 py-16 sm:px-6">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">Legal</p>
        <h1 className="mt-3 font-display text-5xl tracking-wide">Terms of Service</h1>
        <p className="mt-4 text-sm text-muted">Last updated August 25, 2026</p>
        <div className="mt-10 space-y-8 text-sm leading-relaxed text-chrome">
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">The short version</h2>
            <p className="mt-2">
              Green Flash Advertising manages advertising campaigns on Google and Meta. The Business
              Growth Package is $375 per month for management. Advertising spend is billed separately
              through your own platform accounts. There is no long-term contract; either party may
              cancel with written notice before the next billing date.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">What we do</h2>
            <p className="mt-2">
              We build, launch, optimize, and report on campaigns using content you provide. We do
              not guarantee a specific number of leads, sales, or return on ad spend. Results depend
              on your offer, market, budget, and creative.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">What you provide</h2>
            <p className="mt-2">
              You grant us a license to use the photos, videos, trademarks, and copy you send for
              the purpose of running ads on your behalf. You confirm you have the rights to that
              material. You remain responsible for your products, services, and claims made in ads
              you approve.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">Ad spend</h2>
            <p className="mt-2">
              Media spend is paid by you directly to Google, Meta, or other platforms. GFA’s $375
              monthly fee is for management only unless a written agreement says otherwise.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">Limitation</h2>
            <p className="mt-2">
              To the fullest extent allowed by law, GFA is not liable for indirect or consequential
              damages, or for platform outages, policy rejections, or tracking discrepancies outside
              our reasonable control. Total liability for a given month is limited to the management
              fees paid that month.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">Contact</h2>
            <p className="mt-2">
              <a className="text-flash hover:underline" href="mailto:hello@greenflashusa.com">
                hello@greenflashusa.com
              </a>
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
