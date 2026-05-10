"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchOpsReady } from "@/services/ops";

export function useOpsReady() {
  return useQuery({
    queryKey: ["ops-ready"],
    queryFn: fetchOpsReady,
    staleTime: 15_000,
    refetchInterval: 45_000,
  });
}
