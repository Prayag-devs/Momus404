"""
momus404 — app.services.parser_service
Universal Multi-Strategy Excel (.xlsx) Test Specification Parser & Exporter.
Dynamically parses any arbitrary QA test specification spreadsheet format without schema errors.
"""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

from app.core.config import get_settings
from app.core.exceptions import SpecParseError
from app.schemas.spec import TestCase

EXPECTED_COLUMNS = ["ID", "Title", "Preconditions", "Steps", "Expected Result", "Priority", "Tags"]

# QA Column Synonym Mapping across industry standards (Jira, TestRail, Zephyr, Excel specs)
SYNONYM_MAP = {
    "id": [
        "s. no.", "s.no", "s no", "sr no", "sr. no.", "sl no", "sl. no.",
        "id", "tc id", "test id", "case id", "tc_id", "no.", "no", "#",
        "index", "key", "testcase id", "test case id", "test number", "test no",
        "serial no", "sn",
    ],
    "title": [
        "test parameter", "parameter", "test name", "test title", "title",
        "scenario", "test scenario", "scenario name", "summary", "test summary",
        "description", "test description", "objective", "test case",
        "test case name", "feature", "feature name", "name", "topic", "case",
        "functionality", "user story", "requirement",
    ],
    "steps": [
        "test", "test steps", "steps", "steps to reproduce", "method", "action",
        "actions", "procedure", "execution steps", "reproduction steps",
        "instructions", "details", "how to test", "step", "process",
        "test method", "method/steps", "test procedure", "action steps", "input steps",
    ],
    "expected_result": [
        "expected result", "expected results", "expected", "expected outcome",
        "pass criteria", "acceptance criteria", "assertion", "assertions",
        "outcome", "expected behavior", "expected response", "validation",
        "criteria", "success criteria", "then",
    ],
    "preconditions": [
        "test condition/ environment", "test condition", "condition",
        "conditions", "environment", "preconditions", "pre-conditions",
        "prerequisites", "setup", "initial state", "context", "system state",
        "given", "pre-requisite",
    ],
    "priority": [
        "priority", "severity", "importance", "criticality", "level", "prio", "weight",
    ],
    "tags": [
        "test object", "object", "module", "component", "category", "tag",
        "tags", "labels", "area", "feature area", "subsystem", "scope", "domain", "epic",
    ],
}

SAMPLE_DATA = [
    {
        "ID": "TC-0001",
        "Title": "User Login with Valid Credentials",
        "Preconditions": "User account exists and is active.",
        "Steps": "1. Navigate to /login\n2. Fill in username\n3. Fill in password\n4. Click 'Sign In'\n5. Assert dashboard is visible",
        "Expected Result": "User is redirected to /dashboard and avatar is displayed.",
        "Priority": "High",
        "Tags": "auth, smoke, critical",
    },
    {
        "ID": "TC-0002",
        "Title": "Login Fails with Wrong Password",
        "Preconditions": "User account exists.",
        "Steps": "1. Navigate to /login\n2. Fill in username\n3. Fill in wrong password\n4. Click 'Sign In'",
        "Expected Result": "Error message 'Invalid credentials' is displayed.",
        "Priority": "High",
        "Tags": "auth, negative",
    },
    {
        "ID": "TC-0003",
        "Title": "Dashboard Loads All Widgets",
        "Preconditions": "User is logged in.",
        "Steps": "1. Navigate to /dashboard\n2. Observe widgets",
        "Expected Result": "All dashboard widgets load successfully.",
        "Priority": "Medium",
        "Tags": "dashboard",
    },
    {
        "ID": "TC-0004",
        "Title": "Create New Item via Form",
        "Preconditions": "User is logged in with Editor role.",
        "Steps": "1. Click '+ New Item'\n2. Fill in Name = 'Automated Test Item'\n3. Click 'Save'",
        "Expected Result": "Item appears in the list with correct name.",
        "Priority": "Medium",
        "Tags": "crud",
    },
    {
        "ID": "TC-0005",
        "Title": "Logout Clears Session",
        "Preconditions": "User is logged in.",
        "Steps": "1. Click user avatar\n2. Click 'Logout'",
        "Expected Result": "User is redirected to /login. Session cookie cleared.",
        "Priority": "Low",
        "Tags": "auth, smoke",
    },
]


