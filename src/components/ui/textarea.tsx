import type { TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Textarea({
  className,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-28 w-full resize-y rounded-md border border-border bg-card px-3.5 py-3 text-sm text-foreground placeholder:text-muted/80 transition-[box-shadow,border-color] duration-150 outline-none focus:border-flash/50 focus:shadow-[0_0_0_3px_color-mix(in_oklab,var(--color-flash)_22%,transparent)]",
        className,
      )}
      {...props}
    />
  );
}
