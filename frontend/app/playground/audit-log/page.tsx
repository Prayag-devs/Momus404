"use client";

import React, { useState } from "react";
import Link from "next/link";
import { FileText, ArrowLeft, AlertTriangle } from "lucide-react";

interface AuditEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  severity: string;
}

const AUDIT_ENTRIES: AuditEntry[] = [
  {"id": "LOG-101", "timestamp": "2026-10-11T18:02:11Z", "actor": "admin@momus404.local", "action": "LOGIN_SUCCESS", "severity": "INFO"},
  {"id": "LOG-102", "timestamp": "2026-10-11T18:05:40Z", "actor": "system", "action": "VAULT_ROTATION", "severity": "NOTICE"},
  {"id": "LOG-103", "timestamp": "2026-10-11T18:12:00Z", "actor": "unknown_ip", "action": "AUTH_FAILED_RATE_LIMIT", "severity": "WARN"},
  {"id": "LOG-104", "timestamp": "2026-10-11T18:20:15Z", "actor": "admin@momus404.local", "action": "MODEL_DISPATCH_P1000", "severity": "INFO"},
];

export default function PlaygroundAuditLogPage() {
  const [severity, setSeverity] = useState("ALL");
  const [page, setPage] = useState(1);
  const [negativeIndexWarning, setNegativeIndexWarning] = useState<string | null>(null);

  // [INTENTIONAL DEFECT: Negative index pagination allowed]
  const handlePageChange = (delta: number) => {
    const newPage = page + delta;
    setPage(newPage);
    if (newPage < 0) {
      setNegativeIndexWarning(`[SECURITY BUG: NEGATIVE PAGINATION]: Page index ${newPage} accepted; backend dumps unauthenticated log buffer!`);
    } else {
      setNegativeIndexWarning(null);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-5xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 15]: CSS FLOAT BUG & NEGATIVE INDEX
        </span>
      </header>

      <main className="max-w-5xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b-2 border-black gap-3">
          <div className="flex items-center gap-2">
            <FileText size={18} />
            <h1 className="font-mono font-black text-base uppercase">Compliance Audit Trail & Event Log</h1>
          </div>

          <div className="flex items-center gap-2">
            <label htmlFor="select-severity" className="font-mono text-xs text-neutral-500">
              Severity Filter:
            </label>
            {/* [INTENTIONAL DEFECT: Selecting WARN triggers CSS float misaligning table column headers] */}
            <select
              id="select-severity"
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="border-2 border-black p-1.5 font-mono text-xs bg-white focus:outline-none"
            >
              <option value="ALL">All Severities</option>
              <option value="INFO">INFO Only</option>
              <option value="WARN">WARN (Defect: Breaks Column Alignment)</option>
            </select>
          </div>
        </div>

        {negativeIndexWarning && (
          <div id="negative-page-alert" className="mb-4 p-2.5 bg-red-50 border border-red-600 font-mono text-xs text-red-900">
            {negativeIndexWarning}
          </div>
        )}

        {/* [INTENTIONAL DEFECT: CSS Float / Flex conflict when severity == WARN] */}
        <div className={`overflow-x-auto border-2 border-black ${severity === "WARN" ? "pl-24 -ml-12" : ""}`}>
          <table className="w-full text-left font-mono text-xs border-collapse">
            <thead className="bg-black text-white">
              <tr>
                <th className="p-2 border border-neutral-700">Log ID</th>
                <th className="p-2 border border-neutral-700">Timestamp</th>
                <th className="p-2 border border-neutral-700">Actor</th>
                <th className="p-2 border border-neutral-700">Action</th>
                <th className="p-2 border border-neutral-700">Severity</th>
              </tr>
            </thead>
            <tbody>
              {AUDIT_ENTRIES.map((entry) => (
                <tr key={entry.id} className="border-b border-black hover:bg-neutral-50">
                  <td className="p-2 font-bold">{entry.id}</td>
                  <td className="p-2 text-neutral-500">{entry.timestamp}</td>
                  <td className="p-2">{entry.actor}</td>
                  <td className="p-2">{entry.action}</td>
                  <td className="p-2">
                    <span className="px-1.5 py-0.5 border border-black bg-neutral-100">{entry.severity}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination controls with negative index vulnerability */}
        <div className="flex items-center justify-between pt-4 mt-2 font-mono text-xs">
          <span>Current Page Index: <strong id="current-page-label">{page}</strong></span>
          <div className="space-x-2">
            <button
              id="btn-prev-page"
              onClick={() => handlePageChange(-1)}
              className="border border-black px-2.5 py-1 bg-neutral-100 hover:bg-neutral-200"
            >
              Previous Page (Can Go Negative!)
            </button>
            <button
              id="btn-next-page"
              onClick={() => handlePageChange(1)}
              className="border border-black px-2.5 py-1 bg-neutral-100 hover:bg-neutral-200"
            >
              Next Page
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
