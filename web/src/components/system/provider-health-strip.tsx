"use client";

import { Cpu, Gauge, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useLlmConfig } from "@/hooks/use-llm-config";

function Dot({ ok }: { ok: boolean }) {
  return (
    <span
      className={`h-2 w-2 rounded-full ${ok ? "bg-emerald-500/85" : "bg-muted-foreground/30"}`}
      aria-hidden
    />
  );
}

/** Demo-first provider strip — information only, avoids alarming error styling during portfolio runs. */
export function ProviderHealthStrip() {
  const q = useLlmConfig();

  if (q.isLoading) {
    return <Skeleton className="h-9 w-full max-w-3xl rounded-lg" />;
  }

  if (q.isError) {
    return (
      <p className="text-xs text-muted-foreground">
        LLM status refresh skipped — dashboards and relational reads still load normally.
      </p>
    );
  }

  const c = q.data!;

  return (
    <div className="flex flex-wrap items-center gap-2 py-2 text-xs" aria-label="LLM providers">
      <span className="flex items-center gap-1 text-muted-foreground">
        <Cpu className="h-3 w-3" aria-hidden />
        Model routing
      </span>
      <Badge variant="secondary" className="gap-1.5 rounded-full px-2.5 py-0.5 font-normal">
        Active: <span className="font-semibold capitalize text-foreground">{c.llm_provider}</span>
      </Badge>
      <Badge variant="outline" className="rounded-full px-2 font-normal">
        {c.llm_model}
      </Badge>
      <Badge variant="outline" className="cursor-default gap-1.5 rounded-full px-2 font-normal">
        <Dot ok={c.openai_ready} />
        OpenAI configured
      </Badge>
      <Badge variant="outline" className="cursor-default gap-1.5 rounded-full px-2 font-normal">
        <Dot ok={c.gemini_ready} />
        Gemini configured
      </Badge>
      {c.dual_provider_ready && (
        <Badge variant="outline" className="rounded-full border-dashed px-2 font-normal text-muted-foreground">
          Alternate provider keys available · switch via <code className="text-[10px]">LLM_PROVIDER</code>
        </Badge>
      )}
      {c.llm_auto_failover ? (
        <Badge className="gap-1 rounded-full border border-amber-500/30 bg-amber-500/10 font-normal">
          <Zap className="h-3 w-3" aria-hidden />
          experimental failover
        </Badge>
      ) : null}
      {c.rate_limit_fallback_configured && (
        <Badge variant="secondary" className="gap-1 rounded-full px-2 font-normal text-muted-foreground">
          <Gauge className="h-3 w-3" aria-hidden />
          recruiter soft responses on quota
        </Badge>
      )}
    </div>
  );
}
