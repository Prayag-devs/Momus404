"""
momus404 — tests/test_suite.py
Root test suite re-exporting unit and integration tests.
Run with: pytest tests/test_suite.py -v
"""

from tests.unit.test_spec_parser import (
    test_spec_parser_happy_path as test_spec_parser_sample_data,
    test_spec_parser_rejects_non_xlsx,
    test_spec_parser_rejects_oversize,
)
from tests.unit.test_vault import (
    test_redact_email,
    test_redact_password_forms as test_redact_password_form,
    test_mask_email,
    test_vault_store_and_revoke,
)
from tests.unit.test_laya_judge import (
    test_laya_mock_latency,
    test_laya_fail_on_error_keywords,
    test_laya_retry_on_spinner,
)
from tests.integration.test_e2e_run import (
    test_e2e_mock_run_lifecycle as test_e2e_mock_run,
)

__all__ = [
    "test_spec_parser_sample_data",
    "test_spec_parser_rejects_non_xlsx",
    "test_spec_parser_rejects_oversize",
    "test_redact_email",
    "test_redact_password_form",
    "test_mask_email",
    "test_vault_store_and_revoke",
    "test_laya_mock_latency",
    "test_laya_fail_on_error_keywords",
    "test_laya_retry_on_spinner",
    "test_e2e_mock_run",
]