def clean_col_name(s: Any) -> str:
    cleaned = re.sub(r"[^a-z0-9 ]", " ", str(s).lower()).strip()
    return re.sub(r"\s+", " ", cleaned)


def _normalize_col(col: str) -> str:
    cleaned = clean_col_name(col)
    for expected in EXPECTED_COLUMNS:
        if cleaned == clean_col_name(expected):
            return expected
    for field, synonyms in SYNONYM_MAP.items():
        for syn in synonyms:
            if cleaned == clean_col_name(syn):
                if field == "id":
                    return "ID"
                if field == "title":
                    return "Title"
                if field == "steps":
                    return "Steps"
                if field == "expected_result":
                    return "Expected Result"
                if field == "preconditions":
                    return "Preconditions"
                if field == "priority":
                    return "Priority"
                if field == "tags":
                    return "Tags"
    return str(col).strip()


def find_best_sheet(xl: pd.ExcelFile) -> str:
    """Finds the most relevant sheet containing test specifications."""
    sheet_names = xl.sheet_names
    if not sheet_names:
        raise SpecParseError("Excel file contains no sheets.")

    # 1. Look for typical test sheet names
    for s in sheet_names:
        s_lower = s.lower()
        if any(kw in s_lower for kw in ("test", "case", "spec", "scenario", "suite", "tc", "qa", "run")):
            return s

    # 2. Pick sheet with the most non-empty rows
    best_sheet = sheet_names[0]
    best_count = -1
    for s in sheet_names:
        try:
            preview = xl.parse(s, nrows=20, header=None)
            valid_cells = preview.dropna(how="all").size
            if valid_cells > best_count:
                best_count = valid_cells
                best_sheet = s
        except Exception:
            continue

    return best_sheet


def detect_header_row(df_raw: pd.DataFrame) -> int:
    """Detects the index of the header row across the top 15 rows."""
    qa_kw = {
        "test", "title", "name", "scenario", "step", "steps", "action", "actions",
        "method", "expected", "assertion", "result", "condition", "precondition",
        "environment", "setup", "id", "s. no", "sr no", "sl no", "no.", "object",
        "module", "priority", "severity", "tag", "tags", "parameter", "summary",
        "description", "outcome", "requirement",
    }
    best_score = -1
    header_idx = 0
    max_inspect = min(15, len(df_raw))

    for r in range(max_inspect):
        row = df_raw.iloc[r]
        row_vals = [str(v).strip().lower() for v in row if pd.notna(v)]
        if not row_vals:
            continue

        match_count = 0
        for val in row_vals:
            if len(val) > 75:
                continue
            cleaned = clean_col_name(val)
            if any(kw in cleaned for kw in qa_kw):
                match_count += 1

        if match_count > best_score:
            best_score = match_count
            header_idx = r

    return header_idx if best_score > 0 else 0


