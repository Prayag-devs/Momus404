"use client";

import React, { useState } from "react";
import Link from "next/link";
import { KeyRound, ArrowLeft, RefreshCw, AlertCircle } from "lucide-react";

export default function PlaygroundIntegrationsPage() {
  const [apiKey] = useState("momus_live_sec_99410294821");
  const [http405Error, setHttp405Error] = useState<string | null>(null);

  // [INTENTIONAL DEFECT: Makes GET request to endpoint requiring POST, causing HTTP 405 Method Not Allowed]
  const handleRegenerateKey = async () => {
    setHttp405Error(null);
    try {
      const res = await fetch("http://localhost:8000/api/playground/integrations/regenerate-key", {
        method: "GET", // Defect: GET instead of POST
      });
      if (!res.ok) {
        setHttp405Error(`[HTTP 405 METHOD NOT ALLOWED]: ${await res.text()}`);
      }
    } catch (err: any) {
      setHttp405Error(`HTTP 405 Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-4xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 14]: SECRET LEAK & HTTP 405
        </span>
      </header>

      <main className="max-w-4xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex items-center gap-2 border-b-2 border-black pb-3 mb-5">
          <KeyRound size={18} />
          <h1 className="font-mono font-black text-base uppercase">API Key & Webhook Integrations</h1>
        </div>

        {http405Error && (
          <div id="http-405-banner" className="mb-4 p-3 bg-red-50 border border-red-600 font-mono text-xs text-red-900 flex items-start gap-2">
            <AlertCircle size={15} className="text-red-600 shrink-0 mt-0.5" />
            <span>{http405Error}</span>
          </div>
        )}

        <div className="space-y-4">
          <div className="border border-neutral-300 p-4 bg-neutral-50">
            <span className="font-mono text-xs font-bold block mb-1">Production Secret Key</span>
            {/* [INTENTIONAL DEFECT: Secret key exposed in cleartext DOM attribute 'data-raw-secret'] */}
            <div
              id="api-secret-container"
              data-raw-secret={apiKey}
              className="flex items-center justify-between border-2 border-black p-2 bg-white"
            >
              <code className="font-mono text-xs">momus_live_sec_••••••••••••</code>
              <span className="font-mono text-[10px] text-red-600 font-bold">
                [LEAK DEFECT]: Cleartext stored in data-raw-secret attribute!
              </span>
            </div>
          </div>

          <div className="pt-2">
            <button
              id="btn-regenerate-key"
              onClick={handleRegenerateKey}
              className="border-2 border-black bg-black text-white px-4 py-2 text-xs font-mono font-bold flex items-center gap-1.5 hover:bg-neutral-800 transition"
            >
              <RefreshCw size={13} /> Regenerate Secret Key (Buggy GET Method)
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
