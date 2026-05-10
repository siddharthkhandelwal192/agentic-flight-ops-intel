/**
 * All browser-side API calls MUST go through `/afois-api/*`.
 *
 * Next rewrites that path server-side → `AFOIS_BACKEND_URL` (see `next.config.ts`).
 * We intentionally do **not** read `NEXT_PUBLIC_API_URL` here: a stale shell env or
 * old `.env.local` value forces `fetch("http://127.0.0.1:8000")` from the browser,
 * which breaks with **Failed to fetch** (CORS / mixed origin / QUIC quirks) even when
 * the API is healthy. The proxy avoids that entirely.
 */
export function getApiBaseUrl(): string {
  return "/afois-api";
}

/** Shown in header / status chip — never exposes a raw :8000 URL to imply browser calls. */
export function getApiConnectionHint(): string {
  return "Same-origin /afois-api (Next.js → backend)";
}
