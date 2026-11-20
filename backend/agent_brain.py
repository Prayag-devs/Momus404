"""
momus404 — backend/agent_brain.py (Backward Compatibility Facade)
Re-exports from app.services.planner_service.
"""

from app.services.planner_service import (
    AgentBrain,
    get_brain,
    get_tokens_saved,
    record_tokens_saved,
    reset_tokens_saved,
)

brain = get_brain()


def tokens_saved() -> int:
    return get_tokens_saved()


def reset_token_counter() -> None:
    reset_tokens_saved()


__all__ = [
    "AgentBrain",
    "brain",
    "tokens_saved",
    "get_tokens_saved",
    "record_tokens_saved",
    "reset_tokens_saved",
    "reset_token_counter",
]
