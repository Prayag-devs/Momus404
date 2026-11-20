"use client";

import { Info } from "lucide-react";
import type { ComponentHealth, HealthReport } from "@/lib/api";

interface HeaderProps {
  health: HealthReport | null;
  onOpenLore: () => void;
}

export default function Header({ health, onOpenLore }: HeaderProps) {
  const gpuComponent = health?.components?.find((c) => c.name === "Laya Judge" || c.name === "Jev Decision Engine");
  const isRealGpu = gpuComponent?.status === "real";
  const gpuLabel = gpuComponent?.detail ?? "QUADRO P1000";

  return (
    <header className="border-b-[3px] border-black bg-white sticky top-0 z-50">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="min-w-0">
          <h1 className="font-mono font-black text-base sm:text-lg md:text-xl leading-tight tracking-tight">
            MOMUS<span className="text-neutral-500">404</span>
          </h1>
          <p className="font-mono text-[10px] sm:text-xs text-neutral-500 tracking-widest uppercase truncate">
            Hybrid Edge-Cloud QA Orchestrator // Multi-Agent Test Platform
          </p>
        </div>

        {/* Right controls */}
        <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
          {/* GPU indicator */}
          <div className="hidden sm:flex items-center gap-1.5 border-2 border-black px-2 py-1 font-mono text-[10px] font-bold">
            <span
              className={`inline-block w-2 h-2 border border-black ${isRealGpu ? "bg-black animate-pulse" : "bg-neutral-300"}`}
            />
            <span className="uppercase tracking-wider">
              GPU:&nbsp;
              <span className={isRealGpu ? "text-black" : "text-neutral-500"}>
                {isRealGpu ? gpuLabel : "MOCK // NO CUDA"}
              </span>
            </span>
          </div>

          {/* Health dots */}
          {health?.components && (
            <div className="hidden md:flex items-center gap-1">
              {health.components.map((c) => (
                <ComponentDot key={c.name} component={c} />
              ))}
            </div>
          )}

          {/* Target Playground Link */}
          <a
            href="/playground"
            id="link-playground-hub"
            className="flex items-center gap-1.5 border-2 border-black px-2.5 py-1.5 font-mono text-[10px] sm:text-xs font-bold
                       shadow-[2px_2px_0px_0px_#000] bg-neutral-100 hover:bg-black hover:text-white transition-all duration-100"
          >
            TARGET PLAYGROUND (15 PAGES)
          </a>

          {/* Lore button */}
          <button
            id="btn-lore"
            aria-label="Open Momus Protocol Archive"
            onClick={onOpenLore}
            className="flex items-center gap-1.5 border-2 border-black px-2 py-1.5 font-mono text-[10px] sm:text-xs font-bold
                       shadow-[2px_2px_0px_0px_#000]
                       hover:bg-black hover:text-white
                       active:translate-x-0.5 active:translate-y-0.5
                       active:shadow-none transition-all duration-100"
          >
            <Info size={12} strokeWidth={2.5} />
            <span className="hidden sm:inline">ARCHIVES: THE MOMUS PROTOCOL</span>
            <span className="sm:hidden">LORE</span>
          </button>
        </div>
      </div>
    </header>
  );
}

function ComponentDot({ component }: { component: ComponentHealth }) {
  const color =
    component.status === "real"
      ? "bg-black"
      : component.status === "mock"
      ? "bg-neutral-400"
      : "bg-neutral-200";
  return (
    <div
      title={`${component.name}: ${component.status} — ${component.detail}`}
      className={`w-2 h-2 border border-black ${color}`}
    />
  );
}
