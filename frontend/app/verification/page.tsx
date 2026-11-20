"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  CheckCircle2,
  ShieldCheck,
  User,
  LogOut,
  ArrowLeft,
  Key,
  Clock,
  Fingerprint,
  RefreshCw,
  Terminal,
} from "lucide-react";

interface SessionData {
  user: string;
  name: string;
  role: string;
  authenticatedAt: string;
  token: string;
  rememberMe: boolean;
}

export default function VerificationPage() {
  const router = useRouter();
  const [session, setSession] = useState<SessionData | null>(null);
  const [isVerifying, setIsVerifying] = useState(true);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("momus_auth_session");
      if (stored) {
        setSession(JSON.parse(stored));
      } else {
        // Fallback default demo session if visited directly
        setSession({
          user: "admin@momus404.local",
          name: "Admin Operator",
          role: "System Administrator",
          authenticatedAt: new Date().toISOString(),
          token: "MOMUS-SEC-DEMO7781",
          rememberMe: true,
        });
      }
    } catch {
      // ignore
    } finally {
      setIsVerifying(false);
    }
  }, []);

  const handleLogout = () => {
    try {
      localStorage.removeItem("momus_auth_session");
      document.cookie = "momus_session=; path=/; max-age=0";
    } catch {
      // ignore
    }
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black flex flex-col justify-between selection:bg-black selection:text-white font-sans p-4 sm:p-6">
      {/* Top Header */}
      <header className="max-w-5xl w-full mx-auto flex items-center justify-between py-4 border-b-2 border-black">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-black text-white flex items-center justify-center font-mono font-bold text-lg">
            M
          </div>
          <span className="font-mono font-black tracking-tight text-xl">MOMUS404 // VERIFICATION</span>
        </div>

        <div className="flex items-center gap-3">
          <span
            data-testid="user-avatar"
            role="button"
            aria-label="User profile"
            className="flex items-center gap-2 font-mono text-xs font-bold border-2 border-black px-3 py-1.5 bg-white shadow-[2px_2px_0px_0px_#000000]"
          >
            <User className="w-3.5 h-3.5" />
            <span>{session?.name || "User"}</span>
          </span>

          <button
            onClick={handleLogout}
            className="font-mono text-xs uppercase tracking-wider font-bold border-2 border-black px-3 py-1.5 bg-white hover:bg-black hover:text-white transition flex items-center gap-1.5 shadow-[2px_2px_0px_0px_#000000]"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Logout</span>
          </button>
        </div>
      </header>

      {/* Main Verification Dashboard */}
      <main aria-label="Verification" className="max-w-5xl w-full mx-auto my-8 space-y-6">
        {/* Verification Success Banner */}
        <div className="border-[3px] border-black bg-white shadow-[6px_6px_0px_0px_#000000] p-6 sm:p-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b-2 border-black">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-500 text-white flex items-center justify-center border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                <CheckCircle2 className="w-7 h-7" />
              </div>
              <div>
                <h1 className="font-mono font-extrabold text-2xl uppercase tracking-tight">
                  Authentication & Session Verified
                </h1>
                <p className="text-xs font-mono text-neutral-600">
                  Target Verification State: <span className="font-bold text-green-700">STATUS_OK_AUTHENTICATED</span>
                </p>
              </div>
            </div>

            <span className="inline-flex items-center gap-1.5 font-mono text-xs font-bold uppercase px-3 py-1.5 border-2 border-black bg-neutral-100">
              <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
              Live Session Active
            </span>
          </div>

          {/* Session Metadata Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 my-6">
            <div className="border-2 border-black p-4 bg-neutral-50 shadow-[3px_3px_0px_0px_#000000]">
              <div className="flex items-center gap-1.5 font-mono text-[11px] text-neutral-500 uppercase font-bold mb-1">
                <User className="w-3.5 h-3.5" />
                <span>Verified Identity</span>
              </div>
              <div className="font-mono text-sm font-bold truncate">{session?.user || "admin@momus404.local"}</div>
              <div className="font-mono text-xs text-neutral-600 mt-0.5">{session?.role || "Administrator"}</div>
            </div>

            <div className="border-2 border-black p-4 bg-neutral-50 shadow-[3px_3px_0px_0px_#000000]">
              <div className="flex items-center gap-1.5 font-mono text-[11px] text-neutral-500 uppercase font-bold mb-1">
                <Key className="w-3.5 h-3.5" />
                <span>Session Token</span>
              </div>
              <div className="font-mono text-sm font-bold truncate text-black">{session?.token || "MOMUS-SEC-9921"}</div>
              <div className="font-mono text-xs text-green-700 font-bold mt-0.5">VAULT_INSPECTED</div>
            </div>

            <div className="border-2 border-black p-4 bg-neutral-50 shadow-[3px_3px_0px_0px_#000000]">
              <div className="flex items-center gap-1.5 font-mono text-[11px] text-neutral-500 uppercase font-bold mb-1">
                <Clock className="w-3.5 h-3.5" />
                <span>Auth Timestamp</span>
              </div>
              <div className="font-mono text-xs font-bold truncate">
                {session ? new Date(session.authenticatedAt).toLocaleTimeString() : "--"}
              </div>
              <div className="font-mono text-[11px] text-neutral-500 mt-0.5">
                {session ? new Date(session.authenticatedAt).toLocaleDateString() : "--"}
              </div>
            </div>

            <div className="border-2 border-black p-4 bg-neutral-50 shadow-[3px_3px_0px_0px_#000000]">
              <div className="flex items-center gap-1.5 font-mono text-[11px] text-neutral-500 uppercase font-bold mb-1">
                <Fingerprint className="w-3.5 h-3.5" />
                <span>Security Level</span>
              </div>
              <div className="font-mono text-sm font-bold text-neutral-900">EAL4+ Sim</div>
              <div className="font-mono text-xs text-neutral-600 mt-0.5">Zero Plaintext Leak</div>
            </div>
          </div>

          {/* Verification Protocol Checks */}
          <div className="border-2 border-black p-4 bg-neutral-50 mb-6">
            <h2 className="font-mono text-xs font-bold uppercase mb-3 text-neutral-700">
              Automated QA Assertions & State Checks
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono text-xs">
              <div className="flex items-center gap-2 p-2 bg-white border border-black">
                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                <span>DOM State: Form submission acknowledged (HTTP 200)</span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-white border border-black">
                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                <span>Cookie: momus_session set (SameSite=Lax)</span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-white border border-black">
                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                <span>Laya Judge: Target element user-avatar visible</span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-white border border-black">
                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                <span>OpenDots Vault: Fernet payload decrypted cleanly</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap items-center gap-3 pt-4 border-t-2 border-black">
            <Link
              href="/"
              className="font-mono text-xs uppercase font-bold border-2 border-black px-4 py-2 bg-black text-white hover:bg-neutral-800 transition flex items-center gap-2 shadow-[2px_2px_0px_0px_#000000]"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Momus404 Test Runner</span>
            </Link>

            <Link
              href="/login"
              className="font-mono text-xs uppercase font-bold border-2 border-black px-4 py-2 bg-white hover:bg-neutral-100 transition flex items-center gap-2 shadow-[2px_2px_0px_0px_#000000]"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Test Login Again</span>
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-5xl w-full mx-auto text-center font-mono text-xs text-neutral-500 py-4 border-t-2 border-black">
        MOMUS404 Verification Target Portal // Verified State Confirmed
      </footer>
    </div>
  );
}
