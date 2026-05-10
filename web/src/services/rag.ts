import { apiFetch } from "@/lib/api-client";
import type { RagSearchResponse } from "@/types/api";

export async function searchPolicies(q: string, k = 8): Promise<RagSearchResponse> {
  const sp = new URLSearchParams({ q, k: String(k) });
  return apiFetch<RagSearchResponse>(`/v1/rag/search?${sp.toString()}`);
}
