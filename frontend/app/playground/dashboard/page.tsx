"use client";

import React, { useState } from "react";
import Link from "next/link";
import { LayoutDashboard, ArrowLeft, RefreshCw, Calendar, TrendingUp, AlertTriangle } from "lucide-react";

export default function PlaygroundDashboardPage() {
  const [refreshCount, setRefreshCount] = useState(0);

  // [INTENTIONAL BUG]: Date filter button has dead click handler
  const handleDateFilterClick = () => {
    // Intentional no-op: does not update or open datepicker
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-6xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 02]: DASHBOARD & CSS OVERFLOW
        </span>
      </header>

      <main className="max-w-6xl mx-auto space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-black font-mono">Executive Analytics Overview</h1>
            <p className="text-xs text-neutral-500 font-mono">System throughput, latency, and edge telemetry.</p>
          </div>
          <div className="flex items-center gap-2">
            {/* [INTENTIONAL DEFECT: Unresponsive date filter button] */}
            <button
              id="btn-date-filter"
              onClick={handleDateFilterClick}
              className="border-2 border-black bg-white px-3 py-1.5 font-mono text-xs font-bold flex items-center gap-1.5 shadow-[2px_2px_0px_0px_#000000]"
            >
              <Calendar size={13} /> Last 30 Days (Filter Disabled)
            </button>
            <button
              id="btn-refresh"
              onClick={() => setRefreshCount((c) => c + 1)}
              className="border-2 border-black bg-black text-white px-3 py-1.5 font-mono text-xs font-bold flex items-center gap-1.5"
            >
              <RefreshCw size={13} /> Refresh ({refreshCount})
            </button>
          </div>
        </div>

        {/* [INTENTIONAL DEFECT: CSS Grid Overlap & Container Overflow] */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative">
          <div className="border-2 border-black bg-white p-5 shadow-[4px_4px_0px_0px_#000000]">
            <p className="font-mono text-xs text-neutral-500 uppercase">Total Edge Inferences</p>
            <p className="text-3xl font-black font-mono mt-1">1,284,912</p>
            <span className="text-xs font-mono text-emerald-600 flex items-center gap-1 mt-2">
              <TrendingUp size={12} /> +14.2% from last cycle
            </span>
          </div>

          {/* Intentionally misaligned widget with negative margin causing layout collision */}
          <div
            id="widget-overflow-defect"
            className="border-2 border-black bg-white p-5 shadow-[4px_4px_0px_0px_#000000] -mr-8 z-10"
            style={{ width: "115%" }}
          >
            <p className="font-mono text-xs text-neutral-500 uppercase">GPU VRAM Allocated</p>
            <p className="text-3xl font-black font-mono mt-1">3.42 GB / 4.0 GB</p>
            <div className="w-full bg-neutral-200 border border-black h-3 mt-2 overflow-hidden">
              <div className="bg-black h-full" style={{ width: "85.5%" }} />
            </div>
            <p className="text-[10px] font-mono text-neutral-400 mt-1">
              [CSS DEFECT]: Widget overlaps neighbor card container
            </p>
          </div>

          <div className="border-2 border-black bg-white p-5 shadow-[4px_4px_0px_0px_#000000]">
            <p className="font-mono text-xs text-neutral-500 uppercase">Assertion Pass Rate</p>
            <p className="text-3xl font-black font-mono mt-1">94.8%</p>
            <span className="text-xs font-mono text-neutral-600 mt-2 block">
              1,218,100 passing checks
            </span>
          </div>
        </div>
      </main>
    </div>
  );
}
