import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 font-semibold tracking-wide transition-[transform,background-color,color,box-shadow,border-color] duration-150 ease-out focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-flash disabled:pointer-events-none disabled:opacity-50 active:not-disabled:scale-[0.96]",
  {
    variants: {
      variant: {
        primary:
          "bg-flash text-flash-fg shadow-[0_0_24px_color-mix(in_oklab,var(--color-flash)_28%,transparent)] hover:bg-flash-hot",
        outline:
          "border border-border bg-transparent text-foreground hover:border-flash/50 hover:text-flash",
        ghost: "text-muted hover:text-foreground",
        dark: "bg-foreground text-background hover:bg-chrome",
      },
      size: {
        sm: "h-10 rounded-md px-4 text-sm",
        md: "h-11 rounded-md px-5 text-sm",
        lg: "h-12 min-h-12 rounded-lg px-6 text-sm md:h-14 md:px-7",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "lg",
    },
  },
);

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  };

export function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return (
    <Comp className={cn(buttonVariants({ variant, size }), className)} {...props} />
  );
}
