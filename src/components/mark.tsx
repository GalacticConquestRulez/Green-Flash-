/**
 * The real GF mark (chrome G + green bolt F), trimmed from the brand art with
 * a transparent ground so it sits on the header blur without a plate. The
 * wordmark text stays HTML rather than baked into the image: it scales crisp,
 * reads to screen readers, and keeps the header's own type in charge.
 */
export function Wordmark({ compact = false }: { compact?: boolean }) {
  return (
    <span className="group/mark flex items-center gap-2.5">
      <img
        src="/logo-mark.png"
        alt=""
        className="h-9 w-auto drop-shadow-[0_0_12px_rgba(108,255,46,0.28)] transition-[filter] duration-200 group-hover/mark:drop-shadow-[0_0_16px_rgba(108,255,46,0.5)] md:h-10"
        width={178}
        height={120}
        decoding="async"
      />
      <span className="leading-none">
        <span className="font-display text-[1.05rem] font-semibold tracking-[0.12em] text-chrome">
          GREEN <span className="text-flash">FLASH</span>
        </span>
        {!compact ? (
          <span className="mt-0.5 block text-[0.58rem] font-medium uppercase tracking-[0.28em] text-muted">
            Advertising
          </span>
        ) : null}
      </span>
    </span>
  );
}
