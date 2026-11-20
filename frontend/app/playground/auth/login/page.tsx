"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Lock, User, AlertCircle, ArrowLeft, Loader2 } from "lucide-react";

export default function PlaygroundLoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [authSuccess, setAuthSuccess] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // [INTENTIONAL BUG]: If form is empty, button spinner hangs indefinitely
    if (!username && !password) {
      // hangs forever — loading spinner defect
      return;
    }

    setTimeout(() => {
      setLoading(false);
      // [INTENTIONAL BUG: Auth Bypass]: Accepts any credentials without validation
      setAuthSuccess(true);
    }, 400);
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8 flex flex-col justify-between">
      <header className="max-w-xl mx-auto w-full flex items-center justify-between pb-4 border-b-2 border-black">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 01]: AUTH PORTAL
        </span>
      </header>

      <main className="max-w-md mx-auto w-full border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000] my-8">
        <div className="flex items-center gap-2 border-b-2 border-black pb-3 mb-5">
          <Lock size={18} strokeWidth={2.5} />
          <h1 className="font-mono font-black text-base uppercase">Enterprise Sign In</h1>
        </div>

        {authSuccess && (
          <div id="auth-status-banner" className="mb-4 p-3 bg-emerald-50 border border-emerald-600 text-emerald-800 font-mono text-xs">
            ✓ Authenticated successfully! Welcome {username || "Guest"}. (Bypass mode active)
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block font-mono text-xs font-bold mb-1" htmlFor="username">
              Username / Corporate Email
            </label>
            <input
              id="username"
              name="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="operator@corp.local"
              className="w-full border-2 border-black p-2 font-mono text-xs focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-mono text-xs font-bold mb-1" htmlFor="password">
              Password
            </label>
            {/* [INTENTIONAL DEFECT: data-plaintext-leak contains user password in plain DOM attribute] */}
            <input
              id="password"
              name="password"
              type="password"
              data-plaintext-leak={password}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full border-2 border-black p-2 font-mono text-xs focus:outline-none"
            />
          </div>

          <button
            id="login-submit"
            type="submit"
            disabled={loading}
            className="w-full bg-black text-white hover:bg-neutral-800 transition font-mono text-xs font-bold py-3 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 size={13} className="animate-spin" /> Authenticating…
              </>
            ) : (
              "Sign In to Enterprise Portal"
            )}
          </button>
        </form>
      </main>

      <footer className="text-center font-mono text-xs text-neutral-500">
        MOMUS404 TESTBENCH // TARGET MODULE 01
      </footer>
    </div>
  );
}
