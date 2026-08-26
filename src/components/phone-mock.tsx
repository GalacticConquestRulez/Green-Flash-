export function PhoneMock() {
  return (
    <div className="relative mx-auto w-[260px] sm:w-[280px]">
      <div className="absolute -left-16 top-10 hidden rounded-lg bg-card px-3 py-2 hairline lg:block">
        <p className="text-[10px] uppercase tracking-[0.16em] text-muted">Platforms</p>
        <p className="text-sm font-semibold text-foreground">Meta + Google</p>
      </div>
      <div className="absolute -right-14 bottom-24 hidden rounded-lg bg-card px-3 py-2 hairline lg:block">
        <p className="text-[10px] uppercase tracking-[0.16em] text-muted">Tracking</p>
        <p className="text-sm font-semibold text-foreground">HYROS live</p>
      </div>

      <div className="relative overflow-hidden rounded-[2rem] bg-card-2 p-2 shadow-[0_30px_80px_rgba(0,0,0,0.55)] hairline-flash">
        <div className="overflow-hidden rounded-[1.55rem] bg-background">
          <div className="flex items-center justify-between px-5 pt-3 text-[10px] text-muted">
            <span>9:41</span>
            <span className="mx-auto h-4 w-20 rounded-full bg-card-2" />
            <span>5G</span>
          </div>
          <div className="px-3 pb-4 pt-3">
            <p className="px-1 text-[11px] font-medium uppercase tracking-[0.2em] text-muted">
              Sponsored · Meta
            </p>
            <div className="mt-2 overflow-hidden rounded-xl bg-card">
              <img
                src="/owner-cafe.jpg"
                alt="Cafe owner reviewing a phone"
                className="photo h-40 w-full object-cover"
              />
              <div className="space-y-2 p-3">
                <p className="text-[13px] font-semibold leading-snug text-foreground">
                  Busy this week? Walk in. Coffee is on us for first-timers.
                </p>
                <p className="text-[11px] text-muted">Your photos. Our ads. Their visit.</p>
                <div className="flex h-9 items-center justify-center rounded-md bg-flash text-xs font-bold text-flash-fg">
                  Get offer
                </div>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-2">
              {[
                ["Meta", "On"],
                ["Google", "On"],
                ["AI", "On"],
              ].map(([k, v]) => (
                <div key={k} className="rounded-md bg-card px-2 py-2 text-center hairline">
                  <p className="text-[9px] uppercase tracking-[0.14em] text-muted">{k}</p>
                  <p className="font-display text-sm text-flash tabular-nums">{v}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
