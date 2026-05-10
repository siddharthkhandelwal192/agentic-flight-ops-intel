"use client";

import { useState } from "react";
import { useFlights } from "@/hooks/use-flights";
import { summarizeFlights } from "@/lib/flight-metrics";
import { StatCards } from "@/components/dashboard/stat-cards";
import { FlightsTable } from "@/components/dashboard/flights-table";
import { StatusDistribution } from "@/components/dashboard/status-distribution";
import { OpsAlerts } from "@/components/dashboard/ops-alerts";
import { ApiStatusBanner } from "@/components/system/api-status-banner";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function OpsPage() {
  const [airline, setAirline] = useState("");
  const code = airline.trim().toUpperCase() || undefined;
  const flightsQ = useFlights(120, code);
  const flights = flightsQ.data ?? [];
  const metrics = summarizeFlights(flights);

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Flight operations</h1>
        <p className="text-sm text-muted-foreground max-w-2xl">
          Pulled from <code className="text-xs">GET /v1/ops/flights</code>. Filter by IATA airline
          code; data refreshes on an efficient cache window.
        </p>
      </div>
      <ApiStatusBanner />

      <div className="flex flex-col gap-2 sm:max-w-xs">
        <Label htmlFor="airline-filter">Airline code (optional)</Label>
        <Input
          id="airline-filter"
          placeholder="e.g. UA"
          value={airline}
          onChange={(e) => setAirline(e.target.value.replace(/[^a-zA-Z]/g, "").slice(0, 3))}
          className="rounded-xl border-white/15 bg-white/5 uppercase"
          aria-label="Airline IATA code filter"
        />
      </div>

      <StatCards
        loading={flightsQ.isLoading}
        total={metrics.total}
        active={metrics.active}
        delayed={metrics.delayed}
        weatherAlerts={metrics.weatherSkew}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <StatusDistribution byStatus={metrics.byStatus} />
        <OpsAlerts flights={flights} />
      </div>

      <FlightsTable flights={flights} loading={flightsQ.isLoading} />

      {flightsQ.isError && (
        <p className="text-sm text-destructive">Failed to load flights from the API.</p>
      )}
    </div>
  );
}
