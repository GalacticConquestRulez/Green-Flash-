import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Check,
  Cpu,
  FileX2,
  Megaphone,
  Monitor,
  Shirt,
  Users,
} from "lucide-react";
import { MobileCta, SiteChrome } from "@/components/chrome";
import { ContactForm } from "@/components/contact-form";
import { Button } from "@/components/ui/button";
import { ROUTE_META } from "@/lib/route-meta";
import { usePageMeta } from "@/lib/use-page-meta";

const SERVICES = [
  {
    icon: Megaphone,
    to: "/advertising",
    eyebrow: "$375/mo · flagship",
    title: "Advertising",
    body: "AI-powered Google & Meta ads built from the photos and videos you already have, with HYROS tracking so you see what actually paid off.",
    points: ["Facebook + Instagram & Google Ads", "AI optimization, human decisions", "Monthly reporting you can read"],
    cta: "See ad management",
    flagship: true,
  },
  {
    icon: Shirt,
    to: "/merch",
    eyebrow: "$199 one-time setup",
    title: "Merch",
    body: "A custom-branded line — apparel, accessories, bedding — with print-ready files, an ordering sheet, and a store people can actually buy from.",
    points: ["Custom designs, not templates", "Print-ready files included", "Website integration available"],
    cta: "See merch setup",
    flagship: false,
  },
  {
    icon: Monitor,
    to: "/websites",
    eyebrow: "Landing pages from $375",
    title: "Websites",
    body: "A landing page to point your ads at, or a full site from $975 — launched properly, then kept current with a $125/mo care plan.",
    points: ["Mobile-first, fast by default", "SEO wired in from day one", "Maintained monthly, not abandoned"],
    cta: "See website packages",
    flagship: false,
  },
];

const WHY = [
  {
    icon: Cpu,
    title: "AI does the heavy lifting",
    body: "Across ads, sites, and design work, we spend the human hours on decisions — not busywork.",
  },
  {
    icon: FileX2,
    title: "No long-term contracts",
    body: "Everything monthly is month-to-month. We keep clients with results, not paperwork.",
  },
  {
    icon: Users,
    title: "One team for all of it",
    body: "Ads, the page they land on, and the merch that keeps your name around — built to work together, by the same people.",
  },
];

/**
 * The drone footage behind the hero, treated the way the links page treats its
 * backdrop: nothing laid over it — no scrim, no tint — with the text carrying
 * its own outline instead. The <video> ships with no src, so nothing downloads
 * until the client opts in; reduced-motion, data-saver, and slow connections
 * keep the poster frame, which is a still from the same footage.
 */
function HeroBackdrop() {
  const ref = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    type NetInfo = { saveData?: boolean; effectiveType?: string };
    const conn = (navigator as { connection?: NetInfo }).connection;
    if (reduce || conn?.saveData || /2g/.test(conn?.effectiveType ?? "")) return;

    // Two cuts of the footage: the 16:9 desktop view, and a vertical reel for
    // phones — chosen by orientation so neither ever ships to the wrong shape,
    // and swapped live if a tablet rotates.
    const portrait = window.matchMedia("(orientation: portrait)");
    const apply = () => {
      const next = portrait.matches ? "/hero-yacht-portrait.mp4" : "/hero-yacht.mp4";
      if (v.currentSrc.endsWith(next)) return;
      v.classList.replace("opacity-100", "opacity-0");
      v.src = next;
      v.play().catch(() => {
        // Autoplay refused: the poster underneath stays as a still backdrop.
      });
    };
    // replace, not add: with both utilities present, stylesheet order decides
    const onReady = () => v.classList.replace("opacity-0", "opacity-100");
    v.addEventListener("canplay", onReady);
    portrait.addEventListener("change", apply);
    apply();
    return () => {
      v.removeEventListener("canplay", onReady);
      portrait.removeEventListener("change", apply);
    };
  }, []);

  // No poster attribute: until the video has a frame it stays transparent and
  // the <picture> underneath shows through, which already picked the right
  // orientation without JavaScript.
  return (
    <video
      ref={ref}
      className="absolute inset-0 size-full object-cover opacity-0 transition-opacity duration-1000"
      muted
      loop
      playsInline
      preload="none"
      aria-hidden="true"
    />
  );
}

