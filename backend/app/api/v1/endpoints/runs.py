"""
momus404 — app.api.v1.endpoints.runs
Execution orchestration, run ingestion, cancellation, and report generation routes.
"""

import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse

from app.api.deps import (
    get_app_settings,
    get_brain_dep,
    get_bus,
    get_run_manager_dep,
    get_vault_dep,
)
from app.core.config import Settings
from app.core.exceptions import SpecParseError
from app.core.logging import get_logger
from app.core.security import redact
from app.schemas.event import LogEvent
from app.schemas.run import RunRequest
from app.schemas.spec import TestCase
from app.services.event_bus import EventBus
from app.services.orchestrator_service import RunManager
from app.services.parser_service import parse_xlsx
from app.services.planner_service import AgentBrain, reset_tokens_saved
from app.services.vault_service import OpenDotsVault

logger = get_logger("api.runs")
router = APIRouter()

# In-memory storage for active run inputs
_run_specs: Dict[str, List[TestCase]] = {}
_run_targets: Dict[str, str] = {}
_run_sessions: Dict[str, str] = {}


def _safe_filename(name: str) -> str:
    return re.sub(r"[^\w\-.]", "_", Path(name).name)[:128]


@router.post("/ingest", summary="Ingest target URL, Excel spec, and credentials")
async def ingest_test_run(
    target_url: str = Form(...),
    username: str = Form(""),
    password: str = Form(""),
    file: Optional[UploadFile] = File(None),
    settings: Settings = Depends(get_app_settings),
    vault: OpenDotsVault = Depends(get_vault_dep),
    brain: AgentBrain = Depends(get_brain_dep),
    bus: EventBus = Depends(get_bus),
) -> Dict[str, Any]:
    """Ingest URL + .xlsx spec + credentials. Credentials stored in vault only."""
    run_id = uuid.uuid4().hex[:8]
    session_id = f"session_{run_id}"

    clean_url = (target_url or "").strip()
    if not clean_url:
        clean_url = "http://localhost:3000/login"
    elif not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = f"https://{clean_url}"
    target_url = clean_url

    vault.store(session_id, username or "anonymous", password or "", target_domain=target_url)
    _run_sessions[run_id] = session_id
    _run_targets[run_id] = target_url

    test_cases: List[TestCase] = []
    if file:
        filename = _safe_filename(file.filename or "spec.xlsx")
        data = await file.read(settings.MAX_UPLOAD_BYTES + 1)
        if len(data) > settings.MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_BYTES // 1_048_576} MB limit.")
        try:
            test_cases = parse_xlsx(data, filename=filename)
        except SpecParseError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        save_path = settings.SPECS_DIR / f"{run_id}_{filename}"
        save_path.write_bytes(data)

    _run_specs[run_id] = test_cases

    plan_preview: List[Dict[str, Any]] = []
    if test_cases:
        steps = await brain.plan(test_cases[0])
        plan_preview = [s.model_dump() for s in steps]

    await bus.publish(LogEvent(
        source="SYSTEM",
        run_id=run_id,
        message=f"Ingested {len(test_cases)} test case(s) for {redact(target_url)}",
    ))

    return {
        "run_id": run_id,
        "target_url": target_url,
        "test_case_count": len(test_cases),
        "test_cases": [tc.model_dump() for tc in test_cases],
        "plan_preview": plan_preview,
    }


@router.post("/run-agent", summary="Execute autonomous test run")
@router.post("/run-orchestration", summary="Alias for run-agent")
async def trigger_run(
    req: RunRequest,
    background_tasks: BackgroundTasks,
    run_manager: RunManager = Depends(get_run_manager_dep),
    settings: Settings = Depends(get_app_settings),
    vault: OpenDotsVault = Depends(get_vault_dep),
) -> Dict[str, Any]:
    """Triggers the async test run execution pipeline."""
    run_id = req.run_id
    test_cases = _run_specs.get(run_id, [])
    target_url = _run_targets.get(run_id, "http://localhost:3000/login")
    clean_url = (target_url or "").strip()
    if not clean_url:
        clean_url = "http://localhost:3000/login"
    elif not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = f"https://{clean_url}"
    target_url = clean_url
    session_id = _run_sessions.get(run_id, f"session_{run_id}")

    if not test_cases:
        for p in settings.SPECS_DIR.glob(f"{run_id}_*"):
            if p.suffix.lower() in (".xlsx", ".xlsm", ".xltx"):
                try:
                    test_cases = parse_xlsx(p.read_bytes(), filename=p.name)
                    _run_specs[run_id] = test_cases
                    break
                except Exception:
                    pass

    if not test_cases:
        test_cases = [
            TestCase(
                id="TC-QUICK",
                title="Quick Smoke Test",
                preconditions="",
                steps="1. Navigate to /\n2. Assert page loaded",
                expected_result="Page loaded successfully",
                priority="High",
            )
        ]
        _run_specs[run_id] = test_cases

    run_manager.create_run(run_id)

    async def _run_bg():
        try:
            reset_tokens_saved()
            await run_manager.execute_run(run_id, test_cases, target_url, session_id, req.dry_run)
        except Exception as exc:
            logger.exception(f"[API] Run {run_id} execution failed: {exc}")
            run_status = run_manager._runs.get(run_id)
            if run_status:
                run_status.status = Verdict.FAIL
                run_status.finished_at = datetime.now(timezone.utc)
        finally:
            vault.revoke(session_id)

    background_tasks.add_task(_run_bg)
    return {"run_id": run_id, "status": "started", "test_count": len(test_cases)}


