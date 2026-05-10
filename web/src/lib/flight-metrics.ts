import type { FlightRead } from "@/types/api";

export function isDelayedFlight(f: FlightRead): boolean {
  const s = f.status.toLowerCase();
  if (s.includes("delay")) return true;
  if (f.actual_departure_utc && f.scheduled_departure_utc) {
    return new Date(f.actual_departure_utc) > new Date(f.scheduled_departure_utc);
  }
  return false;
}

export function isActiveFlight(f: FlightRead): boolean {
  const s = f.status.toLowerCase();
  if (s.includes("cancel")) return false;
  if (s.includes("arriv") && s.includes("complete")) return false;
  return true;
}

export function weatherImpactEstimate(flights: FlightRead[]): number {
  // Demo heuristic: treat delayed at hub-ish statuses as weather-sensitive slice
  return flights.filter((f) => isDelayedFlight(f) && /weather|wx|atc/i.test(f.status)).length;
}

export function summarizeFlights(flights: FlightRead[]) {
  const active = flights.filter(isActiveFlight);
  const delayed = flights.filter(isDelayedFlight);
  const byStatus = flights.reduce<Record<string, number>>((acc, f) => {
    const k = f.status || "unknown";
    acc[k] = (acc[k] ?? 0) + 1;
    return acc;
  }, {});
  return {
    total: flights.length,
    active: active.length,
    delayed: delayed.length,
    byStatus,
    weatherSkew: weatherImpactEstimate(flights),
  };
}
