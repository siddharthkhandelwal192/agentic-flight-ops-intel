"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { useRagSearch } from "@/hooks/use-rag-search";
import { cn } from "@/lib/utils";

function relevanceFromDistance(d: number | null): { label: string; className: string } {
  if (d == null) return { label: "score n/a", className: "bg-muted text-muted-foreground" };
  // Chroma L2: lower is better; map coarsely for UI
  if (d < 0.85) return { label: "high relevance", className: "bg-emerald-500/20 text-emerald-200" };
  if (d < 1.2) return { label: "medium", className: "bg-amber-500/20 text-amber-100" };
  return { label: "lower match", className: "bg-white/10 text-muted-foreground" };
}

export function RagSearchPanel() {
  const [q, setQ] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [k, setK] = useState(8);
  const search = useRagSearch(submitted, k, submitted.length > 1);

  const onSearch = () => {
    const t = q.trim();
    if (t.length < 2) return;
    setSubmitted(t);
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
      <GlassPanel className="flex flex-col gap-4 p-5">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">Semantic policy search</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Query the Chroma corpus ingested from <code className="text-xs">policy_documents</code>.
            Results include citations, metadata, and L2 distance (lower is closer).
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="e.g. minimum connection time international"
              className="h-11 rounded-xl border-white/15 bg-white/5 pl-9"
              aria-label="Search query"
              onKeyDown={(e) => e.key === "Enter" && onSearch()}
            />
          </div>
          <div className="flex items-center gap-2">
            <label htmlFor="rag-k" className="text-xs text-muted-foreground whitespace-nowrap">
              Top K
            </label>
            <Input
              id="rag-k"
              type="number"
              min={1}
              max={24}
              value={k}
              onChange={(e) => setK(Number(e.target.value) || 8)}
              className="h-11 w-20 rounded-xl border-white/15 bg-white/5"
            />
            <Button className="h-11 rounded-xl" onClick={onSearch} disabled={q.trim().length < 2}>
              Search
            </Button>
          </div>
        </div>

        <ScrollArea className="h-[min(520px,calc(100vh-16rem))] rounded-xl border border-white/10 p-3">
          {search.isFetching && (
            <div className="space-y-3">
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
            </div>
          )}
          {search.isError && (
            <p className="text-sm text-destructive">
              {(search.error as Error)?.message ?? "Search failed. Is Chroma seeded?"}
            </p>
          )}
          {search.data && !search.isFetching && (
            <ul className="space-y-4">
              {search.data.hits.map((hit, i) => {
                const meta = hit.metadata;
                const docCode = meta.doc_code != null ? String(meta.doc_code) : "—";
                const section = meta.section_ref != null ? String(meta.section_ref) : "";
                const rel = relevanceFromDistance(hit.distance);
                return (
                  <li
                    key={`${docCode}-${i}`}
                    className="rounded-xl border border-white/10 bg-black/20 p-4"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="outline" className="font-mono text-[10px]">
                        {docCode}
                      </Badge>
                      {section && (
                        <Badge variant="secondary" className="text-[10px] font-normal">
                          {section}
                        </Badge>
                      )}
                      <Badge className={cn("text-[10px] font-normal", rel.className)}>
                        {rel.label}
                        {hit.distance != null && (
                          <span className="ml-1 tabular-nums opacity-80">
                            (d={hit.distance.toFixed(3)})
                          </span>
                        )}
                      </Badge>
                    </div>
                    <p className="mt-3 text-sm leading-relaxed text-foreground/90">{hit.snippet}</p>
                    {meta.source_attribution != null && (
                      <p className="mt-2 text-xs text-muted-foreground">
                        Source: {String(meta.source_attribution)}
                      </p>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
          {!search.data && !search.isFetching && !search.isError && submitted && (
            <p className="text-sm text-muted-foreground">No results yet.</p>
          )}
        </ScrollArea>
      </GlassPanel>

      <GlassPanel className="h-fit p-5 space-y-3">
        <h3 className="text-sm font-semibold">Knowledge interface</h3>
        <p className="text-xs text-muted-foreground leading-relaxed">
          This screen is wired to <code className="text-[10px]">GET /v1/rag/search</code>. Use it to
          validate chunk quality, attribution fields, and retrieval scores before answers reach the
          ops agent.
        </p>
        <ul className="text-xs text-muted-foreground space-y-2 list-disc pl-4">
          <li>Distances are Chroma L2 — compare ranks, not absolute units across deployments.</li>
          <li>Snippets are truncated server-side (~750 chars).</li>
          <li>Rebuild corpus via admin API when policies change.</li>
        </ul>
      </GlassPanel>
    </div>
  );
}