def map_columns(columns: List[Any], df: pd.DataFrame) -> Dict[str, Any]:
    """Dynamically maps any column schema to standard QA fields with 100% fallback tolerance."""
    mapping: Dict[str, Any] = {}
    assigned: set = set()
    cleaned_cols = [clean_col_name(c) for c in columns]

    # Tier 1: Exact matches against synonym dictionary
    for field, synonyms in SYNONYM_MAP.items():
        for syn in synonyms:
            clean_syn = clean_col_name(syn)
            for idx, c in enumerate(cleaned_cols):
                if idx not in assigned and c == clean_syn:
                    mapping[field] = columns[idx]
                    assigned.add(idx)
                    break
            if field in mapping:
                break

    # Tier 2: Substring matches
    for field, synonyms in SYNONYM_MAP.items():
        if field in mapping:
            continue
        for syn in synonyms:
            clean_syn = clean_col_name(syn)
            if len(clean_syn) < 3:
                continue
            for idx, c in enumerate(cleaned_cols):
                if idx not in assigned and (clean_syn in c or c in clean_syn):
                    mapping[field] = columns[idx]
                    assigned.add(idx)
                    break
            if field in mapping:
                break

    # Tier 3: Universal Heuristic Fallbacks (never fail)
    if "title" not in mapping:
        for idx, col in enumerate(columns):
            if idx not in assigned and not str(col).startswith("Unnamed:"):
                mapping["title"] = col
                assigned.add(idx)
                break
        if "title" not in mapping and columns:
            mapping["title"] = columns[0]

    if "steps" not in mapping:
        best_col = None
        max_avg_len = -1
        for idx, col in enumerate(columns):
            if idx not in assigned:
                try:
                    avg_len = df[col].astype(str).str.len().mean()
                    if avg_len > max_avg_len:
                        max_avg_len = avg_len
                        best_col = col
                except Exception:
                    pass
        if best_col is not None:
            mapping["steps"] = best_col
            assigned.add(columns.index(best_col))
        elif "title" in mapping:
            mapping["steps"] = mapping["title"]
        elif columns:
            mapping["steps"] = columns[0]

    return mapping


def parse_xlsx(file_content: bytes, filename: str = "spec.xlsx") -> List[TestCase]:
    """Universal Excel parser supporting arbitrary sheet layouts, subheaders, and column headers."""
    settings = get_settings()
    if len(file_content) > settings.MAX_UPLOAD_BYTES:
        raise SpecParseError(f"File size {len(file_content)} exceeds {settings.MAX_UPLOAD_BYTES // 1_048_576} MB limit.")

    if not filename.lower().endswith((".xlsx", ".xlsm", ".xltx", ".xls")):
        raise SpecParseError(f"Unsupported file format '{filename}'. Only Excel (.xlsx, .xlsm) files are supported.")

    try:
        xl = pd.ExcelFile(io.BytesIO(file_content), engine="openpyxl")
    except Exception as exc:
        raise SpecParseError(f"Could not read Excel workbook: {exc}")

    sheet_name = find_best_sheet(xl)

    try:
        raw_df = xl.parse(sheet_name, header=None)
    except Exception as exc:
        raise SpecParseError(f"Could not parse sheet '{sheet_name}': {exc}")

    if raw_df.empty:
        raise SpecParseError(f"Excel sheet '{sheet_name}' is empty.")

    header_row_idx = detect_header_row(raw_df)

    try:
        df = xl.parse(sheet_name, skiprows=header_row_idx)
    except Exception as exc:
        raise SpecParseError(f"Failed reading sheet data at row {header_row_idx}: {exc}")

    df = df.dropna(how="all", axis=1)
    if df.empty:
        raise SpecParseError("No data rows found in Excel sheet.")

    col_map = map_columns(list(df.columns), df)

    t_col = col_map.get("title")
    s_col = col_map.get("steps")
    id_col = col_map.get("id")
    exp_col = col_map.get("expected_result")
    pre_col = col_map.get("preconditions")
    tag_col = col_map.get("tags")
    prio_col = col_map.get("priority")

    cases: List[TestCase] = []

    for _, row in df.iterrows():
        t_val = str(row.get(t_col, "")).strip() if t_col and pd.notna(row.get(t_col)) else ""
        s_val = str(row.get(s_col, "")).strip() if s_col and pd.notna(row.get(s_col)) else ""
        id_val = str(row.get(id_col, "")).strip() if id_col and pd.notna(row.get(id_col)) else ""

        # Skip subheader/legend row indicator, e.g. '(Method/Steps)'
        if (not t_val or t_val.lower() == "nan") and s_val.startswith("(") and s_val.endswith(")"):
            continue

        # Handle multi-row steps (continuation rows without title/ID)
        if (not t_val or t_val.lower() == "nan") and s_val and s_val.lower() != "nan" and cases:
            cases[-1].steps += "\n" + s_val
            exp_extra = str(row.get(exp_col, "")).strip() if exp_col and pd.notna(row.get(exp_col)) else ""
            if exp_extra and exp_extra.lower() != "nan" and exp_extra not in cases[-1].expected_result:
                cases[-1].expected_result += " " + exp_extra
            continue

        # Skip rows where both title and steps are missing/NaN
        if (not t_val or t_val.lower() == "nan") and (not s_val or s_val.lower() == "nan"):
            continue

        # Fallback if title is missing but steps exists
        if not t_val or t_val.lower() == "nan":
            t_val = s_val.split("\n")[0][:80]

        # Fallback if steps is missing but title exists
        if not s_val or s_val.lower() == "nan":
            s_val = t_val

        # Normalize ID
        tc_id = ""
        if id_val and id_val.lower() != "nan":
            try:
                num = float(id_val)
                tc_id = f"TC-{int(num):04d}"
            except Exception:
                tc_id = id_val
        if not tc_id:
            tc_id = f"TC-{len(cases) + 1:04d}"

        # Normalize tags
        tags: List[str] = []
        if tag_col and pd.notna(row.get(tag_col)):
            raw_tag = str(row.get(tag_col, "")).strip()
            if raw_tag and raw_tag.lower() != "nan":
                tags = [t.strip() for t in raw_tag.split(",") if t.strip()]

        # Normalize priority
        raw_prio = str(row.get(prio_col, "Medium")).strip() if prio_col and pd.notna(row.get(prio_col)) else "Medium"
        if raw_prio.lower() in ("high", "critical", "blocker"):
            priority = "High"
        elif raw_prio.lower() in ("low", "minor", "trivial"):
            priority = "Low"
        else:
            priority = "Medium"

        # Preconditions & Expected Result
        preconditions = str(row.get(pre_col, "")).strip() if pre_col and pd.notna(row.get(pre_col)) else ""
        if preconditions.lower() == "nan":
            preconditions = ""

        expected_result = str(row.get(exp_col, "")).strip() if exp_col and pd.notna(row.get(exp_col)) else ""
        if not expected_result or expected_result.lower() == "nan":
            expected_result = "System state satisfies expected criteria."

        cases.append(TestCase(
            id=tc_id,
            title=t_val,
            preconditions=preconditions,
            steps=s_val,
            expected_result=expected_result,
            priority=priority,
            tags=tags,
        ))

    if not cases:
        raise SpecParseError("No valid test cases could be extracted from the file.")

    return cases


