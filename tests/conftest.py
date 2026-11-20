"""
momus404 — tests/conftest.py
Global fixtures for unit and integration testing.
"""

import io
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
_ROOT = Path(__file__).resolve().parent.parent
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app import app
from app.services.parser_service import generate_sample_xlsx


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture(scope="session")
def sample_xlsx_bytes() -> bytes:
    """Generates and returns valid sample Excel bytes."""
    buf = io.BytesIO()
    temp_path = _ROOT / "temp_fixture_spec.xlsx"
    generate_sample_xlsx(temp_path)
    content = temp_path.read_bytes()
    temp_path.unlink(missing_ok=True)
    return content
