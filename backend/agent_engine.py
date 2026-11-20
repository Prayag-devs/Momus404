"""
momus404 — backend/agent_engine.py (Backward Compatibility Facade)
Re-exports from app.services.orchestrator_service.
"""

from app.services.orchestrator_service import (
    OrchestratorAdapter,
    RunManager,
    get_run_manager,
    AGY_AVAILABLE,
)

run_manager = get_run_manager()

__all__ = ["OrchestratorAdapter", "RunManager", "run_manager", "AGY_AVAILABLE"]
