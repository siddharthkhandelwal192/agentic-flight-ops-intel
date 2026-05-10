"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchLlmConfig } from "@/services/ops";

export function useLlmConfig() {
  return useQuery({
    queryKey: ["llm-config"],
    queryFn: fetchLlmConfig,
    staleTime: 60_000,
    refetchInterval: 120_000,
  });
}
