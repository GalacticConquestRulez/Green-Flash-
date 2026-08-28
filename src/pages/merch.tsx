import { Link } from "react-router-dom";
import {
  ArrowRight,
  BedDouble,
  Check,
  Globe,
  Monitor,
  PencilRuler,
  Rocket,
  ShoppingCart,
  Smartphone,
  Shirt,
} from "lucide-react";
import { MobileCta, SiteChrome } from "@/components/chrome";
import { ContactForm } from "@/components/contact-form";
import { Button } from "@/components/ui/button";
import { ROUTE_META } from "@/lib/route-meta";
import { usePageMeta } from "@/lib/use-page-meta";

const CATEGORIES = [
  {
    icon: Shirt,
    title: "Apparel",
    body: "Shirts, hoodies, pants and more — printed with your brand, ready to wear and ready to sell.",
  },
  {
    icon: Smartphone,
    title: "Accessories",
    body: "Phone cases, AirPod cases, speakers, mouse pads and more. The small items people actually carry.",
  },
  {
    icon: BedDouble,
    title: "Bedding",
    body: "Add bedding to your store for a small additional fee.",
  },
  {
    icon: Monitor,
    title: "Website Setup",
    body: "We integrate your merch into the site you already have — or we build you one from scratch.",
  },
];

const VALUE = [
  {
    icon: PencilRuler,
    title: "Custom designs",
    body: "Made for your brand. Made to stand out. Not a template with your logo dropped on it.",
  },
  {
    icon: ShoppingCart,
    title: "Ready to sell",
    body: "Print-ready files and an ordering sheet included, so you can produce and fulfill without guesswork.",
  },
  {
    icon: Globe,
    title: "Website ready",
    body: "We set the store up so your customers can shop with ease instead of emailing you for sizes.",
  },
  {
    icon: Rocket,
    title: "Built to grow",
    body: "Quality merch. Happy customers. Stronger brand. Merch people keep wearing is advertising you don't pay twice for.",
  },
];

const INCLUDED = [
  "Custom design work built around your brand",
  "Apparel line — shirts, hoodies, pants and more",
  "Accessories — phone cases, AirPod cases, speakers, mouse pads",
  "Print-ready production files",
  "Ordering sheet so you can reorder without us",
  "Website integration available",
  "Bedding available for a small additional fee",
  "One-time fee — no monthly charge on setup",
];

const WORK = [
  { src: "/merch-wavykidkev.jpg", name: "Wavy Kid Kev", href: "https://wavykidkev.com" },
  { src: "/merch-bat-workshop.jpg", name: "Bat Workshop", href: "https://batworkshop.com" },
  { src: "/merch-2ndact.jpg", name: "2nd Act TV", href: "https://2ndact.tv" },
];