@router.post("/pause/{run_id}", summary="Pause an in-progress run")
async def pause_test_run(
    run_id: str,
    run_manager: RunManager = Depends(get_run_manager_dep),
) -> Dict[str, Any]:
    paused = run_manager.pause_run(run_id)
    return {"run_id": run_id, "paused": paused}


@router.post("/resume/{run_id}", summary="Resume a paused run")
async def resume_test_run(
    run_id: str,
    run_manager: RunManager = Depends(get_run_manager_dep),
) -> Dict[str, Any]:
    resumed = run_manager.resume_run(run_id)
    return {"run_id": run_id, "resumed": resumed}


@router.post("/stop/{run_id}", summary="Stop an in-progress run")
async def stop_test_run(
    run_id: str,
    run_manager: RunManager = Depends(get_run_manager_dep),
) -> Dict[str, Any]:
    stopped = await run_manager.stop_run(run_id)
    return {"run_id": run_id, "stopped": stopped}


@router.post("/cancel/{run_id}", summary="Cancel an in-progress run (alias for stop)")
async def cancel_test_run(
    run_id: str,
    run_manager: RunManager = Depends(get_run_manager_dep),
) -> Dict[str, Any]:
    cancelled = await run_manager.cancel_run(run_id)
    return {"run_id": run_id, "cancelled": cancelled}


from pydantic import BaseModel
class ProvideInputRequest(BaseModel):
    input: str

@router.post("/provide-input/{run_id}", summary="Provide 2FA, OTP, or store selection input to a paused run")
async def provide_input(
    run_id: str,
    req: ProvideInputRequest,
    run_manager: RunManager = Depends(get_run_manager_dep),
) -> Dict[str, Any]:
    accepted = run_manager.provide_user_input(run_id, req.input)
    return {"run_id": run_id, "accepted": accepted}


@router.get("/status/{run_id}", summary="Get run status and logs")
async def get_run_status(
    run_id: str,
    limit: int = 50,
    run_manager: RunManager = Depends(get_run_manager_dep),
    bus: EventBus = Depends(get_bus),
) -> Dict[str, Any]:
    status = run_manager.get_status(run_id)
    recent_logs = bus.get_recent(run_id=run_id, limit=limit)
    return {
        "status": status.model_dump() if status else {"run_id": run_id, "status": "NOT_FOUND"},
        "recent_logs": [e.model_dump() for e in recent_logs],
    }


@router.get("/report/{run_id}", summary="Download test report")
@router.post("/report/{run_id}", summary="Download test report via POST")
async def download_run_report(
    run_id: str,
    fmt: str = "md",
    format: Optional[str] = None,
    settings: Settings = Depends(get_app_settings),
) -> FileResponse:
    target_format = (format or fmt).lower()
    if target_format in ("xlsx", "excel"):
        xlsx_path = settings.REPORTS_DIR / f"{run_id}_report.xlsx"
        if not xlsx_path.exists():
            from app.services.orchestrator_service import get_run_manager
            from app.services.parser_service import export_run_to_xlsx
            status = get_run_manager().get_status(run_id)
            if status and status.results:
                orig_spec = None
                for p in settings.SPECS_DIR.glob(f"{run_id}_*"):
                    if p.suffix.lower() in (".xlsx", ".xlsm", ".xltx"):
                        orig_spec = p
                        break
                export_run_to_xlsx(
                    run_id=run_id,
                    results=status.results,
                    original_file_path=orig_spec,
                    output_path=xlsx_path,
                )
        if xlsx_path.exists():
            return FileResponse(
                str(xlsx_path),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=f"momus404_{run_id}_report.xlsx",
            )
        raise HTTPException(status_code=404, detail=f"Excel report for run {run_id} not found.")

    if target_format == "json":
        json_path = settings.REPORTS_DIR / f"{run_id}_report.json"
        if json_path.exists():
            return FileResponse(
                str(json_path),
                media_type="application/json",
                filename=f"momus404_{run_id}_report.json",
            )

    report_path = settings.REPORTS_DIR / f"{run_id}_report.md"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail=f"Report for run {run_id} not found.")

    return FileResponse(
        str(report_path),
        media_type="text/markdown",
        filename=f"momus404_{run_id}_report.md",
    )
