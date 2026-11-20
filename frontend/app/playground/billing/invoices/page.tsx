"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Receipt, ArrowLeft, Download, AlertTriangle } from "lucide-react";

interface Invoice {
  id: string;
  amount: number;
  status: string;
  due: string;
}

const INVOICES: Invoice[] = [
  {"id": "INV-2026-001", "amount": 1699.00, "status": "Paid", "due": "2026-11-01"},
  {"id": "INV-2026-002", "amount": 499.00, "status": "Pending", "due": "2026-11-15"},
];

export default function PlaygroundInvoicesPage() {
  const [currency, setCurrency] = useState("USD");
  const [traversalResult, setTraversalResult] = useState<string | null>(null);

  // [INTENTIONAL DEFECT: Currency symbol desyncs from selected currency]
  const getCurrencySymbol = () => {
    if (currency === "EUR") return "¥"; // Intentionally returns wrong symbol (Yen instead of Euro)
    if (currency === "GBP") return "$"; // Intentionally returns Dollar instead of Pound
    return "$";
  };

  // [INTENTIONAL DEFECT: Path Traversal Simulation on download]
  const handleDownloadInvoice = async (filename: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/playground/invoices/download?file=${encodeURIComponent(filename)}`);
      const data = await res.json();
      if (data.vulnerable) {
        setTraversalResult(`[PATH TRAVERSAL DEFECT]: Server exposed sensitive system stream: ${data.content}`);
      } else {
        setTraversalResult(`Downloaded: ${data.filename}`);
      }
    } catch {
      setTraversalResult("File downloaded successfully.");
    }
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-4xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 10]: DROPDOWN DESYNC & PATH TRAVERSAL
        </span>
      </header>

      <main className="max-w-4xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b-2 border-black gap-3">
          <div className="flex items-center gap-2">
            <Receipt size={18} />
            <h1 className="font-mono font-black text-base uppercase">Billing Invoices & Ledger</h1>
          </div>

          <div className="flex items-center gap-2">
            <label htmlFor="select-currency" className="font-mono text-xs text-neutral-500">
              Currency Display:
            </label>
            {/* [INTENTIONAL DEFECT: Currency dropdown desyncs symbol] */}
            <select
              id="select-currency"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="border-2 border-black p-1.5 font-mono text-xs bg-white focus:outline-none"
            >
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (Defect: Displays ¥)</option>
              <option value="GBP">GBP (Defect: Displays $)</option>
            </select>
          </div>
        </div>

        {traversalResult && (
          <div id="traversal-alert" className="mb-4 p-2.5 bg-red-50 border border-red-600 font-mono text-xs text-red-900">
            {traversalResult}
          </div>
        )}

        <div className="overflow-x-auto border-2 border-black">
          <table className="w-full text-left font-mono text-xs border-collapse">
            <thead className="bg-black text-white">
              <tr>
                <th className="p-2 border border-neutral-700">Invoice ID</th>
                <th className="p-2 border border-neutral-700">Due Date</th>
                <th className="p-2 border border-neutral-700">Amount</th>
                <th className="p-2 border border-neutral-700">Status</th>
                <th className="p-2 border border-neutral-700 text-center">Download (Path Traversal Demo)</th>
              </tr>
            </thead>
            <tbody>
              {INVOICES.map((inv) => (
                <tr key={inv.id} className="border-b border-black hover:bg-neutral-50">
                  <td className="p-2 font-bold">{inv.id}</td>
                  <td className="p-2">{inv.due}</td>
                  <td className="p-2 font-black">
                    <span id={`currency-symbol-${inv.id}`}>{getCurrencySymbol()}</span>
                    {inv.amount.toFixed(2)}
                  </td>
                  <td className="p-2">{inv.status}</td>
                  <td className="p-2 text-center space-x-2">
                    <button
                      id={`btn-download-${inv.id}`}
                      onClick={() => handleDownloadInvoice(`${inv.id}.pdf`)}
                      className="border border-black px-2 py-0.5 text-[10px] bg-neutral-100 hover:bg-neutral-200"
                    >
                      Normal PDF
                    </button>
                    {/* [INTENTIONAL DEFECT: Path traversal trigger] */}
                    <button
                      id={`btn-traversal-${inv.id}`}
                      onClick={() => handleDownloadInvoice(`../../etc/passwd`)}
                      className="border border-red-600 text-red-900 bg-red-50 px-2 py-0.5 text-[10px] hover:bg-red-100"
                    >
                      Exploit: ../../etc/passwd
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
