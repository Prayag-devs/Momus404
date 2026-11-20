/**
 * momus404 — lib/websocket-client.ts
 * Resilient WebSocket client with automatic reconnection, heartbeat handling,
 * and multi-subscriber fanout.
 */

import { WS_BASE_URL } from "./config";
import type { LogEvent } from "@/types";

export type LogHandler = (event: LogEvent) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private handlers: Set<LogHandler> = new Set();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private shouldReconnect = true;
  private reconnectAttempts = 0;

  constructor(private url: string = WS_BASE_URL) {}

  connect(): void {
    if (typeof window === "undefined") return;
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        console.log("[WebSocketClient] Connected to:", this.url);
      };

      this.ws.onmessage = (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data as string);
          if (data.type === "heartbeat") {
            this.ws?.send("ping");
            return;
          }
          if (data.type === "pong") return;

          const event = data as LogEvent;
          this.handlers.forEach((handler) => handler(event));
        } catch {
          // ignore non-JSON messages
        }
      };

      this.ws.onclose = () => {
        if (this.shouldReconnect) {
          const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), 10000);
          this.reconnectAttempts++;
          this.reconnectTimer = setTimeout(() => this.connect(), delay);
        }
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };
    } catch (err) {
      console.warn("[WebSocketClient] Connection failed:", err);
    }
  }

  subscribe(handler: LogHandler): () => void {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.handlers.clear();
  }
}
