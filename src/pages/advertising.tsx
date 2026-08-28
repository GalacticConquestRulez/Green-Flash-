import { MobileCta, SiteChrome } from "@/components/chrome";
import { Hero } from "@/components/hero";
import {
  Benefits,
  FinalCta,
  MoreServices,
  Offer,
  Problem,
  Process,
  Proof,
  Services,
} from "@/components/sections";
import { ROUTE_META } from "@/lib/route-meta";
import { usePageMeta } from "@/lib/use-page-meta";

/**
 * The original one-page pitch, now living at /advertising: the home page
 * fronts the company and this page sells the flagship service.
 */
export function AdvertisingPage() {
  usePageMeta(ROUTE_META["/advertising"]);
  return (
    <SiteChrome>
      <main id="main" className="pb-20 md:pb-0">
        <Hero />
        <Problem />
        <Services />
        <Process />
        <Offer />
        <Benefits />
        <Proof />
        <MoreServices />
        <FinalCta />
      </main>
      <MobileCta label="Start Growing for $375/mo" to="/advertising#contact" />
    </SiteChrome>
  );
}
