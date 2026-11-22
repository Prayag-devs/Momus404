/**
 * momus404 — hooks/useRunOrchestrator.ts
 * Manages test execution lifecycle, background status polling, and error boundaries.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { apiClient } from "@/lib/api-client";
import type { RunStatus, TestCase } from "@/types";

export function useRunOrchestrator(onRunComplete?: () => void) {
  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<RunStatus | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [parsedCases, setParsedCases] = useState<TestCase[]>([]);
  const [error, setError] = useState<string | null>(null);

  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const [isPaused, setIsPaused] = useState(false);

  // Status Polling Loop
  useEffect(() => {
    if (!isRunning || !runId) return;

    // Immediately fetch initial status
    apiClient.getStatus(runId)
      .then(({ status }) => {
        setRunStatus(status);
        if (status.is_paused !== undefined) setIsPaused(status.is_paused);
      })
      .catch((err) => console.warn("[useRunOrchestrator] Initial status fetch error:", err));

    pollTimerRef.current = setInterval(async () => {
      try {
        const { status } = await apiClient.getStatus(runId);
        setRunStatus(status);
        if (status.is_paused !== undefined) {
          setIsPaused(status.is_paused);
        }

        if (status.status !== "RUNNING" && status.status !== "IDLE" && !status.is_paused) {
          setIsRunning(false);
          setIsPaused(false);
          clearInterval(pollTimerRef.current!);
          onRunComplete?.();
        }
      } catch (err) {
        console.warn("[useRunOrchestrator] Polling error:", err);
      }
    }, 500);

    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [isRunning, runId, onRunComplete]);

  const executeRun = useCallback(
    async (
      targetUrl: string,
      file: File | null,
      username: string,
      password: string,
      dryRun = false
    ) => {
      setError(null);
      setIsRunning(true);
      setIsPaused(false);

      try {
        // Step 1: Ingest spec, url, credentials
        const ingestRes = await apiClient.ingest(targetUrl, file, username, password);
        const newRunId = ingestRes.run_id;
        setRunId(newRunId);
        setParsedCases(ingestRes.test_cases);

        // Step 2: Trigger orchestrated run
        await apiClient.runAgent(newRunId, dryRun);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Run execution failed";
        setError(message);
        setIsRunning(false);
        setIsPaused(false);
      }
    },
    []
  );

  const pauseActiveRun = useCallback(async () => {
    if (!runId) return;
    try {
      await apiClient.pauseRun(runId);
      setIsPaused(true);
    } catch (err: unknown) {
      console.error("[useRunOrchestrator] Pause error:", err);
    }
  }, [runId]);

  const resumeActiveRun = useCallback(async () => {
    if (!runId) return;
    try {
      await apiClient.resumeRun(runId);
      setIsPaused(false);
    } catch (err: unknown) {
      console.error("[useRunOrchestrator] Resume error:", err);
    }
  }, [runId]);

  const stopActiveRun = useCallback(async () => {
    if (!runId) return;
    try {
      await apiClient.stopRun(runId);
      setIsRunning(false);
      setIsPaused(false);
    } catch (err: unknown) {
      console.error("[useRunOrchestrator] Stop error:", err);
    }
  }, [runId]);

  const cancelActiveRun = useCallback(async () => {
    return stopActiveRun();
  }, [stopActiveRun]);

  const resetState = useCallback(() => {
    setRunId(null);
    setRunStatus(null);
    setIsRunning(false);
    setIsPaused(false);
    setParsedCases([]);
    setError(null);
  }, []);

  const provideRunInput = useCallback(async (input: string) => {
    if (!runId) return;
    try {
      await apiClient.provideInput(runId, input);
    } catch (err: unknown) {
      console.error("[useRunOrchestrator] Provide input error:", err);
    }
  }, [runId]);

  return {
    runId,
    runStatus,
    isRunning,
    isPaused,
    parsedCases,
    error,
    executeRun,
    pauseActiveRun,
    resumeActiveRun,
    stopActiveRun,
    cancelActiveRun,
    provideRunInput,
    resetState,
  };
}
