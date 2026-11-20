/**
 * momus404 — types/events.ts
 * WebSocket events and architecture node mapping types.
 */

export interface LogEvent {
  ts: string;
  source: string;
  run_id?: string;
  test_id?: string;
  step?: number;
  message: string;
  verdict?: string;
  data?: Record<string, unknown>;
}
