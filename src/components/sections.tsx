import { Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  Check,
  Cpu,
  Crosshair,
  RefreshCw,
  Search,
  Share2,
  ShieldCheck,
  TrendingUp,
  Wallet,
} from "lucide-react";
import { ContactForm } from "@/components/contact-form";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

function Eyebrow({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">{children}</p>
  );
}

function SectionHead({
  eyebrow,
  title,
  body,
  id,
}: {
  eyebrow: string;
  title: string;
  body?: string;
  id?: string;
}) {
  return (
    <div className="mx-auto max-w-2xl text-center" id={id}>
      <Eyebrow>{eyebrow}</Eyebrow>
      <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
        {title}
      </h2>
      {body ? <p className="mt-4 text-base leading-relaxed text-muted">{body}</p> : null}
    </div>
  );
}

export function Problem() {
  return (
    <section className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-20 sm:px-6 md:grid-cols-2 md:py-28">
      <div className="overflow-hidden rounded-2xl bg-card">
        <img
          src="/restaurant.jpg"
          alt="Busy neighborhood restaurant at night"
          className="photo h-72 w-full object-cover md:h-[420px]"
          loading="lazy"
          decoding="async"
        />
      </div>
      <div>
        <Eyebrow>The problem</Eyebrow>
        <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
          Tired of wasting money on ads that don’t convert?
        </h2>
        <p className="mt-5 text-base leading-relaxed text-muted">
          Most small businesses struggle to get consistent leads from Facebook, Instagram, and
          Google. Spend goes out. Results come in fits and starts. Nobody has time to live inside
          Ads Manager.
        </p>
        <div className="mt-8 rounded-xl bg-card p-5 hairline-flash">
          <p className="font-display text-xl tracking-wide text-flash">The Green Flash way</p>
          <p className="mt-2 text-sm leading-relaxed text-chrome">
            We run your ads, watch the data with AI, and continuously improve so every dollar works
            harder.
          </p>
        </div>
      </div>
    </section>
  );
}

const SERVICES = [
  {
    icon: Share2,
    title: "Facebook + Instagram Ads",
    body: "Campaigns built for the people already scrolling near you — using the photos and videos you already have.",
  },
  {
    icon: Search,
    title: "Google Ads",
    body: "Show up when locals search for what you sell. Search, maps, and Performance Max, managed for you.",
  },
  {
    icon: Cpu,
    title: "AI-Powered Optimization",
    body: "Creative, bids, and audiences get watched around the clock. Winners get budget. Losers get cut.",
  },
  {
    icon: Crosshair,
    title: "Finding the Right Customers",
    body: "We don’t blast the zip code. We find people most likely to buy — then retarget the ones who almost did.",
  },
  {
    icon: BarChart3,
    title: "Ongoing Management & Reporting",
    body: "Month-to-month management, HYROS tracking, and reporting you can actually read. No dashboards to babysit.",
  },
];

