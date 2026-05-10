"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Brain, GitBranch, Lightbulb } from "lucide-react";
import { ChatPanel, type ChatMessage } from "@/components/chat/chat-panel";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const PROMPTS = [
  "Summarize delay attributions in the last 24 hours; call out crew-related cases.",
  "Which station policies apply to minimum connect time for international itineraries?",
  "List delayed flights and group by primary cause if available in the data.",
  "What operational checks should we run before a bank push at a hub?",
];

const STORAGE_KEY = "afois.chat.messages.v1";

function readLastAgentInsight(): { intent: string | null; model?: string; excerpt: string } | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as ChatMessage[];
    const last = [...parsed].reverse().find((m) => m.mode === "agent" && m.role === "assistant");
    if (!last?.content) return null;
    return {
      intent: last.intent ?? null,
      model: last.model,
      excerpt: last.content.slice(0, 280) + (last.content.length > 280 ? "…" : ""),
    };
  } catch {
    return null;
  }
}

export function AgentAnalysisView() {
  const [, setTick] = useState(0);

  useEffect(() => {
    const id = window.setInterval(() => setTick((t) => t + 1), 2000);
    return () => window.clearInterval(id);
  }, []);

  const insight = readLastAgentInsight();

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(280px,1fr)]">
      <ChatPanel defaultTab="agent" showTabs={false} />

      <div className="space-y-4">
        <GlassPanel className="p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Brain className="h-4 w-4 text-indigo-400" />
            Reasoning snapshot
          </div>
          <p className="text-xs text-muted-foreground">
            The supervisor classifies <strong>delay</strong>, <strong>policy</strong>, or{" "}
            <strong>general</strong> intent before invoking tools. Latest assistant message (agent
            tab) drives this panel.
          </p>
          <div className="rounded-xl border border-white/10 bg-black/25 p-4 space-y-3">
            <div className="flex flex-wrap gap-2">
              {insight?.intent != null && insight.intent !== "" ? (
                <Badge className="bg-violet-500/25 text-violet-100">
                  Routed intent: {insight.intent}
                </Badge>
              ) : (
                <Badge variant="secondary">No intent yet — send an ops question</Badge>
              )}
              {insight?.model && (
                <Badge variant="outline" className="text-[10px] font-normal">
                  {insight.model}
                </Badge>
              )}
            </div>
            {insight?.excerpt ? (
              <p className="text-xs leading-relaxed text-muted-foreground">{insight.excerpt}</p>
            ) : (
              <p className="text-xs text-muted-foreground">
                Insights appear after your first successful agent response.
              </p>
            )}
          </div>
        </GlassPanel>

        <GlassPanel className="p-5 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <GitBranch className="h-4 w-4 text-cyan-400" />
            Prompt starters
          </div>
          <ul className="space-y-2">
            {PROMPTS.map((p) => (
              <motion.li key={p} whileHover={{ x: 2 }}>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-auto w-full justify-start whitespace-normal text-left text-xs text-muted-foreground hover:text-foreground"
                  onClick={() => {
                    navigator.clipboard.writeText(p);
                  }}
                >
                  <Lightbulb className="mr-2 h-3.5 w-3.5 shrink-0 text-amber-400" />
                  {p}
                </Button>
              </motion.li>
            ))}
          </ul>
          <p className="text-[10px] text-muted-foreground">Click to copy a prompt into your buffer.</p>
        </GlassPanel>
      </div>
    </div>
  );
}
