import { apiFetch } from "@/lib/api-client";
import type {
  AgentInvokeRequest,
  AgentInvokeResponse,
  ChatCompletionRequest,
  ChatCompletionResponse,
} from "@/types/api";

export async function postChat(body: ChatCompletionRequest): Promise<ChatCompletionResponse> {
  return apiFetch<ChatCompletionResponse>("/v1/llm/chat", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function postOperationsAgent(
  body: AgentInvokeRequest,
): Promise<AgentInvokeResponse> {
  return apiFetch<AgentInvokeResponse>("/v1/llm/agents/operations", {
    method: "POST",
    body: JSON.stringify(body),
    retries: 2,
  });
}
