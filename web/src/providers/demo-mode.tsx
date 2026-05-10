"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { FlaskConical, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const STORAGE_KEY = "afois.demoBannerDismissed";

type Ctx = { dismiss: () => void };
const DemoCtx = createContext<Ctx | null>(null);

/** Top portfolio banner — dismiss persists in localStorage. */
export function DemoModeProvider({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    setMounted(true);
    try {
      setDismissed(localStorage.getItem(STORAGE_KEY) === "1");
    } catch {
      /* ignore */
    }
  }, []);

  const dismiss = useCallback(() => {
    try {
      localStorage.setItem(STORAGE_KEY, "1");
    } catch {
      /* ignore */
    }
    setDismissed(true);
  }, []);

  return (
    <DemoCtx.Provider value={{ dismiss }}>
      {mounted && !dismissed && (
        <div className="border-b border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-center text-xs text-cyan-100 md:text-sm">
          <FlaskConical className="-mt-px mr-2 inline-block h-4 w-4 align-middle text-cyan-300" aria-hidden />
          Demo portfolio mode — sample airline data · quotas may invoke graceful fallback responses.
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="ml-2 h-7 w-7 align-middle rounded-full text-cyan-200 hover:bg-cyan-500/20"
            aria-label="Dismiss demo banner"
            onClick={dismiss}
          >
            <X className="h-3.5 w-3.5" />
          </Button>
        </div>
      )}
      {children}
    </DemoCtx.Provider>
  );
}

export function useDemoBanner() {
  return useContext(DemoCtx);
}
