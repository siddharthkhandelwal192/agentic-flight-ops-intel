"use client";

import type { FlightRead } from "@/types/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Skeleton } from "@/components/ui/skeleton";
import { isDelayedFlight } from "@/lib/flight-metrics";

function formatDt(iso: string | null) {
  if (!iso) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

export function FlightsTable({
  flights,
  loading,
}: {
  flights: FlightRead[];
  loading?: boolean;
}) {
  if (loading) {
    return (
      <GlassPanel className="overflow-hidden">
        <div className="p-4 space-y-3">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-48 w-full" />
        </div>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel className="overflow-hidden">
      <div className="border-b border-white/10 px-4 py-3">
        <h3 className="text-sm font-semibold">Flight board</h3>
        <p className="text-xs text-muted-foreground">
          Relational snapshot from the API — sortable columns coming soon.
        </p>
      </div>
      <div className="max-h-[420px] overflow-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-white/10 hover:bg-transparent">
              <TableHead className="text-xs">Flight</TableHead>
              <TableHead className="text-xs">Route</TableHead>
              <TableHead className="text-xs">STD</TableHead>
              <TableHead className="text-xs">STA</TableHead>
              <TableHead className="text-xs">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {flights.map((f) => {
              const delayed = isDelayedFlight(f);
              return (
                <TableRow key={f.id} className="border-white/10">
                  <TableCell className="font-mono text-xs">
                    {f.airline_code}
                    {f.flight_number}
                  </TableCell>
                  <TableCell className="text-xs">
                    {f.origin_iata} → {f.destination_iata}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {formatDt(f.scheduled_departure_utc)}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {formatDt(f.scheduled_arrival_utc)}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={delayed ? "destructive" : "secondary"}
                      className="text-[10px] font-normal capitalize"
                    >
                      {f.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </GlassPanel>
  );
}
