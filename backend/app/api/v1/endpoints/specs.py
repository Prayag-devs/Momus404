"""
momus404 — app.api.v1.endpoints.specs
Test specification upload and generation routes.
"""

import io
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

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
        priority=payload.priority or "Medium",
        tags=payload.tags or [],
    )
    steps = await brain.plan(
        tc,
        target_url=payload.target_url or "",
        username=payload.username or "",
        password=payload.password or "",
    )
    return {
        "test_case": tc.model_dump(),
        "steps": [s.model_dump() for s in steps],
    }


@router.post("/export-spec", summary="Export test cases to formatted .xlsx specification")
async def export_spec_xlsx(test_cases: List[TestCase]) -> Response:
    """Generates and returns an .xlsx spreadsheet for the given test cases."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    headers = ["ID", "Title", "Preconditions", "Steps", "Expected Result", "Priority", "Tags"]
    header_fill = PatternFill("solid", fgColor="111827")
    header_font = Font(name="Calibri", bold=True, color="FFFFFF")

    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    row_fill_even = PatternFill("solid", fgColor="F9FAFB")
    for r_idx, tc in enumerate(test_cases, start=2):
        row_vals = [
            tc.id,
            tc.title,
            tc.preconditions,
            tc.steps,
            tc.expected_result,
            tc.priority,
            ", ".join(tc.tags) if isinstance(tc.tags, list) else str(tc.tags),
        ]
        fill = row_fill_even if r_idx % 2 == 0 else None
        for c_idx, val in enumerate(row_vals, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if fill:
                cell.fill = fill

    # Column widths
    col_widths = [15, 30, 25, 45, 35, 12, 18]
    for i, w in enumerate(col_widths, start=1):
        col_letter = ws.cell(row=1, column=i).column_letter
        ws.column_dimensions[col_letter].width = w

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"momus404_spec_{uuid.uuid4().hex[:6]}.xlsx"
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

