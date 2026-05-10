"use client";

import { useOpsReady } from "@/hooks/use-ops-ready";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { CheckCircle2, RefreshCw, XCircle } from "lucide-react";
import { getApiBaseUrl, getApiConnectionHint } from "@/lib/config";

function errorDetail(err: unknown): string {
  if (err instanceof Error) return err.message;
  return String(err);
}

export function ApiStatusBanner() {
  const q = useOpsReady();

  if (q.isLoading) {
    return <Skeleton className="h-14 w-full rounded-xl" />;
  }

  if (q.isError) {
    return (
      <Alert variant="destructive" className="border-destructive/50">
        <XCircle className="h-4 w-4" />
        <AlertTitle>API unreachable</AlertTitle>
        <AlertDescription className="space-y-3">
          <p className="text-xs">
            <code className="mr-2">{getApiConnectionHint()}</code>
            <code className="text-muted-foreground">{getApiBaseUrl()}</code>
          </p>
          <p className="text-xs text-muted-foreground">
            {errorDetail(q.error)} — The UI never calls{" "}
            <code className="text-[10px]">:8000</code> from the browser. Ensure the backend is up
            and set <code className="text-[10px]">AFOIS_BACKEND_URL</code> (or{" "}
            <code className="text-[10px]">BACKEND_URL</code>) for <code className="text-[10px]">next dev</code>{" "}
            / <code className="text-[10px]">next build</code> — default{" "}
            <code className="text-[10px]">http://127.0.0.1:8000</code>.
            Remove any <code className="text-[10px]">NEXT_PUBLIC_API_URL</code> from your shell (
            stale value forces broken direct browser calls).
          </p>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="gap-2 border-destructive/40"
            onClick={() => void q.refetch()}
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Retry connection
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  const data = q.data;
  const ok = data?.status === "ready";

  return (
    <Alert
      className={
        ok
          ? "border-emerald-500/40 bg-emerald-500/5"
          : "border-amber-500/40 bg-amber-500/5"
      }
    >
      {ok ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <XCircle className="h-4 w-4" />}
      <AlertTitle>{ok ? "Backend connected" : "Backend degraded"}</AlertTitle>
      <AlertDescription className="text-muted-foreground">
        Database: {String(data?.database ?? "—")} · LLM configured:{" "}
        {data?.llm_configured ? "yes" : "no"} ({String(data?.llm_provider ?? "—")})
      </AlertDescription>
    </Alert>
  );
}
