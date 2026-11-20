"""
momus404 — tests/unit/test_laya_judge.py
Unit tests for Laya decision engine heuristics and latency limits.
"""

from app.services.judge_service import LayaEdgeJudge


def test_laya_mock_latency():
    judge = LayaEdgeJudge(mock_override=True)
    res = judge.evaluate_step("<div>Sign In</div>", "Sign In")
    assert res["verdict"] in ("PASS", "FAIL", "RETRY")
    assert res["latency_ms"] < 100
    assert res["mock"] is True


def test_laya_fail_on_error_keywords():
    judge = LayaEdgeJudge(mock_override=True)
    res = judge.evaluate_step("<div>500 Internal Server Error: Database timeout</div>", "Dashboard loaded")
    assert res["verdict"] == "FAIL"


def test_laya_retry_on_spinner():
    judge = LayaEdgeJudge(mock_override=True)
    res = judge.evaluate_step('<div class="loading-spinner">Connecting to host...</div>', "Dashboard loaded")
    assert res["verdict"] == "RETRY"
