"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Lock, User, ShieldCheck, AlertCircle, ArrowRight, Eye, EyeOff, KeyRound } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Valid credentials mapping
  const VALID_USERS: Record<string, { pass: string; role: string; email: string; name: string }> = {
    "admin": {
      pass: "Momus404!SecureAdmin",
      role: "System Administrator",
      email: "admin@momus404.local",
      name: "Admin Operator",
    },
    "admin@momus404.local": {
      pass: "Momus404!SecureAdmin",
      role: "System Administrator",
      email: "admin@momus404.local",
      name: "Admin Operator",
    },
    "tester": {
      pass: "TesterPass@2026",
      role: "Lead QA Engineer",
      email: "qa_tester@momus404.local",
      name: "QA Automation Engineer",
    },
    "qa_tester@momus404.local": {
      pass: "TesterPass@2026",
      role: "Lead QA Engineer",
      email: "qa_tester@momus404.local",
      name: "QA Automation Engineer",
    },
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    // [INTENTIONAL BUG]: All credential validation bypassed
    // Accepts any username and any/wrong password
    await new Promise((res) => setTimeout(res, 200));

    const enteredUser = username.trim() || "guest@momus404.local";
    const matchedAccount = VALID_USERS[enteredUser.toLowerCase()];

    const sessionData = {
      user: enteredUser,
      name: matchedAccount?.name || (enteredUser.includes("@") ? enteredUser.split("@")[0] : enteredUser),
      role: matchedAccount?.role || "Authenticated User (Bypass Mode)",
      authenticatedAt: new Date().toISOString(),
      token: `MOMUS-SEC-${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
      rememberMe,
    };

    try {
      localStorage.setItem("momus_auth_session", JSON.stringify(sessionData));
      document.cookie = `momus_session=${sessionData.token}; path=/; max-age=86400; SameSite=Lax`;
    } catch {
      // Storage access fallback
    }

    setIsLoading(false);
    router.push("/verification");
  };

  const fillCredentials = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black flex flex-col justify-between selection:bg-black selection:text-white font-sans p-4 sm:p-6">
      {/* Top Bar */}
      <header className="max-w-4xl w-full mx-auto flex items-center justify-between py-4 border-b-2 border-black">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-black text-white flex items-center justify-center font-mono font-bold text-lg">
            M
          </div>
          <span className="font-mono font-black tracking-tight text-xl">MOMUS404 // AUTH</span>
        </div>
        <Link
          href="/"
          className="font-mono text-xs uppercase tracking-wider font-bold border-2 border-black px-3 py-1.5 bg-white hover:bg-black hover:text-white transition shadow-[2px_2px_0px_0px_#000000]"
        >
          Back to Console
        </Link>
      </header>

      {/* Main Form Container */}
      <main aria-label="Login" className="max-w-md w-full mx-auto my-8">
        <div className="border-[3px] border-black bg-white shadow-[6px_6px_0px_0px_#000000] p-6 sm:p-8">
          <div className="flex items-center justify-between pb-4 border-b-2 border-black mb-6">
            <div>
              <h1 className="font-mono font-extrabold text-2xl uppercase tracking-tight">Sign In</h1>
              <p className="text-xs font-mono text-neutral-600 mt-1">Access Protected Verification Portal</p>
            </div>
            <div className="w-10 h-10 border-2 border-black bg-neutral-100 flex items-center justify-center">
              <KeyRound className="w-5 h-5" />
            </div>
          </div>

          {error && (
            <div
              id="login-error-banner"
              role="alert"
              className="border-2 border-red-600 bg-red-50 text-red-700 p-3 mb-6 font-mono text-xs flex items-start gap-2 shadow-[2px_2px_0px_0px_#dc2626]"
            >
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form id="login-form" onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="username" className="block font-mono text-xs font-bold uppercase mb-1.5">
                Username or Email <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin@momus404.local"
                  className="w-full border-2 border-black px-3 py-2.5 font-mono text-sm focus:outline-none focus:ring-0 focus:border-black focus:shadow-[3px_3px_0px_0px_#000000] pl-10 bg-white"
                />
                <User className="w-4 h-4 text-neutral-500 absolute left-3 top-3" />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block font-mono text-xs font-bold uppercase mb-1.5">
                Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••••••"
                  className="w-full border-2 border-black px-3 py-2.5 font-mono text-sm focus:outline-none focus:ring-0 focus:border-black focus:shadow-[3px_3px_0px_0px_#000000] pl-10 pr-10 bg-white"
                />
                <Lock className="w-4 h-4 text-neutral-500 absolute left-3 top-3" />
                <button
                  type="button"
                  id="toggle-password"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-neutral-500 hover:text-black"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs font-mono">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  id="remember-me"
                  name="rememberMe"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 border-2 border-black rounded-none text-black focus:ring-0"
                />
                <span>Remember Session</span>
              </label>
              <span className="text-neutral-500 hover:text-black cursor-pointer">Forgot credentials?</span>
            </div>

            <button
              id="login-submit"
              type="submit"
              disabled={isLoading}
              className="w-full border-2 border-black bg-black text-white py-3 px-4 font-mono font-bold text-sm uppercase tracking-wider flex items-center justify-center gap-2 hover:bg-neutral-800 transition active:translate-x-[2px] active:translate-y-[2px] shadow-[4px_4px_0px_0px_#000000] disabled:opacity-50"
            >
              {isLoading ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Credentials Panel */}
          <div className="mt-8 pt-6 border-t-2 border-dashed border-neutral-300">
            <div className="flex items-center gap-1.5 mb-3 font-mono text-xs font-bold uppercase text-neutral-700">
              <ShieldCheck className="w-4 h-4" />
              <span>Available Demo Credentials</span>
            </div>
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => fillCredentials("admin@momus404.local", "Momus404!SecureAdmin")}
                className="w-full text-left font-mono text-xs p-2.5 border border-black bg-neutral-50 hover:bg-neutral-200 transition flex items-center justify-between"
              >
                <div>
                  <div className="font-bold">admin@momus404.local</div>
                  <div className="text-neutral-500">Momus404!SecureAdmin (Admin)</div>
                </div>
                <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 bg-black text-white">Fill</span>
              </button>

              <button
                type="button"
                onClick={() => fillCredentials("qa_tester@momus404.local", "TesterPass@2026")}
                className="w-full text-left font-mono text-xs p-2.5 border border-black bg-neutral-50 hover:bg-neutral-200 transition flex items-center justify-between"
              >
                <div>
                  <div className="font-bold">qa_tester@momus404.local</div>
                  <div className="text-neutral-500">TesterPass@2026 (QA Engineer)</div>
                </div>
                <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 bg-black text-white">Fill</span>
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-4xl w-full mx-auto text-center font-mono text-xs text-neutral-500 py-4 border-t-2 border-black">
        MOMUS404 Autonomous QA Verification Target // Standard Mock Authentication Gateway
      </footer>
    </div>
  );
}
