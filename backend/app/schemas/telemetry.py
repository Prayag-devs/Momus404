"""
momus404 — app.schemas.telemetry
Hardware, judge, and component health monitoring schemas.
"""

from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, Field
from app.schemas.common import Verdict


def _current_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class LayaVerdict(BaseModel):
    verdict: Verdict
    confidence: float
    latency_ms: int
    vram_used_mb: float
    device: str
    mock: bool = True


class Telemetry(BaseModel):
    device: str
    gpu_util_pct: float = 0.0
    vram_used_mb: float = 0.0
    vram_total_mb: float = 4096.0
    avg_latency_ms: float = 0.0
    last_latency_ms: float = 0.0
    tokens_saved: int = 0
    mock: bool = True


class ComponentHealth(BaseModel):
    name: str
    status: str  # "real" | "mock" | "unavailable"
    detail: str = ""


class HealthReport(BaseModel):
    overall: str  # "real" | "mock" | "hybrid"
    components: List[ComponentHealth]
    timestamp: str = Field(default_factory=_current_utc_iso)