def generate_sample_xlsx(output_path: Union[Path, str] = "sample_spec.xlsx") -> Path:
    output_path = Path(output_path)
    wb = Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    headers = EXPECTED_COLUMNS
    header_font = Font(name="Calibri", bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="111111")
    header_align = Alignment(horizontal="center", vertical="center")

    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align

    for row_idx, tc in enumerate(SAMPLE_DATA, start=2):
        for col_idx, key in enumerate(headers, start=1):
            ws.cell(row=row_idx, column=col_idx, value=tc[key])

    col_widths = [12, 38, 38, 52, 45, 12, 20]
    for col, width in enumerate(col_widths, start=1):
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = width

    wb.save(output_path)
    return output_path


def export_run_to_xlsx(
    run_id: str,
    results: List[Any],
    original_file_path: Optional[Union[Path, str]] = None,
    test_cases: Optional[List[TestCase]] = None,
    output_path: Optional[Union[Path, str]] = None,
) -> Path:
    """Exports test run results to an Excel workbook with PASS/FAIL verdicts and logs.
    If original_file_path is provided, augments the uploaded file with results."""
    settings = get_settings()
    if output_path is None:
        output_path = settings.REPORTS_DIR / f"{run_id}_report.xlsx"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results_by_id = {r.test_case_id: r for r in results}
    results_by_title = {r.title.strip().lower(): r for r in results}

    pass_fill = PatternFill("solid", fgColor="D1E7DD")
    pass_font = Font(name="Calibri", bold=True, color="0F5132")
    fail_fill = PatternFill("solid", fgColor="F8D7DA")
    fail_font = Font(name="Calibri", bold=True, color="842029")
    header_fill = PatternFill("solid", fgColor="222222")
    header_font = Font(name="Calibri", bold=True, color="FFFFFF")

    wb: Optional[Workbook] = None
    if original_file_path and Path(original_file_path).exists():
        try:
            wb = load_workbook(Path(original_file_path))
        except Exception:
            wb = None

    if wb is not None:
        ws = wb.active
        
        # Detect header row in sheet
        header_row_idx = 1
        qa_kw = {"test", "title", "name", "step", "expected", "result", "id", "parameter"}
        for r in range(1, min(15, ws.max_row + 1)):
            row_vals = [str(ws.cell(row=r, column=c).value or "").lower() for c in range(1, ws.max_column + 1)]
            if any(any(kw in v for kw in qa_kw) for v in row_vals):
                header_row_idx = r
                break

        # Detect the true last populated column on header row
        real_cols = [c for c in range(1, ws.max_column + 1) if ws.cell(row=header_row_idx, column=c).value is not None and str(ws.cell(row=header_row_idx, column=c).value).strip() != ""]
        max_col = max(real_cols) if real_cols else ws.max_column

        # Identify ID and Title columns
        id_col_idx = None
        title_col_idx = None
        result_col_idx = None
        
        for col_idx in real_cols:
            val = str(ws.cell(row=header_row_idx, column=col_idx).value or "").strip()
            norm = _normalize_col(val)
            cleaned = clean_col_name(val)
            if norm == "ID" or any(syn == cleaned for syn in SYNONYM_MAP["id"]):
                id_col_idx = col_idx
            elif norm == "Title" or any(syn == cleaned for syn in SYNONYM_MAP["title"]):
                title_col_idx = col_idx
            elif "result" in cleaned or "verdict" in cleaned:
                result_col_idx = col_idx

        # Helper to find or add column
        def _find_or_add_col(name: str) -> int:
            for c in real_cols:
                h = str(ws.cell(row=header_row_idx, column=c).value or "").strip().lower()
                if h == name.lower():
                    return c
            nonlocal max_col
            max_col += 1
            cell = ws.cell(row=header_row_idx, column=max_col, value=name)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            return max_col

        verdict_col = _find_or_add_col("Verdict")
        duration_col = _find_or_add_col("Duration (ms)")
        notes_col = _find_or_add_col("Execution Logs / Failure Reason")

        for row_idx in range(header_row_idx + 1, ws.max_row + 1):
            raw_id_val = ws.cell(row=row_idx, column=id_col_idx).value if id_col_idx else None
            raw_title_val = ws.cell(row=row_idx, column=title_col_idx).value if title_col_idx else None

            # Skip empty / continuation rows
            if raw_id_val is None and raw_title_val is None:
                continue

            tc_id_str = str(raw_id_val).strip() if raw_id_val is not None else ""
            tc_title_str = str(raw_title_val).strip() if raw_title_val is not None else ""

            # Attempt matching result
            res = results_by_id.get(tc_id_str)
            if not res and tc_id_str:
                try:
                    num = float(tc_id_str)
                    res = results_by_id.get(f"TC-{int(num):04d}") or results_by_id.get(str(int(num)))
                except Exception:
                    pass
            if not res and tc_title_str:
                res = results_by_title.get(tc_title_str.lower())

            if not res:
                continue

            # Populate verdict
            v_cell = ws.cell(row=row_idx, column=verdict_col, value=res.verdict.value)
            v_cell.alignment = Alignment(horizontal="center", vertical="center")
            if res.verdict.value == "PASS":
                v_cell.fill = pass_fill
                v_cell.font = pass_font
            else:
                v_cell.fill = fail_fill
                v_cell.font = fail_font

            # Also update existing Result column if present
            if result_col_idx and result_col_idx != verdict_col:
                orig_r_cell = ws.cell(row=row_idx, column=result_col_idx, value=res.verdict.value)
                orig_r_cell.alignment = Alignment(horizontal="center", vertical="center")
                if res.verdict.value == "PASS":
                    orig_r_cell.fill = pass_fill
                    orig_r_cell.font = pass_font
                else:
                    orig_r_cell.fill = fail_fill
                    orig_r_cell.font = fail_font

            ws.cell(row=row_idx, column=duration_col, value=res.duration_ms).alignment = Alignment(horizontal="right")

            # Extract descriptive failure / pass log
            log_str = getattr(res, "notes", None) or ""
            if not log_str and getattr(res, "logs", None):
                log_str = " | ".join(res.logs)
            if not log_str:
                for step in getattr(res, "steps", []):
                    if step.verdict.value == "FAIL":
                        log_str = f"Step {step.step_index} [{step.action}] failed: {step.log or step.error or 'assertion failed'}"
                        break
            if not log_str and res.verdict.value == "PASS":
                log_str = "All assertions verified successfully."

            ws.cell(row=row_idx, column=notes_col, value=log_str)

        ws.column_dimensions[ws.cell(row=header_row_idx, column=verdict_col).column_letter].width = 16
        ws.column_dimensions[ws.cell(row=header_row_idx, column=duration_col).column_letter].width = 16
        ws.column_dimensions[ws.cell(row=header_row_idx, column=notes_col).column_letter].width = 60

    else:
        # Create fresh workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Test Run Results"

        cols = ["ID", "Title", "Preconditions", "Steps", "Expected Result", "Priority", "Tags", "Verdict", "Duration (ms)", "Execution Logs / Failure Reason"]
        for col_idx, col_name in enumerate(cols, start=1):
            cell = ws.cell(row=1, column=col_idx, value=col_name)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        tc_map = {tc.id: tc for tc in (test_cases or [])}

        for row_idx, res in enumerate(results, start=2):
            tc = tc_map.get(res.test_case_id)
            ws.cell(row=row_idx, column=1, value=res.test_case_id)
            ws.cell(row=row_idx, column=2, value=res.title)
            ws.cell(row=row_idx, column=3, value=tc.preconditions if tc else "")
            ws.cell(row=row_idx, column=4, value=tc.steps if tc else "")
            ws.cell(row=row_idx, column=5, value=tc.expected_result if tc else "")
            ws.cell(row=row_idx, column=6, value=tc.priority if tc else "Medium")
            ws.cell(row=row_idx, column=7, value=", ".join(tc.tags) if tc and tc.tags else "")

            v_cell = ws.cell(row=row_idx, column=8, value=res.verdict.value)
            v_cell.alignment = Alignment(horizontal="center", vertical="center")
            if res.verdict.value == "PASS":
                v_cell.fill = pass_fill
                v_cell.font = pass_font
            else:
                v_cell.fill = fail_fill
                v_cell.font = fail_font

            ws.cell(row=row_idx, column=9, value=res.duration_ms).alignment = Alignment(horizontal="right")

            log_str = getattr(res, "notes", None) or ""
            if not log_str and getattr(res, "logs", None):
                log_str = " | ".join(res.logs)
            if not log_str:
                for step in getattr(res, "steps", []):
                    if step.verdict.value == "FAIL":
                        log_str = f"Step {step.step_index} [{step.action}] failed: {step.log or step.error or 'assertion failed'}"
                        break
            if not log_str and res.verdict.value == "PASS":
                log_str = "All assertions verified successfully."

            ws.cell(row=row_idx, column=10, value=log_str)

        widths = [14, 35, 30, 45, 40, 12, 18, 14, 15, 60]
        for idx, w in enumerate(widths, start=1):
            ws.column_dimensions[ws.cell(row=1, column=idx).column_letter].width = w

    wb.save(output_path)
    return output_path
