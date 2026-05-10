import { ChatPanel } from "@/components/chat/chat-panel";
import { ApiStatusBanner } from "@/components/system/api-status-banner";

export const metadata = {
  title: "AI Chat — AFOIS Control",
};

export default function ChatPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">AI chat</h1>
        <p className="text-sm text-muted-foreground max-w-2xl">
          Stateless LLM completion and the LangGraph operations agent share a ChatGPT-style
          experience. History persists locally in your browser.
        </p>
      </div>
      <ApiStatusBanner />
      <ChatPanel defaultTab="llm" />
    </div>
  );
}