export function MerchPage() {
  usePageMeta(ROUTE_META["/merch"]);
  return (
    <SiteChrome>
      <main id="main" className="pb-20 md:pb-0">
        {/* ---------- hero ---------- */}
        <section className="relative overflow-hidden border-b border-border">
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute -left-24 top-10 size-[18rem] rounded-full bg-flash/10 blur-3xl md:size-[26rem]" />
          </div>
          <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 pb-16 pt-10 sm:px-6 md:grid-cols-[1fr_1.05fr] md:pb-24 md:pt-16">
            <div className="stagger-in">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                Custom merch setup
              </p>
              <h1 className="mt-4 font-display text-[2.7rem] font-semibold leading-[0.95] tracking-wide text-foreground sm:text-6xl">
                Everything your brand needs.
                <span className="mt-1 block text-flash">All in one place.</span>
              </h1>
              <p className="mt-6 max-w-xl text-base leading-relaxed text-chrome sm:text-lg">
                We design the line, hand you print-ready files and an ordering sheet, and set up the
                store so people can actually buy it. One flat setup fee.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
                <Button asChild>
                  <Link to="/merch#contact">
                    Start Your Merch Line
                    <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline">
                  <Link to="/merch#whats-included">See What's Included</Link>
                </Button>
              </div>
            </div>
            <div className="overflow-hidden rounded-2xl bg-card hairline">
              <img
                src="/merch-flyer.jpg"
                alt="Green Flash custom merch — hoodie, tee, cap, phone case, speaker, AirPod case and mouse pad, all branded"
                className="h-auto w-full"
                width={1600}
                height={1067}
                fetchPriority="high"
                decoding="async"
              />
            </div>
          </div>
        </section>

        {/* ---------- price ---------- */}
        <section
          id="whats-included"
          className="scroll-mt-20 border-b border-border bg-card/40 py-20 md:py-28"
        >
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                The offer
              </p>
              <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
                Elite Branding
              </h2>
              <p className="mt-4 text-base leading-relaxed text-muted">
                One setup fee gets your whole merch line designed, produced-ready, and live.
              </p>
            </div>

            <div className="mx-auto mt-12 max-w-3xl rounded-2xl bg-card p-6 hairline-flash sm:p-10">
              <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                    One-time setup fee
                  </p>
                  <p className="mt-2 font-display text-6xl tracking-wide text-foreground sm:text-7xl">
                    $199
                  </p>
                  <p className="mt-2 text-sm text-chrome">
                    Production and shipping costs are billed separately.
                  </p>
                </div>
                <p className="rounded-full bg-flash/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-flash">
                  Website integration available
                </p>
              </div>

              <ul className="mt-8 grid gap-3 sm:grid-cols-2">
                {INCLUDED.map((item) => (
                  <li key={item} className="flex items-start gap-2.5 text-sm text-chrome">
                    <Check className="mt-0.5 size-4 shrink-0 text-flash" />
                    {item}
                  </li>
                ))}
              </ul>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Button asChild className="sm:flex-1">
                  <Link to="/merch#contact">
                    Get Started
                    <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" className="sm:flex-1">
                  <Link to="/websites">Need a site too?</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- categories ---------- */}
        <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6 md:py-28">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
              What we make
            </p>
            <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
              More than t-shirts.
            </h2>
          </div>
          <div className="mt-12 grid gap-4 sm:grid-cols-2">
            {CATEGORIES.map((c) => (
              <article key={c.title} className="rounded-xl bg-card p-6 hairline">
                <c.icon className="size-6 text-flash" strokeWidth={1.75} />
                <h3 className="mt-4 font-display text-2xl tracking-wide text-foreground">
                  {c.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{c.body}</p>
              </article>
            ))}
          </div>
        </section>

        {/* ---------- proof ---------- */}
        <section className="border-y border-border bg-card/40 py-20 md:py-28">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                Recent work
              </p>
              <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
                Stores we've built.
              </h2>
            </div>
            <div className="mt-12 grid gap-4 md:grid-cols-3">
              {WORK.map((w) => (
                <a
                  key={w.name}
                  href={w.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group overflow-hidden rounded-xl bg-card hairline transition-[box-shadow] duration-150 hover:shadow-[0_0_0_1px_color-mix(in_oklab,var(--color-flash)_40%,transparent)]"
                >
                  <img
                    src={w.src}
                    alt={`${w.name} merch store`}
                    className="photo h-44 w-full object-cover object-top"
                    loading="lazy"
                    decoding="async"
                  />
                  <p className="flex items-center justify-between px-5 py-4 font-display text-xl tracking-wide text-foreground">
                    {w.name}
                    <ArrowRight className="size-4 text-flash transition-transform duration-150 group-hover:translate-x-0.5" />
                  </p>
                </a>
              ))}
            </div>
          </div>
        </section>

        {/* ---------- value props ---------- */}
        <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6 md:py-28">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
              Why our merch
            </p>
            <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
              Merch that builds trust.
            </h2>
          </div>
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {VALUE.map((v) => (
              <article key={v.title} className="rounded-xl bg-card p-6 hairline">
                <v.icon className="size-5 text-flash" strokeWidth={1.75} />
                <h3 className="mt-4 font-display text-2xl tracking-wide text-foreground">
                  {v.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{v.body}</p>
              </article>
            ))}
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
                Ready to print?
              </p>
              <h2 className="mt-3 font-display text-5xl font-semibold tracking-wide text-foreground sm:text-6xl">
                Start your merch line.
              </h2>
              <p className="mt-5 max-w-md text-base leading-relaxed text-muted">
                Tell us about your brand and what you want on people. We'll come back with a
                direction and what the line would look like.
              </p>
              <ul className="mt-8 space-y-3 text-sm text-chrome">
                {[
                  "$199 one-time setup fee",
                  "Print-ready files and ordering sheet included",
                  "Website integration available",
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
                interest="Merch"
                prompt="What do you want on your merch?"
                placeholder="Tell us about your brand, the pieces you want, and roughly how many people you'd sell to."
                submitLabel="Start my merch line"
              />
            </div>
          </div>
        </section>
      </main>
      <MobileCta label="Start Your Merch Line" to="/merch#contact" />
    </SiteChrome>
  );
}
