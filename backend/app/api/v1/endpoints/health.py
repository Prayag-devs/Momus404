"""
momus404 — app.api.v1.endpoints.health
Component and system health checks.
"""

from fastapi import APIRouter, Depends

from app.api.deps import (
    get_app_settings,
    get_brain_dep,
    get_judge_dep,
    get_vault_dep,
)
from app.core.config import Settings
from app.schemas.telemetry import ComponentHealth, HealthReport
from app.services.judge_service import CUDA_AVAILABLE, DEVICE_NAME, TORCH_AVAILABLE, LayaEdgeJudge
from app.services.planner_service import AgentBrain
from app.services.vault_service import OpenDotsVault

router = APIRouter()


@router.get("/health", response_model=HealthReport, summary="Component health status")
async def get_health_status(
    settings: Settings = Depends(get_app_settings),
    judge: LayaEdgeJudge = Depends(get_judge_dep),
    brain: AgentBrain = Depends(get_brain_dep),
    vault: OpenDotsVault = Depends(get_vault_dep),
) -> HealthReport:
    """Report mock vs real status for all subsystem components."""
    components = [
        ComponentHealth(
            name="Jev Decision Engine",
            status="real" if judge._api_key else "offline-heuristic",
            detail=f"{DEVICE_NAME} (Cloud API Connected)" if judge._api_key else "System-1 Local Heuristic (Set JEV_API_KEY in .env to connect Cloud)",
        ),
        ComponentHealth(
            name="Nous Hermes",
            status="real" if not brain.health()["mock"] else "mock",
            detail=brain.health()["hermes_model"],
        ),
        ComponentHealth(
            name="OpenAI",
            status="real" if brain.health()["openai_key_set"] else "mock",
            detail=brain.health()["openai_model"],
        ),
        ComponentHealth(
            name="OpenDots Vault",
            status="real" if not vault.health()["mock"] else "mock",
            detail=f"Sessions: {vault.health()['active_sessions']}",
        ),
        ComponentHealth(
            name="Playwright MCP",
            status="mock" if settings.MOCK_MCP else "real",
            detail="mock simulation" if settings.MOCK_MCP else "STDIO transport",
        ),
        ComponentHealth(
            name="PyTorch",
            status="real" if TORCH_AVAILABLE else "unavailable",
            detail="Installed" if TORCH_AVAILABLE else "Not installed",
        ),
    ]

    all_real = all(c.status == "real" for c in components)
    all_unavailable = all(c.status in ("mock", "unavailable") for c in components)
    overall = "real" if all_real else ("mock" if all_unavailable else "hybrid")

    return HealthReport(overall=overall, components=components)
