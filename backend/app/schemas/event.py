"""
momus404 — app.schemas.event
Real-time log and WebSocket streaming event models.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


def _current_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class LogEvent(BaseModel):
    ts: str = Field(default_factory=_current_utc_iso)
    source: str  # MCP | VAULT | LAYA-P1000 | HEAL | ENGINE | BRAIN | SYSTEM
    run_id: Optional[str] = None
    test_id: Optional[str] = None
    step: Optional[int] = None
    message: str
    verdict: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
