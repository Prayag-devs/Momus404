"use client";

import { useEffect, useRef, useState, useCallback, useId } from "react";
import { Terminal, Pause, Play, Trash2 } from "lucide-react";
import type { LogEvent } from "@/lib/api";

interface ActiveLogTerminalProps {
  events: LogEvent[];
  isRunning: boolean;
}

const SOURCE_COLORS: Record<string, string> = {
  MCP: "text-neutral-300",
  VAULT: "text-neutral-400",
  "LAYA-P1000": "text-white font-bold",
  HEAL: "text-neutral-300 italic",
  ENGINE: "text-neutral-400",
  BRAIN: "text-neutral-400",
  SYSTEM: "text-neutral-500",
};

const VERDICT_SUFFIX: Record<string, string> = {
  PASS: " → [ PASS ]",
  FAIL: " → [ FAIL ]",
  RETRY: " → [ RETRY ]",
};

export default function ActiveLogTerminal({ events, isRunning }: ActiveLogTerminalProps) {
  const liveRegionId = useId();
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [clearedAt, setClearedAt] = useState<number>(0);
  const [pausedSnapshot, setPausedSnapshot] = useState<LogEvent[]>([]);

  const handleTogglePause = () => {
    if (!isPaused) {
      setPausedSnapshot(events.filter((e) => new Date(e.ts).getTime() >= clearedAt));
      setIsPaused(true);
    } else {
      setIsPaused(false);
    }
  };

  const handleClear = () => {
    setClearedAt(Date.now());
    setPausedSnapshot([]);
  };

  const visibleEvents = isPaused
    ? pausedSnapshot
    : events.filter((e) => !clearedAt || new Date(e.ts).getTime() >= clearedAt);

  // Auto-scroll instantly on new events without thrashing layout
  useEffect(() => {
    if (!isPaused && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [visibleEvents.length, isPaused]);

  const formatLine = (e: LogEvent): string => {
    const ts = e.ts.slice(11, 23); // HH:MM:SS.mmm
    const verdict = e.verdict ? VERDICT_SUFFIX[e.verdict] ?? "" : "";
    return `[${ts}] [${e.source}]${e.test_id ? ` [${e.test_id}]` : ""}${e.step != null ? ` step#${e.step}` : ""} ${e.message}${verdict}`;
  };

  const lineClass = (e: LogEvent): string => {
    if (e.verdict === "PASS") return "log-pass";
    if (e.verdict === "FAIL") return "log-fail";
    if (e.verdict === "RETRY") return "log-retry";
    if (e.source === "HEAL") return "log-heal";
    if (e.source === "SYSTEM") return "log-sys";
    return SOURCE_COLORS[e.source] ?? "text-neutral-300";
  };

  return (
    <section className="nb-card flex flex-col overflow-hidden">
      {/* Terminal header */}
      <div className="flex items-center justify-between border-b-2 border-black px-4 py-2 bg-black text-white">
        <div className="flex items-center gap-2">
          <Terminal size={14} strokeWidth={2} />
          <span className="font-mono font-bold text-xs tracking-widest uppercase">
            Active Log Terminal
          </span>
          {isRunning && (
            <span className="font-mono text-[9px] text-neutral-400 animate-pulse">
              ● LIVE
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-[9px] text-neutral-500">
            {visibleEvents.length} lines
          </span>
          <button
            onClick={handleTogglePause}
            title={isPaused ? "Resume auto-scroll" : "Pause auto-scroll"}
            className="flex items-center gap-1 border border-neutral-600 px-2 py-0.5 font-mono text-[9px]
                       hover:border-white transition-colors"
          >
            {isPaused ? (
              <><Play size={9} /> RESUME</>
            ) : (
              <><Pause size={9} /> PAUSE</>
            )}
          </button>
          <button
            onClick={handleClear}
            title="Clear terminal"
            className="border border-neutral-600 px-2 py-0.5 font-mono text-[9px]
                       hover:border-white transition-colors flex items-center gap-1"
          >
            <Trash2 size={9} /> CLEAR
          </button>
        </div>
      </div>

      {/* Log body */}
      <div
        ref={containerRef}
        role="log"
        aria-live="polite"
        aria-label="Live test execution log"
        aria-atomic="false"
        className="log-terminal flex-1 min-h-[280px] max-h-[400px] p-3 overflow-y-auto"
      >
        {visibleEvents.length === 0 ? (
          <p className="text-neutral-600 font-mono text-xs">
            {isRunning
              ? "Waiting for log events…"
              : "No logs yet. Start a run to see live output."}
            <span className="cursor-blink" />
          </p>
        ) : (
          visibleEvents.map((e, i) => (
            <div key={`${e.ts}-${e.source}-${e.step ?? 0}-${i}`} className={`font-mono text-[11px] leading-[1.55] ${lineClass(e)}`}>
              {formatLine(e)}
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* Aria live summary (off-screen) */}
      <div
        id={liveRegionId}
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {isRunning
          ? `Running — ${visibleEvents.length} log events`
          : `Idle — ${visibleEvents.length} log events`}
      </div>

      {/* Footer */}
      <div className="border-t border-black bg-black px-3 py-1 flex items-center gap-4">
        <span className="font-mono text-[9px] text-neutral-600">
          STDOUT → MOMUS404 ORCHESTRATOR
        </span>
        {isPaused && (
          <span className="font-mono text-[9px] text-neutral-500 border border-neutral-700 px-1">
            SCROLL PAUSED
          </span>
        )}
      </div>
    </section>
  );
}
