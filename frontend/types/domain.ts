/**
 * momus404 — types/domain.ts
 * Core test automation and execution domain types.
 */

export type Verdict = "PASS" | "FAIL" | "RETRY" | "RUNNING" | "IDLE" | "SKIPPED";

export interface TestCase {
  id: string;
  title: string;
  preconditions: string;
  steps: string;
  expected_result: string;
  priority: string;
  tags: string[];
}

export interface PlannedStep {
  index: number;
  action: string;
  target: string;
  value: string;
  expect: string;
}

export interface StepResult {
  step_index: number;
  action: string;
  target: string;
  value?: string;
  log?: string;
  verdict: Verdict;
  confidence: number;
  latency_ms: number;
  heal_count: number;
  error?: string;
  screenshot_path?: string;
  mock: boolean;
}

export interface TestCaseResult {
  test_case_id: string;
  title: string;
  verdict: Verdict;
  steps: StepResult[];
  heal_count: number;
  duration_ms: number;
  notes?: string;
  logs?: string[];
  report_path?: string;
}

export interface RunStatus {
  run_id: string;
  status: Verdict;
  progress: number;
  current_test?: string;
  current_step?: string;
  results: TestCaseResult[];
  started_at?: string;
  finished_at?: string;
  total_tests: number;
  passed: number;
  failed: number;
  tokens_saved: number;
  is_paused?: boolean;
  awaiting_input?: boolean;
  input_prompt?: string;
  input_type?: string;
}

export interface IngestResponse {
  run_id: string;
  target_url: string;
  test_case_count: number;
  test_cases: TestCase[];
  plan_preview: PlannedStep[];
}
