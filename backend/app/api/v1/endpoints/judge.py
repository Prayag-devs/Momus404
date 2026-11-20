"""
momus404 — app.api.v1.endpoints.judge
Edge decision evaluation endpoint.
"""

import asyncio
from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.api.deps import get_judge_dep
from app.services.judge_service import LayaEdgeJudge

router = APIRouter()


@router.post("/local-check", summary="Evaluate DOM snippet against expected condition")
async def evaluate_local_check(
    payload: Dict[str, Any],
    judge: LayaEdgeJudge = Depends(get_judge_dep),
) -> Dict[str, Any]:
    """Runs LayaEdgeJudge binary assertion on a DOM snippet."""
    dom_snippet = payload.get("dom_snippet", "")
    expected_condition = payload.get("expected_condition", "")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, judge.evaluate_step, dom_snippet, expected_condition)
    return result
