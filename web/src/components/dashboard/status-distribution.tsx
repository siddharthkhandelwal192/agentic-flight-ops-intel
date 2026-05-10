"use client";

import { GlassPanel } from "@/components/ui/glass-panel";
import { motion } from "framer-motion";

export function StatusDistribution({ byStatus }: { byStatus: Record<string, number> }) {
  const entries = Object.entries(byStatus).sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...entries.map(([, v]) => v));

  if (entries.length === 0) {
    return (
      <GlassPanel className="p-6">
        <p className="text-sm text-muted-foreground">No flight rows loaded yet.</p>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel className="p-6">
      <h3 className="text-sm font-semibold tracking-tight">Status distribution</h3>
      <p className="mt-1 text-xs text-muted-foreground">
        Quick read on operational mix from the latest `/v1/ops/flights` pull.
      </p>
      <ul className="mt-5 space-y-3" aria-label="Flights by status">
        {entries.map(([status, count], i) => (
          <motion.li
            key={status}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className="space-y-1"
          >
            <div className="flex justify-between text-xs">
              <span className="font-medium capitalize">{status}</span>
              <span className="tabular-nums text-muted-foreground">{count}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-white/10">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400"
                initial={{ width: 0 }}
                animate={{ width: `${(count / max) * 100}%` }}
                transition={{ duration: 0.5, delay: i * 0.05 }}
              />
            </div>
          </motion.li>
        ))}
      </ul>
    </GlassPanel>
  );
}
