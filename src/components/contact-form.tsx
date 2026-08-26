import { useState, type FormEvent } from "react";
import { CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const TYPES = [
  "Restaurant",
  "Retail",
  "Home Services",
  "Health",
  "Professional",
  "Automotive",
  "Real Estate",
  "Other",
] as const;

type Status = "idle" | "submitting" | "success";

const FORMSPREE_ENDPOINT = "https://formspree.io/f/mjybnjko";

export function ContactForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [type, setType] = useState<string>("");
  const [error, setError] = useState<string>("");

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const data = new FormData(e.currentTarget);
    const name = String(data.get("name") ?? "").trim();
    const email = String(data.get("email") ?? "").trim();
    const message = String(data.get("message") ?? "").trim();
    if (name.length < 2) {
      setError("Please add your name.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Enter a valid email so we can reach you.");
      return;
    }
    if (!type) {
      setError("Pick a business type.");
      return;
    }
    if (message.length < 8) {
      setError("Tell us a bit about what you want to grow.");
      return;
    }
    setStatus("submitting");
    data.set("businessType", type);
    try {
      const res = await fetch(FORMSPREE_ENDPOINT, {
        method: "POST",
        body: data,
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error("Formspree request failed");
      setStatus("success");
    } catch {
      setStatus("idle");
      setError("Something went wrong sending your request. Please email us directly at hello@greenflashads.com.");
    }
  }

  if (status === "success") {
    return (
      <div className="flex flex-col items-start gap-3 rounded-xl bg-card p-6 hairline-flash">
        <CheckCircle2 className="size-8 text-flash" />
        <h3 className="font-display text-2xl tracking-wide text-foreground">Request received.</h3>
        <p className="text-sm leading-relaxed text-muted">
          We’ll review your business and reach out to book a free strategy call. Watch for an email
          from Green Flash Advertising.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4" noValidate>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="name">Name</Label>
          <Input id="name" name="name" autoComplete="name" placeholder="Jordan Lee" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            placeholder="you@business.com"
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label>Business type</Label>
        <div className="flex flex-wrap gap-2" role="group" aria-label="Business type">
          {TYPES.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setType(t)}
              className={cn(
                "h-10 rounded-full px-3.5 text-sm font-medium transition-colors duration-150",
                type === t
                  ? "bg-flash text-flash-fg"
                  : "bg-card text-muted hairline hover:text-foreground",
              )}
            >
              {t}
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="message">What should we grow?</Label>
        <Textarea
          id="message"
          name="message"
          placeholder="Tell us about your business, current ads, and what more customers would mean."
        />
      </div>
      {error ? <p className="text-sm text-danger">{error}</p> : null}
      <Button type="submit" className="w-full" disabled={status === "submitting"}>
        {status === "submitting" ? "Sending…" : "Book a free strategy call"}
      </Button>
      <p className="text-center text-xs text-muted">
        No long-term contracts. We’ll reply by email — usually within one business day.
      </p>
    </form>
  );
}
