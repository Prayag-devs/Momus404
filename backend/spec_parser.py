"""
momus404 — backend/spec_parser.py (Backward Compatibility Facade)
Re-exports from app.services.parser_service and app.core.exceptions.
"""

import sys
from app.core.exceptions import SpecParseError
from app.services.parser_service import parse_xlsx, generate_sample_xlsx, SAMPLE_DATA, EXPECTED_COLUMNS

__all__ = ["parse_xlsx", "generate_sample_xlsx", "SpecParseError", "SAMPLE_DATA", "EXPECTED_COLUMNS"]

if __name__ == "__main__":
    if "--sample" in sys.argv:
        target = "sample_spec.xlsx"
        idx = sys.argv.index("--sample")
        if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("-"):
            target = sys.argv[idx + 1]
        out = generate_sample_xlsx(target)
        print(f"Sample spec written to: {out.resolve()}")
