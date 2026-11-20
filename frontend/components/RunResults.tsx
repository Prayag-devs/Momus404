"use client";

import { ClipboardList, Download, ChevronDown, ChevronUp, Loader2 } from "lucide-react";
import React, { useState } from "react";
import { downloadReport } from "@/lib/api";
import type { RunStatus, TestCaseResult, StepResult } from "@/lib/api";

interface RunResultsProps {
  runStatus: RunStatus | null;
}

export default function RunResults({ runStatus }: RunResultsProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (!runStatus || (runStatus.results.length === 0 && runStatus.status !== "RUNNING")) {
    return (
      <section className="nb-card p-5">
        <div className="flex items-center gap-2 border-b-2 border-black pb-3 mb-4">
          <ClipboardList size={16} strokeWidth={2.5} />
          <span className="font-mono font-black text-sm tracking-wider uppercase">Run Results</span>
        </div>
        <p className="font-mono text-xs text-neutral-500">
          No results yet. Run a test to see per-case PASS / FAIL table.
        </p>
      </section>
    );
  }

  const { run_id, results, passed, failed, total_tests, tokens_saved, status, progress, current_test } = runStatus;
  const passRate = total_tests > 0 ? ((passed / total_tests) * 100).toFixed(1) : "0.0";
  const pct = Math.round((progress ?? 0) * 100);

  return (
    <section className="nb-card p-5 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-start justify-between border-b-2 border-black pb-3">
        <div className="flex items-center gap-2">
          <ClipboardList size={16} strokeWidth={2.5} />
          <span className="font-mono font-black text-sm tracking-wider uppercase">Run Results</span>
          {status === "RUNNING" && (
            <span className="flex items-center gap-1.5 font-mono text-xs text-emerald-700 bg-emerald-50 border border-emerald-700 px-2 py-0.5 animate-pulse">
              <Loader2 size={11} className="animate-spin" />
              EXECUTING {pct}%
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => downloadReport(run_id, "xlsx")}
            className="btn-primary text-[10px] py-1 px-2.5 flex items-center gap-1 bg-emerald-700 text-white hover:bg-emerald-800 transition"
            title="Download Excel spreadsheet with PASS / FAIL status and logs"
          >
            <Download size={11} strokeWidth={2} />
            EXCEL (.XLSX)
          </button>
          <button
            onClick={() => downloadReport(run_id, "md")}
            className="btn-secondary text-[10px] py-1 px-2 flex items-center gap-1"
            title="Download Markdown report"
          >
            <Download size={11} strokeWidth={2} />
            REPORT (.MD)
          </button>
        </div>
      </div>

      {/* Live execution progress bar */}
      {status === "RUNNING" && (
        <div className="border-2 border-black p-3 bg-neutral-50 flex flex-col gap-2">
          <div className="flex items-center justify-between font-mono text-xs">
            <span className="font-bold truncate max-w-[320px]">
              {current_test || "Executing test cases..."}
            </span>
            <span className="font-black">{pct}% ({results.length}/{total_tests})</span>
          </div>
          <div className="w-full bg-neutral-200 border border-black h-3 overflow-hidden">
            <div
              className="bg-black h-full transition-all duration-300"
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
      )}

      {/* Summary bar */}
      <div className="grid grid-cols-4 gap-2">
        <SummaryCell label="TOTAL" value={String(total_tests)} />
        <SummaryCell label="PASSED" value={String(passed)} inverted />
        <SummaryCell label="FAILED" value={String(failed)} />
        <SummaryCell label="PASS RATE" value={`${passRate}%`} />
      </div>

      {/* Tokens saved */}
      <div className="border-2 border-black bg-black text-white px-3 py-2 flex items-center justify-between">
        <span className="font-mono text-xs">Tokens saved by Laya edge judge</span>
        <span className="font-mono font-black text-base">{tokens_saved.toLocaleString()}</span>
      </div>

      {/* Results table */}
      <div className="overflow-x-auto max-h-[520px] overflow-y-auto border-2 border-black">
        <table className="w-full border-collapse font-mono text-xs">
          <thead className="sticky top-0 z-10 bg-black text-white shadow-sm">
            <tr>
              <th className="border border-neutral-700 px-2 py-1 text-left">#</th>
              <th className="border border-neutral-700 px-2 py-1 text-left">Title</th>
              <th className="border border-neutral-700 px-2 py-1 text-center">Verdict</th>
              <th className="border border-neutral-700 px-2 py-1 text-center">Steps</th>
              <th className="border border-neutral-700 px-2 py-1 text-center">Heals</th>
              <th className="border border-neutral-700 px-2 py-1 text-right">Duration</th>
              <th className="border border-neutral-700 px-2 py-1 text-center">Details</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <React.Fragment key={`${r.test_case_id || i}-${i}`}>
                <tr
                  className={`hover:bg-neutral-50 cursor-pointer ${i % 2 === 0 ? "bg-white" : "bg-neutral-50"}`}
                  onClick={() => setExpanded(expanded === r.test_case_id ? null : r.test_case_id)}
                >
                  <td className="border border-black px-2 py-1.5 text-neutral-500">{i + 1}</td>
                  <td className="border border-black px-2 py-1.5 font-medium max-w-[200px] truncate" title={r.title}>
                    {r.title}
                  </td>
                  <td className="border border-black px-2 py-1.5 text-center">
                    <VerdictBadge verdict={r.verdict} />
                  </td>
                  <td className="border border-black px-2 py-1.5 text-center">{r.steps.length}</td>
                  <td className="border border-black px-2 py-1.5 text-center">{r.heal_count}</td>
                  <td className="border border-black px-2 py-1.5 text-right">{r.duration_ms}ms</td>
                  <td className="border border-black px-2 py-1.5 text-center">
                    {expanded === r.test_case_id ? (
                      <ChevronUp size={12} className="mx-auto" />
                    ) : (
                      <ChevronDown size={12} className="mx-auto" />
                    )}
                  </td>
                </tr>

                {/* Step detail row */}
                {expanded === r.test_case_id && (
                  <tr key={`${r.test_case_id}-steps`}>
                    <td
                      colSpan={7}
                      className="border border-black bg-neutral-50 px-3 py-2"
                    >
                      <StepDetails steps={r.steps} />
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function VerdictBadge({ verdict }: { verdict: string }) {
  if (verdict === "PASS") return <span className="badge-pass">[ PASS ]</span>;
  if (verdict === "FAIL") return <span className="badge-fail">[ FAIL ]</span>;
  if (verdict === "RETRY") return <span className="badge-retry">[ RETRY ]</span>;
  if (verdict === "RUNNING") return <span className="badge-running">[ RUNNING ]</span>;
  return <span className="badge-idle">[ {verdict} ]</span>;
}

function StepDetails({ steps }: { steps: StepResult[] }) {
  return (
    <div className="flex flex-col gap-2">
      <p className="font-mono text-[9px] text-neutral-500 uppercase mb-1">Step Breakdown & Execution Trace</p>
      {steps.map((s) => (
        <div key={s.step_index} className="flex flex-col gap-0.5 border-b border-neutral-200 pb-1.5 last:border-0">
          <div className="flex items-start gap-2 font-mono text-[10px]">
            <VerdictBadge verdict={s.verdict} />
            <span className="text-neutral-600">#{s.step_index}</span>
            <span className="font-bold uppercase">{s.action}</span>
            <span className="text-neutral-700 truncate max-w-[200px]" title={s.target}>
              {s.target || "—"}
            </span>
            {s.value && (
              <span className="bg-neutral-200 text-neutral-800 px-1 py-0.2 rounded text-[9px] truncate max-w-[140px]" title={s.value}>
                val: {s.value}
              </span>
            )}
            <span className="text-neutral-400 ml-auto whitespace-nowrap">
              {s.latency_ms}ms • conf={s.confidence.toFixed(2)}
              {s.heal_count > 0 && ` • ${s.heal_count} heal(s)`}
              {s.mock && " [mock]"}
            </span>
          </div>
          {s.log && (
            <p className="text-[10px] text-neutral-600 pl-6 font-mono bg-neutral-100 p-1 border-l-2 border-black">
              {s.log}
            </p>
          )}
          {s.error && (
            <p className="text-[10px] text-red-700 pl-6 font-mono bg-red-50 p-1 border-l-2 border-red-500 font-bold">
              {s.error}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

function SummaryCell({ label, value, inverted = false }: { label: string; value: string; inverted?: boolean }) {
  return (
    <div className={`border-2 border-black p-2 text-center ${inverted ? "bg-black text-white" : "bg-white"}`}>
      <p className={`font-mono text-[9px] uppercase tracking-wider ${inverted ? "text-neutral-400" : "text-neutral-500"}`}>
        {label}
      </p>
      <p className={`font-mono font-black text-lg leading-tight ${inverted ? "text-white" : "text-black"}`}>
        {value}
      </p>
    </div>
  );
}
