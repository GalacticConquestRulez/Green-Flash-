import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Check,
  ListPlus,
  Pause,
  Play,
  Search,
  Server,
  SkipBack,
  SkipForward,
} from "lucide-react";
import { MobileCta, SiteChrome } from "@/components/chrome";
import { ContactForm } from "@/components/contact-form";
import { Button } from "@/components/ui/button";
import { ROUTE_META } from "@/lib/route-meta";
import { usePageMeta } from "@/lib/use-page-meta";

const WEB_APP = [
  "Built around your workflow — not a template bent to fit it",
  "Runs in the browser: nothing for your customers to install",
  "Your data, your accounts, your server",
  "Admin views, logins, and roles as the job needs them",
  "Deployed, secured, and monitored like our own",
];

const MULTI = [
  "One product shipped as iOS, Android, and web applications",
  "App Store and Google Play submission handled",
  "Shared backend, so every platform shows the same truth",
  "Push notifications, offline behavior, device features",
  "A rollout plan, not just a repository handover",
];

/* ------------------------------------------------------------------ */
/* The demo: our LodiStudios media-server logic, cut down to three     */
/* tracks and reskinned for Green Flash. Everything on the card works  */
/* — search, playback transport, the queue — as real application       */
/* state, which is the point: this is what "custom web app" means.     */
/* ------------------------------------------------------------------ */

const LIBRARY = [
  { id: 1, title: "Sunshine", artist: "LodiStudios", length: 192 },
  { id: 2, title: "Calling Your Name", artist: "LodiStudios", length: 227 },
  { id: 3, title: "Success", artist: "LodiStudios", length: 178 },
];

