"use client";

import { Plane, Sparkles } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { getApiConnectionHint } from "@/lib/config";
import { MobileNav } from "@/components/layout/mobile-nav";

export function SiteHeader() {
  const { setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-background/75 backdrop-blur-xl">
      <div className="flex h-14 items-center justify-between gap-4 px-4 sm:px-6">
        <div className="flex min-w-0 items-center gap-2 md:hidden">
          <MobileNav />
          <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
            <motion.span
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-400 text-white shadow-lg shadow-indigo-500/25"
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.98 }}
            >
              <Plane className="h-4 w-4" aria-hidden />
            </motion.span>
            <span>AFOIS</span>
          </Link>
        </div>

        <div className="hidden min-w-0 flex-1 items-center md:flex">
          <p className="text-sm font-semibold tracking-tight">Flight operations control</p>
          <span
            className="ml-2 hidden truncate text-xs text-muted-foreground lg:inline xl:max-w-md"
            title={getApiConnectionHint()}
          >
            · {getApiConnectionHint()}
          </span>
        </div>

        <div className="flex shrink-0 items-center gap-2 md:ml-auto">
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full"
            aria-label={mounted && resolvedTheme === "dark" ? "Light mode" : "Dark mode"}
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
          >
            {mounted && resolvedTheme === "dark" ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>
          <Link
            href="/chat"
            className="inline-flex h-8 items-center gap-1 rounded-full bg-primary px-3 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            <Sparkles className="h-3.5 w-3.5" aria-hidden />
            Ask AI
          </Link>
        </div>
      </div>
    </header>
  );
}
