import { Link } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Wordmark } from "@/components/mark";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const NAV = [
  { hash: "services", label: "Services" },
  { hash: "how-it-works", label: "How It Works" },
  { hash: "pricing", label: "Pricing" },
  { hash: "contact", label: "Contact" },
] as const;

export function SiteHeader() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    document.body.classList.toggle("menu-open", open);
    return () => {
      document.body.style.overflow = "";
      document.body.classList.remove("menu-open");
    };
  }, [open]);

  return (
    <header
      className={cn(
        "sticky top-0 z-50 border-b transition-[background-color,border-color,backdrop-filter] duration-200",
        scrolled || open
          ? "border-border bg-background/90 backdrop-blur-md"
          : "border-transparent bg-background/40 backdrop-blur-sm",
      )}
    >
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link to="/" aria-label="Green Flash Advertising home" onClick={() => setOpen(false)}>
          <Wordmark />
        </Link>

        <nav className="hidden items-center gap-8 md:flex" aria-label="Primary">
          {NAV.map((item) => (
            <Link
              key={item.hash}
              to={`/#${item.hash}`}
              className="text-sm font-medium text-muted transition-colors duration-150 hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="hidden md:block">
          <Button asChild size="md">
            <Link to="/#contact">
              Start Growing
            </Link>
          </Button>
        </div>

        <button
          type="button"
          className="relative flex size-11 items-center justify-center rounded-md text-foreground md:hidden"
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </div>

      <div
        className={cn(
          "md:hidden overflow-hidden border-t border-border bg-background transition-[max-height,opacity] duration-200 ease-[cubic-bezier(0.22,1,0.36,1)]",
          open ? "max-h-[420px] opacity-100" : "max-h-0 border-transparent opacity-0",
        )}
      >
        <nav className="flex flex-col gap-1 px-4 py-4" aria-label="Mobile">
          {NAV.map((item) => (
            <Link
              key={item.hash}
              to={`/#${item.hash}`}
              onClick={() => setOpen(false)}
              className="flex min-h-12 items-center rounded-md px-3 text-base font-medium text-foreground"
            >
              {item.label}
            </Link>
          ))}
          <Button asChild className="mt-2 w-full">
            <Link to="/#contact" onClick={() => setOpen(false)}>
              Start Growing for $375/mo
            </Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-card">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-14 sm:px-6 md:grid-cols-[1.4fr_1fr_1fr]">
        <div>
          <Wordmark />
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-muted">
            Affordable AI-assisted Google and Meta ads for small businesses that want more
            customers — without the headache of running campaigns themselves.
          </p>
        </div>
        <div>
          <p className="font-display text-sm tracking-[0.18em] text-chrome uppercase">Links</p>
          <ul className="mt-4 space-y-2.5 text-sm">
            {NAV.map((item) => (
              <li key={item.hash}>
                <Link to={`/#${item.hash}`} className="text-muted hover:text-flash">
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p className="font-display text-sm tracking-[0.18em] text-chrome uppercase">Legal</p>
          <ul className="mt-4 space-y-2.5 text-sm">
            <li>
              <Link to="/privacy" className="text-muted hover:text-flash">
                Privacy
              </Link>
            </li>
            <li>
              <Link to="/terms" className="text-muted hover:text-flash">
                Terms
              </Link>
            </li>
            <li>
              <a href="mailto:hello@greenflashads.com" className="text-muted hover:text-flash">
                hello@greenflashads.com
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-5 text-xs text-muted sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p>© {new Date().getFullYear()} Green Flash Advertising (GFA). All rights reserved.</p>
          <p className="tracking-[0.18em] uppercase">More clicks. More customers. More growth.</p>
        </div>
      </div>
    </footer>
  );
}

export function MobileCta() {
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const sync = () => {
      const target = document.getElementById("contact");
      if (!target) return;
      const top = target.getBoundingClientRect().top;
      setHidden(top < window.innerHeight * 0.72);
    };
    sync();
    window.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync);
    return () => {
      window.removeEventListener("scroll", sync);
      window.removeEventListener("resize", sync);
    };
  }, []);

  return (
    <div
      className={cn(
        "mobile-cta fixed inset-x-0 bottom-0 z-40 p-3 md:hidden transition-[transform,opacity] duration-200 ease-out",
        hidden
          ? "pointer-events-none translate-y-[120%] opacity-0"
          : "translate-y-0 opacity-100",
      )}
    >
      <Button asChild className="w-full shadow-[0_12px_40px_rgba(0,0,0,0.45)]">
        <Link to="/#contact">
          Start Growing for $375/mo
        </Link>
      </Button>
    </div>
  );
}

export function SiteChrome({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-svh flex-col bg-background text-foreground">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[60] focus:rounded-md focus:bg-flash focus:px-3 focus:py-2 focus:text-flash-fg"
      >
        Skip to content
      </a>
      <SiteHeader />
      <div className="flex-1">{children}</div>
      <SiteFooter />
    </div>
  );
}
