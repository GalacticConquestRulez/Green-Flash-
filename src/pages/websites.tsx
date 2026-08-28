import { Link } from "react-router-dom";
import {
  ArrowRight,
  Check,
  Gauge,
  LifeBuoy,
  LockKeyhole,
  RefreshCw,
  Search,
  Smartphone,
  Sparkles,
} from "lucide-react";
import { MobileCta, SiteChrome } from "@/components/chrome";
import { ContactForm } from "@/components/contact-form";
import { Button } from "@/components/ui/button";
import { ROUTE_META } from "@/lib/route-meta";
import { usePageMeta } from "@/lib/use-page-meta";

const BUILD = [
  "Custom design built around your brand — not a template",
  "Mobile-first: it looks right on a phone before anything else",
  "Contact form wired to your inbox",
  "SEO fundamentals — titles, descriptions, structured data, sitemap",
  "Fast by default: optimized images and no bloat",
  "SSL certificate and secure hosting setup",
  "Google Search Console and analytics connected",
  "Merch store integration available",
];

const CARE = [
  "Monthly content updates — new photos, prices, hours, offers",
  "Security patches and software updates",
  "Uptime monitoring so you hear it from us first",
  "Regular backups",
  "Small copy and layout changes on request",
  "Direct email access — no ticket system",
];

const WHY = [
  {
    icon: Smartphone,
    title: "Built for phones first",
    body: "Most of your visitors are on a phone. We design there first and scale up, not the other way round.",
  },
  {
    icon: Gauge,
    title: "Fast, because slow costs you",
    body: "Every extra second of load time costs visitors. Optimized images, minimal scripts, no page-builder bloat.",
  },
  {
    icon: Search,
    title: "Findable",
    body: "Titles, descriptions, structured data, and a sitemap set up properly, so search engines can read it.",
  },
  {
    icon: LockKeyhole,
    title: "Secure and current",
    body: "SSL from day one, and the care plan keeps the software patched instead of rotting quietly.",
  },
  {
    icon: RefreshCw,
    title: "It stays current",
    body: "Monthly updates mean the site still says the right prices and hours a year from now.",
  },
  {
    icon: LifeBuoy,
    title: "One person to email",
    body: "Something needs changing, you email us. No ticket queue, no agency account manager.",
  },
];

const STEPS = [
  {
    n: "01",
    title: "Tell us about the business",
    body: "What you do, who you want walking in, and any photos or copy you already have.",
  },
  {
    n: "02",
    title: "We design and build",
    body: "You see the layout before it goes anywhere. Changes are part of the build, not an upsell.",
  },
  {
    n: "03",
    title: "We launch it",
    body: "Domain, SSL, analytics, search console — wired up and live. You don't touch a config file.",
  },
  {
    n: "04",
    title: "We keep it current",
    body: "The care plan handles updates, patches, and the monthly changes so it never goes stale.",
  },
];

