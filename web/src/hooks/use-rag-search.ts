"use client";

import { useQuery } from "@tanstack/react-query";
import { searchPolicies } from "@/services/rag";

export function useRagSearch(query: string, k: number, enabled: boolean) {
  return useQuery({
    queryKey: ["rag", query, k],
    queryFn: () => searchPolicies(query, k),
    enabled: enabled && query.trim().length > 1,
    staleTime: 60_000,
  });
}
