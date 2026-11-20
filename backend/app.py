"""
momus404 — backend/app.py
Production entry point exposing ASGI application `app` for Uvicorn,
with backward-compatible re-exports for existing modules and tests.
"""

import sys
import asyncio

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from app.main import create_app
from app.services.event_bus import get_event_bus
from app.services.judge_service import get_judge
from app.services.orchestrator_service import get_run_manager
from app.services.parser_service import parse_xlsx
from app.services.planner_service import get_brain
from app.services.vault_service import get_vault
from app.core.config import get_settings

# ASGI Application instance
app = create_app()

# Backward-compatibility facades
settings = get_settings()
bus = get_event_bus()
judge = get_judge()
vault = get_vault()
brain = get_brain()
run_manager = get_run_manager()

SPECS_DIR = settings.SPECS_DIR
REPORTS_DIR = settings.REPORTS_DIR
ARTIFACTS_DIR = settings.ARTIFACTS_DIR

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
