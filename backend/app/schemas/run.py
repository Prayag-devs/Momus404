"""
momus404 — app.schemas.run
Execution step, run request, and run status schemas.
"""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import Verdict


class PlannedStep(BaseModel):
    index: int
    action: str  # navigate | click | fill | assert | wait
    target: str
    value: str = ""
    expect: str = ""


class StepResult(BaseModel):
    step_index: int
    action: str
    target: str
    value: Optional[str] = None
    log: Optional[str] = None
    verdict: Verdict
    confidence: float = 0.0
    latency_ms: int = 0
    heal_count: int = 0
    error: Optional[str] = None
    screenshot_path: Optional[str] = None
    mock: bool = False


class TestCaseResult(BaseModel):
    test_case_id: str
    title: str
    verdict: Verdict
    steps: List[StepResult] = Field(default_factory=list)
    heal_count: int = 0
    duration_ms: int = 0
    notes: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    report_path: Optional[str] = None


class RunRequest(BaseModel):
    run_id: str
    dry_run: bool = False


class RunStatus(BaseModel):
    run_id: str
    status: Verdict = Verdict.IDLE
    progress: float = 0.0  # 0.0 to 1.0
    current_test: Optional[str] = None
    current_step: Optional[str] = None
    results: List[TestCaseResult] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    tokens_saved: int = 0
    is_paused: bool = False
    awaiting_input: bool = False
    input_prompt: Optional[str] = None
    input_type: Optional[str] = None
