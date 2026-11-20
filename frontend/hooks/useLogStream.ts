/**
 * momus404 — hooks/useLogStream.ts
 * Manages WebSocket log streaming, buffer limits, and active architecture node pulses.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { WebSocketClient } from "@/lib/websocket-client";
import type { LogEvent } from "@/types";

export function useLogStream(maxLogs = 1000) {
  const [logEvents, setLogEvents] = useState<LogEvent[]>([]);
  const clientRef = useRef<WebSocketClient | null>(null);

  useEffect(() => {
    const client = new WebSocketClient();
    clientRef.current = client;

    const buffer: LogEvent[] = [];
    let flushTimer: ReturnType<typeof setTimeout> | null = null;

    const flush = () => {
      if (buffer.length === 0) return;
      const batch = buffer.splice(0, buffer.length);
      setLogEvents((prev) => {
        const combined = [...prev, ...batch];
        return combined.length > maxLogs ? combined.slice(-maxLogs) : combined;
      });
    };

    const unsubscribe = client.subscribe((event: LogEvent) => {
      buffer.push(event);

      if (!flushTimer) {
        flushTimer = setTimeout(() => {
          flushTimer = null;
          flush();
        }, 60);
      }
    });

    client.connect();

    return () => {
      if (flushTimer) {
        clearTimeout(flushTimer);
        flush();
      }
      unsubscribe();
      client.disconnect();
    };
  }, [maxLogs]);

  const clearLogs = useCallback(() => {
    setLogEvents([]);
  }, []);

  return { logEvents, clearLogs };
}
