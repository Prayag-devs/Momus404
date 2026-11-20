"""
momus404 — app.schemas.common
Common enumerations and types.
"""

from enum import Enum


class Verdict(str, Enum):
    PASS_ = "PASS"
    FAIL = "FAIL"
    RETRY = "RETRY"
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    SKIPPED = "SKIPPED"


class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
