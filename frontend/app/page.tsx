"use client";

import { useState } from "react";
import Header from "@/components/Header";
import ControlPanel from "@/components/ControlPanel";
import HardwareMonitor from "@/components/HardwareMonitor";
import ActiveLogTerminal from "@/components/ActiveLogTerminal";
import RunResults from "@/components/RunResults";
import MomusLoreModal from "@/components/MomusLoreModal";
import LiveBrowserViewport from "@/components/LiveBrowserViewport";

import {
  useHealth,
  useTelemetry,
  useLogStream,
  useRunOrchestrator,
} from "@/hooks";
import { apiClient } from "@/lib/api-client";

export default function HomePage() {
  const [loreOpen, setLoreOpen] = useState(false);
  const [operatorInput, setOperatorInput] = useState("");

  // Custom Domain Hooks
  const { health, refreshHealth } = useHealth();
  const { telemetry } = useTelemetry(1200);
  const { logEvents, clearLogs } = useLogStream(1000);
  const {
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
  } = useRunOrchestrator(refreshHealth);

  const handleClearAll = () => {
    resetState();
    clearLogs();
  };

  const handleGenerate = async (url: string, file: File | null) => {
    if (file) {
      try {
        const uploadRes = await apiClient.uploadSpec(file);
        if (uploadRes.test_cases.length > 0) {
          await apiClient.generateTest(uploadRes.test_cases[0]);
        }
      } catch (err) {
        console.warn("[HomePage] Generate test failed:", err);
      }
    }
  };

  // Derive active action, target, and URL from latest log event
  const latestEvent = logEvents.length > 0 ? logEvents[logEvents.length - 1] : null;
  const latestData = latestEvent?.data as Record<string, any> | undefined;
  const currentAction = (latestData?.action || latestEvent?.source || (isRunning ? "RUNNING" : "IDLE")).toUpperCase();
  const currentTarget = latestData?.target || latestData?.selector || "";
  const currentViewportUrl =
    latestData?.url ||
    (latestEvent?.message?.includes("http") ? latestEvent.message.match(/https?:\/\/[^\s]+/)?.[0] : undefined) ||
    "http://localhost:3000/login";

  return (
    <div className="min-h-screen bg-white text-black font-sans selection:bg-black selection:text-white pb-16">
      {/* ── Top Command Bar ── */}
      <Header health={health} onOpenLore={() => setLoreOpen(true)} />

      {/* ── Main Dashboard Layout ── */}
      <main className="max-w-[1700px] mx-auto px-4 sm:px-6 pt-6 space-y-6">
        {/* System Error Banner */}
        {error && (
          <div className="border-[3px] border-black bg-black text-white p-4 font-mono text-sm shadow-[4px_4px_0px_0px_#000000] flex justify-between items-center">
            <span>[ SYSTEM ERROR ]: {error}</span>
            <button
              onClick={() => handleClearAll()}
              className="text-xs uppercase border border-white px-2 py-1 hover:bg-white hover:text-black transition-colors"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* ── Operator Prompt Modal Pop-up for 2FA / OTP / Store / Unit Selection ── */}
        {runStatus?.awaiting_input && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in duration-200">
            <div className="border-[3px] border-black bg-white text-black p-6 font-mono shadow-[10px_10px_0px_0px_#f59e0b] max-w-xl w-full relative">
              <div className="flex items-center gap-2 font-black text-sm uppercase text-amber-900 border-b-2 border-amber-300 pb-3">
                <span className="inline-block w-3 h-3 bg-amber-500 rounded-full animate-ping" />
                <span>[ ACTION REQUIRED: {(runStatus.input_type || "2FA / OTP / STORE / UNIT").toUpperCase()} ]</span>
                <span className="ml-auto text-xs bg-amber-200 text-amber-900 px-2 py-0.5 border border-amber-400 font-bold">
                  TEST PAUSED
                </span>
              </div>
              <p className="text-xs text-neutral-800 my-4 leading-relaxed">
                {runStatus.input_prompt || "The application requires additional verification, OTP, or unit selection to proceed."}
                <br />
                <span className="text-[11px] text-neutral-600 block mt-2">
                  Enter your value below to auto-fill it, or complete the step directly in the headed browser window and click Continue.
                </span>
              </p>
              <div className="flex flex-col sm:flex-row gap-2 mt-4">
                <input
                  id="input-operator-code"
                  type="text"
                  value={operatorInput}
                  onChange={(e) => setOperatorInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && operatorInput.trim()) {
                      provideRunInput(operatorInput.trim());
                      setOperatorInput("");
                    }
                  }}
                  placeholder={`Enter ${(runStatus.input_type || "code").toUpperCase()}...`}
                  className="nb-input flex-1 text-sm bg-neutral-50 border-2 border-black px-3 py-2 font-mono font-bold focus:bg-white"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => {
                    if (operatorInput.trim()) {
                      provideRunInput(operatorInput.trim());
                      setOperatorInput("");
                    }
                  }}
                  className="bg-black text-white hover:bg-neutral-800 font-bold text-xs px-4 py-2 uppercase border-2 border-black transition-colors cursor-pointer"
                >
                  [ Submit ]
                </button>
                <button
                  type="button"
                  onClick={() => {
                    provideRunInput("__COMPLETED_IN_BROWSER__");
                    setOperatorInput("");
                  }}
                  className="bg-amber-400 text-black hover:bg-amber-300 font-bold text-xs px-4 py-2 uppercase border-2 border-black transition-colors cursor-pointer"
                >
                  [ Completed in Browser ]
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Control Center & Hardware Telemetry Grid ── */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Operator Ingest & Dispatch Controls (7 cols) */}
          <div className="lg:col-span-7">
            <ControlPanel
              isRunning={isRunning}
              isPaused={isPaused}
              parsedCases={parsedCases}
              runId={runId}
              onRun={(url, file, user, pass) => {
                executeRun(url, file, user, pass, false);
              }}
              onDryRun={(url, file, user, pass) => {
                executeRun(url, file, user, pass, true);
              }}
              onGenerate={handleGenerate}
              onPause={pauseActiveRun}
              onResume={resumeActiveRun}
              onStop={stopActiveRun}
              onCancel={cancelActiveRun}
              onClear={handleClearAll}
            />
          </div>

          {/* Edge Hardware & Latency Telemetry (5 cols) */}
          <div className="lg:col-span-5">
            <HardwareMonitor
              telemetry={telemetry}
              tokensSaved={runStatus?.tokens_saved ?? telemetry?.tokens_saved ?? 0}
            />
          </div>
        </section>

        {/* ── Real-Time Chrome DevTools Screencast Viewport ── */}
        <section>
          <LiveBrowserViewport
            runId={runId}
            currentUrl={currentViewportUrl}
            activeAction={currentAction}
            activeTarget={currentTarget}
            isRunning={isRunning}
          />
        </section>

        {/* ── Real-Time Streaming Terminal & Per-Test Execution Table ── */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Active Log Terminal (6 cols) */}
          <div className="lg:col-span-6">
            <ActiveLogTerminal events={logEvents} isRunning={isRunning} />
          </div>

          {/* Test Case & Step Results Table (6 cols) */}
          <div className="lg:col-span-6">
            <RunResults runStatus={runStatus} />
          </div>
        </section>
      </main>

      {/* ── Momus Dossier Lore Modal ── */}
      <MomusLoreModal isOpen={loreOpen} onClose={() => setLoreOpen(false)} />

      {/* ── Persistent System Footer ── */}
      <footer className="mt-12 text-center text-xs font-mono text-neutral-500 space-y-1">
        <p>MOMUS404 // HYBRID EDGE-CLOUD QA ORCHESTRATOR // ALL SYSTEMS NOMINAL</p>
        <p>Laya 421M · Nous Hermes · OpenAI · Playwright MCP · OpenDots Vault</p>
      </footer>
    </div>
  );
}
