/**
 * momus404 — hooks/useHealth.ts
 * Manages system and component health queries.
 */

import { useState, useEffect, useCallback } from "react";
import { apiClient } from "@/lib/api-client";
import type { HealthReport } from "@/types";

export function useHealth() {
  const [health, setHealth] = useState<HealthReport | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshHealth = useCallback(async () => {
    try {
      const data = await apiClient.getHealth();
      setHealth(data);
    } catch {
      // Backend may be starting or offline
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshHealth();
  }, [refreshHealth]);

  return { health, loading, refreshHealth };
}
