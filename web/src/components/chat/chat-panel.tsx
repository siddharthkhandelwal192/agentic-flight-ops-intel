"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Send, Trash2, Bot, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { MarkdownMessage } from "@/components/chat/markdown-message";
import { useStreamingText } from "@/hooks/use-streaming-text";
import { toast } from "sonner";
import { postChat, postOperationsAgent } from "@/services/llm";
import { ApiError } from "@/lib/api-errors";
import type { ChatRoleMessage } from "@/types/api";
import { cn } from "@/lib/utils";

const STORAGE_KEY = "afois.chat.messages.v1";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  mode: "llm" | "agent";
  model?: string;
  intent?: string | null;
  error?: string;
  provider?: string | null;
  latencyMs?: number | null;
  failoverUsed?: boolean;
};

function uid() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function loadStored(): ChatMessage[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as ChatMessage[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function AssistantBubble({
  text,
  animate,
  isError,
}: {
  text: string;
  animate: boolean;
  isError?: boolean;
}) {
  const streamed = useStreamingText(text, animate && !isError, 4, 12);
  const show = isError ? text : streamed;
  return (
    <div
      className={cn(
        "rounded-2xl rounded-tl-sm border px-4 py-3",
        isError
          ? "border-destructive/40 bg-destructive/10"
          : "border-white/10 bg-white/5 dark:bg-black/30",
      )}
    >
      {isError ? (
        <p className="text-sm text-destructive">{show}</p>
      ) : (
        <MarkdownMessage content={show} />
      )}
      {animate && !isError && streamed.length < text.length && (
        <span className="mt-2 inline-block h-2 w-2 animate-pulse rounded-full bg-cyan-400/80" />
      )}
    </div>
  );
}

export function ChatPanel({
  defaultTab = "llm",
  showTabs = true,
}: {
  defaultTab?: "llm" | "agent";
  showTabs?: boolean;
}) {
  const [tab, setTab] = useState<"llm" | "agent">(defaultTab);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [hydrated, setHydrated] = useState(false);
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages(loadStored());
    setHydrated(true);
  }, []);

  useEffect(() => {
    setTab(defaultTab);
  }, [defaultTab]);

  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-80)));
  }, [messages, hydrated]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const apiMessagesFor = useCallback(
    (mode: "llm" | "agent"): ChatRoleMessage[] => {
      const relevant = messages.filter((m) => m.mode === mode);
      const tail = relevant.slice(-20);
      return tail.map((m) => ({
        role: m.role,
        content: m.content,
      }));
    },
    [messages],
  );

  const send = async () => {
    const trimmed = input.trim();
    if (!trimmed || busy) return;
    const mode = tab;
    setBusy(true);
    const userMsg: ChatMessage = {
      id: uid(),
      role: "user",
      content: trimmed,
      mode,
    };
    setMessages((m) => [...m, userMsg]);
    setInput("");

    const assistantId = uid();
    setMessages((m) => [
      ...m,
      { id: assistantId, role: "assistant", content: "", mode, model: undefined },
    ]);

    try {
      if (mode === "llm") {
        const history = [...apiMessagesFor("llm"), { role: "user" as const, content: trimmed }];
        const res = await postChat({ messages: history, temperature: 0.2 });
        const lat = typeof res.latency_ms === "number" ? `${res.latency_ms}ms` : "";
        const meta = [res.provider && `provider: ${res.provider}`, res.failover_used && "failover"]
          .filter(Boolean)
          .join(" · ");
        toast.success(lat ? `Response · ${lat}` : "Response ready", {
          description: meta || undefined,
          duration: 3400,
        });
        setMessages((m) =>
          m.map((row) =>
            row.id === assistantId
              ? {
                  ...row,
                  content: res.reply,
                  model: res.model,
                  provider: res.provider ?? undefined,
                  latencyMs: res.latency_ms ?? undefined,
                  failoverUsed: !!res.failover_used,
                }
              : row,
          ),
        );
      } else {
        const history = [...apiMessagesFor("agent"), { role: "user" as const, content: trimmed }];
        const res = await postOperationsAgent({ messages: history });
        toast.success("Agent completed", {
          description: res.intent ? `intent · ${res.intent}` : undefined,
        });
        setMessages((m) =>
          m.map((row) =>
            row.id === assistantId
              ? { ...row, content: res.reply, model: res.model, intent: res.intent }
              : row,
          ),
        );
      }
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.message
          : e instanceof Error
            ? e.message
            : "Request failed.";
      toast.error(msg.slice(0, 120));
      setMessages((m) =>
        m.map((row) =>
          row.id === assistantId ? { ...row, content: msg, error: msg } : row,
        ),
      );
    } finally {
      setBusy(false);
    }
  };

  const clear = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  const filtered = useMemo(() => messages.filter((m) => m.mode === tab), [messages, tab]);

  const inner = (
    <div className="flex h-[min(720px,calc(100vh-12rem))] flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          {tab === "llm" ? (
            <>
              <Sparkles className="h-4 w-4 text-indigo-400" />
              Direct LLM completion — fast general answers.
            </>
          ) : (
            <>
              <Bot className="h-4 w-4 text-cyan-400" />
              LangGraph ops agent — SQL + policy tools.
            </>
          )}
        </div>
        <Button variant="ghost" size="sm" onClick={clear} className="gap-1 text-muted-foreground">
          <Trash2 className="h-3.5 w-3.5" />
          Clear history
        </Button>
      </div>

      <ScrollArea className="min-h-0 flex-1 rounded-2xl border border-white/10 bg-black/20 p-4">
        <div className="space-y-4 pr-3">
          {filtered.length === 0 && (
            <p className="text-center text-sm text-muted-foreground">
              Start a conversation — responses render as markdown with a typing reveal.
            </p>
          )}
          <AnimatePresence initial={false}>
            {filtered.map((m, idx) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}
              >
                <div
                  className={cn(
                    "max-w-[min(100%,36rem)] space-y-1",
                    m.role === "user" ? "text-right" : "text-left",
                  )}
                >
                  {m.role === "user" ? (
                    <div className="inline-block rounded-2xl rounded-tr-sm bg-gradient-to-br from-indigo-600 to-cyan-600 px-4 py-2.5 text-left text-sm text-white shadow-lg">
                      {m.content}
                    </div>
                  ) : (
                    <>
                      <AssistantBubble
                        text={m.content}
                        animate={!!m.content && idx === filtered.length - 1 && !m.error}
                        isError={!!m.error}
                      />
                      <div className="flex flex-wrap gap-2 px-1">
                        {m.model && (
                          <Badge variant="secondary" className="text-[10px] font-normal">
                            {m.model}
                          </Badge>
                        )}
                        {m.provider && tab === "llm" && (
                          <Badge variant="outline" className="text-[10px] font-normal capitalize">
                            {m.provider}
                          </Badge>
                        )}
                        {m.latencyMs != null && (
                          <Badge variant="outline" className="text-[10px] font-normal tabular-nums">
                            {m.latencyMs} ms
                          </Badge>
                        )}
                        {m.failoverUsed && (
                          <Badge className="text-[10px] font-normal bg-amber-500/20 text-amber-100">
                            failover
                          </Badge>
                        )}
                        {m.intent != null && m.intent !== "" && (
                          <Badge className="text-[10px] font-normal bg-indigo-500/20 text-indigo-200">
                            intent: {m.intent}
                          </Badge>
                        )}
                      </div>
                    </>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {busy && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Thinking with your configured provider…
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            tab === "llm"
              ? "Ask for a weather brief, operational summary…"
              : "Ask about delays, policies, station rules…"
          }
          className="min-h-[88px] flex-1 resize-none rounded-xl border-white/15 bg-white/5"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void send();
            }
          }}
          aria-label="Message"
        />
        <Button
          className="h-11 rounded-xl sm:h-[88px] sm:w-28"
          onClick={() => void send()}
          disabled={busy || !input.trim()}
        >
          {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          <span className="sr-only sm:not-sr-only sm:ml-2">Send</span>
        </Button>
      </div>
    </div>
  );

  if (!showTabs) {
    return <GlassPanel className="p-5">{inner}</GlassPanel>;
  }

  return (
    <GlassPanel className="p-5">
      <Tabs
        value={tab}
        onValueChange={(v) => setTab(v as "llm" | "agent")}
        className="flex flex-col gap-4"
      >
        <TabsList className="grid w-full max-w-md grid-cols-2 bg-white/10">
          <TabsTrigger value="llm" className="gap-1">
            <Sparkles className="h-3.5 w-3.5" />
            Assistant
          </TabsTrigger>
          <TabsTrigger value="agent" className="gap-1">
            <Bot className="h-3.5 w-3.5" />
            Ops agent
          </TabsTrigger>
        </TabsList>
        {inner}
      </Tabs>
    </GlassPanel>
  );
}
