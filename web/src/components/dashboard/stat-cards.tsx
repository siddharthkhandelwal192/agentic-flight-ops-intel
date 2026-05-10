"use client";

import { motion } from "framer-motion";
import { Activity, AlertTriangle, CloudRain, Plane } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Skeleton } from "@/components/ui/skeleton";

const cardMotion = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
};

export function StatCards(props: {
  active: number;
  delayed: number;
  weatherAlerts: number;
  total: number;
  loading?: boolean;
}) {
  const { active, delayed, weatherAlerts, total, loading } = props;

  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <GlassPanel key={i} className="p-5">
            <Skeleton className="mb-3 h-4 w-24" />
            <Skeleton className="h-9 w-16" />
          </GlassPanel>
        ))}
      </div>
    );
  }

  const items = [
    {
      label: "Tracked flights",
      value: total,
      icon: Plane,
      accent: "from-indigo-500/30 to-transparent",
    },
    {
      label: "Active / in-progress",
      value: active,
      icon: Activity,
      accent: "from-emerald-500/25 to-transparent",
    },
    {
      label: "Delayed",
      value: delayed,
      icon: AlertTriangle,
      accent: "from-amber-500/25 to-transparent",
    },
    {
      label: "Weather-flagged",
      value: weatherAlerts,
      icon: CloudRain,
      accent: "from-sky-500/25 to-transparent",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item, i) => (
        <motion.div
          key={item.label}
          variants={cardMotion}
          initial="initial"
          animate="animate"
          transition={{ delay: i * 0.06, duration: 0.35 }}
        >
          <GlassPanel className="relative overflow-hidden p-5">
            <div
              className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${item.accent} opacity-80`}
              aria-hidden
            />
            <div className="relative flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  {item.label}
                </p>
                <p className="mt-2 text-3xl font-semibold tabular-nums tracking-tight">
                  {item.value}
                </p>
              </div>
              <item.icon className="h-5 w-5 text-muted-foreground" aria-hidden />
            </div>
          </GlassPanel>
        </motion.div>
      ))}
    </div>
  );
}
