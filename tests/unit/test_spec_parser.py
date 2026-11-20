"""
momus404 — tests/unit/test_spec_parser.py
Unit tests for Excel test specification parsing and validation.
"""

import pytest
from app.core.exceptions import SpecParseError
from app.services.parser_service import parse_xlsx


def test_spec_parser_happy_path(sample_xlsx_bytes: bytes):
    cases = parse_xlsx(sample_xlsx_bytes, filename="spec.xlsx")
    assert len(cases) == 5
    assert cases[0].id == "TC-0001"
    assert "Login" in cases[0].title
    assert "auth" in cases[0].tags


def test_spec_parser_rejects_non_xlsx():
    with pytest.raises(SpecParseError, match="Unsupported file format"):
        parse_xlsx(b"plain text content", filename="spec.csv")


def test_spec_parser_rejects_oversize():
    oversize = b"0" * (11 * 1024 * 1024)
    with pytest.raises(SpecParseError, match="exceeds"):
        parse_xlsx(oversize, filename="huge.xlsx")
