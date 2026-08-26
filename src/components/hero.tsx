import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { PhoneMock } from "@/components/phone-mock";
import { Button } from "@/components/ui/button";

const TRUST = [
  "Facebook + Instagram Ads",
  "Google Ads",
  "AI Optimization",
  "Ongoing Management",
];

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <img
          src="/hero-street.jpg"
          alt=""
          className="size-full object-cover opacity-35"
        />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(7,8,7,0.55)_0%,rgba(7,8,7,0.78)_45%,rgba(7,8,7,1)_100%)]" />
        <div className="absolute -left-24 top-24 size-[18rem] rounded-full bg-flash/10 blur-3xl md:size-[28rem]" />
      </div>

      <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 pb-16 pt-10 sm:px-6 md:grid-cols-[1.1fr_0.9fr] md:pb-24 md:pt-16">
        <div className="stagger-in">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
            Green Flash Advertising · GFA
          </p>
          <h1 className="mt-4 font-display text-[2.7rem] font-semibold leading-[0.95] tracking-wide text-foreground sm:text-6xl md:text-7xl">
            Get More Customers.
            <span className="mt-1 block text-flash">Grow Your Business.</span>
          </h1>
          <p className="mt-6 max-w-xl text-base leading-relaxed text-chrome sm:text-lg">
            Affordable AI-powered Google & Meta ads that actually work. We take the photos and
            videos you already have and turn them into paying customers.
          </p>
          <p className="mt-3 text-sm font-medium text-muted">
            Powered by AI optimization + HYROS tracking.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Button asChild>
              <Link to="/#contact">
                Start Growing for $375/mo
                <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link to="/#how-it-works">
                See How It Works
              </Link>
            </Button>
          </div>
        </div>

        <div className="relative">
          <PhoneMock />
          <p className="mt-4 text-center text-[11px] uppercase tracking-[0.18em] text-muted">
            Sample ad layout · your photos, our campaigns
          </p>
        </div>
      </div>

      <div className="relative border-y border-border bg-card/80">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-x-8 gap-y-3 px-4 py-4 text-center sm:px-6">
          {TRUST.map((item) => (
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
  );
}
