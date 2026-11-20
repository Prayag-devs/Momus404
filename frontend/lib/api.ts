/**
 * momus404 — lib/api.ts (Backward-Compatibility Facade)
 * Re-exports typed API methods, WebSocket clients, and domain interfaces.
 */

import { apiClient } from "./api-client";
import { WebSocketClient } from "./websocket-client";

export * from "@/types";
export { apiClient };
export { WebSocketClient as LogStream };

export const getHealth = apiClient.getHealth;
export const getTelemetry = apiClient.getTelemetry;
export const uploadSpec = apiClient.uploadSpec;
export const ingest = apiClient.ingest;
export const runAgent = apiClient.runAgent;
export const cancelRun = apiClient.cancelRun;
export const getStatus = apiClient.getStatus;
export const generateTest = apiClient.generateTest;
export const localCheck = apiClient.localCheck;
export const downloadReport = apiClient.downloadReport;
