import { getApiBaseUrl } from "@/lib/config";
import { ApiError, isRetryableStatus } from "@/lib/api-errors";

const DEFAULT_RETRIES = 3;
const BASE_DELAY_MS = 400;
/** Avoid hung UI when the Next proxy cannot reach the API (TCP stall, wrong AFOIS_BACKEND_URL). */
const DEFAULT_FETCH_TIMEOUT_MS = 12_000;

function abortAfter(ms: number): AbortSignal {
  if (typeof AbortSignal !== "undefined" && typeof AbortSignal.timeout === "function") {
    return AbortSignal.timeout(ms);
  }
  const c = new AbortController();
  setTimeout(() => c.abort(), ms);
  return c.signal;
}

function mergeAbortSignals(user: AbortSignal | undefined, deadline: AbortSignal): AbortSignal {
  if (!user) return deadline;
  if (typeof AbortSignal !== "undefined" && typeof AbortSignal.any === "function") {
    return AbortSignal.any([user, deadline]);
  }
  return deadline;
}

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

export type ApiFetchOptions = RequestInit & {
  retries?: number;
  /** Override default per-request timeout (ms). */
  timeoutMs?: number;
};

async function parseBody(res: Response): Promise<string> {
  const text = await res.text();
  return text;
}

function detailFromFastApi(body: string): string {
  try {
    const j = JSON.parse(body) as { detail?: unknown };
    if (typeof j.detail === "string") return j.detail;
    if (Array.isArray(j.detail)) return JSON.stringify(j.detail);
  } catch {
    /* ignore */
  }
  return body.slice(0, 500);
}

export async function apiFetch<T>(
  path: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  const { retries = DEFAULT_RETRIES, timeoutMs = DEFAULT_FETCH_TIMEOUT_MS, ...init } = options;
  const url = `${getApiBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`;
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }

  let lastError: unknown;
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const deadline = abortAfter(timeoutMs);
      const signal = mergeAbortSignals(init.signal ?? undefined, deadline);
      const res = await fetch(url, { ...init, headers, signal });
      const raw = await parseBody(res);
      if (!res.ok) {
        const msg = detailFromFastApi(raw) || res.statusText;
        const err = new ApiError(msg, res.status, raw);
        if (isRetryableStatus(res.status) && attempt < retries - 1) {
          lastError = err;
          await sleep(BASE_DELAY_MS * (attempt + 1));
          continue;
        }
        throw err;
      }
      if (!raw) return undefined as T;
      return JSON.parse(raw) as T;
    } catch (e) {
      lastError = e;
      if (e instanceof ApiError) throw e;
      const aborted =
        (e instanceof DOMException && e.name === "AbortError") ||
        (e instanceof Error && e.name === "TimeoutError");
      if (aborted) {
        throw new ApiError(
          "Request timed out — ensure the API is up (port 8000) and AFOIS_BACKEND_URL matches your backend.",
          408,
        );
      }
      if (attempt < retries - 1) {
        await sleep(BASE_DELAY_MS * (attempt + 1));
        continue;
      }
      throw e;
    }
  }
  throw lastError;
}