export function HomePage() {
  usePageMeta(ROUTE_META["/"]);
  return (
    <SiteChrome>
      <main id="main" className="pb-20 md:pb-0">
        {/* ---------- hero ---------- */}
        <section className="relative overflow-hidden border-b border-border">
          {/* Poster underneath so there is never a black flash before the
              video's first frame; the video fades in over it. Nothing dims
              either layer — the text below carries contour outlines instead. */}
          <div className="pointer-events-none absolute inset-0">
            <picture className="block size-full">
              <source media="(orientation: portrait)" srcSet="/hero-yacht-portrait.jpg" />
              <img
                src="/hero-yacht.jpg"
                alt=""
                className="size-full object-cover"
                fetchPriority="high"
                decoding="async"
              />
            </picture>
            <HeroBackdrop />
          </div>

          <div className="relative mx-auto max-w-6xl px-4 pb-16 pt-12 text-center sm:px-6 md:pb-24 md:pt-20">
            <div className="stagger-in relative mx-auto max-w-3xl">
              {/* A feathered pool of backdrop blur behind the copy — no tint, no
                  darkening, just softening the detail behind the letters so
                  their colours separate. The radial mask fades the effect out,
                  so there is no frosted rectangle with visible edges. */}
              <div
                aria-hidden="true"
                className="pointer-events-none absolute -inset-x-10 -inset-y-8 backdrop-blur-[6px] [mask-image:radial-gradient(ellipse_70%_65%_at_50%_50%,#000_45%,transparent_95%)]"
              />
              {/* Max's designed lockup carries the visual headline — badge,
                  gradient type, glow, arrow, results pill — as he built it.
                  The real heading stays in the document for search engines and
                  screen readers, just visually hidden. */}
              <h1 className="sr-only">
                Green Flash USA — more clicks, more customers, more growth. Real results, scalable
                growth.
              </h1>
              <img
                src="/hero-lockup.webp"
                alt=""
                width={1100}
                height={759}
                fetchPriority="high"
                decoding="async"
                className="mx-auto w-full max-w-[34rem] md:max-w-[40rem]"
              />
              <p className="[text-shadow:0_1px_2px_rgba(7,8,7,0.55),0_6px_28px_rgba(7,8,7,0.5)] mx-auto mt-2 max-w-2xl text-base font-medium leading-relaxed text-foreground sm:text-lg">
                One team for the whole growth stack — the ads that bring people in, the website
                they land on, and the merch that keeps your name around. Founded by media
                entrepreneur Max Glaser and partner Tanner Lodini.
              </p>
              <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row sm:items-center">
                <Button asChild>
                  <Link to="/#services">
                    See What We Do
                    <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" className="bg-background/70 backdrop-blur-[2px]">
                  <Link to="/#contact">Book a Free Call</Link>
                </Button>
              </div>
            </div>
          </div>

          <div className="relative border-t border-border bg-card/80">
            <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-x-8 gap-y-3 px-4 py-4 text-center sm:px-6">
              {["Google & Meta Ads", "Custom Merch", "Websites", "AI-Powered"].map((item) => (
                <p
                  key={item}
                  className="text-[11px] font-semibold uppercase tracking-[0.2em] text-muted"
                >
                  {item}
                </p>
              ))}
            </div>
          </div>
        </section>

        {/* ---------- the three services ---------- */}
        <section id="services" className="scroll-mt-20 mx-auto max-w-6xl px-4 py-20 sm:px-6 md:py-28">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
              What we do
            </p>
            <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
              Three ways to grow.
            </h2>
            <p className="mt-4 text-base leading-relaxed text-muted">
              Take one, or let them feed each other — the ads bring people in, the site converts
              them, the merch keeps you on their backs.
            </p>
          </div>

          <div className="mt-12 grid gap-4 lg:grid-cols-3">
            {SERVICES.map((s) => (
              <Link
                key={s.to}
                to={s.to}
                className={
                  "group relative flex flex-col rounded-2xl bg-card p-7 transition-[box-shadow] duration-150 hover:shadow-[0_0_0_1px_color-mix(in_oklab,var(--color-flash)_45%,transparent)] " +
                  (s.flagship ? "hairline-flash" : "hairline")
                }
              >
                {s.flagship ? (
                  <p className="absolute right-6 top-6 rounded-full bg-flash/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-flash">
                    Flagship
                  </p>
                ) : null}
                <s.icon className="size-7 text-flash" strokeWidth={1.6} />
                <p className="mt-5 text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                  {s.eyebrow}
                </p>
                <h3 className="mt-2 font-display text-3xl tracking-wide text-foreground">
                  {s.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-muted">{s.body}</p>
                <ul className="mt-5 flex-1 space-y-2.5">
                  {s.points.map((pt) => (
                    <li key={pt} className="flex items-start gap-2.5 text-sm text-chrome">
                      <Check className="mt-0.5 size-4 shrink-0 text-flash" />
                      {pt}
                    </li>
                  ))}
                </ul>
                <p className="mt-6 flex items-center gap-2 text-sm font-semibold text-flash">
                  {s.cta}
                  <ArrowRight className="size-4 transition-transform duration-150 group-hover:translate-x-0.5" />
                </p>
              </Link>
            ))}
          </div>
        </section>

        {/* ---------- why ---------- */}
        <section className="border-y border-border bg-card/40 py-20 md:py-28">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                Why Green Flash
              </p>
              <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
                Built for owners, not agencies.
              </h2>
            </div>
            <div className="mt-12 grid gap-4 md:grid-cols-3">
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

        {/* ---------- contact ---------- */}
        <section id="contact" className="scroll-mt-20 px-4 py-20 sm:px-6 md:py-28">
          <div className="mx-auto grid max-w-6xl items-start gap-12 md:grid-cols-[1fr_1.05fr]">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                Ready to grow?
              </p>
              <h2 className="mt-3 font-display text-5xl font-semibold tracking-wide text-foreground sm:text-6xl">
                Tell us what you want to grow.
              </h2>
              <p className="mt-5 max-w-md text-base leading-relaxed text-muted">
                Ads, a website, merch, or all three — book a free call and we'll tell you exactly
                where we'd start for your business.
              </p>
              <ul className="mt-8 space-y-3 text-sm text-chrome">
                {[
                  "Free strategy call, no obligation",
                  "No long-term contracts on anything monthly",
                  "One team across ads, web, and merch",
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
                interest="General"
                prompt="What should we grow?"
                placeholder="Tell us about your business and whether you're thinking ads, a website, merch — or you're not sure yet. That's what the call is for."
              />
            </div>
          </div>
        </section>
      </main>
      <MobileCta />
    </SiteChrome>
  );
}
