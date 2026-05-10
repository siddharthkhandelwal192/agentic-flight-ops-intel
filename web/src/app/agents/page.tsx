import { AgentAnalysisView } from "@/components/agents/agent-analysis";
import { ApiStatusBanner } from "@/components/system/api-status-banner";

export const metadata = {
  title: "Ops Agent — AFOIS Control",
};

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Agent analysis</h1>
        <p className="text-sm text-muted-foreground max-w-2xl">
          Grounded operations Q&amp;A via <code className="text-xs">POST /v1/llm/agents/operations</code>
          . The side panel reflects the latest routed intent and model metadata.
        </p>
      </div>
      <ApiStatusBanner />
      <AgentAnalysisView />
    </div>
  );
}
