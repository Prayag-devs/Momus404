"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  X,
  Zap,
  Play,
  Download,
  FileSpreadsheet,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowRight,
  Code2,
  Copy,
  Check,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import type { TestCase, PlannedStep } from "@/types";

interface GenerateTestModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetUrl: string;
  initialFile: File | null;
  username?: string;
  password?: string;
  onExecuteTest: (testCase: TestCase, targetUrl: string) => void;
}

interface PresetScenario {
  id: string;
  title: string;
  description: string;
  testCase: TestCase;
}

const PRESET_SCENARIOS: PresetScenario[] = [
  {
    id: "preset-login-valid",
    title: "Authentication / Happy Path",
    description: "Valid credentials, form submit, and session redirection verification",
    testCase: {
      id: "TC-AUTH-01",
      title: "Verify Successful Authentication with Valid Credentials",
      preconditions: "Operator at login portal with active network",
      steps:
        "1. Navigate to target login URL\n2. Fill username input with configured user\n3. Fill password input with configured password\n4. Click submit login button\n5. Verify dashboard redirection and session verification badge",
      expected_result: "dashboard visible or redirected",
      priority: "High",
      tags: ["auth", "smoke", "p0"],
    },
  },
  {
    id: "preset-login-invalid",
    title: "Boundary / Invalid Password",
    description: "Incorrect password rejection and error banner visibility test",
    testCase: {
      id: "TC-AUTH-02",
      title: "Verify Login Rejection on Invalid Password",
      preconditions: "User at login portal",
      steps:
        "1. Navigate to target URL\n2. Fill username with valid user\n3. Fill password with 'WrongPassword!99'\n4. Click Login button\n5. Observe rejection banner",
      expected_result: "Error banner or invalid credentials message displayed",
      priority: "High",
      tags: ["auth", "negative", "security"],
    },
  },
  {
    id: "preset-security-absence",
    title: "Security / Link Absence",
    description: "Strict absence check for prohibited reset/signup links in restricted portals",
    testCase: {
      id: "TC-SEC-03",
      title: "Verify Absence of Prohibited Self-Registration & Reset Links",
      preconditions: "Restricted enterprise portal login screen",
      steps:
        "1. Open login portal\n2. Inspect portal interface\n3. Verify absence of 'Forgot Password' or 'Sign Up' links",
      expected_result:
        "Forgot Password' or 'Sign Up' links should strictly NOT be present",
      priority: "Medium",
      tags: ["security", "compliance", "absence"],
    },
  },
  {
    id: "preset-crud-item",
    title: "Dashboard / Record Creation",
    description: "Navigation to dashboard, clicking + New Item, filling details, and saving",
    testCase: {
      id: "TC-DASH-04",
      title: "Verify Dashboard Navigation and Item Creation",
      preconditions: "Authenticated session",
      steps:
        "1. Navigate to /dashboard\n2. Click button '+ New Item'\n3. Fill name with 'Automated Quality Metric'\n4. Click 'Save' button\n5. Verify item appears in widget list",
      expected_result: "dashboard loaded and item appears in list",
      priority: "Medium",
      tags: ["dashboard", "crud"],
    },
  },
  {
    id: "preset-quick-smoke",
    title: "System / Quick Smoke",
    description: "Fast HTTP & DOM presence verification of root container",
    testCase: {
      id: "TC-SMOKE-05",
      title: "Verify Root Viewport Container Render",
      preconditions: "Web application running",
      steps: "1. Navigate to /\n2. Inspect DOM content and verify main viewport rendered",
      expected_result: "page loaded successfully and content visible",
      priority: "Low",
      tags: ["smoke", "health"],
    },
  },
];

