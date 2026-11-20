"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  Monitor,
  Activity,
  Globe,
  Zap,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Eye,
} from "lucide-react";
import { WS_SCREENCAST_URL } from "@/lib/config";

interface LiveBrowserViewportProps {
  runId?: string | null;
  currentUrl?: string;
  activeAction?: string;
  activeTarget?: string;
  isRunning?: boolean;
  className?: string;
}

export default function LiveBrowserViewport({
  runId,
  currentUrl = "http://localhost:3000/login",
  activeAction = "IDLE",
  activeTarget = "",
  isRunning = false,
  className = "",
}: LiveBrowserViewportProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [frameCount, setFrameCount] = useState(0);
  const [lastFrameTime, setLastFrameTime] = useState<number | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  const [hudAction, setHudAction] = useState(activeAction);
  const [hudTarget, setHudTarget] = useState(activeTarget);

  useEffect(() => {
    if (activeAction) setHudAction(activeAction);
    if (activeTarget) setHudTarget(activeTarget);
  }, [activeAction, activeTarget]);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let isMounted = true;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      try {
        const url = runId ? `${WS_SCREENCAST_URL}/${runId}` : WS_SCREENCAST_URL;
        ws = new WebSocket(url);

        ws.onopen = () => {
          if (!isMounted) return;
          setConnectionStatus("connected");
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          const data = event.data;
          if (!data || data === "pong" || data.startsWith("{")) return;

          const img = new Image();
          img.onload = () => {
            if (!isMounted || !canvasRef.current) return;
            const canvas = canvasRef.current;
            const ctx = canvas.getContext("2d");
            if (ctx) {
              ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
              setIsStreaming(true);
              setFrameCount((c) => c + 1);
              setLastFrameTime(Date.now());
            }
          };
          img.src = `data:image/jpeg;base64,${data}`;
        };

        ws.onerror = () => {
          if (isMounted) setConnectionStatus("disconnected");
        };

        ws.onclose = () => {
          if (!isMounted) return;
          setConnectionStatus("disconnected");
          reconnectTimeout = setTimeout(connect, 2000);
        };
      } catch (err) {
        if (isMounted) {
          setConnectionStatus("disconnected");
          reconnectTimeout = setTimeout(connect, 3000);
        }
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) ws.close();
    };
  }, [runId]);

  return (
    <div
      className={`border-[3px] border-black bg-white shadow-[6px_6px_0px_0px_#000000] flex flex-col overflow-hidden font-mono ${className}`}
    >
      {/* ── Top Bar ── */}
      <div className="bg-black text-white px-3 py-2 flex items-center justify-between border-b-2 border-black text-xs">
        <div className="flex items-center gap-2">
          <Monitor className="w-4 h-4 text-emerald-400" />
          <span className="font-bold tracking-wider uppercase">
            CHROME DEVTOOLS STREAM // LIVE BROWSER AUTOMATION
          </span>
          {isStreaming ? (
            <span className="flex items-center gap-1.5 px-2 py-0.5 bg-emerald-400 text-black font-black text-[10px] uppercase">
              <span className="w-2 h-2 rounded-full bg-black animate-ping" />
              LIVE (CDP)
            </span>
          ) : isRunning ? (
            <span className="px-2 py-0.5 bg-amber-400 text-black font-black text-[10px] uppercase animate-pulse">
              INITIALIZING BROWSER...
            </span>
          ) : (
            <span className="px-2 py-0.5 bg-neutral-700 text-neutral-300 font-bold text-[10px] uppercase">
              STANDBY
            </span>
          )}
        </div>
        <div className="flex items-center gap-3 text-[11px] text-neutral-300">
          <span>RES: 1280x800</span>
          <span>FRAMES: {frameCount}</span>
          <span
            className={`w-2 h-2 rounded-full ${
              connectionStatus === "connected" ? "bg-emerald-400" : "bg-red-500"
            }`}
            title={`WebSocket: ${connectionStatus}`}
          />
        </div>
      </div>

      {/* ── Address & Current Action Ribbon ── */}
      <div className="bg-neutral-100 border-b-2 border-black px-3 py-1.5 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2 flex-1 min-w-[280px]">
          <Globe className="w-3.5 h-3.5 text-neutral-600 flex-shrink-0" />
          <span className="text-[10px] font-bold text-neutral-500 uppercase">TARGET:</span>
          <span className="bg-white border border-black px-2 py-0.5 font-bold truncate max-w-[480px]">
            {currentUrl}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Zap className="w-3.5 h-3.5 text-black" />
          <span className="text-[10px] font-bold text-neutral-500 uppercase">JEV AGENT ACT:</span>
          <span className="bg-black text-white px-2 py-0.5 font-black uppercase text-[11px]">
            {hudAction}
          </span>
          {hudTarget && (
            <span className="border border-black bg-white px-2 py-0.5 text-[11px] text-neutral-800 font-bold truncate max-w-[260px]">
              {hudTarget}
            </span>
          )}
        </div>
      </div>

      {/* ── Viewport Canvas Display ── */}
      <div className="relative bg-neutral-900 w-full aspect-[16/10] max-h-[560px] flex items-center justify-center overflow-hidden">
        {/* Real-time HTML5 Canvas */}
        <canvas
          ref={canvasRef}
          width={1280}
          height={800}
          className={`w-full h-full object-contain ${
            isStreaming ? "block" : "hidden"
          }`}
        />

        {/* Standby & Pre-run HUD Overlay */}
        {!isStreaming && (
          <div className="p-8 text-center flex flex-col items-center justify-center space-y-4">
            <div className="border-2 border-neutral-700 bg-black/60 p-6 text-left font-mono max-w-lg shadow-[4px_4px_0px_0px_#262626]">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs pb-3 border-b border-neutral-800">
                <Eye className="w-4 h-4" />
                <span>MOMUS404 // JEV AUTONOMOUS AGENT VIEWPORT</span>
              </div>
              <div className="py-4 space-y-2 text-xs text-neutral-400">
                <p>
                  <span className="text-white font-bold">&gt; CDP STREAM:</span>{" "}
                  {connectionStatus === "connected" ? "Connected (Listening for frames)" : "Waiting for backend..."}
                </p>
                <p>
                  <span className="text-white font-bold">&gt; MODE:</span> Autonomous AI Execution + Jev Decision Engine
                </p>
                <p>
                  <span className="text-white font-bold">&gt; PIPELINE:</span> Real-time 1280x800 Chromium viewport streamed via WebSocket
                </p>
                <p className="text-[11px] text-neutral-500 pt-2 border-t border-neutral-800">
                  Click [ RUN TEST ] or [ RUN DRY ] to launch the browser session and watch live automation here.
                </p>
              </div>
              {isRunning && (
                <div className="flex items-center gap-2 pt-2 text-amber-400 text-xs font-bold animate-pulse">
                  <Activity className="w-3.5 h-3.5 animate-spin" />
                  <span>Launching Playwright browser session on server...</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ── Viewport Status Footer ── */}
      <div className="bg-black text-neutral-400 px-3 py-1.5 flex items-center justify-between text-[11px] border-t-2 border-black">
        <div className="flex items-center gap-3">
          <span className="text-emerald-400 font-bold">● PROTOCOL: CDP SCREENCAST</span>
          <span>ENGINE: JEV SYSTEM-1 (&lt;50MS)</span>
        </div>
        <div className="flex items-center gap-2">
          <span>{isStreaming ? "STREAM ACTIVE" : "AWAITING RUN"}</span>
        </div>
      </div>
    </div>
  );
}
