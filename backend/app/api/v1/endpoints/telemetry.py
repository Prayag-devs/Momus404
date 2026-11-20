"""
momus404 — app.api.v1.endpoints.telemetry
Hardware and edge decision telemetry.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_judge_dep
from app.schemas.telemetry import Telemetry
from app.services.judge_service import LayaEdgeJudge
from app.services.planner_service import get_tokens_saved

router = APIRouter()


@router.get("/telemetry", response_model=Telemetry, summary="Hardware and inference telemetry")
async def get_telemetry_metrics(
    judge: LayaEdgeJudge = Depends(get_judge_dep),
) -> Telemetry:
    """Returns GPU metrics, inference latency, and tokens saved by Laya."""
    t = judge.telemetry()
    return Telemetry(
        device=t["device"],
        gpu_util_pct=t["gpu_util_pct"],
        vram_used_mb=t["vram_used_mb"],
        vram_total_mb=t["vram_total_mb"],
        avg_latency_ms=t["avg_latency_ms"],
        last_latency_ms=t["last_latency_ms"],
        tokens_saved=get_tokens_saved(),
        mock=t["mock"],
    )