export function Services() {
  return (
    <section id="services" className="scroll-mt-20 border-y border-border bg-card/40 py-20 md:py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionHead
          eyebrow="What we handle"
          title="You provide the content. We run the ads."
          body="The results speak for themselves. You stay in the business. We stay in the campaigns."
        />
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {SERVICES.map((s, i) => (
            <article
              key={s.title}
              className={cn(
                "rounded-xl bg-card p-6 hairline transition-[box-shadow] duration-150 hover:shadow-[0_0_0_1px_color-mix(in_oklab,var(--color-flash)_40%,transparent)]",
                i === 4 && "sm:col-span-2 lg:col-span-1",
              )}
            >
              <s.icon className="size-6 text-flash" strokeWidth={1.75} />
              <h3 className="mt-4 font-display text-2xl tracking-wide text-foreground">{s.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted">{s.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

const STEPS = [
  {
    n: "01",
    title: "Send your photos and videos",
    body: "Use what you already have — storefront shots, team photos, product clips. No studio required.",
  },
  {
    n: "02",
    title: "We build and launch",
    body: "Campaigns go live on Meta and Google, with tracking wired so you can see what actually paid off.",
  },
  {
    n: "03",
    title: "AI + HYROS keep watch",
    body: "Our AI system and HYROS tracking monitor performance and optimize in real time.",
  },
  {
    n: "04",
    title: "You get more customers",
    body: "You keep running the business. We handle the ads, the tweaks, and the reporting.",
  },
];

export function Process() {
  return (
    <section id="how-it-works" className="scroll-mt-20 px-4 py-20 sm:px-6 md:py-28">
      <div className="mx-auto max-w-6xl">
        <SectionHead
          eyebrow="How it works"
          title="Four steps. Then it runs."
          body="No six-week onboarding. No 40-page strategy deck. Send the content. We take it from there."
        />
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
      </div>
    </section>
  );
}

const INCLUDED = [
  "Meta Ads (Facebook + Instagram)",
  "Google Ads setup & management",
  "AI-powered optimization",
  "HYROS tracking & attribution",
  "Audience research & targeting",
  "Campaigns built from your existing photos & videos",
  "Weekly optimizations",
  "Monthly performance reporting",
  "Direct email access to your manager",
  "Month-to-month — cancel anytime",
];

export function Offer() {
  return (
    <section id="pricing" className="scroll-mt-20 border-y border-border bg-card/40 py-20 md:py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionHead
          eyebrow="The offer"
          title="Business Growth Package"
          body="Professional ad management at a price built for small and growing businesses."
        />
        <div className="mx-auto mt-12 max-w-3xl rounded-2xl bg-card p-6 hairline-flash sm:p-10">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                Monthly management
              </p>
              <p className="mt-2 font-display text-6xl tracking-wide text-foreground sm:text-7xl">
                $375
                <span className="text-3xl text-muted"> / mo</span>
              </p>
              <p className="mt-2 text-sm text-chrome">Your advertising budget is separate.</p>
            </div>
            <p className="rounded-full bg-flash/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-flash">
              No long-term contracts
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
              <Link to="/#contact">
                Get Started Today
                <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" className="sm:flex-1">
              <Link to="/#contact">
                Book a Call
              </Link>
            </Button>
          </div>
          <p className="mt-4 text-center text-sm text-muted">
            No long-term contracts. Simple as that.
          </p>
        </div>
      </div>
    </section>
  );
}

const BENEFITS = [
  {
    icon: Wallet,
    title: "Affordable professional management",
    body: "$375/month for Google + Meta — not a junior freelancer, not a $3k retainer.",
  },
  {
    icon: Cpu,
    title: "AI does the heavy lifting",
    body: "We spend human time on the decisions that move budget toward what actually converts.",
  },
  {
    icon: ShieldCheck,
    title: "HYROS-level tracking",
    body: "See which ads, creatives, and audiences created the customer — not just the click.",
  },
  {
    icon: RefreshCw,
    title: "Hands-off for the owner",
    body: "Send content. Approve the direction. Get customers. We live in the accounts.",
  },
  {
    icon: TrendingUp,
    title: "Built for growing businesses",
    body: "Clear reporting. No jargon theater. Results without the complexity.",
  },
];

export function Benefits() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6 md:py-28">
      <SectionHead
        eyebrow="Why Green Flash"
        title="Ads without the headache."
        body="We built GFA for owners who want more customers, not another job."
      />
      <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {BENEFITS.map((b, i) => (
          <article
            key={b.title}
            className={cn("rounded-xl bg-card p-6 hairline", i === 4 && "md:col-span-2 lg:col-span-1")}
          >
            <b.icon className="size-5 text-flash" strokeWidth={1.75} />
            <h3 className="mt-4 font-display text-2xl tracking-wide text-foreground">{b.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted">{b.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

const METRICS = [
  { k: "More leads", v: "People who actually inquire, book, or buy." },
  { k: "Lower CPA", v: "Every optimization pass is aimed at cheaper acquisition." },
  { k: "Clear ROI", v: "HYROS attribution so you can see what the $375 plus ad spend returned." },
];

export function Proof() {
  return (
    <section id="results" className="scroll-mt-20 border-y border-border bg-card/40 py-20 md:py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionHead
          eyebrow="Results"
          title="Results speak for themselves."
          body="We’re building a public case-study library. Until then, this is what every campaign is pointed at."
        />
        <div className="mt-12 grid gap-4 md:grid-cols-3">
          {METRICS.map((m) => (
            <article key={m.k} className="rounded-xl bg-card p-6 hairline">
              <p className="font-display text-3xl tracking-wide text-flash">{m.k}</p>
              <p className="mt-2 text-sm leading-relaxed text-muted">{m.v}</p>
            </article>
          ))}
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <img
            src="/owner-cafe.jpg"
            alt="Local cafe owner"
            className="photo h-56 w-full rounded-xl object-cover"
            loading="lazy"
            decoding="async"
          />
          <img
            src="/handshake.jpg"
            alt="Home-services contractor meeting a customer"
            className="photo h-56 w-full rounded-xl object-cover"
            loading="lazy"
            decoding="async"
          />
          <img
            src="/phone-hands.jpg"
            alt="Reviewing ad performance on a phone"
            className="photo h-56 w-full rounded-xl object-cover"
            loading="lazy"
            decoding="async"
          />
        </div>
        <p className="mt-6 text-center text-sm text-muted">
          Built for cafes, shops, home services, clinics, gyms, and growing local brands.
        </p>
      </div>
    </section>
  );
}

export function FinalCta() {
  return (
    <section id="contact" className="scroll-mt-20 px-4 py-20 sm:px-6 md:py-28">
      <div className="mx-auto grid max-w-6xl items-start gap-12 md:grid-cols-[1fr_1.05fr]">
        <div>
          <Eyebrow>Ready to grow?</Eyebrow>
          <h2 className="mt-3 font-display text-5xl font-semibold tracking-wide text-foreground sm:text-6xl">
            Start growing for $375/mo.
          </h2>
          <p className="mt-5 max-w-md text-base leading-relaxed text-muted">
            Book a free strategy call. Bring the photos and videos you already have. We’ll tell you
            exactly how we’d run Google and Meta for your business.
          </p>
          <ul className="mt-8 space-y-3 text-sm text-chrome">
            {[
              "Ad spend billed in your own Google & Meta accounts",
              "No long-term contracts",
              "HYROS tracking included",
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
          <ContactForm />
        </div>
      </div>
    </section>
  );
}
