"use client";

import { useEffect, useState } from "react";

/**
 * Reveals text incrementally for a ChatGPT-like typing feel (backend returns full JSON, not SSE).
 */
export function useStreamingText(
  fullText: string,
  enabled: boolean,
  chunkSize = 3,
  tickMs = 14,
): string {
  const [shown, setShown] = useState("");

  useEffect(() => {
    if (!enabled) {
      setShown(fullText);
      return;
    }
    setShown("");
    if (!fullText) return;
    let i = 0;
    const id = window.setInterval(() => {
      i = Math.min(fullText.length, i + chunkSize);
      setShown(fullText.slice(0, i));
      if (i >= fullText.length) window.clearInterval(id);
    }, tickMs);
    return () => window.clearInterval(id);
  }, [fullText, enabled, chunkSize, tickMs]);

  return shown;
}
