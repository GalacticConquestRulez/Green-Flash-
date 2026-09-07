import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Check,
  ListPlus,
  Pause,
  Play,
  RotateCcw,
  RotateCw,
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
/* The demo: our LodiStudios media-server logic reskinned for Green    */
/* Flash, streaming five real tracks from Maxgod's album 2TheMax.      */
/* Search, transport, and queue are live application state; the audio  */
/* element does the actual playing. If the files can't load (as in a   */
/* static preview), the card drops to a simulated "demo mode" instead  */
/* of breaking.                                                        */
/* ------------------------------------------------------------------ */

const ARTIST = "Maxgod";
const ALBUM = "2TheMax";

const LIBRARY = [
  { id: 1, title: "Games", file: "/audio/games.mp3", length: 224 },
  { id: 2, title: "Silver Lines", file: "/audio/silver-lines.mp3", length: 197 },
  { id: 3, title: "Shoot the Liar", file: "/audio/shoot-the-liar.mp3", length: 196 },
  { id: 4, title: "Root and Rise", file: "/audio/root-and-rise.mp3", length: 152 },
  { id: 5, title: "Dividends", file: "/audio/dividends.mp3", length: 118 },
];

const mmss = (s: number) =>
  `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

function DemoPlayer() {
  const [current, setCurrent] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [query, setQuery] = useState("");
  const [queue, setQueue] = useState<number[]>([]);
  const [fallback, setFallback] = useState(false);
  const [coverBroken, setCoverBroken] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const queueRef = useRef(queue);
  queueRef.current = queue;
  const currentRef = useRef(current);
  currentRef.current = current;

  const track = LIBRARY[current];

  const load = (i: number) => {
    const a = audioRef.current;
    if (!a) return;
    if (!a.currentSrc.endsWith(LIBRARY[i].file)) {
      a.src = LIBRARY[i].file;
    }
  };

  const startTrack = (i: number) => {
    setCurrent(i);
    setElapsed(0);
    const a = audioRef.current;
    if (a && !fallback) {
      load(i);
      a.play().catch(() => setFallback(true));
    }
    setPlaying(true);
  };

  const toggle = () => {
    const a = audioRef.current;
    if (fallback || !a) {
      setPlaying((p) => !p);
      return;
    }
    if (playing) {
      a.pause();
    } else {
      load(current);
      a.play().catch(() => {
        setFallback(true);
        setPlaying(true);
      });
    }
  };

  const advance = () => {
    const q = queueRef.current;
    if (q.length > 0) {
      setQueue(q.slice(1));
      startTrack(LIBRARY.findIndex((x) => x.id === q[0]));
    } else {
      startTrack((currentRef.current + 1) % LIBRARY.length);
    }
  };

  const jump = (dir: 1 | -1) =>
    startTrack((current + dir + LIBRARY.length) % LIBRARY.length);

  const seekTo = (t: number) => {
    const clamped = Math.max(0, Math.min(t, LIBRARY[currentRef.current].length - 1));
    const a = audioRef.current;
    if (a && !fallback && a.currentSrc) {
      a.currentTime = clamped;
    }
    setElapsed(clamped);
  };
  const nudge = (delta: number) =>
    seekTo((audioRef.current && !fallback ? audioRef.current.currentTime : elapsed) + delta);

  // Media Session: hands the track — artwork, title, transport — to the
  // OS, so lock screens, watches, Bluetooth displays, and CarPlay/Android
  // Auto "Now Playing" all show and control this player.
  useEffect(() => {
    if (!("mediaSession" in navigator)) return;
    const ms = navigator.mediaSession;
    ms.metadata = new MediaMetadata({
      title: LIBRARY[current].title,
      artist: ARTIST,
      album: ALBUM,
      artwork: [
        { src: "/audio/cover.jpg", sizes: "480x480", type: "image/jpeg" },
        { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
      ],
    });
    const set = (action: MediaSessionAction, fn: MediaSessionActionHandler | null) => {
      try { ms.setActionHandler(action, fn); } catch { /* older browsers */ }
    };
    set("play", () => audioRef.current?.play().catch(() => {}));
    set("pause", () => audioRef.current?.pause());
    set("previoustrack", () => startTrack((currentRef.current - 1 + LIBRARY.length) % LIBRARY.length));
    set("nexttrack", () => startTrack((currentRef.current + 1) % LIBRARY.length));
    set("seekbackward", (d) => nudge(-(d.seekOffset ?? 10)));
    set("seekforward", (d) => nudge(d.seekOffset ?? 10));
    set("seekto", (d) => { if (d.seekTime != null) seekTo(d.seekTime); });
    return () => {
      (["play", "pause", "previoustrack", "nexttrack", "seekbackward", "seekforward", "seekto"] as const)
        .forEach((a) => set(a, null));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current]);

  // keep the OS scrubber in sync with real playback
  useEffect(() => {
    if (!("mediaSession" in navigator) || fallback) return;
    try {
      navigator.mediaSession.setPositionState({
        duration: LIBRARY[current].length,
        position: Math.min(elapsed, LIBRARY[current].length),
        playbackRate: 1,
      });
    } catch { /* unsupported */ }
  }, [elapsed, current, fallback]);

  // Simulated clock, only when real audio is unavailable.
  useEffect(() => {
    if (!fallback || !playing) return;
    const t = setInterval(() => {
      setElapsed((e) => {
        if (e + 1 < LIBRARY[currentRef.current].length) return e + 1;
        advance();
        return 0;
      });
    }, 1000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fallback, playing]);

  const results = LIBRARY.filter((t) =>
    t.title.toLowerCase().includes(query.trim().toLowerCase()),
  );

  return (
    <div className="overflow-hidden rounded-2xl bg-card hairline-flash">
      {/* the actual player; the UI below is its remote control */}
      <audio
        ref={audioRef}
        preload="none"
        onTimeUpdate={(e) => setElapsed(e.currentTarget.currentTime)}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onEnded={advance}
        onError={() => setFallback(true)}
      />

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
          {fallback ? "Demo mode" : "Online"}
        </p>
      </div>

      {/* search */}
      <div className="border-b border-border px-5 py-3">
        <label className="flex items-center gap-2.5 text-sm text-muted">
          <Search className="size-4 shrink-0" strokeWidth={1.75} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search 2TheMax…"
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
                    onClick={() => (active ? toggle() : startTrack(i))}
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
                    <p className="text-xs text-muted">{ARTIST}</p>
                  </div>
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
        <div className="flex items-center gap-3">
          {/* album art; falls back to the GF mark until the 2TheMax cover ships */}
          <img
            src={coverBroken ? "/logo-mark.png" : "/audio/cover.jpg"}
            onError={() => setCoverBroken(true)}
            alt={`${ALBUM} album cover`}
            className="size-12 shrink-0 rounded-lg border border-border object-cover"
            loading="lazy"
          />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-foreground">{track.title}</p>
            <p className="truncate text-xs text-muted">
              {ARTIST} · {ALBUM}
            </p>
          </div>
          <p className="shrink-0 text-xs tabular-nums text-muted">
            {mmss(elapsed)} / {mmss(track.length)}
          </p>
        </div>

        {/* a real scrubber: drag or tap anywhere to seek */}
        <input
          type="range"
          min={0}
          max={track.length}
          step={1}
          value={Math.min(elapsed, track.length)}
          onChange={(e) => seekTo(Number(e.target.value))}
          aria-label="Seek"
          className="mt-3 block h-1.5 w-full cursor-pointer appearance-auto accent-flash"
        />

        <div className="mt-2 flex items-center justify-center gap-2">
          <button
            type="button"
            onClick={() => jump(-1)}
            aria-label="Previous track"
            className="flex size-10 items-center justify-center rounded-full text-muted transition-colors duration-150 hover:text-foreground"
          >
            <SkipBack className="size-4" />
          </button>
          <button
            type="button"
            onClick={() => nudge(-10)}
            aria-label="Rewind 10 seconds"
            className="flex size-10 items-center justify-center rounded-full text-muted transition-colors duration-150 hover:text-foreground"
          >
            <RotateCcw className="size-4" />
          </button>
          <button
            type="button"
            onClick={toggle}
            aria-label={playing ? "Pause" : "Play"}
            className="flex size-12 items-center justify-center rounded-full bg-flash text-flash-fg transition-colors duration-150 hover:bg-flash-hot"
          >
            {playing ? <Pause className="size-5" /> : <Play className="ml-0.5 size-5" />}
          </button>
          <button
            type="button"
            onClick={() => nudge(10)}
            aria-label="Forward 10 seconds"
            className="flex size-10 items-center justify-center rounded-full text-muted transition-colors duration-150 hover:text-foreground"
          >
            <RotateCw className="size-4" />
          </button>
          <button
            type="button"
            onClick={() => jump(1)}
            aria-label="Next track"
            className="flex size-10 items-center justify-center rounded-full text-muted transition-colors duration-150 hover:text-foreground"
          >
            <SkipForward className="size-4" />
          </button>
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
                same application logic as our LodiStudios platform, reskinned for Green Flash and
                streaming Maxgod's album 2TheMax.
              </p>
              <p className="mt-4 text-base leading-relaxed text-muted">
                Everything on the card is real: press play and the music streams. Search, pause,
                skip, rewind, scrub, queue — and once it's playing, your phone treats it like any
                music app: artwork and controls on the lock screen and in the car. Add the page to
                your home screen and it opens standalone, like something from the App Store.
              </p>
              <ul className="mt-8 space-y-3 text-sm text-chrome">
                {[
                  "Modeled on streaming software we run in production",
                  "Streams real audio — turn your sound on",
                  "Controls it from your lock screen, watch, or car's Now Playing display",
                  "Installs to your home screen and launches like a native app",
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
