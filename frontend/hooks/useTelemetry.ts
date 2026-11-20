/**
 * momus404 — hooks/useTelemetry.ts
 * Polls edge device telemetry, GPU utilization, and Laya latency metrics.
 */

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import type { Telemetry } from "@/types";

export function useTelemetry(intervalMs = 1200) {
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);

  useEffect(() => {
    let mounted = true;

    const poll = async () => {
      try {
        const data = await apiClient.getTelemetry();
        if (mounted) setTelemetry(data);
      } catch {
        // Suppress transient network errors
      }
    };

    poll();
    const timer = setInterval(poll, intervalMs);

    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, [intervalMs]);

  return { telemetry };
}
