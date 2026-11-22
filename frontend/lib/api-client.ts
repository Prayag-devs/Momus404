/**
 * momus404 — lib/api-client.ts
 * Type-safe HTTP API client for Momus404 backend services.
 */

import { API_BASE_URL } from "./config";
import type {
  HealthReport,
  Telemetry,
  TestCase,
  PlannedStep,
  RunStatus,
  IngestResponse,
  LogEvent,
  Verdict,
} from "@/types";

function getFallbackUrl(url: string): string {
  if (url.includes("localhost")) {
    return url.replace("localhost", "127.0.0.1");
  }
  if (url.includes("127.0.0.1")) {
    return url.replace("127.0.0.1", "localhost");
  }
  return url;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unknown network error");
      throw new Error(`API Error [${response.status}] ${path}: ${errorText}`);
    }

    return response.json() as Promise<T>;
  } catch (err: any) {
    if (err?.message?.includes("Failed to fetch") || err?.name === "TypeError") {
      const fallbackUrl = getFallbackUrl(url);
      if (fallbackUrl !== url) {
        try {
          const response = await fetch(fallbackUrl, {
            ...options,
            headers: {
              "Content-Type": "application/json",
              ...options?.headers,
            },
          });
          if (!response.ok) {
            const errorText = await response.text().catch(() => "Unknown network error");
            throw new Error(`API Error [${response.status}] ${path}: ${errorText}`);
          }
          return response.json() as Promise<T>;
        } catch {
          // rethrow original
        }
      }
    }
    throw err;
  }
}

export const apiClient = {
  async getHealth(): Promise<HealthReport> {
    return request<HealthReport>("/api/health");
  },

  async getTelemetry(): Promise<Telemetry> {
    return request<Telemetry>("/api/telemetry");
  },

  async uploadSpec(file: File): Promise<{ test_case_count: number; test_cases: TestCase[] }> {
    const formData = new FormData();
    formData.append("file", file);
    const url = `${API_BASE_URL}/api/upload-spec`;
    let res: Response;
    try {
      res = await fetch(url, { method: "POST", body: formData });
    } catch {
      res = await fetch(getFallbackUrl(url), { method: "POST", body: formData });
    }
    if (!res.ok) throw new Error(`Upload failed: ${await res.text()}`);
    return res.json();
  },

  async ingest(
    targetUrl: string,
    file: File | null,
    username: string,
    password: string,
    testCases?: TestCase[] | string
  ): Promise<IngestResponse> {
    const formData = new FormData();
    formData.append("target_url", targetUrl);
    formData.append("username", username);
    formData.append("password", password);
    if (file) formData.append("file", file);
    if (testCases) {
      formData.append(
        "test_cases_json",
        typeof testCases === "string" ? testCases : JSON.stringify(testCases)
      );
    }

    const url = `${API_BASE_URL}/api/ingest`;
    let res: Response;
    try {
      res = await fetch(url, { method: "POST", body: formData });
    } catch {
      res = await fetch(getFallbackUrl(url), { method: "POST", body: formData });
    }
    if (!res.ok) throw new Error(`Ingest failed: ${await res.text()}`);
    return res.json();
  },

  async runAgent(runId: string, dryRun = false): Promise<{ run_id: string; status: string }> {
    return request("/api/run-agent", {
      method: "POST",
      body: JSON.stringify({ run_id: runId, dry_run: dryRun }),
    });
  },

  async pauseRun(runId: string): Promise<{ run_id: string; paused: boolean }> {
    return request(`/api/pause/${runId}`, { method: "POST" });
  },

  async resumeRun(runId: string): Promise<{ run_id: string; resumed: boolean }> {
    return request(`/api/resume/${runId}`, { method: "POST" });
  },

  async stopRun(runId: string): Promise<{ run_id: string; stopped: boolean }> {
    return request(`/api/stop/${runId}`, { method: "POST" });
  },

  async cancelRun(runId: string): Promise<{ run_id: string; cancelled: boolean }> {
    return request(`/api/cancel/${runId}`, { method: "POST" });
  },

  async provideInput(runId: string, input: string): Promise<{ run_id: string; accepted: boolean }> {
    return request(`/api/provide-input/${runId}`, {
      method: "POST",
      body: JSON.stringify({ input }),
    });
  },

  async getStatus(runId: string): Promise<{ status: RunStatus; recent_logs: LogEvent[] }> {
    return request(`/api/status/${runId}`);
  },

  async generateTest(
    payload: Partial<TestCase> & { target_url?: string; username?: string; password?: string }
  ): Promise<{ test_case?: TestCase; steps: PlannedStep[] }> {
    return request("/api/generate-test", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async exportSpec(testCases: TestCase[]): Promise<Blob> {
    const url = `${API_BASE_URL}/api/export-spec`;
    let res: Response;
    try {
      res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(testCases),
      });
    } catch {
      res = await fetch(getFallbackUrl(url), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(testCases),
      });
    }
    if (!res.ok) throw new Error(`Export spec failed: ${await res.text()}`);
    return res.blob();
  },

  async localCheck(
    domSnippet: string,
    expectedCondition: string
  ): Promise<{ verdict: Verdict; confidence: number; latency_ms: number; mock: boolean }> {
    return request("/api/local-check", {
      method: "POST",
      body: JSON.stringify({ dom_snippet: domSnippet, expected_condition: expectedCondition }),
    });
  },

  downloadReport(runId: string, format = "md"): void {
    if (typeof window !== "undefined") {
      window.open(`${API_BASE_URL}/api/report/${runId}?fmt=${format}`, "_blank");
    }
  },
};
