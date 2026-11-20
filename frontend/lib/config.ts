/**
 * momus404 — lib/config.ts
 * Frontend environment settings and endpoints.
 */

const defaultHost =
  typeof window !== "undefined" && window.location.hostname === "127.0.0.1"
    ? "127.0.0.1"
    : "localhost";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || `http://${defaultHost}:8000`;

export const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL || `ws://${defaultHost}:8000/ws/logs`;

export const WS_SCREENCAST_URL =
  process.env.NEXT_PUBLIC_WS_SCREENCAST_URL || `ws://${defaultHost}:8000/ws/screencast`;

