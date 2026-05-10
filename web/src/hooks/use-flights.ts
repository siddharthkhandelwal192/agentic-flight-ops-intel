"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchFlights } from "@/services/ops";

export function useFlights(limit = 100, airline_code?: string) {
  return useQuery({
    queryKey: ["flights", limit, airline_code ?? ""],
    queryFn: () => fetchFlights({ limit, airline_code }),
    staleTime: 30_000,
  });
}
