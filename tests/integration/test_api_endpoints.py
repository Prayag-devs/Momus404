"""
momus404 — tests/integration/test_api_endpoints.py
Integration tests for FastAPI REST endpoints.
"""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "overall" in data
    assert "components" in data
    assert len(data["components"]) >= 5


def test_telemetry_endpoint(client: TestClient):
    response = client.get("/api/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "device" in data
    assert "gpu_util_pct" in data
    assert "vram_total_mb" in data


def test_upload_spec_endpoint(client: TestClient, sample_xlsx_bytes: bytes):
    response = client.post(
        "/api/upload-spec",
        files={"file": ("test_spec.xlsx", sample_xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["test_case_count"] == 5
    assert len(data["test_cases"]) == 5
