export type ChatRole = "system" | "user" | "assistant";

export interface ChatRoleMessage {
  role: ChatRole;
  content: string;
}

export interface ChatCompletionRequest {
  messages: ChatRoleMessage[];
  temperature?: number;
}

export interface ChatCompletionResponse {
  reply: string;
  model: string;
  provider?: string | null;
  latency_ms?: number | null;
  failover_used?: boolean;
}

export interface AgentInvokeRequest {
  messages: ChatRoleMessage[];
}

export interface AgentInvokeResponse {
  intent: string | null;
  reply: string;
  model: string;
}

export interface FlightRead {
  id: string;
  airline_code: string;
  flight_number: string;
  origin_iata: string;
  destination_iata: string;
  scheduled_departure_utc: string;
  scheduled_arrival_utc: string;
  actual_departure_utc: string | null;
  actual_arrival_utc: string | null;
  aircraft_tail: string | null;
  aircraft_type: string | null;
  status: string;
}

export interface RagSearchHit {
  metadata: Record<string, unknown>;
  snippet: string;
  distance: number | null;
}

export interface RagSearchResponse {
  query: string;
  hits: RagSearchHit[];
}

export interface OpsReadyResponse {
  status: string;
  database?: string;
  llm_configured?: boolean;
  llm_provider?: string;
}

export interface LlmConfigSnapshot {
  llm_provider: string;
  openai_ready: boolean;
  gemini_ready: boolean;
  llm_configured: boolean;
  llm_model: string;
  embedding_provider: string;
  llm_auto_failover?: boolean;
  rate_limit_fallback_configured?: boolean;
  dual_provider_ready?: boolean;
}
