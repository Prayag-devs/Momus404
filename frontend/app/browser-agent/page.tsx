"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Globe,
  Lock,
  RefreshCw,
  Terminal,
  Activity,
  CheckCircle2,
  XCircle,
  Shield,
  MousePointer,
} from "lucide-react";
import { useLogStream, useRunOrchestrator } from "@/hooks";
import LiveBrowserViewport from "@/components/LiveBrowserViewport";

function BrowserAgentPageContent() {
  const searchParams = useSearchParams();
  const initUrl = searchParams.get("url") || "http://localhost:3000/login";
  const initRunId = searchParams.get("runId") || "";

  const [currentUrl, setCurrentUrl] = useState(initUrl);
  const [activeAction, setActiveAction] = useState<string>("Active");
  const [activeTarget, setActiveTarget] = useState<string>("");
  const [activeValue, setActiveValue] = useState<string>("");
  const [activeTestTitle, setActiveTestTitle] = useState<string>("Live Agent Automation");
  const [activeTestId, setActiveTestId] = useState<string>("MOMUS-AGENT");
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number }>({ x: 50, y: 50 });
  const [isClicking, setIsClicking] = useState(false);
  const [iframeKey, setIframeKey] = useState(0);

  const { logEvents } = useLogStream(1000);
  const { runStatus, isRunning } = useRunOrchestrator();
  const consoleEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!logEvents || logEvents.length === 0) return;
    const latest = logEvents[logEvents.length - 1];
    if (!latest) return;

    const data = latest.data as Record<string, any> | undefined;

    if (data?.url && typeof data.url === "string") {
      setCurrentUrl(data.url);
    } else if (latest.message?.includes("navigate →")) {
      const match = latest.message.match(/navigate\s*→\s*([^\s]+)/i);
      if (match && match[1]) setCurrentUrl(match[1]);
    }

    if (data?.test_id) {
      setActiveTestId(data.test_id);
    } else if (latest.test_id) {
      setActiveTestId(latest.test_id);
    }

    if (data?.title) {
      setActiveTestTitle(data.title);
    } else if (runStatus?.current_test) {
      setActiveTestTitle(runStatus.current_test);
    }

    const action = data?.action || "";
    const target = data?.target || data?.selector || "";
    const val = data?.value || "";

    if (action || target) {
      setActiveAction(action.toUpperCase() || "INTERACT");
      setActiveTarget(target);
      setActiveValue(val);

      const targetLower = target.toLowerCase();
      if (targetLower.includes("username") || targetLower.includes("email")) {
        setCursorPos({ x: 38, y: 36 });
      } else if (targetLower.includes("password")) {
        setCursorPos({ x: 38, y: 48 });
      } else if (targetLower.includes("submit") || targetLower.includes("login")) {
        setCursorPos({ x: 50, y: 64 });
        setIsClicking(true);
        setTimeout(() => setIsClicking(false), 400);
      }
    }
  }, [logEvents, runStatus]);

  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logEvents]);

  const passedCount = runStatus?.passed ?? 0;
  const failedCount = runStatus?.failed ?? 0;
  const totalCount = runStatus?.total_tests ?? 100;
  const progressPct = totalCount > 0 ? Math.round(((passedCount + failedCount) / totalCount) * 100) : 0;

  return (
    <div className="min-h-screen bg-neutral-900 text-black flex flex-col font-sans select-none p-2 sm:p-4">
      <div className="flex-1 border-[3px] border-black bg-white shadow-[8px_8px_0px_0px_#000000] flex flex-col overflow-hidden">
        {/* Title Bar */}
        <div className="bg-black text-white px-4 py-2.5 flex items-center justify-between font-mono text-xs">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-emerald-400" />
            <span className="font-bold tracking-wider">
              MOMUS404 PLAYWRIGHT AGENT // DEDICATED DESKTOP VIEWPORT
            </span>
            {isRunning && (
              <span className="px-2 py-0.5 bg-emerald-400 text-black font-bold text-[10px] uppercase ml-2 animate-pulse">
                LIVE TESTING ACTIVE
              </span>
            )}
          </div>
          <div className="font-mono text-xs text-neutral-400">
            {initRunId ? `SESSION: ${initRunId}` : "ACTIVE INSTANCE"}
          </div>
        </div>

        {/* Address Bar */}
        <div className="bg-neutral-100 border-b-2 border-black p-2.5 flex items-center gap-3 font-mono text-xs">
          <button
            onClick={() => setIframeKey((k) => k + 1)}
            title="Reload viewport"
            className="p-1 hover:bg-neutral-200 border border-black bg-white transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
          <div className="flex-1 bg-white border-2 border-black px-3 py-1 flex items-center gap-2 shadow-[2px_2px_0px_0px_#000000]">
            <Lock className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
            <span className="text-[10px] font-bold text-neutral-500 uppercase flex-shrink-0">
              SANDBOX
            </span>
            <span className="text-neutral-300">|</span>
            <input
              type="text"
              readOnly
              value={currentUrl}
              className="w-full text-xs font-mono bg-transparent outline-none truncate"
            />
          </div>

          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className="border border-black px-2 py-1 bg-white font-bold">
              {passedCount + failedCount} / {totalCount}
            </span>
            <span className="border border-emerald-600 bg-emerald-100 text-emerald-900 px-2 py-1 font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              {passedCount} PASS
            </span>
            <span className="border border-red-600 bg-red-100 text-red-900 px-2 py-1 font-bold flex items-center gap-1">
              <XCircle className="w-3 h-3 text-red-600" />
              {failedCount} FAIL
            </span>
          </div>
        </div>

        {/* HUD */}
        <div className="bg-neutral-900 text-white px-4 py-2 flex items-center justify-between font-mono text-xs border-b-2 border-black">
          <div className="flex items-center gap-2 truncate">
            <span className="px-2 py-0.5 bg-emerald-400 text-black font-bold text-[10px]">
              {activeTestId}
            </span>
            <span className="font-bold text-neutral-200 truncate">{activeTestTitle}</span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-amber-300 uppercase font-bold">{activeAction}:</span>
            <span className="text-neutral-300">{activeTarget || currentUrl}</span>
          </div>
        </div>

        {/* Live Browser Viewport (CDP Canvas) */}
        <div className="relative flex-1 bg-black flex items-center justify-center overflow-hidden">
          <LiveBrowserViewport
            runId={initRunId}
            currentUrl={currentUrl}
            activeAction={activeAction}
            activeTarget={activeTarget || activeValue}
            isRunning={isRunning}
            className="w-full h-full border-none shadow-none"
          />
        </div>

        {/* Console */}
        <div className="h-36 bg-black text-neutral-200 p-2.5 font-mono text-xs overflow-y-auto border-t-2 border-black space-y-1">
          {logEvents.slice(-60).map((ev, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-neutral-500 text-[10px] flex-shrink-0">
                {ev.ts ? ev.ts.split("T")[1]?.slice(0, 8) : "--:--:--"}
              </span>
              <span
                className={`font-bold px-1 text-[9px] uppercase flex-shrink-0 ${
                  ev.source === "MCP"
                    ? "bg-purple-900 text-purple-200"
                    : "bg-neutral-800 text-neutral-300"
                }`}
              >
                {ev.source}
              </span>
              <span className="text-neutral-300 break-all">{ev.message}</span>
            </div>
          ))}
          <div ref={consoleEndRef} />
        </div>
      </div>
    </div>
  );
}

export default function BrowserAgentPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-black text-white p-4 font-mono">Loading...</div>}>
      <BrowserAgentPageContent />
    </Suspense>
  );
}
