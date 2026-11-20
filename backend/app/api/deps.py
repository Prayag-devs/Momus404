"""
momus404 — app.api.deps
Dependency injection providers for FastAPI route handlers.
"""

from app.core.config import Settings, get_settings
from app.services.event_bus import EventBus, get_event_bus
from app.services.judge_service import LayaEdgeJudge, get_judge
from app.services.orchestrator_service import RunManager, get_run_manager
from app.services.planner_service import AgentBrain, get_brain
from app.services.vault_service import OpenDotsVault, get_vault


def get_app_settings() -> Settings:
    return get_settings()


def get_bus() -> EventBus:
    return get_event_bus()


def get_vault_dep() -> OpenDotsVault:
    return get_vault()


def get_judge_dep() -> LayaEdgeJudge:
    return get_judge()


def get_brain_dep() -> AgentBrain:
    return get_brain()


def get_run_manager_dep() -> RunManager:
    return get_run_manager()
