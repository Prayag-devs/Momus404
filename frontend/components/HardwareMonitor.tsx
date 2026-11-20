"use client";

import { useEffect, useState } from "react";
import { Cpu } from "lucide-react";
import type { Telemetry } from "@/lib/api";

interface HardwareMonitorProps {
  telemetry: Telemetry | null;
  tokensSaved: number;
}

export default function HardwareMonitor({ telemetry, tokensSaved }: HardwareMonitorProps) {
  const [sparkline, setSparkline] = useState<number[]>(Array(20).fill(0));

  const t = telemetry ?? {
    device: "No PyTorch",
    gpu_util_pct: 0,
    vram_used_mb: 0,
    vram_total_mb: 4096,
    avg_latency_ms: 0,
    last_latency_ms: 0,
    tokens_saved: 0,
    mock: true,
  };

  const vramUsedMb = t.vram_used_mb > 0 ? t.vram_used_mb : 85;
  const vramPct = Math.min((vramUsedMb / t.vram_total_mb) * 100, 100);
  const vramUsedGb = (vramUsedMb / 1024).toFixed(2);
  const vramTotalGb = (t.vram_total_mb / 1024).toFixed(1);

  // Build VRAM bar string (20 blocks)
  const filledBlocks = Math.max(1, Math.round(vramPct / 5));
  const vramBarStr =
    "█".repeat(filledBlocks) + "░".repeat(20 - filledBlocks);

  // Update sparkline on new telemetry poll readings
  useEffect(() => {
    if (telemetry && telemetry.last_latency_ms > 0) {
      setSparkline((prev) => [...prev.slice(1), telemetry.last_latency_ms]);
    }
  }, [telemetry]);

  const sparkMax = Math.max(...sparkline, 1);

  return (
    <section className="nb-card p-5 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b-2 border-black pb-3">
        <div className="flex items-center gap-2">
          <Cpu size={16} strokeWidth={2.5} />
          <span className="font-mono font-black text-sm tracking-wider uppercase">Hardware Monitor</span>
        </div>
        <div className="flex items-center gap-1.5">
          {t.mock && (
            <span className="badge-mock">MOCK</span>
          )}
          <span
            className={`inline-block w-2.5 h-2.5 border border-black ${
              t.mock ? "bg-neutral-300" : "bg-black animate-pulse"
            }`}
          />
        </div>
      </div>

      {/* Device name */}
      <div>
        <p className="section-label">Edge Inference Device</p>
        <p className="font-mono font-bold text-sm">
          {t.mock ? "NVIDIA Quadro P1000 (4GB GDDR5)" : t.device}
          {t.mock && <span className="text-neutral-400 font-normal"> [SIMULATED]</span>}
        </p>
      </div>

      {/* VRAM bar */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="section-label mb-0">VRAM Usage</span>
          <span className="font-mono text-xs font-bold">
            {vramUsedGb}GB / {vramTotalGb}GB
          </span>
        </div>
        <div className="vram-bar">
          <div className="vram-fill" style={{ width: `${vramPct}%` }} />
        </div>
        <p className="font-mono text-[10px] text-neutral-500 mt-1">
          [{vramBarStr}] {vramPct.toFixed(1)}%
        </p>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 gap-2">
        <MetricBox label="Avg Inference" value={`~${t.avg_latency_ms.toFixed(0)}ms`} sub="per step" />
        <MetricBox label="Last Inference" value={`${t.last_latency_ms.toFixed(0)}ms`} sub="latest" />
        <MetricBox
          label="GPU Utilisation"
          value={`${t.gpu_util_pct.toFixed(1)}%`}
          sub={t.mock ? "simulated" : "real"}
        />
        <MetricBox
          label="Tokens Saved"
          value={String(tokensSaved || t.tokens_saved)}
          sub="by Laya edge judge"
          highlight
        />
      </div>

      {/* Latency sparkline */}
      <div>
        <p className="section-label mb-1">Latency History (ms)</p>
        <div className="flex items-end gap-[2px] h-10 border-b border-black">
          {sparkline.map((val, i) => {
            const h = sparkMax > 0 ? Math.round((val / sparkMax) * 40) : 0;
            return (
              <div
                key={i}
                className="flex-1 bg-black transition-all duration-300"
                style={{ height: `${h}px` }}
              />
            );
          })}
        </div>
        <div className="flex justify-between mt-0.5">
          <span className="font-mono text-[8px] text-neutral-400">oldest</span>
          <span className="font-mono text-[8px] text-neutral-400">latest</span>
        </div>
      </div>
    </section>
  );
}

function MetricBox({
  label,
  value,
  sub,
  highlight = false,
}: {
  label: string;
  value: string;
  sub: string;
  highlight?: boolean;
}) {
  return (
    <div className={`border-2 border-black p-2 ${highlight ? "bg-black text-white" : "bg-neutral-50"}`}>
      <p className={`font-mono text-[9px] uppercase tracking-wider ${highlight ? "text-neutral-400" : "text-neutral-500"}`}>
        {label}
      </p>
      <p className={`font-mono font-black text-base leading-tight ${highlight ? "text-white" : "text-black"}`}>
        {value}
      </p>
      <p className={`font-mono text-[9px] ${highlight ? "text-neutral-400" : "text-neutral-400"}`}>
        {sub}
      </p>
    </div>
  );
}
