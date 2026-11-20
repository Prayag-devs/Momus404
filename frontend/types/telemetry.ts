/**
 * momus404 — types/telemetry.ts
 * Hardware monitoring, Laya judge, and system health types.
 */

export interface ComponentHealth {
  name: string;
  status: "real" | "mock" | "unavailable";
  detail: string;
}

export interface HealthReport {
  overall: string;
  components: ComponentHealth[];
  timestamp: string;
}

export interface Telemetry {
  device: string;
  gpu_util_pct: number;
  vram_used_mb: number;
  vram_total_mb: number;
  avg_latency_ms: number;
  last_latency_ms: number;
  tokens_saved: number;
  mock: boolean;
}
