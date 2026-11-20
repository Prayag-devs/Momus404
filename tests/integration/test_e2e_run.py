"""
momus404 — tests/integration/test_e2e_run.py
End-to-end integration test for the entire mock execution lifecycle.
"""

import time
from fastapi.testclient import TestClient


def test_e2e_mock_run_lifecycle(client: TestClient, sample_xlsx_bytes: bytes):
    # 1. Ingest
    ingest_resp = client.post(
        "/api/ingest",
        data={
            "target_url": "https://demo.playwright.dev/todomvc",
            "username": "qa_operator@momus.local",
            "password": "SuperSecretPassword99!",
        },
        files={"file": ("sample.xlsx", sample_xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert ingest_resp.status_code == 200
    data = ingest_resp.json()
    run_id = data["run_id"]
    assert data["test_case_count"] == 5

    # 2. Run
    run_resp = client.post("/api/run-agent", json={"run_id": run_id, "dry_run": True})
    assert run_resp.status_code == 200
    assert run_resp.json()["status"] == "started"

    # 3. Status Poll
    completed = False
    for _ in range(30):
        time.sleep(0.2)
        st_resp = client.get(f"/api/status/{run_id}")
        assert st_resp.status_code == 200
        st = st_resp.json()["status"]
        if st.get("status") in ("PASS", "FAIL", "COMPLETED", "FAILED"):
            completed = True
            break

    assert completed, "Run did not complete within the timeout window"

    # 4. Report Download
    report_resp = client.get(f"/api/report/{run_id}")
    assert report_resp.status_code == 200
    assert "MOMUS404 Test Report" in report_resp.text
