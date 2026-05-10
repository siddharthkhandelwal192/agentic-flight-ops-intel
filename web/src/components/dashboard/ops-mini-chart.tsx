"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RTooltip,
  Cell,
} from "recharts";
import { GlassPanel } from "@/components/ui/glass-panel";

const COLORS = ["#6366f1", "#06b6d4", "#a78bfa", "#fbbf24", "#34d399", "#f472b6"];

export function OpsMiniChart({ byStatus }: { byStatus: Record<string, number> }) {
  const entries = Object.entries(byStatus)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, count]) => ({ name: name.length > 12 ? `${name.slice(0, 11)}…` : name, count }));

  if (entries.length === 0) {
    return null;
  }

  return (
    <GlassPanel className="overflow-hidden p-6">
      <div className="mb-4">
        <h3 className="text-sm font-semibold tracking-tight">Operational mix chart</h3>
        <p className="text-xs text-muted-foreground">Fleet status counts from synced flight rows.</p>
      </div>
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={entries} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <XAxis
              dataKey="name"
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              tickLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              tickLine={false}
            />
            <RTooltip
              contentStyle={{
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.12)",
                background: "rgba(15,23,42,0.92)",
              }}
              labelStyle={{ color: "#e2e8f0", fontSize: 11 }}
              itemStyle={{ fontSize: 12 }}
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
            />
            <Bar dataKey="count" radius={[8, 8, 4, 4]} maxBarSize={48}>
              {entries.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </GlassPanel>
  );
}
