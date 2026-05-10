"use client";

import { GlassPanel } from "@/components/ui/glass-panel";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, Info } from "lucide-react";
import type { FlightRead } from "@/types/api";
import { isDelayedFlight } from "@/lib/flight-metrics";

export function OpsAlerts({ flights }: { flights: FlightRead[] }) {
  const delayed = flights.filter(isDelayedFlight);
  const top = delayed.slice(0, 4);

  if (delayed.length === 0) {
    return (
      <GlassPanel className="p-5">
        <Alert className="border-emerald-500/30 bg-emerald-500/5">
          <Info className="h-4 w-4 text-emerald-500" />
          <AlertTitle>No delay alerts</AlertTitle>
          <AlertDescription className="text-muted-foreground">
            Current board shows no delayed flights under demo heuristics. Seed data or live feeds
            will populate this panel.
          </AlertDescription>
        </Alert>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel className="p-5 space-y-3">
      <h3 className="text-sm font-semibold">Operational alerts</h3>
      {top.map((f) => (
        <Alert key={f.id} variant="destructive" className="border-destructive/40 bg-destructive/5">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle className="text-sm">
            {f.airline_code}
            {f.flight_number} · {f.origin_iata}→{f.destination_iata}
          </AlertTitle>
          <AlertDescription className="text-xs capitalize text-muted-foreground">
            Status: {f.status}
          </AlertDescription>
        </Alert>
      ))}
      {delayed.length > top.length && (
        <p className="text-xs text-muted-foreground">
          +{delayed.length - top.length} more delayed flights on the board.
        </p>
      )}
    </GlassPanel>
  );
}
