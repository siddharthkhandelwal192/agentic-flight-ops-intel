import { cn } from "@/lib/utils";
import type { HTMLAttributes } from "react";

export function GlassPanel({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-white/15 bg-white/[0.06] shadow-[0_8px_32px_rgba(0,0,0,0.28)] backdrop-blur-xl",
        "dark:border-white/10 dark:bg-black/25",
        className,
      )}
      {...props}
    />
  );
}
