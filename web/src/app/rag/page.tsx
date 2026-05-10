import { RagSearchPanel } from "@/components/rag/rag-search-panel";
import { ApiStatusBanner } from "@/components/system/api-status-banner";

export const metadata = {
  title: "Policy RAG — AFOIS Control",
};

export default function RagPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Retrieval & policy corpus</h1>
        <p className="text-sm text-muted-foreground max-w-2xl">
          Semantic search over ingested airline policy chunks with transparent citations and
          distance scores.
        </p>
      </div>
      <ApiStatusBanner />
      <RagSearchPanel />
    </div>
  );
}