export default function GenerateTestModal({
  isOpen,
  onClose,
  targetUrl: initialTargetUrl,
  initialFile,
  username = "",
  password = "",
  onExecuteTest,
}: GenerateTestModalProps) {
  const [activeTab, setActiveTab] = useState<"preset" | "file">("preset");
  const [targetUrl, setTargetUrl] = useState(initialTargetUrl || "http://localhost:3000/login");
  const [selectedPresetId, setSelectedPresetId] = useState<string>("preset-login-valid");

  // Custom / Selected test case
  const [tcId, setTcId] = useState<string>("TC-GEN-01");
  const [tcTitle, setTcTitle] = useState<string>("Verify Authentication & Portal Flow");
  const [tcPreconditions, setTcPreconditions] = useState<string>("Portal accessible");
  const [tcSteps, setTcSteps] = useState<string>(
    "1. Navigate to target URL\n2. Enter username and password\n3. Click Login button\n4. Verify dashboard visible"
  );
  const [tcExpected, setTcExpected] = useState<string>("dashboard visible or redirected");
  const [tcPriority, setTcPriority] = useState<string>("High");

  // Excel mode state
  const [file, setFile] = useState<File | null>(initialFile);
  const [parsedCases, setParsedCases] = useState<TestCase[]>([]);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [selectedCaseIndex, setSelectedCaseIndex] = useState<number>(0);

  // Generation state
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generatedSteps, setGeneratedSteps] = useState<PlannedStep[] | null>(null);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [showJson, setShowJson] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  const modalRef = useRef<HTMLDivElement>(null);

  // Synchronize initial file / url when modal opens
  useEffect(() => {
    if (isOpen) {
      setTargetUrl(initialTargetUrl || "http://localhost:3000/login");
      if (initialFile) {
        setFile(initialFile);
        setActiveTab("file");
        handleUploadAndParse(initialFile);
      } else {
        setActiveTab("preset");
        // Load initial default preset
        const p = PRESET_SCENARIOS[0];
        setTcId(p.testCase.id);
        setTcTitle(p.testCase.title);
        setTcPreconditions(p.testCase.preconditions);
        setTcSteps(p.testCase.steps);
        setTcExpected(p.testCase.expected_result);
        setTcPriority(p.testCase.priority);
      }
    }
  }, [isOpen, initialFile, initialTargetUrl]);

  // Handle Preset Selection
  const handleSelectPreset = (preset: PresetScenario) => {
    setSelectedPresetId(preset.id);
    setTcId(preset.testCase.id);
    setTcTitle(preset.testCase.title);
    setTcPreconditions(preset.testCase.preconditions);
    setTcSteps(preset.testCase.steps);
    setTcExpected(preset.testCase.expected_result);
    setTcPriority(preset.testCase.priority);
    setGeneratedSteps(null);
    setGenerationError(null);
  };

  // Upload and parse excel
  const handleUploadAndParse = async (f: File) => {
    setIsUploading(true);
    setGenerationError(null);
    try {
      const res = await apiClient.uploadSpec(f);
      setParsedCases(res.test_cases);
      if (res.test_cases.length > 0) {
        setSelectedCaseIndex(0);
        const first = res.test_cases[0];
        setTcId(first.id);
        setTcTitle(first.title);
        setTcPreconditions(first.preconditions);
        setTcSteps(first.steps);
        setTcExpected(first.expected_result);
        setTcPriority(first.priority);
      }
    } catch (err) {
      setGenerationError(err instanceof Error ? err.message : "Failed to parse spec file.");
    } finally {
      setIsUploading(false);
    }
  };

  // Generate Test Plan
  const handleGeneratePlan = async () => {
    setIsGenerating(true);
    setGenerationError(null);
    try {
      const payload: Partial<TestCase> & { target_url?: string; username?: string; password?: string } = {
        id: tcId,
        title: tcTitle,
        preconditions: tcPreconditions,
        steps: tcSteps,
        expected_result: tcExpected,
        priority: tcPriority,
        target_url: targetUrl,
        username,
        password,
      };

      const res = await apiClient.generateTest(payload);
      setGeneratedSteps(res.steps);
    } catch (err) {
      setGenerationError(err instanceof Error ? err.message : "Failed to generate plan.");
    } finally {
      setIsGenerating(false);
    }
  };

  // Execute directly
  const handleExecuteNow = () => {
    const currentCase: TestCase = {
      id: tcId || "TC-GEN-01",
      title: tcTitle || "Generated Test Scenario",
      preconditions: tcPreconditions,
      steps: tcSteps,
      expected_result: tcExpected,
      priority: tcPriority,
      tags: ["generated", "autonomous-qa"],
    };
    onExecuteTest(currentCase, targetUrl);
    onClose();
  };

  // Export as .xlsx
  const handleExportXlsx = async () => {
    setIsExporting(true);
    try {
      const currentCase: TestCase = {
        id: tcId || "TC-GEN-01",
        title: tcTitle || "Generated Test Scenario",
        preconditions: tcPreconditions,
        steps: tcSteps,
        expected_result: tcExpected,
        priority: tcPriority,
        tags: ["generated", "autonomous-qa"],
      };
      const casesToExport = parsedCases.length > 0 && activeTab === "file" ? parsedCases : [currentCase];
      const blob = await apiClient.exportSpec(casesToExport);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${tcId || "momus404"}_spec.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("[GenerateModal] Export failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  // Copy JSON
  const handleCopyJson = () => {
    if (!generatedSteps) return;
    navigator.clipboard.writeText(JSON.stringify(generatedSteps, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="MOMUS404 Test Generator"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto"
      ref={modalRef}
    >
      <div className="bg-white border-[3px] border-black text-black w-full max-w-5xl shadow-[10px_10px_0px_0px_#000000] flex flex-col max-h-[92vh] overflow-hidden">
        {/* ── Modal Header ── */}
        <div className="border-b-[3px] border-black bg-black text-white p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-white text-black">
              <Zap size={18} strokeWidth={2.5} />
            </div>
            <div>
              <h2 className="font-mono font-black text-sm tracking-wider uppercase flex items-center gap-2">
                TEST GENERATOR & ACTION PLAN RESOLVER
                <span className="text-[10px] bg-neutral-800 text-neutral-300 px-2 py-0.5 border border-neutral-700">
                  SYSTEM-1 JEV + HERMES
                </span>
              </h2>
              <p className="text-[11px] font-mono text-neutral-400 mt-0.5">
                Generate deterministic browser action sequences with sub-50ms assertion trees.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="p-1 hover:bg-neutral-800 text-neutral-400 hover:text-white transition-colors"
          >
            <X size={20} strokeWidth={2.5} />
          </button>
        </div>

        {/* ── Target URL Bar & Source Tabs ── */}
        <div className="border-b-2 border-black bg-neutral-100 p-3 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2 flex-1">
            <span className="font-mono text-xs font-bold uppercase text-neutral-600 shrink-0">
              Target URL:
            </span>
            <input
              type="text"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              placeholder="http://localhost:3000/login"
              className="font-mono text-xs font-bold px-3 py-1.5 border-2 border-black bg-white flex-1 focus:outline-none"
            />
          </div>

          <div className="flex border-2 border-black bg-white shrink-0">
            <button
              type="button"
              onClick={() => setActiveTab("preset")}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase flex items-center gap-1.5 transition-colors ${
                activeTab === "preset"
                  ? "bg-black text-white"
                  : "bg-white text-black hover:bg-neutral-100"
              }`}
            >
              <Cpu size={14} />
              AI Presets / Custom
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("file")}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase flex items-center gap-1.5 transition-colors border-l-2 border-black ${
                activeTab === "file"
                  ? "bg-black text-white"
                  : "bg-white text-black hover:bg-neutral-100"
              }`}
            >
              <FileSpreadsheet size={14} />
              From Excel Spec {file ? `(${parsedCases.length})` : ""}
            </button>
          </div>
        </div>

        {/* ── Main Body Split ── */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-y-auto">
          {/* Left Column: Spec Configuration & Presets (5 cols) */}
          <div className="lg:col-span-5 p-4 border-r-0 lg:border-r-2 border-black space-y-4 bg-neutral-50/50">
            {activeTab === "preset" ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-[11px] font-mono font-bold uppercase text-neutral-600 mb-1.5">
                    1. Select QA Scenario Preset:
                  </label>
                  <div className="grid grid-cols-1 gap-1.5">
                    {PRESET_SCENARIOS.map((p) => {
                      const isSelected = selectedPresetId === p.id;
                      return (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => handleSelectPreset(p)}
                          className={`text-left p-2.5 border-2 text-xs font-mono transition-all ${
                            isSelected
                              ? "border-black bg-black text-white shadow-[3px_3px_0px_0px_#f59e0b]"
                              : "border-black/30 bg-white hover:border-black text-neutral-800"
                          }`}
                        >
                          <div className="flex items-center justify-between font-bold">
                            <span>{p.title}</span>
                            <span
                              className={`text-[9px] px-1.5 py-0.2 uppercase border ${
                                isSelected
                                  ? "bg-neutral-800 text-amber-400 border-neutral-700"
                                  : "bg-neutral-100 text-neutral-600 border-neutral-300"
                              }`}
                            >
                              {p.testCase.priority}
                            </span>
                          </div>
                          <p
                            className={`text-[10px] mt-1 line-clamp-1 ${
                              isSelected ? "text-neutral-300" : "text-neutral-500"
                            }`}
                          >
                            {p.description}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="space-y-3 pt-2 border-t-2 border-neutral-200">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono font-bold uppercase text-neutral-600">
                      2. Scenario Details:
                    </span>
                    <input
                      type="text"
                      value={tcId}
                      onChange={(e) => setTcId(e.target.value)}
                      className="text-[10px] font-mono font-bold border border-black px-2 py-0.5 bg-white w-28 text-center"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-mono text-neutral-500 uppercase mb-1">
                      Title
                    </label>
                    <input
                      type="text"
                      value={tcTitle}
                      onChange={(e) => setTcTitle(e.target.value)}
                      className="w-full text-xs font-mono font-bold p-2 border-2 border-black bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-mono text-neutral-500 uppercase mb-1">
                      Step Instructions (Gherkin / Natural Language)
                    </label>
                    <textarea
                      rows={4}
                      value={tcSteps}
                      onChange={(e) => setTcSteps(e.target.value)}
                      className="w-full text-xs font-mono p-2 border-2 border-black bg-white resize-none"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-mono text-neutral-500 uppercase mb-1">
                      Expected Validation / Verdict Rule
                    </label>
                    <input
                      type="text"
                      value={tcExpected}
                      onChange={(e) => setTcExpected(e.target.value)}
                      className="w-full text-xs font-mono p-2 border-2 border-black bg-white"
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-[11px] font-mono font-bold uppercase text-neutral-600 mb-1.5">
                    Excel Test Spec (.xlsx):
                  </label>
                  <label className="border-2 border-dashed border-black p-4 flex flex-col items-center justify-center gap-2 bg-white cursor-pointer hover:bg-neutral-50">
                    <FileSpreadsheet size={24} className="text-neutral-700" />
                    <span className="font-mono text-xs font-bold text-neutral-700">
                      {file ? file.name : "Select or Drop .xlsx spec file"}
                    </span>
                    <span className="text-[10px] font-mono text-neutral-400">
                      (ID, Title, Preconditions, Steps, Expected Result)
                    </span>
                    <input
                      type="file"
                      accept=".xlsx,.xlsm,.xltx"
                      onChange={(e) => {
                        const f = e.target.files?.[0];
                        if (f) {
                          setFile(f);
                          handleUploadAndParse(f);
                        }
                      }}
                      className="hidden"
                    />
                  </label>
                </div>

                {isUploading && (
                  <div className="p-3 bg-neutral-100 border border-black font-mono text-xs flex items-center gap-2">
                    <Loader2 size={14} className="animate-spin" />
                    Parsing Excel specification...
                  </div>
                )}

                {parsedCases.length > 0 && (
                  <div>
                    <label className="block text-[11px] font-mono font-bold uppercase text-neutral-600 mb-1.5">
                      Extracted Test Cases ({parsedCases.length}):
                    </label>
                    <div className="max-h-60 overflow-y-auto space-y-1.5">
                      {parsedCases.map((tc, idx) => {
                        const isSelected = selectedCaseIndex === idx;
                        return (
                          <button
                            key={tc.id || idx}
                            type="button"
                            onClick={() => {
                              setSelectedCaseIndex(idx);
                              setTcId(tc.id);
                              setTcTitle(tc.title);
                              setTcPreconditions(tc.preconditions);
                              setTcSteps(tc.steps);
                              setTcExpected(tc.expected_result);
                              setTcPriority(tc.priority);
                              setGeneratedSteps(null);
                            }}
                            className={`w-full text-left p-2 border text-xs font-mono transition-colors ${
                              isSelected
                                ? "border-black bg-black text-white"
                                : "border-neutral-300 bg-white hover:border-black text-neutral-800"
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-bold">{tc.id}</span>
                              <span className="text-[9px] uppercase">{tc.priority}</span>
                            </div>
                            <p className="text-[10px] truncate mt-0.5">{tc.title}</p>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Generate Action Button */}
            <div className="pt-2">
              <button
                type="button"
                onClick={handleGeneratePlan}
                disabled={isGenerating || !tcSteps.trim()}
                className="w-full py-3 bg-black text-white hover:bg-neutral-800 font-mono font-bold text-xs uppercase border-2 border-black shadow-[4px_4px_0px_0px_#000000] flex items-center justify-center gap-2 transition-transform active:translate-x-0.5 active:translate-y-0.5 disabled:opacity-50 cursor-pointer"
              >
                {isGenerating ? (
                  <>
                    <Loader2 size={14} className="animate-spin text-amber-400" />
                    GENERATING ACTION SEQUENCE...
                  </>
                ) : (
                  <>
                    <Zap size={14} className="text-amber-400" strokeWidth={2.5} />
                    RESOLVE ACTION PLAN (HERMES / JEV)
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Generated Action Sequence Plan Preview (7 cols) */}
          <div className="lg:col-span-7 p-4 flex flex-col justify-between bg-white overflow-y-auto">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b-2 border-black pb-2">
                <div className="flex items-center gap-2 font-mono font-black text-xs uppercase">
                  <Layers size={14} />
                  <span>Executable Step Sequence</span>
                  {generatedSteps && (
                    <span className="text-[10px] bg-emerald-100 text-emerald-900 border border-emerald-400 px-1.5 py-0.2">
                      {generatedSteps.length} STEPS
                    </span>
                  )}
                </div>

                {generatedSteps && (
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setShowJson(!showJson)}
                      className="text-[10px] font-mono font-bold uppercase border border-black px-2 py-0.5 hover:bg-neutral-100 flex items-center gap-1"
                    >
                      <Code2 size={11} />
                      {showJson ? "Table View" : "JSON"}
                    </button>
                    <button
                      type="button"
                      onClick={handleCopyJson}
                      className="text-[10px] font-mono font-bold uppercase border border-black px-2 py-0.5 hover:bg-neutral-100 flex items-center gap-1"
                    >
                      {copied ? <Check size={11} className="text-emerald-600" /> : <Copy size={11} />}
                      {copied ? "Copied" : "Copy"}
                    </button>
                  </div>
                )}
              </div>

              {/* Status / Notice when no plan generated yet */}
              {!generatedSteps && !isGenerating && !generationError && (
                <div className="border-2 border-dashed border-neutral-300 p-8 text-center font-mono space-y-2">
                  <Cpu size={32} className="mx-auto text-neutral-400" />
                  <p className="text-xs font-bold text-neutral-700">NO ACTION PLAN LOADED</p>
                  <p className="text-[11px] text-neutral-500 max-w-sm mx-auto">
                    Click <strong>RESOLVE ACTION PLAN</strong> on the left to synthesize high-speed
                    JSON-RPC Playwright commands with Jev System-1 verification assertions.
                  </p>
                </div>
              )}

              {/* Loading indicator */}
              {isGenerating && (
                <div className="border-2 border-black bg-neutral-50 p-8 text-center font-mono space-y-3">
                  <Loader2 size={32} className="mx-auto text-black animate-spin" />
                  <p className="text-xs font-bold text-neutral-800">
                    SYNTHESIZING ACTION PLAN VIA NOUS HERMES...
                  </p>
                  <p className="text-[11px] text-neutral-500">
                    Extracting selectors, typing values, and boundary assertions for target DOM.
                  </p>
                </div>
              )}

              {/* Generation Error */}
              {generationError && (
                <div className="border-2 border-red-600 bg-red-50 p-4 font-mono text-xs text-red-900 flex items-start gap-2">
                  <AlertCircle size={16} className="text-red-600 shrink-0 mt-0.5" />
                  <div>
                    <strong>Plan Generation Error:</strong> {generationError}
                  </div>
                </div>
              )}

              {/* Generated Steps View */}
              {generatedSteps && !isGenerating && (
                <div>
                  {showJson ? (
                    <pre className="bg-black text-green-400 p-3 font-mono text-[11px] max-h-96 overflow-auto border-2 border-black">
                      {JSON.stringify(generatedSteps, null, 2)}
                    </pre>
                  ) : (
                    <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                      {generatedSteps.map((s, idx) => {
                        const action = (s.action || "").toLowerCase();
                        let badgeColor = "bg-neutral-100 text-neutral-800 border-neutral-400";
                        if (action === "navigate") badgeColor = "bg-blue-100 text-blue-900 border-blue-400";
                        else if (action === "fill") badgeColor = "bg-emerald-100 text-emerald-900 border-emerald-400";
                        else if (action === "click") badgeColor = "bg-amber-100 text-amber-900 border-amber-400";
                        else if (action === "assert") badgeColor = "bg-purple-100 text-purple-900 border-purple-400";
                        else if (action === "hover") badgeColor = "bg-cyan-100 text-cyan-900 border-cyan-400";

                        return (
                          <div
                            key={idx}
                            className="border-2 border-black bg-white p-2.5 font-mono text-xs space-y-1.5 shadow-[2px_2px_0px_0px_#000000]"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="font-black text-neutral-400">#{s.index ?? idx + 1}</span>
                                <span
                                  className={`px-2 py-0.5 text-[10px] font-bold uppercase border ${badgeColor}`}
                                >
                                  {action}
                                </span>
                              </div>
                              <span className="text-[10px] text-neutral-500 truncate max-w-[200px]">
                                {s.target || "document root"}
                              </span>
                            </div>

                            {s.value && (
                              <div className="text-[11px] text-neutral-700 bg-neutral-50 p-1 border border-neutral-200">
                                <strong>Input Value:</strong>{" "}
                                <span className="font-bold text-black">{s.value}</span>
                              </div>
                            )}

                            {s.expect && (
                              <div className="text-[11px] text-neutral-600 flex items-start gap-1">
                                <CheckCircle2 size={12} className="text-emerald-600 shrink-0 mt-0.5" />
                                <span>
                                  <strong>Expected Verdict:</strong> {s.expect}
                                </span>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}

                  <div className="mt-4 p-2 bg-neutral-100 border border-black font-mono text-[10px] text-neutral-600 flex items-center justify-between">
                    <span>ASSERTION ENGINE: Jev System-1 Edge Runtime (&lt;50ms)</span>
                    <span className="text-black font-bold">ZERO CLOUD TOKENS ON LOCAL PASS</span>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Bottom Action Bar */}
            <div className="border-t-2 border-black pt-4 mt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={handleExportXlsx}
                  disabled={isExporting}
                  className="px-3 py-2 border-2 border-black font-mono font-bold text-xs uppercase hover:bg-neutral-100 flex items-center gap-1.5 w-full sm:w-auto justify-center"
                >
                  <Download size={13} />
                  {isExporting ? "Exporting..." : "Export as .XLSX"}
                </button>
              </div>

              <div className="flex items-center gap-2 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 border-2 border-black font-mono font-bold text-xs uppercase hover:bg-neutral-100 w-full sm:w-auto"
                >
                  Close
                </button>
                <button
                  type="button"
                  onClick={handleExecuteNow}
                  className="px-5 py-2 bg-black text-white hover:bg-neutral-800 font-mono font-bold text-xs uppercase border-2 border-black shadow-[3px_3px_0px_0px_#f59e0b] flex items-center justify-center gap-2 w-full sm:w-auto cursor-pointer"
                >
                  <Play size={13} className="text-amber-400 fill-amber-400" />
                  [ RUN THIS TEST NOW ]
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
