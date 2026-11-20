"""
momus404 — tests/unit/test_vault.py
Unit tests for Fernet credential storage, masking, and string redaction.
"""

from app.core.security import mask_email, redact
from app.services.vault_service import OpenDotsVault


def test_redact_email():
    text = "User admin@company.com attempted login"
    result = redact(text)
    assert "admin@company.com" not in result
    assert "***" in result


def test_redact_password_forms():
    text = 'POST /login with password="superSecretPassword123!"'
    result = redact(text)
    assert "superSecretPassword123!" not in result
    assert "***" in result


def test_mask_email():
    assert mask_email("johndoe@example.com") == "j***@example.com"
    assert mask_email("a@b.com") == "a***@b.com"


def test_vault_store_and_revoke():
    v = OpenDotsVault(mock_override=True)
    v.store("sess-001", "operator@example.com", "mypassword", "https://app.test")

    assert "sess-001" in v._store
    user, pwd = v.retrieve_plaintext("sess-001")
    assert user == "operator@example.com"
    assert pwd == "mypassword"

    v.revoke("sess-001")
    assert "sess-001" not in v._store
