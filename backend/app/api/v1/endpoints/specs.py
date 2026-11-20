"""
momus404 — app.api.v1.endpoints.specs
Test specification upload and generation routes.
"""

import re
import uuid
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_app_settings, get_brain_dep
from app.core.config import Settings
from app.core.exceptions import SpecParseError
from app.schemas.spec import GenerateTestRequest, SpecUploadResponse, TestCase
from app.services.parser_service import parse_xlsx
from app.services.planner_service import AgentBrain

router = APIRouter()


def _safe_filename(name: str) -> str:
    return re.sub(r"[^\w\-.]", "_", Path(name).name)[:128]


@router.post("/upload-spec", response_model=SpecUploadResponse, summary="Upload .xlsx specification")
async def upload_test_spec(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_app_settings),
) -> SpecUploadResponse:
    """Accepts an Excel test spec, parses cases, and saves the file."""
    filename = _safe_filename(file.filename or "spec.xlsx")
    content = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_BYTES // 1_048_576} MB limit.")

    try:
        cases = parse_xlsx(content, filename=filename)
    except SpecParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    save_path = settings.SPECS_DIR / f"{uuid.uuid4().hex[:8]}_{filename}"
    save_path.write_bytes(content)

    return SpecUploadResponse(
        filename=filename,
        test_case_count=len(cases),
        test_cases=cases,
        spec_path=str(save_path),
    )


@router.post("/generate-test", summary="Generate test plan from case description")
async def generate_test_plan(
    payload: GenerateTestRequest,
    brain: AgentBrain = Depends(get_brain_dep),
) -> Dict[str, Any]:
    """Generates an action sequence plan from a test case definition."""
    tc = TestCase(
        id=payload.id or "TC-CUSTOM",
        title=payload.title or "Custom Test",
        preconditions=payload.preconditions or "",
        steps=payload.steps or "",
        expected_result=payload.expected_result or "",
    )
    steps = await brain.plan(tc)
    return {"steps": [s.model_dump() for s in steps]}