export function WebsitesPage() {
  usePageMeta(ROUTE_META["/websites"]);
  return (
    <SiteChrome>
      <main id="main" className="pb-20 md:pb-0">
        {/* ---------- hero ---------- */}
        <section className="relative overflow-hidden border-b border-border">
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute -left-24 top-10 size-[18rem] rounded-full bg-flash/10 blur-3xl md:size-[26rem]" />
          </div>
          <div className="relative mx-auto max-w-6xl px-4 pb-16 pt-10 text-center sm:px-6 md:pb-24 md:pt-16">
            <div className="stagger-in mx-auto max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                Website design &amp; care
              </p>
              <h1 className="mt-4 font-display text-[2.7rem] font-semibold leading-[0.95] tracking-wide text-foreground sm:text-6xl md:text-7xl">
                A site that works.
                <span className="mt-1 block text-flash">And stays working.</span>
              </h1>
              <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-chrome sm:text-lg">
                We build it, launch it, and keep it current every month — so your website is still
                accurate and fast a year from now, not quietly broken.
              </p>
              <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row sm:items-center">
                <Button asChild>
                  <Link to="/websites#contact">
                    Get Your Website
                    <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline">
                  <Link to="/websites#pricing">See Pricing</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- pricing ---------- */}
        <section id="pricing" className="scroll-mt-20 border-b border-border bg-card/40 py-20 md:py-28">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">Pricing</p>
              <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
                Build it once. Keep it alive.
              </h2>
              <p className="mt-4 text-base leading-relaxed text-muted">
                One fee to build the site. A small monthly to make sure it never goes stale.
              </p>
            </div>

            <div className="mx-auto mt-12 grid max-w-5xl gap-4 md:grid-cols-2">
              {/* build */}
              <div className="rounded-2xl bg-card p-6 hairline-flash sm:p-8">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                  Website build
                </p>
                <p className="mt-2 font-display text-6xl tracking-wide text-foreground">
                  $375
                  <span className="text-2xl text-muted"> one-time</span>
                </p>
                <p className="mt-2 text-sm text-chrome">
                  Design, build, and launch. Domain and hosting billed at cost in your own accounts.
                </p>
                <ul className="mt-7 space-y-3">
                  {BUILD.map((item) => (
                    <li key={item} className="flex items-start gap-2.5 text-sm text-chrome">
                      <Check className="mt-0.5 size-4 shrink-0 text-flash" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              {/* care */}
              <div className="rounded-2xl bg-card p-6 hairline sm:p-8">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                  Care plan
                </p>
                <p className="mt-2 font-display text-6xl tracking-wide text-foreground">
                  $125
                  <span className="text-2xl text-muted"> / mo</span>
                </p>
                <p className="mt-2 text-sm text-chrome">
                  Maintenance and monthly updates. Month-to-month — cancel anytime.
                </p>
                <ul className="mt-7 space-y-3">
                  {CARE.map((item) => (
                    <li key={item} className="flex items-start gap-2.5 text-sm text-chrome">
                      <Check className="mt-0.5 size-4 shrink-0 text-flash" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="mx-auto mt-8 flex max-w-5xl flex-col gap-3 sm:flex-row">
              <Button asChild className="sm:flex-1">
                <Link to="/websites#contact">
                  Get Your Website
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" className="sm:flex-1">
                <Link to="/#contact">Pair it with ads</Link>
              </Button>
            </div>
            <p className="mt-4 text-center text-sm text-muted">
              No long-term contracts. Simple as that.
            </p>
          </div>
        </section>

        {/* ---------- process ---------- */}
        <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6 md:py-28">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
              How it works
            </p>
            <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
              Four steps. Then it runs.
            </h2>
          </div>
          <ol className="mt-14 grid gap-6 md:grid-cols-4">
            {STEPS.map((step, i) => (
              <li key={step.n} className="relative">
                {i < STEPS.length - 1 ? (
                  <span className="pointer-events-none absolute left-[3.25rem] right-[-0.75rem] top-5 hidden h-px bg-border md:block" />
                ) : null}
                <p className="font-display text-4xl text-flash">{step.n}</p>
                <h3 className="mt-3 font-display text-2xl tracking-wide text-foreground">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{step.body}</p>
              </li>
            ))}
          </ol>
        </section>

        {/* ---------- why ---------- */}
        <section className="border-y border-border bg-card/40 py-20 md:py-28">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                Why Green Flash
              </p>
              <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
                Most small-business sites die quietly.
              </h2>
              <p className="mt-4 text-base leading-relaxed text-muted">
                Built once, never touched, slowly wrong about prices and hours. The care plan exists
                so that doesn't happen to yours.
              </p>
            </div>
            <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {WHY.map((w) => (
                <article key={w.title} className="rounded-xl bg-card p-6 hairline">
                  <w.icon className="size-5 text-flash" strokeWidth={1.75} />
                  <h3 className="mt-4 font-display text-2xl tracking-wide text-foreground">
                    {w.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted">{w.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* ---------- bundle nudge ---------- */}
        <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
          <div className="rounded-2xl bg-card p-6 hairline-flash sm:p-10">
            <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
              <div className="max-w-xl">
                <Sparkles className="size-6 text-flash" strokeWidth={1.75} />
                <h2 className="mt-4 font-display text-3xl tracking-wide text-foreground">
                  A site is where the ads land.
                </h2>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  Running Google and Meta ads into a slow or outdated page wastes the spend. If
                  you're doing both, we'll build the site around where the traffic is going.
                </p>
              </div>
              <Button asChild variant="outline" className="shrink-0">
                <Link to="/#pricing">
                  See ad management
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
            </div>
          </div>
        </section>

        {/* ---------- contact ---------- */}
        <section
          id="contact"
          className="scroll-mt-20 border-t border-border px-4 py-20 sm:px-6 md:py-28"
        >
          <div className="mx-auto grid max-w-6xl items-start gap-12 md:grid-cols-[1fr_1.05fr]">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                Ready to build?
              </p>
              <h2 className="mt-3 font-display text-5xl font-semibold tracking-wide text-foreground sm:text-6xl">
                Get your website.
              </h2>
              <p className="mt-5 max-w-md text-base leading-relaxed text-muted">
                Tell us what the business does and what the site needs to accomplish. We'll come
                back with a plan and a timeline.
              </p>
              <ul className="mt-8 space-y-3 text-sm text-chrome">
                {[
                  "$375 one-time build",
                  "$125/mo care plan — maintenance and monthly updates",
                  "No long-term contracts",
                ].map((t) => (
                  <li key={t} className="flex items-center gap-2.5">
                    <Check className="size-4 text-flash" />
                    {t}
                  </li>
                ))}
              </ul>
              <p className="mt-8 text-sm text-muted">
                Or email{" "}
                <a href="mailto:greenflashusa@gmail.com" className="text-flash hover:underline">
                  greenflashusa@gmail.com
                </a>
              </p>
            </div>
            <div className="rounded-2xl bg-card p-6 hairline sm:p-8">
              <ContactForm
                interest="Website"
                prompt="What does the site need to do?"
                placeholder="Tell us about the business, whether you have a site now, and what you want visitors to do when they land."
                submitLabel="Get my website"
              />
            </div>
          </div>
        </section>
      </main>
      <MobileCta label="Get Your Website" to="/websites#contact" />
    </SiteChrome>
  );
}
