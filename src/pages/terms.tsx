import { Link } from "react-router-dom";
import { SiteChrome } from "@/components/chrome";
import { ROUTE_META } from "@/lib/route-meta";
import { usePageMeta } from "@/lib/use-page-meta";

export function TermsPage() {
  usePageMeta(ROUTE_META["/terms"]);
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
              Green Flash Advertising offers three things: ad management, custom merch, and
              websites. The Business Growth Package is $375 per month for ad management, with
              advertising spend billed separately through your own platform accounts. Merch setup is
              a $199 one-time fee. A website build is a $375 one-time fee, with an optional $125 per
              month care plan. Nothing here is a long-term contract; either party may cancel a
              recurring plan with written notice before the next billing date.
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
            <h2 className="font-display text-2xl tracking-wide text-foreground">Merch</h2>
            <p className="mt-2">
              The $199 Elite Branding fee covers design work, print-ready production files, an
              ordering sheet, and store setup. It does not cover the cost of producing or shipping
              physical goods, which you pay directly to the printer or supplier. Bedding is
              available for an additional fee quoted before work starts. You own the finished
              designs we produce for your brand; we may show the work in our portfolio unless you
              ask us not to.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">Websites</h2>
            <p className="mt-2">
              The $375 build fee covers design, build, and launch of one site. Domain registration
              and hosting are billed at cost in your own accounts and are not included. The $125
              per month care plan covers maintenance, security updates, monitoring, backups, and
              routine monthly content changes; substantial new pages or features are quoted
              separately. If the care plan is cancelled, the site remains yours and we hand over
              access, but we stop maintaining it.
            </p>
          </section>
          <section>
            <h2 className="font-display text-2xl tracking-wide text-foreground">Ad spend</h2>
            <p className="mt-2">
              Media spend is paid by you directly to Google, Meta, or other platforms. GFA’s $375
              monthly ad-management fee is for management only unless a written agreement says
              otherwise. It is a separate charge from the one-time $375 website build fee.
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
              <a className="text-flash hover:underline" href="mailto:greenflashusa@gmail.com">
                greenflashusa@gmail.com
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
