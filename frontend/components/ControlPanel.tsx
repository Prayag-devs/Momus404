"use client";

import { useState, useRef, useCallback, useId } from "react";
import {
  UploadCloud,
  Link,
  Lock,
  User,
  Play,
  Pause,
  Zap,
  FlaskConical,
  Square,
  Trash2,
  FileText,
} from "lucide-react";
import type { TestCase } from "@/lib/api";

interface ControlPanelProps {
  onRun: (url: string, file: File | null, username: string, password: string) => void;
  onDryRun: (url: string, file: File | null, username: string, password: string) => void;
  onGenerate: (url: string, file: File | null, username?: string, password?: string) => void;
  onPause?: () => void;
  onResume?: () => void;
  onStop?: () => void;
  onCancel: () => void;
  onClear: () => void;
  isRunning: boolean;
  isPaused?: boolean;
  parsedCases: TestCase[];
  runId: string | null;
}

export default function ControlPanel({
  onRun,
  onDryRun,
  onGenerate,
  onPause,
  onResume,
  onStop,
  onCancel,
  onClear,
  isRunning,
  isPaused = false,
  parsedCases,
  runId,
}: ControlPanelProps) {
  const urlId = useId();
  const userIdField = useId();
  const passId = useId();

  const [targetUrl, setTargetUrl] = useState("http://localhost:3000/login");
  const [file, setFile] = useState<File | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [urlError, setUrlError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const normalizeUrl = (raw: string): string => {
    let u = raw.trim();
    if (!u) return "";
    if (!/^https?:\/\//i.test(u)) {
      if (/^(localhost|127\.0\.0\.1)(:\d+)?/i.test(u)) {
        u = `http://${u}`;
      } else {
        u = `https://${u}`;
      }
    }
    return u;
  };

  const validateUrl = (url: string): boolean => {
    const norm = normalizeUrl(url);
    if (!norm) {
      setUrlError("Please enter a target URL (e.g. https://staging.example.com)");
      return false;
    }
    try {
      new URL(norm);
      setUrlError("");
      return true;
    } catch {
      setUrlError("Enter a valid URL (e.g. https://example.com)");
      return false;
    }
  };

  const handleFile = useCallback((f: File | null) => {
    if (!f) return;
    if (!f.name.endsWith(".xlsx")) {
      alert("Only .xlsx files are supported.");
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      alert("File exceeds 10 MB limit.");
      return;
    }
    setFile(f);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const f = e.dataTransfer.files[0];
      handleFile(f);
    },
    [handleFile]
  );

  const handleRun = () => {
    const norm = normalizeUrl(targetUrl);
    if (!validateUrl(norm)) return;
    setTargetUrl(norm);
    onRun(norm, file, username, password);
  };

  const handleDryRun = () => {
    const norm = normalizeUrl(targetUrl);
    if (!validateUrl(norm)) return;
    setTargetUrl(norm);
    onDryRun(norm, file, username, password);
  };

  const handleGenerate = () => {
    const norm = normalizeUrl(targetUrl);
    setTargetUrl(norm);
    onGenerate(norm, file, username, password);
  };

  const clearAll = () => {
    setTargetUrl("http://localhost:3000/login");
    setFile(null);
    setUsername("");
    setPassword("");
    setUrlError("");
    onClear();
  };

  return (
    <section className="nb-card p-5 flex flex-col gap-5">
      {/* Section header */}
      <div className="flex items-center gap-2 border-b-2 border-black pb-3">
        <Zap size={16} strokeWidth={2.5} />
        <span className="font-mono font-black text-sm tracking-wider uppercase">Control Panel</span>
        {runId && (
          <span className="ml-auto font-mono text-[10px] text-neutral-500 border border-neutral-400 px-1.5 py-0.5">
            RUN&nbsp;{runId}
          </span>
        )}
      </div>

      {/* Target URL */}
      <div className="flex flex-col gap-1.5">
        <label htmlFor={urlId} className="section-label flex items-center gap-1.5">
          <Link size={11} strokeWidth={2.5} />
          Target URL
        </label>
        <input
          id={urlId}
          type="url"
          className={`nb-input ${urlError ? "border-black shadow-[inset_2px_0_0_0_#000]" : ""}`}
          placeholder="https://staging.example.com"
          value={targetUrl}
          onChange={(e) => {
            setTargetUrl(e.target.value);
            if (urlError) validateUrl(e.target.value);
          }}
          onBlur={() => targetUrl && validateUrl(targetUrl)}
          disabled={isRunning}
          aria-describedby={urlError ? `${urlId}-error` : undefined}
        />
        <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
          <span className="font-mono text-[9px] text-neutral-400">Presets:</span>
          <button
            type="button"
            onClick={() => setTargetUrl("http://localhost:3000/login")}
            className="font-mono text-[9px] border border-neutral-300 bg-neutral-100 hover:bg-neutral-200 px-1.5 py-0.5"
          >
            Local Login
          </button>
          <button
            type="button"
            onClick={() => setTargetUrl("http://localhost:3000/playground")}
            className="font-mono text-[9px] border border-neutral-300 bg-neutral-100 hover:bg-neutral-200 px-1.5 py-0.5 font-bold"
          >
            Target Playground (15 Pages)
          </button>
          <button
            type="button"
            onClick={() => setTargetUrl("https://the-internet.herokuapp.com/login")}
            className="font-mono text-[9px] border border-neutral-300 bg-neutral-100 hover:bg-neutral-200 px-1.5 py-0.5"
          >
            External Heroku Login
          </button>
        </div>
        {urlError && (
          <p id={`${urlId}-error`} className="font-mono text-xs text-black flex items-center gap-1">
            <span className="font-bold">✗</span> {urlError}
          </p>
        )}
      </div>

      {/* File upload */}
      <div className="flex flex-col gap-1.5">
        <span className="section-label flex items-center gap-1.5">
          <FileText size={11} strokeWidth={2.5} />
          Test Specification (.xlsx)
        </span>
        <div
          role="button"
          tabIndex={0}
          aria-label="Drop .xlsx file here or click to select"
          className={`drop-zone h-24 p-3 text-center ${isDragging ? "active" : ""} ${isRunning ? "opacity-50 cursor-not-allowed" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={onDrop}
          onClick={() => !isRunning && fileInputRef.current?.click()}
          onKeyDown={(e) => e.key === "Enter" && !isRunning && fileInputRef.current?.click()}
        >
          <UploadCloud size={20} strokeWidth={2} className="mx-auto mb-1 text-neutral-500" />
          {file ? (
            <div>
              <p className="font-mono text-xs font-bold truncate max-w-[200px] mx-auto">{file.name}</p>
              <p className="font-mono text-[10px] text-neutral-500">
                {(file.size / 1024).toFixed(1)} KB
                {parsedCases.length > 0 && ` · ${parsedCases.length} test cases`}
              </p>
            </div>
          ) : (
            <p className="font-mono text-xs text-neutral-500">
              Drop .xlsx here or click to select
            </p>
          )}
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {/* Credentials */}
      <div className="flex flex-col gap-2 border-2 border-black p-3 bg-neutral-50">
        <div className="flex items-center gap-1.5 mb-1">
          <Lock size={12} strokeWidth={2.5} />
          <span className="font-mono text-[10px] font-bold tracking-wider uppercase">OpenDots Secure Vault</span>
          <span className="ml-auto font-mono text-[9px] text-neutral-500 border border-neutral-400 px-1 py-0.5">
            Isolated from LLM Context
          </span>
        </div>
        <div className="flex flex-col gap-2">
          <div className="relative">
            <User size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-neutral-400" strokeWidth={2} />
            <input
              id={userIdField}
              type="text"
              className="nb-input pl-7"
              placeholder="Username / Email"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isRunning}
              autoComplete="username"
            />
          </div>
          <div className="relative">
            <Lock size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-neutral-400" strokeWidth={2} />
            <input
              id={passId}
              type="password"
              className="nb-input pl-7"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isRunning}
              autoComplete="current-password"
            />
          </div>
        </div>
        <p className="font-mono text-[9px] text-neutral-400 leading-tight">
          Credentials encrypted with Fernet in-memory only. Never logged or sent to LLMs.
        </p>
      </div>

      {/* Primary action */}
      {!isRunning ? (
        <button
          id="btn-run-agent"
          onClick={handleRun}
          className="btn-primary w-full py-3 text-sm tracking-widest flex items-center justify-center gap-2 cursor-pointer"
        >
          <Play size={15} strokeWidth={2.5} />
          [ RUN MOMUS AGENT ]
        </button>
      ) : (
        <div className="grid grid-cols-2 gap-3 w-full">
          <button
            id="btn-pause-agent"
            type="button"
            onClick={() => (isPaused ? onResume?.() : onPause?.())}
            className={`py-3 text-xs font-mono font-bold tracking-wider flex items-center justify-center gap-2 border-2 transition-all cursor-pointer ${
              isPaused
                ? "bg-amber-400 border-black text-black hover:bg-amber-300 shadow-[3px_3px_0px_0px_#000]"
                : "bg-neutral-900 border-black text-amber-300 hover:bg-neutral-800 shadow-[3px_3px_0px_0px_#000]"
            }`}
          >
            {isPaused ? (
              <>
                <Play size={14} strokeWidth={2.5} />
                [ RESUME RUN ]
              </>
            ) : (
              <>
                <Pause size={14} strokeWidth={2.5} />
                [ PAUSE RUN ]
              </>
            )}
          </button>

          <button
            id="btn-stop-agent"
            type="button"
            onClick={() => (onStop ? onStop() : onCancel())}
            className="py-3 text-xs font-mono font-bold tracking-wider flex items-center justify-center gap-2 bg-red-600 border-2 border-black text-white hover:bg-red-500 shadow-[3px_3px_0px_0px_#000] transition-all cursor-pointer"
          >
            <Square size={14} strokeWidth={2.5} />
            [ STOP RUN ]
          </button>
        </div>
      )}

      {/* Secondary actions */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <button
          id="btn-generate"
          onClick={handleGenerate}
          disabled={isRunning}
          className="btn-secondary text-xs py-2 flex items-center justify-center gap-1"
        >
          <Zap size={12} strokeWidth={2} />
          GENERATE TEST
        </button>
        <button
          id="btn-dry-run"
          onClick={handleDryRun}
          disabled={isRunning}
          className="btn-secondary text-xs py-2 flex items-center justify-center gap-1"
        >
          <FlaskConical size={12} strokeWidth={2} />
          DRY RUN
        </button>
        <button
          id="btn-cancel"
          onClick={() => (onStop ? onStop() : onCancel())}
          disabled={!isRunning}
          className="btn-secondary text-xs py-2 flex items-center justify-center gap-1"
        >
          <Square size={12} strokeWidth={2} />
          STOP
        </button>
        <button
          id="btn-clear"
          onClick={clearAll}
          disabled={isRunning}
          className="btn-secondary text-xs py-2 flex items-center justify-center gap-1"
        >
          <Trash2 size={12} strokeWidth={2} />
          CLEAR
        </button>
      </div>
    </section>
  );
}
