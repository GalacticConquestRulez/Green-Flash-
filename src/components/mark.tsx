import { cn } from "@/lib/utils";

export function FlashMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 48 48"
      className={cn("text-flash", className)}
      fill="currentColor"
      aria-hidden
    >
      <path d="M27.2 3.2 8.6 25.2h13.1l-4.6 19.6L40.2 21.4H25.8L27.2 3.2Z" />
    </svg>
  );
}

export function Wordmark({ compact = false }: { compact?: boolean }) {
  return (
    <span className="flex items-center gap-2">
      <span className="flex size-9 items-center justify-center rounded-md bg-card hairline-flash">
        <FlashMark className="size-5" />
      </span>
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