const mmss = (s: number) =>
  `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

function DemoPlayer() {
  const [current, setCurrent] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [query, setQuery] = useState("");
  const [queue, setQueue] = useState<number[]>([]);
  const queueRef = useRef(queue);
  queueRef.current = queue;

  const track = LIBRARY[current];

  useEffect(() => {
    if (!playing) return;
    const t = setInterval(() => {
      setElapsed((e) => {
        if (e + 1 < LIBRARY[current].length) return e + 1;
        // track finished: the queue wins, otherwise walk the library
        const q = queueRef.current;
        if (q.length > 0) {
          setQueue(q.slice(1));
          setCurrent(LIBRARY.findIndex((x) => x.id === q[0]));
        } else {
          setCurrent((c) => (c + 1) % LIBRARY.length);
        }
        return 0;
      });
    }, 1000);
    return () => clearInterval(t);
  }, [playing, current]);

  const jump = (dir: 1 | -1) => {
    setCurrent((c) => (c + dir + LIBRARY.length) % LIBRARY.length);
    setElapsed(0);
  };

  const select = (i: number) => {
    setCurrent(i);
    setElapsed(0);
    setPlaying(true);
  };

  const results = LIBRARY.filter((t) =>
    t.title.toLowerCase().includes(query.trim().toLowerCase()),
  );

  return (
    <div className="overflow-hidden rounded-2xl bg-card hairline-flash">
      {/* server chrome */}
      <div className="flex items-center justify-between border-b border-border px-5 py-3.5">
        <p className="flex items-center gap-2 font-display text-lg tracking-wide text-foreground">
          <Server className="size-4 text-flash" strokeWidth={1.75} />
          GF Media Server
        </p>
        <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-[0.16em] text-flash">
          <span className="relative flex size-2">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-flash opacity-60" />
            <span className="relative inline-flex size-2 rounded-full bg-flash" />
          </span>
          Online
        </p>
      </div>

      {/* search */}
      <div className="border-b border-border px-5 py-3">
        <label className="flex items-center gap-2.5 text-sm text-muted">
          <Search className="size-4 shrink-0" strokeWidth={1.75} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search the library…"
            className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted"
            aria-label="Search the demo library"
          />
        </label>
      </div>

      {/* library */}
      <ul className="divide-y divide-border">
        {results.length === 0 ? (
          <li className="px-5 py-4 text-sm text-muted">No tracks match “{query.trim()}”.</li>
        ) : (
          results.map((t) => {
            const i = LIBRARY.indexOf(t);
            const active = i === current;
            return (
              <li key={t.id} className={active ? "bg-flash/[0.06]" : undefined}>
                <div className="flex items-center gap-3 px-5 py-3">
                  <button
                    type="button"
                    onClick={() => (active ? setPlaying((p) => !p) : select(i))}
                    aria-label={active && playing ? `Pause ${t.title}` : `Play ${t.title}`}
                    className="flex size-9 shrink-0 items-center justify-center rounded-full border border-border text-foreground transition-colors duration-150 hover:border-flash hover:text-flash"
                  >
                    {active && playing ? (
                      <Pause className="size-4" />
                    ) : (
                      <Play className="ml-0.5 size-4" />
                    )}
                  </button>
                  <div className="min-w-0 flex-1">
                    <p className={`truncate text-sm font-semibold ${active ? "text-flash" : "text-foreground"}`}>
                      {t.title}
                    </p>
                    <p className="text-xs text-muted">{t.artist}</p>
                  </div>
                  {/* tiny equalizer, moving only while this row is playing */}
                  {active && playing ? (
                    <span className="flex h-4 items-end gap-0.5" aria-hidden="true">
                      <span className="eq-bar w-1 rounded-sm bg-flash" />
                      <span className="eq-bar w-1 rounded-sm bg-flash [animation-delay:120ms]" />
                      <span className="eq-bar w-1 rounded-sm bg-flash [animation-delay:240ms]" />
                    </span>
                  ) : null}
                  <span className="w-10 text-right text-xs tabular-nums text-muted">
                    {mmss(t.length)}
                  </span>
                  <button
                    type="button"
                    onClick={() => setQueue((q) => [...q, t.id])}
                    aria-label={`Queue ${t.title}`}
                    className="text-muted transition-colors duration-150 hover:text-flash"
                  >
                    <ListPlus className="size-4" />
                  </button>
                </div>
              </li>
            );
          })
        )}
      </ul>

      {/* transport */}
      <div className="border-t border-border px-5 py-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => jump(-1)}
              aria-label="Previous track"
              className="flex size-9 items-center justify-center rounded-full text-muted transition-colors duration-150 hover:text-foreground"
            >
              <SkipBack className="size-4" />
            </button>
            <button
              type="button"
              onClick={() => setPlaying((p) => !p)}
              aria-label={playing ? "Pause" : "Play"}
              className="flex size-11 items-center justify-center rounded-full bg-flash text-flash-fg transition-colors duration-150 hover:bg-flash-hot"
            >
              {playing ? <Pause className="size-5" /> : <Play className="ml-0.5 size-5" />}
            </button>
            <button
              type="button"
              onClick={() => jump(1)}
              aria-label="Next track"
              className="flex size-9 items-center justify-center rounded-full text-muted transition-colors duration-150 hover:text-foreground"
            >
              <SkipForward className="size-4" />
            </button>
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-baseline justify-between gap-3">
              <p className="truncate text-sm font-semibold text-foreground">{track.title}</p>
              <p className="text-xs tabular-nums text-muted">
                {mmss(elapsed)} / {mmss(track.length)}
              </p>
            </div>
            <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-border">
              <div
                className="h-full rounded-full bg-flash transition-[width] duration-500"
                style={{ width: `${(elapsed / track.length) * 100}%` }}
              />
            </div>
          </div>
        </div>
        <p className="mt-3 text-xs text-muted">
          {queue.length > 0
            ? `Up next: ${LIBRARY.find((t) => t.id === queue[0])?.title}${queue.length > 1 ? ` · ${queue.length - 1} more queued` : ""}`
            : "Queue is empty — tap + on a track."}
        </p>
      </div>
    </div>
  );
}

export function AppsPage() {
  usePageMeta(ROUTE_META["/apps"]);
  return (
    <SiteChrome>
      <main id="main" className="pb-20 md:pb-0">
        {/* ---------- hero ---------- */}
        <section className="relative overflow-hidden border-b border-border">
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute -right-24 top-10 size-[18rem] rounded-full bg-flash/10 blur-3xl md:size-[26rem]" />
          </div>
          <div className="relative mx-auto max-w-6xl px-4 pb-16 pt-10 text-center sm:px-6 md:pb-24 md:pt-16">
            <div className="stagger-in mx-auto max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                Custom app development
              </p>
              <h1 className="mt-4 font-display text-[2.7rem] font-semibold leading-[0.95] tracking-wide text-foreground sm:text-6xl md:text-7xl">
                Software built for you.
                <span className="mt-1 block text-flash">Web, iOS, and Android.</span>
              </h1>
              <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-chrome sm:text-lg">
                Our boutique tier: real applications designed and built around your business —
                from a custom web app to a full three-platform rollout.
              </p>
              <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row sm:items-center">
                <Button asChild>
                  <Link to="/apps#contact">
                    Get a Quote
                    <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline">
                  <Link to="/apps#demo">Try a Live Demo</Link>
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
                Scoped to the job. Quoted up front.
              </h2>
              <p className="mt-4 text-base leading-relaxed text-muted">
                Every application is different, so these are floors, not flat fees — you get a
                written quote before anything is built.
              </p>
            </div>

            <div className="mx-auto mt-12 grid max-w-5xl gap-4 md:grid-cols-2">
              <div className="flex flex-col rounded-2xl bg-card p-6 hairline sm:p-8">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                  Custom web apps
                </p>
                <p className="mt-2 font-display text-6xl tracking-wide text-foreground">
                  <span className="text-2xl text-muted">from </span>$1,249
                </p>
                <p className="mt-2 text-sm text-chrome">
                  A real application in the browser — dashboards, portals, booking systems, internal
                  tools, media servers.
                </p>
                <ul className="mt-7 space-y-3">
                  {WEB_APP.map((item) => (
                    <li key={item} className="flex items-start gap-2.5 text-sm text-chrome">
                      <Check className="mt-0.5 size-4 shrink-0 text-flash" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="relative flex flex-col rounded-2xl bg-card p-6 hairline-flash sm:p-8">
                <p className="absolute right-6 top-6 rounded-full bg-flash/10 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.16em] text-flash sm:right-8 sm:top-8">
                  Full rollout
                </p>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                  Multi-platform apps
                </p>
                <p className="mt-2 font-display text-6xl tracking-wide text-foreground">
                  <span className="text-2xl text-muted">from </span>$12,499
                </p>
                <p className="mt-2 text-sm text-chrome">
                  One product, everywhere your customers are — an iOS, Android, and web application
                  rollout on a shared backend.
                </p>
                <ul className="mt-7 space-y-3">
                  {MULTI.map((item) => (
                    <li key={item} className="flex items-start gap-2.5 text-sm text-chrome">
                      <Check className="mt-0.5 size-4 shrink-0 text-flash" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- live demo ---------- */}
        <section id="demo" className="scroll-mt-20 py-20 md:py-28">
          <div className="mx-auto grid max-w-6xl items-center gap-12 px-4 sm:px-6 md:grid-cols-[1fr_1.05fr]">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-flash">
                Proof, not promises
              </p>
              <h2 className="mt-3 font-display text-4xl font-semibold tracking-wide text-foreground sm:text-5xl">
                Try one right here.
              </h2>
              <p className="mt-5 text-base leading-relaxed text-muted">
                We build and run custom media servers and streaming software — this widget runs the
                same application logic as our LodiStudios platform, cut down to a three-track
                library and reskinned for Green Flash.
              </p>
              <p className="mt-4 text-base leading-relaxed text-muted">
                Everything on the card works: search the library, play and pause, skip, queue
                tracks and watch them take over when the current one ends. That responsiveness is
                the difference between a website and an application.
              </p>
              <ul className="mt-8 space-y-3 text-sm text-chrome">
                {[
                  "Modeled on streaming software we run in production",
                  "Live application state — no page reloads",
                  "Yours would run your logic, not our jukebox",
                ].map((t) => (
                  <li key={t} className="flex items-center gap-2.5">
                    <Check className="size-4 text-flash" />
                    {t}
                  </li>
                ))}
              </ul>
            </div>
            <DemoPlayer />
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
                Tell us about the app.
              </h2>
              <p className="mt-5 max-w-md text-base leading-relaxed text-muted">
                What it should do, who uses it, and where it needs to run. We'll come back with a
                scope, a written quote, and a timeline.
              </p>
              <ul className="mt-8 space-y-3 text-sm text-chrome">
                {[
                  "Custom web apps from $1,249",
                  "iOS + Android + web rollouts from $12,499",
                  "Quoted in writing before work begins",
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
                interest="Apps"
                prompt="What should the app do?"
                placeholder="Describe the app — what it does, who uses it, and whether you need web only or iOS and Android too."
                submitLabel="Get my app quote"
              />
            </div>
          </div>
        </section>
      </main>
      <MobileCta label="Get an App Quote" to="/apps#contact" />
    </SiteChrome>
  );
}
