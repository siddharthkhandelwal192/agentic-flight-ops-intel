"use client";

import { Toaster } from "sonner";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function AppToaster() {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  return (
    <Toaster
      richColors
      closeButton
      position="bottom-right"
      theme={mounted && resolvedTheme === "dark" ? "dark" : "light"}
    />
  );
}
