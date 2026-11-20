"""
momus404 — app.services.planner_service
Cognitive tier: Hermes structured planning + OpenAI self-healing + report generator.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import redact
from app.schemas.common import Verdict
from app.schemas.event import LogEvent
from app.schemas.run import PlannedStep, TestCaseResult
from app.schemas.spec import TestCase
from app.services.event_bus import get_event_bus

logger = get_logger("brain")

_TOKENS_SAVED_BY_LAYA = 0
CLOUD_TOKENS_PER_CHECK = 300


def record_tokens_saved(steps_passed: int = 1) -> int:
    global _TOKENS_SAVED_BY_LAYA
    _TOKENS_SAVED_BY_LAYA += steps_passed * CLOUD_TOKENS_PER_CHECK
    return _TOKENS_SAVED_BY_LAYA


def get_tokens_saved() -> int:
    return _TOKENS_SAVED_BY_LAYA


def reset_tokens_saved() -> None:
    global _TOKENS_SAVED_BY_LAYA
    _TOKENS_SAVED_BY_LAYA = 0


_CANNED_PLANS: Dict[str, List[Dict[str, Any]]] = {
    "login": [
        {"action": "navigate", "target": "/login", "value": "", "expect": "login form visible"},
        {"action": "fill", "target": '[name="username"]', "value": "{{username}}", "expect": "username filled"},
        {"action": "fill", "target": '[name="password"]', "value": "{{password}}", "expect": "password filled"},
        {"action": "click", "target": 'button[type="submit"]', "value": "", "expect": "form submitted"},
        {"action": "assert", "target": "", "value": "", "expect": "dashboard visible or redirected"},
    ],
    "dashboard": [
        {"action": "navigate", "target": "/dashboard", "value": "", "expect": "dashboard loaded"},
        {"action": "assert", "target": "", "value": "", "expect": "widgets rendered"},
    ],
    "crud": [
        {"action": "navigate", "target": "/dashboard", "value": "", "expect": "dashboard loaded"},
        {"action": "click", "target": 'button:text("+ New Item")', "value": "", "expect": "dialog opened"},
        {"action": "fill", "target": '[name="name"]', "value": "Automated Test Item", "expect": "name entered"},
        {"action": "click", "target": 'button:text("Save")', "value": "", "expect": "saved"},
        {"action": "assert", "target": "", "value": "", "expect": "item appears in list"},
    ],
    "logout": [
        {"action": "navigate", "target": "/dashboard", "value": "", "expect": "dashboard loaded"},
        {"action": "click", "target": '[data-testid="user-avatar"]', "value": "", "expect": "menu opened"},
        {"action": "click", "target": 'button:text("Logout")', "value": "", "expect": "logout clicked"},
        {"action": "assert", "target": "", "value": "", "expect": "login screen shown"},
    ],
    "default": [
        {"action": "navigate", "target": "/", "value": "", "expect": "page loaded"},
        {"action": "assert", "target": "", "value": "", "expect": "content visible"},
    ],
}


class AgentBrain:
    """Cognitive reasoning and plan generation tier."""

    def __init__(self, mock_override: Optional[bool] = None) -> None:
        settings = get_settings()
        self._mock = mock_override if mock_override is not None else settings.MOCK_LLM
        self._hermes_url = settings.HERMES_BASE_URL
        self._hermes_key = settings.HERMES_API_KEY
        self._hermes_model = settings.HERMES_MODEL
        self._openai_key = settings.OPENAI_API_KEY
        self._openai_model = settings.OPENAI_MODEL

        if not self._mock and not self._hermes_key:
            logger.warning("[BRAIN] No HERMES_API_KEY set — falling back to mock planner.")
            self._mock = True

    def _parse_test_case_to_steps(
        self,
        test_case: TestCase,
        username: str = "",
        password: str = "",
        target_url: str = "",
    ) -> List[Dict[str, Any]]:
        steps_text = test_case.steps or ""
        title = test_case.title or ""
        preconditions = test_case.preconditions or ""
        expected = test_case.expected_result or ""
        tc_id = test_case.id or ""
        tags_str = " ".join(test_case.tags).lower()

        is_backend = (
            tc_id.startswith("BE-") or
            "backend" in tags_str or
            "/api/" in steps_text or
            "/api/" in title
        )

        if is_backend:
            # Backend API step extraction
            method = "POST"
            for m in ["GET", "POST", "OPTIONS", "PUT", "DELETE"]:
                if f" {m} " in f" {steps_text} " or f" {m} " in f" {title} " or f"Send {m}" in steps_text:
                    method = m
                    break

            endpoint = "/api/auth/login"
            for ep in ["/api/auth/verify", "/api/auth/logout", "/api/auth/login", "/api/ingest"]:
                if ep in steps_text or ep in title:
                    endpoint = ep
                    break

            # Extract payload or construct from steps
            payload = ""
            json_match = re.search(r'(\{[^{}]*\})', steps_text)
            if json_match:
                payload = json_match.group(1)
            else:
                user_match = re.search(r'username\s*=\s*"([^"]*)"', steps_text)
                pass_match = re.search(r'password\s*=\s*"([^"]*)"', steps_text)
                remember_match = re.search(r'remember_me\s*=\s*(true|false)', steps_text, re.IGNORECASE)
                
                body_dict = {}
                if user_match:
                    body_dict["username"] = user_match.group(1)
                elif "tester" in title.lower() or "qa" in title.lower():
                    body_dict["username"] = "qa_tester@momus404.local"
                elif "locked" in title.lower():
                    body_dict["username"] = "locked_user@momus404.local"
                elif "disabled" in title.lower():
                    body_dict["username"] = "disabled_user@momus404.local"
                elif not any(w in title.lower() for w in ["missing \"username\"", "missing username", "empty body"]):
                    body_dict["username"] = username or "admin@momus404.local"
                
                if pass_match:
                    body_dict["password"] = pass_match.group(1)
                elif "tester" in title.lower() or "qa" in title.lower():
                    body_dict["password"] = "TesterPass@2026"
                elif "locked" in title.lower():
                    body_dict["password"] = "LockedPass123!"
                elif "disabled" in title.lower():
                    body_dict["password"] = "DisabledPass123!"
                elif "case" in title.lower() and "password" in title.lower():
                    body_dict["password"] = "momus404!secureadmin"
                elif not any(w in title.lower() for w in ["missing \"password\"", "missing password", "empty body"]):
                    body_dict["password"] = password or "Momus404!SecureAdmin"
                    
                if remember_match:
                    body_dict["remember_me"] = remember_match.group(1).lower() == "true"
                elif "remember_me=true" in title.lower():
                    body_dict["remember_me"] = True
                elif "remember_me=false" in title.lower():
                    body_dict["remember_me"] = False
                    
                if body_dict:
                    payload = json.dumps(body_dict)

            return [
                {
                    "action": "http",
                    "target": f"{method} {endpoint}",
                    "value": payload,
                    "expect": f"{method} {endpoint} -> {expected[:60]}",
                },
                {
                    "action": "assert",
                    "target": "status_and_body",
                    "value": "",
                    "expect": expected,
                },
            ]

        # Frontend UI step extraction: Cognitive Test Case Semantic Analyzer
        title_lower = title.lower()
        steps_lower = steps_text.lower()
        expected_lower = expected.lower()
        full_text = f"{title_lower}\n{steps_lower}\n{expected_lower}"

        clean_target = (target_url or "").strip()
        if clean_target:
            start_url = clean_target
        elif "/verification" in preconditions.lower() and "logout" in title_lower:
            start_url = "/verification"
        else:
            start_url = "http://localhost:3000/login"

        resolved_user = username or "admin@jppl.com"
        resolved_pass = password or "Momus404!SecureAdmin"

        steps: List[Dict[str, Any]] = [{
            "action": "navigate",
            "target": start_url,
            "value": "",
            "expect": f"{start_url} loaded",
        }]

        # ── SPECIALIZED SCENARIO 1: Eye Icon & Password Visibility ──
        is_eye_test = any(kw in full_text for kw in [
            "eye icon", "visibility toggle", "toggle to visible", "toggle to masked",
            "input masking", "plain text", "masked bullets", "password eye", "show/hide",
        ])
        if is_eye_test:
            # 1. First always fill password so real characters exist to reveal/mask
            steps.append({
                "action": "fill",
                "target": 'input[type="password"], input[name*="pass" i], #password',
                "value": resolved_pass,
                "expect": "Filled password to verify visibility",
            })

            # Check if toggling to masked (needs reveal then mask back)
            if "toggle to masked" in full_text or "revert back to masked" in full_text:
                steps.append({
                    "action": "click",
                    "target": 'button:has(svg):near(input[type="password"]), button:has(svg):near(input[type="text"]), input ~ button:has(svg), #toggle-password, button[aria-label*="password" i]',
                    "value": "",
                    "expect": "Clicked eye icon to reveal password",
                })
                steps.append({
                    "action": "click",
                    "target": 'button:has(svg):near(input[type="password"]), button:has(svg):near(input[type="text"]), input ~ button:has(svg), #toggle-password, button[aria-label*="password" i]',
                    "value": "",
                    "expect": "Clicked eye icon again to toggle masked",
                })
                steps.append({
                    "action": "assert_visibility",
                    "target": "password_visibility",
                    "value": "password",
                    "expect": "Password input switched back to type='password' (masked bullets)",
                })
                return steps

            elif "toggle to visible" in full_text or "readable plain text" in full_text:
                steps.append({
                    "action": "click",
                    "target": 'button:has(svg):near(input[type="password"]), button:has(svg):near(input[type="text"]), input ~ button:has(svg), #toggle-password, button[aria-label*="password" i]',
                    "value": "",
                    "expect": "Clicked eye icon to reveal password",
                })
                steps.append({
                    "action": "assert_visibility",
                    "target": "password_visibility",
                    "value": "text",
                    "expect": "Password input switched to type='text' (plain text visible)",
                })
                return steps

            elif "hover" in full_text or "clickability" in full_text or "eye shape" in full_text:
                steps.append({
                    "action": "click",
                    "target": 'button:has(svg):near(input[type="password"]), button:has(svg):near(input[type="text"]), input ~ button:has(svg), #toggle-password, button[aria-label*="password" i]',
                    "value": "",
                    "expect": "Clicked eye icon button",
                })
                steps.append({
                    "action": "assert",
                    "target": 'button:has(svg):near(input[type="password"]), #toggle-password',
                    "value": "",
                    "expect": expected,
                })
                return steps

        # ── SPECIALIZED SCENARIO 2: Standalone Unit Dropdown Checks ──
        is_dropdown_isolated = any(kw in title_lower for kw in [
            "dropdown clickability", "list availability", "hover state highlight",
            "item selection action", "value replacement", "click-away closure",
        ])
        if is_dropdown_isolated:
            if "item selection" in title_lower or "value replacement" in title_lower:
                steps.append({
                    "action": "select",
                    "target": 'select, [role="combobox"], #unit, #unit-select',
                    "value": "Unit 1",
                    "expect": "Selected unit 'Unit 1'",
                })
                steps.append({
                    "action": "assert",
                    "target": 'select',
                    "value": "Unit 1",
                    "expect": expected,
                })
                return steps
            else:
                steps.append({
                    "action": "click",
                    "target": 'select, [role="combobox"], #unit-select, button:has-text("Select Unit")',
                    "value": "",
                    "expect": "Interacted with unit dropdown",
                })
                steps.append({
                    "action": "assert",
                    "target": 'select',
                    "value": "",
                    "expect": expected,
                })
                return steps

        # ── SCENARIO 3: Multi-Step Natural Language Form Execution ──
        raw_lines = [s.strip() for s in steps_text.split('\n') if s.strip()]
        if not raw_lines:
            raw_lines = [title]

        for line in raw_lines:
            clean = re.sub(r'^\d+\.\s*', '', line).strip()
            if not clean:
                continue
            c_lower = clean.lower()

            # 1. Email / Username Fields
            if any(w in c_lower for w in ["email", "username"]):
                if any(w in c_lower for w in ["leave", "empty", "blank"]):
                    steps.append({"action": "fill", "target": 'input[type="email"], input[name*="user" i], input[name*="email" i], #username', "value": "", "expect": "Left email blank"})
                elif "trailing space" in c_lower or "space at the end" in c_lower:
                    steps.append({"action": "fill", "target": 'input[type="email"], input[name*="user" i], input[name*="email" i], #username', "value": f"{resolved_user}   ", "expect": "Entered email with trailing spaces"})
                elif "leading space" in c_lower or "space at the beginning" in c_lower:
                    steps.append({"action": "fill", "target": 'input[type="email"], input[name*="user" i], input[name*="email" i], #username', "value": f"   {resolved_user}", "expect": "Entered email with leading spaces"})
                elif "without the '@'" in c_lower or "without @" in c_lower:
                    steps.append({"action": "fill", "target": 'input[type="email"], input[name*="user" i], input[name*="email" i], #username', "value": "adminjppl.com", "expect": "Entered email without @"})
                elif "ending with '@'" in c_lower or "no domain" in c_lower:
                    steps.append({"action": "fill", "target": 'input[type="email"], input[name*="user" i], input[name*="email" i], #username', "value": "admin@", "expect": "Entered email ending with @ no domain"})
                elif "non-existent" in c_lower or "unregistered" in c_lower:
                    steps.append({"action": "fill", "target": 'input[type="email"], input[name*="user" i], input[name*="email" i], #username', "value": "unregistered_99@test.com", "expect": "Entered non-existent email"})
                else:
                    quoted_user = re.search(r'"([^"]*)"', clean)
                    user_val = quoted_user.group(1) if quoted_user else resolved_user
                    steps.append({"action": "fill", "target": 'input[type="email"], input[name*="user" i], input[name*="email" i], #username', "value": user_val, "expect": f"Entered email ({user_val})"})
                continue

            # 2. Password Fields
            if "password" in c_lower:
                if any(w in c_lower for w in ["leave", "empty", "blank"]):
                    steps.append({"action": "fill", "target": 'input[type="password"], input[name*="pass" i], #password', "value": "", "expect": "Left password blank"})
                elif any(w in c_lower for w in ["incorrect", "wrong", "invalid"]):
                    steps.append({"action": "fill", "target": 'input[type="password"], input[name*="pass" i], #password', "value": "WrongPassword!99", "expect": "Entered incorrect password"})
                else:
                    quoted_pass = re.search(r'"([^"]*)"', clean)
                    pass_val = quoted_pass.group(1) if quoted_pass else resolved_pass
                    steps.append({"action": "fill", "target": 'input[type="password"], input[name*="pass" i], #password', "value": pass_val, "expect": "Entered password"})
                continue

            # 3. Unit Dropdown
            if "unit" in c_lower:
                if any(w in c_lower for w in ["unselected", "leave", "default placeholder"]):
                    pass  # Explicitly leave unselected
                else:
                    quoted_unit = re.search(r'"([^"]*)"', clean)
                    unit_label = quoted_unit.group(1) if quoted_unit else "Unit 1"
                    steps.append({
                        "action": "select",
                        "target": 'select, [role="combobox"], #unit, #unit-select',
                        "value": unit_label,
                        "expect": f"Selected unit '{unit_label}'",
                    })
                continue

            # 4. OTP / 2FA / Verification Code
            if any(w in c_lower for w in ["otp", "2fa", "verification code", "token"]):
                quoted_otp = re.search(r'"([^"]*)"', clean)
                otp_code = quoted_otp.group(1) if quoted_otp else "123456"
                steps.append({
                    "action": "fill",
                    "target": 'input[autocomplete="one-time-code"], input[name*="otp" i], input[name*="2fa" i], #otp, input[placeholder*="code" i]',
                    "value": otp_code,
                    "expect": f"Entered OTP ({otp_code})",
                })
                continue

            # 5. Compound: "fill other fields" or "fill all fields"
            if "fill other fields" in c_lower or "fill all fields" in c_lower:
                steps.append({"action": "fill", "target": 'input[type="password"], input[name*="pass" i], #password', "value": resolved_pass, "expect": "Filled password"})
                steps.append({"action": "select", "target": 'select, [role="combobox"], #unit, #unit-select', "value": "Unit 1", "expect": "Selected unit 'Unit 1'"})
                continue

            # 6. Eye icon toggle within multi-step
            if "eye icon" in c_lower or "toggle" in c_lower:
                steps.append({
                    "action": "click",
                    "target": 'button:has(svg):near(input[type="password"]), button:has(svg):near(input[type="text"]), input ~ button:has(svg), #toggle-password, button[aria-label*="password" i]',
                    "value": "",
                    "expect": "Clicked eye icon button",
                })
                continue

            # 7. Remember session checkbox
            if "remember" in c_lower:
                steps.append({"action": "click", "target": '#remember-me, input[type="checkbox"]', "value": "", "expect": "Toggled remember session"})
                continue

            # 8. Logout
            if "logout" in c_lower:
                steps.append({"action": "click", "target": 'button:has-text("Logout"), a:has-text("Logout")', "value": "", "expect": "Clicked logout"})
                continue

            # 9. Click Login / Submit
            submit_keywords = [
                "click login", "click submit", "click sign in", "click 'login'", 'click "login"',
                "click 'submit'", 'click "submit"', "press login", "press submit", "press sign in",
                "press enter", "hit enter", "hit login", "tap login", "submit the form", "submit form",
                "click the login", "click the submit", "login button", "submit button"
            ]
            is_click_submit = any(k in c_lower for k in submit_keywords) or c_lower.strip() in ["login", "submit", "sign in"]
            if any(skip in c_lower for skip in ["observe", "navigate", "open", "url", "inspect", "check", "verify", "view", "presence", "field", "form"]):
                is_click_submit = False

            if is_click_submit:
                steps.append({
                    "action": "click",
                    "target": 'button[type="submit"], button:has-text("Login"), button:has-text("Sign in"), #login-submit',
                    "value": "",
                    "expect": "Clicked Login button",
                })
                continue

        # Final assertion step
        steps.append({
            "action": "assert",
            "target": "#verification-status" if ("verification" in expected_lower or "dashboard" in expected_lower) else "",
            "value": "",
            "expect": expected,
        })
        return steps

    async def plan(
        self,
        test_case: TestCase,
        target_url: str = "",
        username: str = "",
        password: str = "",
    ) -> List[PlannedStep]:
        event_bus = get_event_bus()

        if self._mock:
            raw_steps = self._parse_test_case_to_steps(
                test_case,
                username=username,
                password=password,
                target_url=target_url,
            )
            logger.info(f"[BRAIN] Dynamic plan generated for {test_case.id} ({len(raw_steps)} steps)")
            await event_bus.publish(LogEvent(
                source="BRAIN",
                test_id=test_case.id,
                message=f"Plan generated: {len(raw_steps)} steps with extracted credentials/payloads",
            ))
            return [
                PlannedStep(
                    index=i,
                    action=s["action"],
                    target=s["target"],
                    value=s["value"],
                    expect=s["expect"],
                )
                for i, s in enumerate(raw_steps)
            ]

        # Real Hermes LLM call
        prompt = (
            f"You are Nous Hermes test planner. Turn this test case into JSON steps:\n"
            f"Title: {test_case.title}\nPreconditions: {test_case.preconditions}\n"
            f"Steps: {test_case.steps}\nExpected: {test_case.expected_result}\n\n"
            f"Output strictly a JSON list of objects with keys: action, target, value, expect.\n"
            f"Valid actions: navigate, click, fill, assert, wait."
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{self._hermes_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._hermes_key}", "Content-Type": "application/json"},
                    json={
                        "model": self._hermes_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                    },
                )
                res.raise_for_status()
                content = res.json()["choices"][0]["message"]["content"]
                match = re.search(r"\[.*\]", content, re.DOTALL)
                raw_steps = json.loads(match.group(0)) if match else []
                return [
                    PlannedStep(
                        index=i,
                        action=s.get("action", "assert"),
                        target=s.get("target", ""),
                        value=s.get("value", ""),
                        expect=s.get("expect", ""),
                    )
                    for i, s in enumerate(raw_steps)
                ]
        except Exception as exc:
            logger.error(f"[BRAIN] Hermes call failed: {exc} — fallback to mock.")
            return await AgentBrain(mock_override=True).plan(test_case)

    async def self_heal(
        self,
        step: PlannedStep,
        dom_snippet: str,
        attempt: int,
        error_msg: str = "",
    ) -> Optional[PlannedStep]:
        event_bus = get_event_bus()
        clean_dom = redact(dom_snippet[:2000])

        if self._mock or not self._openai_key:
            alt_selectors = {
                'button[type="submit"]': 'button:has-text("Sign In")',
                '[name="username"]': '#username',
                '[name="password"]': '#password',
            }
            new_target = alt_selectors.get(step.target, f"{step.target}-healed")
            logger.info(f"[HEAL] MOCK healed: {step.target} → {new_target}")
            await event_bus.publish(LogEvent(
                source="HEAL",
                message=f"Healed selector {step.target} → {new_target} (attempt {attempt}) [MOCK]",
            ))
            return PlannedStep(
                index=step.index,
                action=step.action,
                target=new_target,
                value=step.value,
                expect=step.expect,
            )

        # Real OpenAI self-heal call
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self._openai_key}", "Content-Type": "application/json"},
                    json={
                        "model": self._openai_model,
                        "messages": [
                            {"role": "system", "content": "You are a Playwright test self-healer. Return JSON {new_target: str, reason: str}."},
                            {"role": "user", "content": f"Failed selector: {step.target}\nDOM:\n{clean_dom}"},
                        ],
                        "temperature": 0.1,
                    },
                )
                res.raise_for_status()
                data = json.loads(res.json()["choices"][0]["message"]["content"])
                new_target = data.get("new_target", step.target)
                return PlannedStep(
                    index=step.index,
                    action=step.action,
                    target=new_target,
                    value=step.value,
                    expect=step.expect,
                )
        except Exception as exc:
            logger.error(f"[HEAL] OpenAI healing failed: {exc}")
            return None

    async def generate_report(
        self,
        run_id: str,
        results: List[TestCaseResult],
        tokens_saved_count: int = 0,
    ) -> str:
        total = len(results)
        passed = sum(1 for r in results if r.verdict == Verdict.PASS_)
        failed = total - passed
        pass_rate = (passed / total * 100) if total else 0

        lines = [
            "# MOMUS404 Test Report",
            f"**Run ID:** `{run_id}`",
            f"**Result:** {passed}/{total} passed ({pass_rate:.1f}%)",
            f"**Tokens saved by Laya:** {tokens_saved_count}",
            "",
            "## Test Case Results",
            "",
            "| # | ID | Title | Verdict | Steps | Heals | Duration | Notes / Failure Summary |",
            "|---|----|-------|---------|-------|-------|----------|-------------------------|",
        ]
        for i, r in enumerate(results, 1):
            verdict_tag = "✅ PASS" if r.verdict == Verdict.PASS_ else "❌ FAIL"
            summary_note = (r.notes or (r.logs[0] if r.logs else "")).replace("|", "/")[:65]
            lines.append(f"| {i} | `{r.test_case_id}` | {r.title} | {verdict_tag} | {len(r.steps)} | {r.heal_count} | {r.duration_ms}ms | {summary_note} |")

        lines += ["", "## Step Execution Logs & Traces", ""]
        for r in results:
            lines.append(f"### [{r.test_case_id}] {r.title} — `{r.verdict.value}`")
            if r.notes:
                lines.append(f"> **Verdict Notes:** {r.notes}\n")
            
            for s in r.steps:
                icon = {"PASS": "✅", "FAIL": "❌", "RETRY": "🔁"}.get(s.verdict.value, "❓")
                val_display = f" | value: `{redact(s.value)}`" if getattr(s, "value", None) else ""
                lines.append(f"- {icon} Step {s.step_index}: `{s.action}` on `{s.target}`{val_display} ({s.latency_ms}ms, conf={s.confidence:.2f})")
                if getattr(s, "log", None):
                    lines.append(f"  - 📝 Log: {s.log}")
                if s.error:
                    lines.append(f"  - ⚠️ Error: {redact(s.error)}")
                    
            if r.logs:
                lines.append("")
                lines.append("  **Case Logs:**")
                for l in r.logs:
                    lines.append(f"  - {l}")
            lines.append("")

        return "\n".join(lines)

    def health(self) -> Dict[str, Any]:
        return {
            "mock": self._mock,
            "hermes_model": self._hermes_model if not self._mock else "mock",
            "openai_model": self._openai_model if not self._mock else "mock",
            "hermes_key_set": bool(self._hermes_key),
            "openai_key_set": bool(self._openai_key),
        }


_global_brain: Optional[AgentBrain] = None


def get_brain() -> AgentBrain:
    global _global_brain
    if _global_brain is None:
        _global_brain = AgentBrain()
    return _global_brain
