"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  Plane,
  LayoutDashboard,
  Radar,
  MessageSquare,
  Bot,
  BookOpen,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const STORAGE_KEY = "afois.sidebarCollapsed";

const items = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/ops", label: "Operations", icon: Radar },
  { href: "/chat", label: "AI Chat", icon: MessageSquare },
  { href: "/agents", label: "Ops Agent", icon: Bot },
  { href: "/rag", label: "Policy RAG", icon: BookOpen },
];

function useStatePersisted(key: string, defaultValue: boolean): readonly [boolean, (next: boolean | ((b: boolean) => boolean)) => void] {
  const [v, setV] = useState(defaultValue);
  useEffect(() => {
    try {
      const raw = localStorage.getItem(key);
      if (raw !== null) setV(raw === "1");
    } catch {
      /* ignore */
    }
  }, [key]);
  const setBoth = useCallback(
    (next: boolean | ((b: boolean) => boolean)) => {
      setV((prev) => {
        const n = typeof next === "function" ? (next as (b: boolean) => boolean)(prev) : next;
        try {
          localStorage.setItem(key, n ? "1" : "0");
        } catch {
          /* ignore */
        }
        return n;
      });
    },
    [key],
  );
  return [v, setBoth] as const;
}

export function AppSidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useStatePersisted(STORAGE_KEY, false);

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 76 : 220 }}
      transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
      className="relative hidden shrink-0 flex-col border-r border-white/10 bg-background/50 backdrop-blur-xl md:flex"
    >
      <div className="flex h-14 items-center gap-2 border-b border-white/10 px-3">
        {!collapsed ? (
          <Link href="/" className="flex flex-1 items-center gap-2 truncate font-semibold">
            <Plane className="h-5 w-5 shrink-0 text-cyan-400" />
            <span className="truncate tracking-tight">AFOIS</span>
          </Link>
        ) : (
          <Link
            href="/"
            className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-400 text-white"
          >
            <Plane className="h-4 w-4" aria-hidden />
          </Link>
        )}
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-2" aria-label="Sidebar">
        {items.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link key={href} href={href} title={collapsed ? label : undefined}>
              <motion.div
                whileHover={{ x: 2 }}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                  active
                    ? "bg-white/15 text-foreground"
                    : "text-muted-foreground hover:bg-white/5 hover:text-foreground",
                  collapsed && "justify-center px-2",
                )}
              >
                <Icon className="h-4 w-4 shrink-0" aria-hidden />
                {!collapsed && <span>{label}</span>}
              </motion.div>
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-white/10 p-2">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className={cn("w-full justify-center gap-2 text-muted-foreground", collapsed && "px-0")}
          aria-expanded={!collapsed}
          onClick={() => setCollapsed((x) => !x)}
        >
          {collapsed ? <PanelLeft className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          {!collapsed && <span className="text-xs">Collapse</span>}
        </Button>
      </div>
    </motion.aside>
  );
}
