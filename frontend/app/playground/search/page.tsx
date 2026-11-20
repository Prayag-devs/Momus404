"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Search, ArrowLeft, Database, AlertTriangle } from "lucide-react";

export default function PlaygroundSearchPage() {
  const [query, setQuery] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [sqliAlert, setSqliAlert] = useState(false);

  // [INTENTIONAL DEFECT: On mouse hover, dropdown disappears immediately]
  const handleDropdownHover = () => {
    setShowSuggestions(false); // Disappears on mouse enter!
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`http://localhost:8000/api/playground/search?query=${encodeURIComponent(query)}`);
      const data = await res.json();
      setSearchResults(data.results || []);
      setSqliAlert(data.sqli_detected || false);
    } catch {
      setSearchResults([]);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-3xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 12]: HOVER DROPDOWN FLICKER & SQLI
        </span>
      </header>

      <main className="max-w-3xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex items-center gap-2 border-b-2 border-black pb-3 mb-5">
          <Search size={18} />
          <h1 className="font-mono font-black text-base uppercase">Global Search & Knowledge Engine</h1>
        </div>

        {sqliAlert && (
          <div id="sqli-alert-banner" className="mb-4 p-3 bg-red-50 border border-red-600 text-red-900 font-mono text-xs">
            <p className="font-bold">⚠️ CRITICAL: SQL INJECTION VULNERABILITY EXPLOITED</p>
            <p>Query string contains unescaped single quote or boolean bypass syntax.</p>
          </div>
        )}

        <form onSubmit={handleSearch} className="relative mb-6">
          <div className="flex gap-2">
            <input
              id="search-input"
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setShowSuggestions(e.target.value.length > 0);
              }}
              placeholder="Search products or try injection payload: ' OR '1'='1"
              className="flex-1 border-2 border-black p-2.5 font-mono text-xs focus:outline-none"
            />
            <button
              id="btn-search-submit"
              type="submit"
              className="bg-black text-white px-5 py-2.5 font-mono text-xs font-bold hover:bg-neutral-800 transition"
            >
              Search
            </button>
          </div>

          {/* [INTENTIONAL DEFECT: onMouseEnter closes suggestions dropdown!] */}
          {showSuggestions && (
            <div
              id="suggestions-dropdown"
              onMouseEnter={handleDropdownHover}
              className="absolute left-0 right-0 top-full mt-1 border-2 border-black bg-white p-2 z-50 shadow-[4px_4px_0px_0px_#000000]"
            >
              <p className="text-[10px] font-mono text-red-600 font-bold mb-1">
                [HOVER BUG]: Hovering over this dropdown immediately closes it!
              </p>
              <div className="space-y-1 font-mono text-xs text-neutral-700">
                <div className="p-1 hover:bg-neutral-100 cursor-pointer">Edge AI Inference Accelerator P1000</div>
                <div className="p-1 hover:bg-neutral-100 cursor-pointer">Momus Enterprise License</div>
                <div className="p-1 hover:bg-neutral-100 cursor-pointer">Vault Encrypted Storage 1TB</div>
              </div>
            </div>
          )}
        </form>

        <div className="space-y-2">
          <h3 className="font-mono text-xs font-bold uppercase text-neutral-500">Query Results ({searchResults.length})</h3>
          {searchResults.length === 0 ? (
            <p className="font-mono text-xs text-neutral-400">No matching search records found.</p>
          ) : (
            searchResults.map((r, i) => (
              <div key={i} className="border border-black p-2.5 bg-neutral-50 font-mono text-xs flex justify-between">
                <span className="font-bold">{r.title || r.name}</span>
                <span className="text-neutral-500">{r.match || `$${r.price}`}</span>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}
