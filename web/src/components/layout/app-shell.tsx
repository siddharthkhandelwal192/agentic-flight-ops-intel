import type { ReactNode } from "react";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { SiteHeader } from "@/components/layout/site-header";
import { ProviderHealthStrip } from "@/components/system/provider-health-strip";
import { TooltipProvider } from "@/components/ui/tooltip";
import { DemoModeProvider } from "@/providers/demo-mode";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <TooltipProvider delay={200}>
      <DemoModeProvider>
        <div className="relative flex min-h-screen overflow-x-hidden">
          <div
            className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(ellipse_90%_60%_at_50%_-15%,rgba(99,102,241,0.22),transparent_55%),radial-gradient(ellipse_70%_50%_at_100%_0%,rgba(6,182,212,0.12),transparent_50%),radial-gradient(ellipse_60%_40%_at_0%_100%,rgba(167,139,250,0.1),transparent_55%)]"
            aria-hidden
          />
          <div
            className="pointer-events-none fixed inset-0 -z-10 bg-background/80 dark:bg-background/90"
            aria-hidden
          />

          <AppSidebar />

          <div className="flex min-w-0 flex-1 flex-col">
            <SiteHeader />
            <div className="border-b border-white/10 bg-background/60 px-4 backdrop-blur-md sm:px-6">
              <ProviderHealthStrip />
            </div>
            <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">{children}</main>
          </div>
        </div>
      </DemoModeProvider>
    </TooltipProvider>
  );
}
