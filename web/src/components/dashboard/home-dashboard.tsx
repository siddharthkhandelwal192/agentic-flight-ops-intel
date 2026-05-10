"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, MessageSquare, Radar, RefreshCw, Search } from "lucide-react";
import { useFlights } from "@/hooks/use-flights";
import { summarizeFlights } from "@/lib/flight-metrics";
import { StatCards } from "@/components/dashboard/stat-cards";
import { StatusDistribution } from "@/components/dashboard/status-distribution";
import { FlightsTable } from "@/components/dashboard/flights-table";
import { OpsAlerts } from "@/components/dashboard/ops-alerts";
import { OpsMiniChart } from "@/components/dashboard/ops-mini-chart";
import { ApiStatusBanner } from "@/components/system/api-status-banner";
import { GlassPanel } from "@/components/ui/glass-panel";
import { cn } from "@/lib/utils";
import { Button, buttonVariants } from "@/components/ui/button";

export function HomeDashboard() {
  const flightsQ = useFlights(80);
  const flights = flightsQ.data ?? [];
  const metrics = summarizeFlights(flights);

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-2"
        >
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400/90">
            Agentic Flight Ops Intelligence
          </p>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Operations command center
          </h1>
          <p className="max-w-2xl text-sm text-muted-foreground sm:text-base">
            Live board data from your FastAPI service, paired with AI chat, LangGraph agents, and
            Chroma-backed policy search — a credible full-stack AI platform demo.
          </p>
        </motion.div>
        <ApiStatusBanner />
      </div>

      <div className="flex flex-wrap gap-3">
        <Link
          href="/chat"
          className={cn(buttonVariants({ variant: "default", size: "lg" }), "rounded-full gap-2")}
        >
          <MessageSquare className="h-4 w-4" />
          AI chat
          <ArrowRight className="h-3.5 w-3.5 opacity-80" />
        </Link>
        <Link
          href="/ops"
          className={cn(buttonVariants({ variant: "secondary", size: "lg" }), "rounded-full gap-2")}
        >
          <Radar className="h-4 w-4" />
          Full operations
        </Link>
        <Link
          href="/rag"
          className={cn(
            buttonVariants({ variant: "outline", size: "lg" }),
            "rounded-full gap-2 border-white/20",
          )}
        >
          <Search className="h-4 w-4" />
          Policy RAG
        </Link>
      </div>

      <StatCards
        loading={flightsQ.isLoading}
        total={metrics.total}
        active={metrics.active}
        delayed={metrics.delayed}
        weatherAlerts={metrics.weatherSkew}
      />

      <div className="grid gap-6 xl:grid-cols-3">
        <StatusDistribution byStatus={metrics.byStatus} />
        <OpsMiniChart byStatus={metrics.byStatus} />
        <OpsAlerts flights={flights} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_minmax(0,1fr)]">
        <FlightsTable flights={flights} loading={flightsQ.isLoading} />
        <GlassPanel className="p-6 space-y-3 h-fit">
          <h3 className="text-sm font-semibold">Why this ships</h3>
          <ul className="text-sm text-muted-foreground space-y-2 list-disc pl-4">
            <li>Glass surfaces, motion, and dark-first theming tuned for demo recordings.</li>
            <li>React Query handles retries, caching, and skeleton states against real APIs.</li>
            <li>Chat uses markdown + typing reveal; agent path surfaces intent metadata.</li>
          </ul>
        </GlassPanel>
      </div>

      {flightsQ.isError && (
        <div className="flex flex-wrap items-center gap-3 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3">
          <p className="text-sm text-destructive">
            Could not load flights. Is the API up on port 8000? (Default UI uses the Next proxy at{" "}
            <code className="text-xs">/afois-api</code>.)
          </p>
          <Button type="button" variant="outline" size="sm" onClick={() => void flightsQ.refetch()}>
            <RefreshCw className="h-3.5 w-3.5" />
            Retry
          </Button>
        </div>
      )}
    </div>
  );
}
