import { apiFetch } from "@/lib/api-client";
import type { FlightRead, LlmConfigSnapshot, OpsReadyResponse } from "@/types/api";

export async function fetchFlights(params?: {
  limit?: number;
  airline_code?: string;
}): Promise<FlightRead[]> {
  const sp = new URLSearchParams();
  if (params?.limit != null) sp.set("limit", String(params.limit));
  if (params?.airline_code) sp.set("airline_code", params.airline_code);
  const q = sp.toString();
  return apiFetch<FlightRead[]>(`/v1/ops/flights${q ? `?${q}` : ""}`);
}

export async function fetchOpsReady(): Promise<OpsReadyResponse> {
  return apiFetch<OpsReadyResponse>("/v1/ops/ready");
}

export async function fetchLlmConfig(): Promise<LlmConfigSnapshot> {
  return apiFetch<LlmConfigSnapshot>("/v1/ops/llm-config");
}
