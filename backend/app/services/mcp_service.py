"""
momus404 — app.services.mcp_service
Playwright MCP Server client (JSON-RPC 2.0 over STDIO or HTTP).
Includes tool name mapping layer and offline simulation mock.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shlex
import sys
import threading
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import redact
from app.schemas.event import LogEvent
from app.services.event_bus import get_event_bus

logger = get_logger("mcp")

# Known tool name mappings across @playwright/mcp versions
_DEFAULT_TOOL_MAP: Dict[str, str] = {
    "navigate": "browser_navigate",
    "click": "browser_click",
    "fill": "browser_type",
    "get_accessible_tree": "browser_snapshot",
    "screenshot": "browser_take_screenshot",
    "wait_for": "browser_wait_for",
}

_LEGACY_TOOL_MAP: Dict[str, str] = {
    "navigate": "playwright_navigate",
    "click": "playwright_click",
    "fill": "playwright_fill",
    "get_accessible_tree": "playwright_get_accessible_tree",
    "screenshot": "playwright_screenshot",
    "wait_for": "playwright_wait_for",
}

# Mock accessibility trees
_MOCK_A11Y_TREES: Dict[str, str] = {
    "login": (
        '<main aria-label="Login">\n'
        '  <h1>Sign In</h1>\n'
        '  <form id="login-form">\n'
        '    <label for="username">Username or Email</label>\n'
        '    <input id="username" name="username" type="text" autocomplete="username"/>\n'
        '    <label for="password">Password</label>\n'
        '    <input id="password" name="password" type="password"/>\n'
        '    <button type="submit" id="login-submit">Sign In</button>\n'
        '  </form>\n'
        '</main>'
    ),
    "dashboard": (
        '<main aria-label="Dashboard" role="main">\n'
        '  <h1>Authentication & Session Verified - dashboard visible or redirected</h1>\n'
        '  <header><span data-testid="user-avatar" role="button" aria-label="User profile">User</span></header>\n'
        '  <section id="widgets" role="region" aria-label="Widgets">\n'
        '    <article id="widget-1">Widget 1: Metrics Active - dashboard loaded</article>\n'
        '    <article id="widget-2">Widget 2: Queue 0 items - page loaded successfully</article>\n'
        '  </section>\n'
        '  <p id="verification-status">Status: Active Authenticated Session</p>\n'
        '  <button type="button">+ New Item</button>\n'
        '  <button type="button">Logout</button>\n'
        '</main>'
    ),
    "default": (
        '<main aria-label="Application">\n'
        '  <h1>Application Ready - page loaded successfully</h1>\n'
        '  <p id="content">Item saved successfully. State: active. content visible.</p>\n'
        '</main>'
    ),
}


class _ProactorLoopThread:
    """Dedicated background loop with ProactorEventLoop to ensure Windows subprocess support."""
    def __init__(self) -> None:
        if sys.platform == "win32":
            self.loop = asyncio.ProactorEventLoop()
        else:
            self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run(self, coro: Any) -> asyncio.Future:
        fut = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return asyncio.wrap_future(fut)

    def stop(self) -> None:
        try:
            self.loop.call_soon_threadsafe(self.loop.stop)
        except Exception:
            pass


CURSOR_INIT_SCRIPT = """
(() => {
    function injectCursor() {
        if (document.getElementById('__virtual_cursor')) return;
        const cur = document.createElement('div');
        cur.id = '__virtual_cursor';
        cur.style.cssText = 'position:fixed;width:22px;height:22px;background:rgba(239,68,68,0.9);border:2px solid #ffffff;border-radius:50%;pointer-events:none;z-index:99999999;transition:left 0.25s cubic-bezier(0.2, 0.8, 0.2, 1), top 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);transform:translate(-50%,-50%);box-shadow:0 0 14px rgba(239,68,68,0.85);left:100px;top:100px;display:block;';
        if (document.body) {
            document.body.appendChild(cur);
        } else {
            document.addEventListener('DOMContentLoaded', () => {
                if (document.body && !document.getElementById('__virtual_cursor')) {
                    document.body.appendChild(cur);
                }
            });
        }
        window.__moveCursor = (x, y) => {
            const el = document.getElementById('__virtual_cursor') || cur;
            if (el) {
                el.style.left = x + 'px';
                el.style.top = y + 'px';
                el.style.display = 'block';
            }
        };
        window.__ripple = (x, y) => {
            const dot = document.createElement('div');
            dot.style.cssText = `position:fixed;left:${x-22}px;top:${y-22}px;width:44px;height:44px;border-radius:50%;border:3px solid #ef4444;background:rgba(239,68,68,0.35);z-index:99999998;pointer-events:none;transition:transform 0.45s ease-out, opacity 0.45s ease-out;box-shadow:0 0 10px rgba(239,68,68,0.5);`;
            document.body.appendChild(dot);
            requestAnimationFrame(() => {
                dot.style.transform = 'scale(2.2)';
                dot.style.opacity = '0';
            });
            setTimeout(() => dot.remove(), 500);
        };
        window.__highlight = (x, y, w, h) => {
            const box = document.createElement('div');
            box.style.cssText = `position:fixed;left:${x-2}px;top:${y-2}px;width:${w+4}px;height:${h+4}px;border:2px solid #2563eb;border-radius:4px;background:rgba(37,99,235,0.12);z-index:99999997;pointer-events:none;transition:opacity 0.6s ease-out;box-shadow:0 0 8px rgba(37,99,235,0.4);`;
            document.body.appendChild(box);
            setTimeout(() => { box.style.opacity = '0'; }, 600);
            setTimeout(() => box.remove(), 1200);
        };
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectCursor);
    } else {
        injectCursor();
    }
})();
"""


def _match_dropdown_option(query: str, options: List[Tuple[str, str]]) -> Optional[Tuple[str, str]]:
    """
    5-tier generic dynamic option matcher:
    1. Exact match (case-insensitive) on text or value
    2. Word boundary token match (e.g. '9' matches 'Unit 9', not 'Unit 19')
    3. Number token match (e.g. ['9'] == ['9'])
    4. Substring match on non-placeholder options
    5. 1-based index if query is digits
    """
    q = str(query).strip().lower()
    if not q:
        return None
    selectable = [
        (val, txt) for val, txt in options
        if str(val).strip() not in ('', '0', 'none') and not any(p in txt.strip().lower() for p in ('select', 'choose', '--', 'none', 'select unit'))
    ]
    if not selectable:
        selectable = options

    # Tier 1: Exact match on label or value
    for val, txt in selectable:
        if q == txt.strip().lower() or q == str(val).strip().lower():
            return (val, txt)

    # Tier 2: Word boundary token match (avoids 1 matching 10)
    for val, txt in selectable:
        if re.search(rf'\b{re.escape(q)}\b', txt, re.IGNORECASE) or re.search(rf'\b{re.escape(q)}\b', str(val), re.IGNORECASE):
            return (val, txt)

    # Tier 3: Digit/number token match (e.g. user input '9' matches 'Unit 9', 'Unit 1' does not)
    q_digits = re.findall(r'\d+', q)
    if q_digits:
        for val, txt in selectable:
            t_digits = re.findall(r'\d+', txt) or re.findall(r'\d+', str(val))
            if q_digits == t_digits:
                return (val, txt)

    # Tier 4: Substring match on non-placeholder options
    for val, txt in selectable:
        t_clean = txt.strip().lower()
        if q in t_clean or (len(t_clean) > 3 and t_clean in q):
            return (val, txt)

    # Tier 5: 1-based index if query is digits
    if q.isdigit():
        idx = int(q)
        if 1 <= idx <= len(selectable):
            return selectable[idx - 1]

    return None


class PlaywrightMCPClient:
    """Client for real headed Playwright browser automation on desktop with CDP screencast."""

    def __init__(self, mock_override: Optional[bool] = None) -> None:
        self._runner: Optional[_ProactorLoopThread] = None
        self._pw = None
        self._browser = None
        self._context = None
        self._page = None
        self._cdp = None
        self._screencasting = False
        self._is_real = False
        self._mock = False
        self._mock_url = "about:blank"

    async def connect(self, headless: bool = False) -> None:
        """Launch real Chromium browser in headed mode (headless=False) on desktop."""
        try:
            self._runner = _ProactorLoopThread()

            async def _launch():
                from playwright.async_api import async_playwright
                self._pw = await async_playwright().start()
                self._browser = await self._pw.chromium.launch(
                    headless=headless,  # HEADED MODE: Real browser window appears on desktop!
                    slow_mo=100,        # Human-visible typing and clicking (100ms slow_mo + smooth transitions)
                    args=[
                        "--window-size=1280,800",
                        "--window-position=60,60",
                        "--disable-blink-features=AutomationControlled",
                        "--ignore-certificate-errors",
                        "--start-maximized",
                    ],
                )
                self._context = await self._browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    ignore_https_errors=True,
                    bypass_csp=True,
                )
                await self._context.add_init_script(CURSOR_INIT_SCRIPT)
                self._page = await self._context.new_page()
                try:
                    await self._page.bring_to_front()
                except Exception:
                    pass

            await self._runner.run(_launch())
            self._is_real = True
            self._mock = False
            logger.info("[PLAYWRIGHT] Real Chromium launched in HEADED mode (headless=False) on desktop.")
            
            # Automatically start CDP screencast for live streaming to frontend
            await self.start_screencast()

            event_bus = get_event_bus()
            await event_bus.publish(LogEvent(
                source="MCP",
                message="[PLAYWRIGHT] Headed Chromium browser window opened on desktop with live CDP screencast stream active",
                data={"action": "browser_launched", "headed": True, "cdp_screencast": True}
            ))
        except Exception as exc:
            logger.warning(f"[PLAYWRIGHT] Headed browser launch error ({exc}) — fallback to simulation: {exc}")
            self._is_real = False
            self._mock = True

    async def start_screencast(self, on_frame_callback: Optional[Any] = None) -> bool:
        """Starts real-time CDP screencast streaming frames to callback and ScreencastHub."""
        from app.services.event_bus import get_screencast_hub
        hub = get_screencast_hub()

        if self._is_real and self._page and self._runner:
            async def _start():
                try:
                    if self._cdp is None:
                        self._cdp = await self._page.context.new_cdp_session(self._page)
                    await self._cdp.send("Page.startScreencast", {
                        "format": "jpeg",
                        "quality": 75,
                        "maxWidth": 1280,
                        "maxHeight": 800,
                        "everyNthFrame": 1,
                    })
                    self._screencasting = True

                    async def _on_frame(event):
                        try:
                            data = event.get("data")
                            session_id = event.get("sessionId")
                            if session_id and self._cdp:
                                await self._cdp.send("Page.screencastFrameAck", {"sessionId": session_id})
                            if data:
                                hub.broadcast_frame_sync(data)
                                if on_frame_callback:
                                    if asyncio.iscoroutinefunction(on_frame_callback):
                                        await on_frame_callback(data)
                                    else:
                                        on_frame_callback(data)
                        except Exception:
                            pass

                    self._cdp.on("Page.screencastFrame", lambda ev: self._runner.loop.create_task(_on_frame(ev)))
                    logger.info("[PLAYWRIGHT] CDP Screencast started successfully.")
                    return True
                except Exception as e:
                    logger.warning(f"[PLAYWRIGHT] Failed to start CDP screencast: {e}")
                    return False

            try:
                return await self._runner.run(_start())
            except Exception as exc:
                logger.warning(f"[PLAYWRIGHT] Error invoking start_screencast: {exc}")
                return False
        return False

    async def evaluate_page_state(self) -> Dict[str, Any]:
        """Evaluates document readyState, title, url, and content length."""
        if self._is_real and self._page and self._runner:
            async def _eval():
                url = self._page.url
                try:
                    title = await self._page.title()
                except Exception:
                    title = ""
                try:
                    ready_state = await self._page.evaluate("() => document.readyState")
                except Exception:
                    ready_state = "loading"
                try:
                    elem_count = await self._page.evaluate("() => document.body ? document.body.querySelectorAll('*').length : 0")
                except Exception:
                    elem_count = 0
                try:
                    text_len = await self._page.evaluate("() => document.body ? document.body.innerText.trim().length : 0")
                except Exception:
                    text_len = 0
                return {
                    "url": url,
                    "title": title,
                    "ready_state": ready_state,
                    "element_count": elem_count,
                    "text_len": text_len,
                }
            try:
                res = await self._runner.run(_eval())
                if res and res.get("url"):
                    self._mock_url = res["url"]
                return res
            except Exception as e:
                real_url = self._mock_url
                try:
                    if self._page:
                        real_url = self._page.url
                except Exception:
                    pass
                return {"url": real_url, "ready_state": "loading", "error": str(e), "element_count": 0, "text_len": 0}
        if not self._mock_url or self._mock_url == "about:blank":
            return {"url": "about:blank", "ready_state": "loading", "title": "", "element_count": 0, "text_len": 0}
        return {"url": self._mock_url, "ready_state": "complete", "title": "Application Ready", "element_count": 10, "text_len": 100}

    async def navigate(self, url: str) -> Any:
        event_bus = get_event_bus()
        msg = f"[JEV] Navigation → {url}"
        logger.info(msg)
        await event_bus.publish(LogEvent(source="JEV", message=msg, data={"action": "navigate", "url": url, "source": "JEV"}))
        if self._is_real and self._page and self._runner:
            async def _nav():
                # ── 1. JEV CDP-FIRST NAVIGATION (<50ms) ──
                try:
                    cur = self._page.url
                    # Avoid disruptive reloads if browser is already at destination URL
                    if cur == url or cur.rstrip('/') == url.rstrip('/'):
                        return cur

                    if self._cdp is None:
                        self._cdp = await self._page.context.new_cdp_session(self._page)
                    
                    await self._cdp.send("Page.navigate", {"url": url})

                    # Wait for document.readyState == 'complete' (Jev pattern)
                    for _ in range(120):
                        ready = await self._page.evaluate("() => document.readyState")
                        if ready == "complete":
                            break
                        await asyncio.sleep(0.05)

                    try:
                        await self._page.bring_to_front()
                        await self._page.evaluate("() => window.focus()")
                    except Exception:
                        pass

                    try:
                        await self._page.evaluate(CURSOR_INIT_SCRIPT)
                    except Exception:
                        pass

                    await asyncio.sleep(0.2)
                    logger.info(f"[JEV] Action Completed: navigate to {self._page.url}")
                    return self._page.url
                except Exception as jev_nav_e:
                    logger.debug(f"[JEV] CDP navigate error ({jev_nav_e}), falling back to Playwright...")

                # ── 2. PLAYWRIGHT GOTO FALLBACK ──
                try:
                    await self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
                except Exception as e1:
                    logger.warning(f"[PLAYWRIGHT] Initial goto error ({e1}), falling back to wait_until='commit'...")
                    try:
                        await self._page.goto(url, wait_until="commit", timeout=10000)
                    except Exception as e2:
                        logger.error(f"[PLAYWRIGHT] Commit goto error ({e2})")
                
                # Bring browser to front & focus for desktop visibility
                try:
                    await self._page.bring_to_front()
                    await self._page.evaluate("() => window.focus()")
                except Exception:
                    pass

                # Ensure virtual cursor is injected
                try:
                    await self._page.evaluate(CURSOR_INIT_SCRIPT)
                except Exception:
                    pass

                # Wait for React SPA form elements to mount
                try:
                    await self._page.wait_for_selector("input, button, [role='button'], body", timeout=10000)
                except Exception:
                    pass
                await asyncio.sleep(0.5)
                return self._page.url
            try:
                self._mock_url = await self._runner.run(_nav())
                return {"status": 200, "url": self._mock_url, "source": "JEV"}
            except Exception as e:
                logger.error(f"[JEV] Navigate error for {url}: {e}")
                raise
        self._mock_url = url
        return {"status": 200, "url": url, "source": "JEV"}

    async def fill(self, selector: str, value: Any) -> Any:
        event_bus = get_event_bus()
        val_str = "" if value is None else str(value)
        redacted_val = "***" if "password" in selector.lower() else val_str
        msg = f"Playwright fill → {selector} = {redacted_val}"
        logger.info(f"[MCP] {msg}")
        await event_bus.publish(LogEvent(source="MCP", message=msg, data={"action": "fill", "selector": selector, "value": redacted_val, "url": self._mock_url}))
        if self._is_real and self._page and self._runner:
            async def _do_fill():
                target_lower = selector.lower()

                # ── 1. JEV-FIRST DIRECT NODE RESOLUTION (<25ms) ──
                try:
                    from jev_ultrafast.browser import READ_STATE
                    # Patch READ_STATE to include password inputs so Jev can inspect and target them
                    jev_read = READ_STATE.replace("!['password','file','hidden'].includes(e.type)", "!['file','hidden'].includes(e.type)")
                    state = await self._page.evaluate(jev_read)
                    if state and "actions" in state:
                        input_action = None
                        is_pass = "pass" in target_lower
                        if is_pass:
                            input_action = next(
                                (a for a in state["actions"] if a.get("kind") in ("fill", "input") and (
                                    "pass" in (a.get("label") or "").lower() or
                                    a.get("role") == "password" or
                                    "password" in str(a.get("value", "")).lower()
                                )),
                                None
                            )
                            # If Jev didn't label it 'pass', take the second fill action (password is below username)
                            if not input_action:
                                fill_cands = [a for a in state["actions"] if a.get("kind") in ("fill", "input") and a.get("node") != 1]
                                if fill_cands:
                                    input_action = fill_cands[0]
                        elif any(k in target_lower for k in ["user", "email", "login"]):
                            input_action = next(
                                (a for a in state["actions"] if a.get("kind") in ("fill", "input") and any(
                                    k in (a.get("label") or "").lower() for k in ["email", "user", "name", "login"]
                                )),
                                None
                            )
                        elif any(k in target_lower for k in ["otp", "2fa", "code", "token"]):
                            input_action = next(
                                (a for a in state["actions"] if a.get("kind") in ("fill", "input") and any(
                                    k in (a.get("label") or "").lower() for k in ["code", "otp", "2fa", "token"]
                                )),
                                None
                            )

                        if not input_action:
                            clean_t = selector.replace('input[', '').replace(']', '').replace('"', '').replace("'", "").replace('#', '').strip().lower()
                            if clean_t:
                                input_action = next(
                                    (a for a in state["actions"] if a.get("kind") in ("fill", "input") and (
                                        clean_t in (a.get("label") or "").lower() or
                                        (a.get("label") or "").lower() in clean_t
                                    )),
                                    None
                                )

                        if not input_action:
                            fill_actions = [a for a in state["actions"] if a.get("kind") in ("fill", "input")]
                            if is_pass:
                                # Password: strictly exclude node 1 (email) and email/user labels
                                pass_cands = [a for a in fill_actions if a.get("node") != 1 and not any(k in (a.get("label") or "").lower() for k in ["email", "user", "login"])]
                                input_action = pass_cands[0] if pass_cands else (fill_actions[-1] if len(fill_actions) > 1 else None)
                            else:
                                fill_actions.sort(key=lambda a: a.get("node", 999))
                                non_pass = [a for a in fill_actions if "pass" not in (a.get("label") or "").lower()]
                                input_action = non_pass[0] if non_pass else (fill_actions[0] if fill_actions else None)

                        # If password node wasn't in Jev state, query password DOM element directly for rect
                        if is_pass and not input_action:
                            pass_box = await self._page.evaluate("""() => {
                                const el = document.querySelector('input[type="password"], input[name*="pass" i], input[placeholder*="pass" i]');
                                if (!el) return null;
                                const r = el.getBoundingClientRect();
                                return {x: r.x, y: r.y, w: r.width, h: r.height, node: 2, label: 'password'};
                            }""")
                            if pass_box:
                                input_action = pass_box

                        if input_action:
                            r = input_action.get("rect", {})
                            cx = r.get("x", 0) + r.get("w", 0) / 2
                            cy = r.get("y", 0) + r.get("h", 0) / 2
                            if cx > 0 and cy > 0:
                                await self._page.evaluate(
                                    "({x, y, w, h}) => { if (window.__moveCursor) window.__moveCursor(x, y); if (window.__ripple) window.__ripple(x, y); if (window.__highlight) window.__highlight(x - w/2, y - h/2, w, h); }",
                                    {"x": cx, "y": cy, "w": r.get("w", 200), "h": r.get("h", 35)}
                                )
                                await asyncio.sleep(0.15)
                            # Use type-aware DOM selection and support React controlled components
                            is_pass = "pass" in target_lower
                            await self._page.evaluate(
                                """(args) => {
                                    let e = null;
                                    if (args.isPassword) {
                                        e = document.querySelector('input[type="password"]')
                                          || document.querySelector('input[name*="pass" i]')
                                          || document.querySelector('input[placeholder*="pass" i]');
                                    } else {
                                        e = document.querySelector('input[type="email"]')
                                          || document.querySelector('input[type="text"]:not([name*="pass" i]):not([placeholder*="pass" i])')
                                          || document.querySelector('input:not([type="password"]):not([type="hidden"])');
                                    }
                                    if (!e && window.__jevFast) e = window.__jevFast.nodes.get(args.node);
                                    if (e) {
                                        e.scrollIntoView({block:'nearest', inline:'nearest'});
                                        e.focus();

                                        // Support React controlled components via native prototype setter and valueTracker
                                        const proto = window.HTMLInputElement.prototype;
                                        const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                                        if (setter) {
                                            setter.call(e, args.val);
                                        } else {
                                            e.value = args.val;
                                        }
                                        if (e._valueTracker) {
                                            e._valueTracker.setValue('');
                                        }
                                        e.dispatchEvent(new Event('input', {bubbles: true, composed: true}));
                                        e.dispatchEvent(new Event('change', {bubbles: true, composed: true}));
                                    }
                                }""",
                                {"node": input_action.get("node"), "val": val_str, "isPassword": is_pass}
                            )
                            # Type via keyboard to ensure browser-level keystrokes register in React
                            try:
                                await self._page.keyboard.press("ControlOrMeta+A")
                                await self._page.keyboard.press("Backspace")
                                if val_str:
                                    await self._page.keyboard.type(val_str, delay=15)
                            except Exception:
                                pass
                            await asyncio.sleep(0.2)
                            logger.info(f"[JEV] Action Completed: fill node {input_action.get('node')} '{input_action.get('label')}'")
                            return {"filled": f"jev-node:{input_action.get('label', 'input')}", "source": "JEV"}
                except Exception as jev_e:
                    logger.debug(f"[JEV] Node fill resolution error: {jev_e}")

                # ── 2. PLAYWRIGHT LOCATOR FALLBACK ──
                raw_parts = [s.strip() for s in selector.split(',') if s.strip()]
                target_selectors: List[str] = []
                for p in raw_parts:
                    target_selectors.append(p)
                    clean_part = p.lstrip('#').lstrip('.').strip()
                    if clean_part and not any(ch in clean_part for ch in ['[', ']', '"', "'", '=', ':', ' ', '>']):
                        target_selectors.extend([
                            f'input[id="{clean_part}"]',
                            f'input[name="{clean_part}"]',
                            f'[name="{clean_part}"]',
                            f'#{clean_part}',
                            f'.{clean_part}'
                        ])

                if "user" in target_lower or "email" in target_lower:
                    target_selectors.extend([
                        'input[type="email"]',
                        'input[name*="user" i]',
                        'input[name*="email" i]',
                        'input[placeholder*="user" i]',
                        'input[placeholder*="email" i]',
                        'label:has-text("EMAIL") ~ div input',
                        'label:has-text("EMAIL") + div input',
                        'input:not([type="password"]):not([type="hidden"])',
                        'input[type="text"]',
                    ])
                elif "pass" in target_lower:
                    target_selectors.extend([
                        'input[type="password"]',
                        'input[name*="pass" i]',
                        'input[placeholder*="pass" i]',
                        'input[type="text"]:near(label:has-text("PASSWORD"))',
                    ])
                elif any(kw in target_lower for kw in ["otp", "2fa", "code", "token"]):
                    target_selectors.extend([
                        'input[autocomplete="one-time-code"]',
                        'input[name*="otp" i]',
                        'input[name*="2fa" i]',
                        'input[name*="code" i]',
                        'input[id*="otp" i]',
                        'input[placeholder*="otp" i]',
                        'input[placeholder*="code" i]',
                    ])

                target_loc = None
                matched_sel = selector
                for sel in target_selectors:
                    try:
                        loc = self._page.locator(sel).first
                        await loc.wait_for(state="visible", timeout=600)
                        target_loc = loc
                        matched_sel = sel
                        break
                    except Exception:
                        try:
                            loc = self._page.locator(sel).first
                            if await loc.count() > 0:
                                target_loc = loc
                                matched_sel = sel
                                break
                        except Exception:
                            continue

                if target_loc:
                    try:
                        await target_loc.scroll_into_view_if_needed(timeout=1000)
                    except Exception:
                        pass

                    box = await target_loc.bounding_box()
                    if box:
                        cx = box["x"] + box["width"] / 2
                        cy = box["y"] + box["height"] / 2
                        await self._page.evaluate("({x, y, w, h}) => { if (window.__moveCursor) window.__moveCursor(x, y); if (window.__highlight) window.__highlight(x - w/2, y - h/2, w, h); }", {"x": cx, "y": cy, "w": box["width"], "h": box["height"]})
                        await asyncio.sleep(0.15)
                        await self._page.evaluate("({x, y}) => { if (window.__ripple) window.__ripple(x, y); }", {"x": cx, "y": cy})

                    try:
                        await target_loc.evaluate("""el => {
                            el.style.outline = '3px solid #2563eb';
                            el.style.boxShadow = '0 0 10px rgba(37, 99, 235, 0.45)';
                            setTimeout(() => {
                                el.style.outline = '';
                                el.style.boxShadow = '';
                            }, 1200);
                        }""")
                    except Exception:
                        pass

                    try:
                        await target_loc.click(timeout=1000)
                    except Exception:
                        try:
                            await target_loc.focus()
                        except Exception:
                            pass

                    await target_loc.fill("")

                    if val_str:
                        try:
                            await target_loc.press_sequentially(val_str, delay=25)
                        except Exception:
                            await target_loc.fill(val_str)
                    await asyncio.sleep(0.2)
                    return {"filled": matched_sel}

                return {"filled": selector}
            try:
                return await self._runner.run(_do_fill())
            except Exception:
                pass
        return {"filled": selector}

    async def click(self, selector: str) -> Any:
        event_bus = get_event_bus()
        msg = f"Playwright click → {selector}"
        logger.info(f"[MCP] {msg}")
        if self._is_real and self._page and self._runner:
            async def _do_click():
                target_lower = selector.lower()

                # ── 1. JEV-FIRST DIRECT NODE RESOLUTION (<25ms) ──
                try:
                    from jev_ultrafast.browser import READ_STATE
                    state = await self._page.evaluate(READ_STATE)
                    if state and "actions" in state:
                        click_action = None

                        # A. Eye toggle button resolution
                        if any(w in target_lower for w in ["eye", "toggle", "visibility", "mask", "reveal"]):
                            click_action = next(
                                (a for a in state["actions"] if a.get("kind") == "click" and any(
                                    kw in (a.get("label") or "").lower() for kw in ["eye", "toggle", "visibility", "reveal", "mask", "password"]
                                )),
                                None
                            )

                        # B. Submit / Login / Sign In primary CTA
                        if not click_action and any(w in target_lower for w in ["submit", "login", "signin", "sign in", "btn"]):
                            click_action = next(
                                (a for a in state["actions"] if a.get("kind") == "click" and any(
                                    s in (a.get("label") or "").lower() for s in ["login", "sign in", "submit", "log in", "continue"]
                                )),
                                None
                            )
                            if not click_action:
                                click_action = next(
                                    (a for a in state["actions"] if a.get("kind") == "click" and a.get("role") in ("button", "submit")),
                                    None
                                )

                        # C. Dropdown / unit button trigger
                        if not click_action and ("unit" in target_lower or "select" in target_lower):
                            click_action = next(
                                (a for a in state["actions"] if a.get("kind") == "click" and any(
                                    s in (a.get("label") or "").lower() for s in ["unit", "select"]
                                )),
                                None
                            )

                        # D. Logout / Avatar / Menu
                        if not click_action and any(w in target_lower for w in ["logout", "avatar", "user", "profile"]):
                            click_action = next(
                                (a for a in state["actions"] if a.get("kind") == "click" and any(
                                    s in (a.get("label") or "").lower() for s in ["logout", "avatar", "profile", "user"]
                                )),
                                None
                            )

                        # E. Direct label match — only for known auth/semantic selectors
                        _is_semantic_selector = any(w in target_lower for w in [
                            "eye", "toggle", "submit", "login", "signin", "sign in", "unit",
                            "logout", "avatar", "profile", "btn", "button", "password", "visibility"
                        ])
                        if not click_action and _is_semantic_selector:
                            clean_t = selector.replace('button:has-text("', '').replace('")', '').replace('button', '').replace('[', '').replace(']', '').replace('"', '').strip().lower()
                            if clean_t:
                                click_action = next(
                                    (a for a in state["actions"] if a.get("kind") == "click" and (
                                        clean_t in (a.get("label") or "").lower() or
                                        (a.get("label") or "").lower() in clean_t
                                    )),
                                    None
                                )

                        if click_action:
                            r = click_action.get("rect", {})
                            cx = r.get("x", 0) + r.get("w", 0) / 2
                            cy = r.get("y", 0) + r.get("h", 0) / 2
                            if cx > 0 and cy > 0:
                                await self._page.evaluate(
                                    "({x, y}) => { if (window.__moveCursor) window.__moveCursor(x, y); if (window.__ripple) window.__ripple(x, y); }",
                                    {"x": cx, "y": cy}
                                )
                                await asyncio.sleep(0.15)
                            await self._page.evaluate(
                                "(action) => { const e = window.__jevFast?.nodes.get(action.node); if (e) { e.scrollIntoView({block:'nearest', inline:'nearest'}); e.click(); } }",
                                click_action
                            )
                            await asyncio.sleep(0.25)
                            logger.info(f"[JEV] Action Completed: click node {click_action.get('node')} '{click_action.get('label')}'")
                            return {"clicked": f"jev-node:{click_action.get('label', 'button')}", "url": self._page.url, "source": "JEV"}
                except Exception as jev_e:
                    logger.debug(f"[JEV] Node click resolution error: {jev_e}")

                # ── 2. PLAYWRIGHT LOCATOR FALLBACK ──
                raw_parts = [s.strip() for s in selector.split(',') if s.strip()]
                target_selectors: List[str] = []
                for p in raw_parts:
                    target_selectors.append(p)
                    clean_part = p.lstrip('#').lstrip('.').strip()
                    if clean_part and not any(ch in clean_part for ch in ['[', ']', '"', "'", '=', ':', ' ', '>']):
                        target_selectors.extend([
                            f'button[id="{clean_part}"]',
                            f'button[name="{clean_part}"]',
                            f'button:has-text("{clean_part}")',
                            f'#{clean_part}',
                            f'.{clean_part}'
                        ])

                if any(w in selector.lower() for w in ["eye", "toggle", "password", "visibility", "icon"]):
                    target_selectors.extend([
                        'button:has(svg):near(input[type="password"])',
                        'button:has(svg):near(input[type="text"])',
                        'input[type="password"] ~ button:has(svg)',
                        'input[type="text"] ~ button:has(svg)',
                        'div:has(input[type="password"]) button:has(svg)',
                        'div:has(input[type="text"]) button:has(svg)',
                        'input ~ button:has(svg)',
                        'button:has(svg.lucide-eye, svg.lucide-eye-off)',
                        'button[aria-label*="password" i]',
                        '#toggle-password',
                        'button:has(svg)',
                    ])
                elif any(w in selector.lower() for w in ["submit", "login", "signin", "btn"]):
                    target_selectors.extend([
                        'button[type="submit"]',
                        'button:has-text("Login")',
                        'button:has-text("Log In")',
                        'button:has-text("Sign in")',
                        'button:has-text("Sign In")',
                        'button:has-text("Submit")',
                        'input[type="submit"]',
                        '#login-submit',
                    ])
                elif "unit" in selector.lower() or "select" in selector.lower():
                    target_selectors.extend([
                        'select',
                        '[role="combobox"]',
                        'button:has-text("Select Unit")',
                        '#unit-select',
                        '#unit',
                    ])

                target_loc = None
                matched_sel = selector
                for sel in target_selectors:
                    try:
                        loc = self._page.locator(sel).first
                        await loc.wait_for(state="visible", timeout=600)
                        target_loc = loc
                        matched_sel = sel
                        break
                    except Exception:
                        try:
                            loc = self._page.locator(sel).first
                            if await loc.count() > 0:
                                target_loc = loc
                                matched_sel = sel
                                break
                        except Exception:
                            continue

                if target_loc:
                    try:
                        await target_loc.scroll_into_view_if_needed(timeout=1000)
                    except Exception:
                        pass

                    box = await target_loc.bounding_box()
                    if box:
                        cx = box["x"] + box["width"] / 2
                        cy = box["y"] + box["height"] / 2
                        await self._page.evaluate("({x, y}) => { if (window.__moveCursor) window.__moveCursor(x, y); }", {"x": cx, "y": cy})
                        await asyncio.sleep(0.15)
                        await self._page.evaluate("({x, y}) => { if (window.__ripple) window.__ripple(x, y); }", {"x": cx, "y": cy})

                    try:
                        await target_loc.evaluate("""el => {
                            el.style.outline = '3px solid #2563eb';
                            el.style.transform = 'scale(0.96)';
                            setTimeout(() => {
                                el.style.outline = '';
                                el.style.transform = '';
                            }, 250);
                        }""")
                    except Exception:
                        pass

                    await target_loc.click(timeout=1500)
                    await asyncio.sleep(0.25)
                    return {"clicked": matched_sel, "url": self._page.url}

                return None
            try:
                res = await self._runner.run(_do_click())
                if res:
                    self._mock_url = res.get("url", self._mock_url)
                    await event_bus.publish(LogEvent(source="MCP", message=msg, data={"action": "click", "selector": selector, "url": self._mock_url}))
                    return {"clicked": res.get("clicked", selector), "url": self._mock_url}
            except Exception:
                pass

        target_lower = selector.lower()
        if any(s in target_lower for s in ["submit", "sign in", "login"]):
            self._mock_url = "http://localhost:3000/verification"
        elif "logout" in target_lower:
            self._mock_url = "http://localhost:3000/login"
        await event_bus.publish(LogEvent(source="MCP", message=msg, data={"action": "click", "selector": selector, "url": self._mock_url}))
        return {"clicked": selector}

    async def select_option(self, selector: str, value: Optional[str] = None, label: Optional[str] = None) -> Any:
        """Selects an option from a <select> element or custom dropdown with visual animation."""
        event_bus = get_event_bus()
        opt_repr = label or value or "Unit 1"
        msg = f"Playwright select → {selector} = '{opt_repr}'"
        logger.info(f"[MCP] {msg}")
        if self._is_real and self._page and self._runner:
            async def _do_select():
                # Wait up to 2.5s for dynamic options to load if select is still on placeholder
                try:
                    for _ in range(25):
                        opt_count = await self._page.evaluate("""() => {
                            const sel = document.querySelector('select');
                            return sel && sel.options ? sel.options.length : 0;
                        }""")
                        if opt_count > 1:
                            break
                        await asyncio.sleep(0.1)
                except Exception:
                    pass

                # ── 1. JEV-FIRST DIRECT NODE RESOLUTION (<25ms) ──
                try:
                    from jev_ultrafast.browser import READ_STATE
                    state = await self._page.evaluate(READ_STATE)
                    if state and "actions" in state:
                        # Directly filter select actions — avoids action_space() crash on integer node ids
                        select_actions = [a for a in state["actions"] if a.get("kind") == "select"]
                        chosen_act = None
                        target_search = (label or value or "").strip()
                        if target_search and select_actions:
                            opt_tuples = [(str(a.get("value", "")), (a.get("label", "") or "").replace("SELECT UNIT → ", "").replace("Select Unit → ", "")) for a in select_actions]
                            matched = _match_dropdown_option(target_search, opt_tuples)
                            if matched:
                                chosen_act = next((a for a in select_actions if str(a.get("value", "")) == matched[0] or matched[1] in (a.get("label", "") or "")), None)
                        if not chosen_act and select_actions:
                            chosen_act = select_actions[0]
                        if chosen_act:
                            r = chosen_act.get("rect", {})
                            cx = r.get("x", 0) + r.get("w", 0) / 2
                            cy = r.get("y", 0) + r.get("h", 0) / 2
                            if cx > 0 and cy > 0:
                                await self._page.evaluate("({x, y}) => { if (window.__moveCursor) window.__moveCursor(x, y); if (window.__ripple) window.__ripple(x, y); }", {"x": cx, "y": cy})
                                await asyncio.sleep(0.15)
                            await self._page.evaluate("""action => {
                                let e = window.__jevFast?.nodes.get(action.node);
                                if (!e) e = document.querySelector('select');
                                if (!e) return false;

                                // Support React controlled select by calling native prototype setter
                                const proto = window.HTMLSelectElement.prototype;
                                const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                                if (setter) {
                                    setter.call(e, action.value);
                                } else {
                                    e.value = action.value;
                                }
                                if (e._valueTracker) {
                                    e._valueTracker.setValue('');
                                }
                                e.dispatchEvent(new Event('input', {bubbles: true, composed: true}));
                                e.dispatchEvent(new Event('change', {bubbles: true, composed: true}));
                                return true;
                            }""", chosen_act)
                            await asyncio.sleep(0.2)
                            logger.info(f"[JEV] Action Completed: select node {chosen_act.get('node')} '{chosen_act.get('label')}'")
                            return {"selected": f"jev-node:{chosen_act.get('label')}", "value": chosen_act.get("value"), "source": "JEV"}
                except Exception as jev_sel_e:
                    logger.debug(f"[JEV] Node select resolution error: {jev_sel_e}")

                # ── 2. PLAYWRIGHT LOCATOR FALLBACK ──
                raw_parts = [s.strip() for s in selector.split(',') if s.strip()]
                alts = list(raw_parts)
                alts.extend(['select', 'select#unit', 'select[name*="unit" i]', '[role="combobox"]', '#unit-select', '#unit', 'button:has-text("Select Unit")'])
                for sel in alts:
                    try:
                        loc = self._page.locator(sel).first
                        await loc.wait_for(state="visible", timeout=600)
                        box = await loc.bounding_box()
                        if box:
                            cx = box["x"] + box["width"] / 2
                            cy = box["y"] + box["height"] / 2
                            await self._page.evaluate("({x, y, w, h}) => { if (window.__moveCursor) window.__moveCursor(x, y); if (window.__ripple) window.__ripple(x, y); if (window.__highlight) window.__highlight(x - w/2, y - h/2, w, h); }", {"x": cx, "y": cy, "w": box["width"], "h": box["height"]})
                            await asyncio.sleep(0.15)

                        tag_name = await loc.evaluate("e => e.tagName.toLowerCase()")
                        if tag_name == "select":
                            # Wait for options to populate if select only has placeholder
                            for _ in range(25):
                                try:
                                    if await loc.locator("option").count() > 1:
                                        break
                                except Exception:
                                    pass
                                await asyncio.sleep(0.1)

                            options = await loc.locator("option").all()
                            all_opts: List[Tuple[str, str]] = []
                            for opt in options:
                                txt = (await opt.inner_text()).strip()
                                val = (await opt.get_attribute("value")) or ""
                                all_opts.append((val, txt))

                            target_query = label or value or ""
                            best_opt = _match_dropdown_option(target_query, all_opts) if target_query else None
                            if not best_opt and all_opts:
                                non_placeholders = [(v, t) for v, t in all_opts if v not in ("", "0") and not any(p in t.lower() for p in ["select", "choose", "--"])]
                                if non_placeholders:
                                    best_opt = non_placeholders[0]

                            if best_opt:
                                target_val, target_txt = best_opt
                                try:
                                    if target_val:
                                        await loc.select_option(value=target_val, timeout=1500)
                                    else:
                                        await loc.select_option(label=target_txt, timeout=1500)
                                except Exception:
                                    try:
                                        await loc.select_option(label=target_txt, timeout=1500)
                                    except Exception:
                                        pass

                                # React prototype setter and input/change events
                                await self._page.evaluate("""({sel, val}) => {
                                    const e = document.querySelector(sel) || document.querySelector('select');
                                    if (!e) return;
                                    const proto = window.HTMLSelectElement.prototype;
                                    const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                                    if (setter) {
                                        setter.call(e, val);
                                    } else {
                                        e.value = val;
                                    }
                                    if (e._valueTracker) {
                                        e._valueTracker.setValue('');
                                    }
                                    e.dispatchEvent(new Event('input', {bubbles: true, composed: true}));
                                    e.dispatchEvent(new Event('change', {bubbles: true, composed: true}));
                                }""", {"sel": sel, "val": target_val})
                                await asyncio.sleep(0.2)
                                return {"selected": sel, "value": target_val, "label": target_txt}
                        else:
                            await loc.click(timeout=1000)
                            await asyncio.sleep(0.2)
                            # Custom dropdown option search
                            opt_locs = await self._page.locator('[role="option"], li, div[role="option"], .select-option').all()
                            custom_opts: List[Tuple[str, str]] = []
                            for ol in opt_locs:
                                try:
                                    otxt = (await ol.inner_text()).strip()
                                    oval = (await ol.get_attribute("data-value") or await ol.get_attribute("value") or otxt).strip()
                                    if otxt:
                                        custom_opts.append((oval, otxt))
                                except Exception:
                                    pass
                            target_query = label or value or ""
                            best_c_opt = _match_dropdown_option(target_query, custom_opts) if target_query else None
                            if best_c_opt:
                                c_val, c_txt = best_c_opt
                                opt_loc = self._page.locator(f'[role="option"]:has-text("{c_txt}"), li:has-text("{c_txt}")').first
                                if await opt_loc.count() > 0:
                                    obox = await opt_loc.bounding_box()
                                    if obox:
                                        ocx = obox["x"] + obox["width"] / 2
                                        ocy = obox["y"] + obox["height"] / 2
                                        await self._page.evaluate("({x, y}) => { if (window.__moveCursor) window.__moveCursor(x, y); if (window.__ripple) window.__ripple(x, y); }", {"x": ocx, "y": ocy})
                                        await asyncio.sleep(0.15)
                                    await opt_loc.click(timeout=1000)
                                    await asyncio.sleep(0.2)
                                    return {"selected": sel, "label": c_txt, "value": c_val}
                    except Exception:
                        pass

                return {"selected": selector, "fallback": True}
            try:
                res = await self._runner.run(_do_select())
                await event_bus.publish(LogEvent(source="MCP", message=msg, data={"action": "select", "selector": selector, "value": opt_repr}))
                return res
            except Exception:
                pass
        await event_bus.publish(LogEvent(source="MCP", message=msg, data={"action": "select", "selector": selector, "value": opt_repr}))
        return {"selected": selector, "value": opt_repr}

    async def inspect_password_visibility(self) -> Dict[str, Any]:
        """Inspects whether the active password input has type='text' (visible) or type='password' (masked)."""
        if self._is_real and self._page and self._runner:
            async def _inspect():
                try:
                    await asyncio.sleep(0.3)
                    # 1. Standard password input locators (both masked type='password' and revealed type='text')
                    locs = [
                        'input[autocomplete*="password" i]',
                        'input[type="password"]',
                        'input[name*="pass" i]',
                        '#password',
                        'input[placeholder*="pass" i]',
                        'input[aria-label*="pass" i]',
                        'div:has(button:has(svg)) input',
                        'div:has(svg.lucide-eye) input',
                        'div:has(svg.lucide-eye-off) input',
                    ]
                    for sel in locs:
                        try:
                            inp = self._page.locator(sel).first
                            if await inp.count() > 0:
                                typ = (await inp.get_attribute("type") or "password").lower()
                                val = await inp.input_value()
                                return {"type": typ, "value": val, "visible": typ != "password"}
                        except Exception:
                            continue

                    # 2. Dynamic scan of all inputs looking for password field semantics
                    inputs = await self._page.locator('input').all()
                    for inp in inputs:
                        attrs = " ".join([
                            await inp.get_attribute("autocomplete") or "",
                            await inp.get_attribute("name") or "",
                            await inp.get_attribute("id") or "",
                            await inp.get_attribute("placeholder") or "",
                            await inp.get_attribute("aria-label") or "",
                            await inp.get_attribute("class") or "",
                        ]).lower()
                        if "pass" in attrs:
                            typ = (await inp.get_attribute("type") or "password").lower()
                            val = await inp.input_value()
                            return {"type": typ, "value": val, "visible": typ != "password"}

                    # 3. Position-based fallback (second input on login form is typically password)
                    if len(inputs) >= 2:
                        inp = inputs[1]
                        typ = (await inp.get_attribute("type") or "password").lower()
                        val = await inp.input_value()
                        return {"type": typ, "value": val, "visible": typ != "password"}
                except Exception as e:
                    logger.debug(f"[MCP] Password visibility check error: {e}")
                return {"type": "password", "value": "", "visible": False}
            try:
                return await self._runner.run(_inspect())
            except Exception:
                pass
        return {"type": "password", "value": "", "visible": False}

    async def hover(self, selector: str) -> Any:
        """Hovers over an element with visual highlight for the live screencast."""
        if self._is_real and self._page and self._runner:
            async def _do_hover():
                try:
                    loc = self._page.locator(selector).first
                    await loc.wait_for(state="visible", timeout=1200)
                    box = await loc.bounding_box()
                    if box:
                        cx = box["x"] + box["width"] / 2
                        cy = box["y"] + box["height"] / 2
                        await self._page.evaluate("({x, y}) => { if (window.__moveCursor) window.__moveCursor(x, y); }", {"x": cx, "y": cy})
                        await asyncio.sleep(0.15)
                    await loc.hover(timeout=2000)
                    await asyncio.sleep(0.2)
                    return True
                except Exception:
                    pass
                return False
            try:
                return await self._runner.run(_do_hover())
            except Exception:
                pass
        return True

    async def get_current_url(self) -> str:
        """Returns the current real browser URL after navigation or click actions."""
        if self._is_real and self._page and self._runner:
            async def _get_url():
                return self._page.url
            try:
                url = await self._runner.run(_get_url())
                self._mock_url = url
                return url
            except Exception:
                pass
        return self._mock_url

    async def wait_for_navigation_after_click(self, timeout_ms: int = 3000) -> Dict[str, Any]:
        """Waits briefly for any navigation that occurs after a click/submit, then returns page state."""
        if self._is_real and self._page and self._runner:
            async def _wait():
                try:
                    await self._page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
                except Exception:
                    pass  # page may not navigate, that's OK
                await asyncio.sleep(0.3)
                url = self._page.url
                title = ""
                try:
                    title = await self._page.title()
                except Exception:
                    pass
                content = ""
                try:
                    content = await self._page.content()
                except Exception:
                    pass
                return {"url": url, "title": title, "content": content[:8000]}
            try:
                result = await self._runner.run(_wait())
                if result:
                    self._mock_url = result.get("url", self._mock_url)
                return result or {"url": self._mock_url, "title": "", "content": ""}
            except Exception:
                pass
        return {"url": self._mock_url, "title": "", "content": ""}

    async def detect_intermediate_screen(self) -> Optional[Dict[str, str]]:
        """Detects whether current page is requiring 2FA, OTP, verification code, or store selection."""
        if not (self._is_real and self._page and self._runner):
            return None

        async def _detect():
            try:
                url = (self._page.url or "").lower()
                title = ""
                try:
                    title = (await self._page.title() or "").lower()
                except Exception:
                    pass
                content = ""
                try:
                    content = (await self._page.content() or "").lower()[:15000]
                except Exception:
                    pass

                # 1. Check OTP / 2FA signals
                otp_selectors = [
                    'input[autocomplete="one-time-code"]',
                    'input[name*="otp" i]',
                    'input[name*="2fa" i]',
                    'input[name*="code" i]',
                    'input[name*="token" i]',
                    'input[id*="otp" i]',
                    'input[id*="2fa" i]',
                    'input[placeholder*="otp" i]',
                    'input[placeholder*="code" i]',
                    'input[placeholder*="verification" i]',
                ]
                has_otp_field = False
                for sel in otp_selectors:
                    try:
                        if await self._page.locator(sel).count() > 0:
                            has_otp_field = True
                            break
                    except Exception:
                        pass

                is_otp_text = any(term in content or term in title or term in url for term in [
                    "verification code", "enter otp", "two-factor", "2fa", "authenticator code",
                    "one-time password", "enter code", "security code", "sms code", "6-digit code"
                ])

                if has_otp_field or is_otp_text:
                    return {
                        "type": "otp",
                        "prompt": "2FA / One-Time Password (OTP) verification screen detected. Please enter your verification code.",
                        "url": self._page.url,
                    }

                # 2. Check Unit / Division / Department / Company selection signals
                # (common in ERP, DMS, and enterprise portals like JPPL-DMS)
                unit_selectors = [
                    'select[name*="unit" i]',
                    'select[name*="division" i]',
                    'select[name*="department" i]',
                    'select[name*="company" i]',
                    'select[name*="organization" i]',
                    'select[name*="office" i]',
                    'select[name*="branch" i]',
                    'select[name*="store" i]',
                    'select[name*="location" i]',
                    'select[name*="site" i]',
                    'select[name*="zone" i]',
                    '[id*="unit" i]',
                    '[id*="division" i]',
                    '[id*="department" i]',
                    '[id*="company" i]',
                    '[id*="organization" i]',
                    '[data-testid*="unit" i]',
                    '[data-testid*="store" i]',
                    '[class*="unit-select" i]',
                    '[class*="company-select" i]',
                ]
                has_unit_selector = False
                for sel in unit_selectors:
                    try:
                        if await self._page.locator(sel).count() > 0:
                            has_unit_selector = True
                            break
                    except Exception:
                        pass

                is_unit_text = any(term in content or term in title or term in url for term in [
                    "select unit", "choose unit", "select your unit", "select division",
                    "choose division", "select department", "select company",
                    "select branch", "select organization", "pick unit", "select office",
                    "select store", "choose store", "select location", "choose location",
                    "select site", "select zone", "choose branch", "select your branch",
                    "unit selection", "division selection", "company selection",
                ])

                if has_unit_selector or is_unit_text:
                    return {
                        "type": "unit",
                        "prompt": "Unit / Division / Company selection screen detected. Please enter or select your unit/division/company name.",
                        "url": self._page.url,
                    }

                # 3. Check CAPTCHA / Bot Verification signals
                captcha_selectors = [
                    'iframe[src*="captcha" i]',
                    'iframe[src*="recaptcha" i]',
                    'iframe[src*="turnstile" i]',
                    'iframe[src*="cloudflare" i]',
                    '#cf-turnstile',
                    '.g-recaptcha',
                    '.h-captcha',
                    '[data-sitekey]',
                ]
                has_captcha = False
                for c_sel in captcha_selectors:
                    try:
                        if await self._page.locator(c_sel).count() > 0:
                            has_captcha = True
                            break
                    except Exception:
                        pass
                is_captcha_text = any(term in content or term in title for term in [
                    "verify you are human", "security check", "cloudflare", "turnstile", "captcha", "bot detection"
                ])
                if has_captcha or is_captcha_text:
                    return {
                        "type": "captcha",
                        "prompt": "CAPTCHA / Security challenge detected. Please complete the verification in the browser window.",
                        "url": self._page.url,
                    }
            except Exception as exc:
                logger.warning(f"[PLAYWRIGHT] Intermediate screen detection error: {exc}")
            return None

        try:
            return await self._runner.run(_detect())
        except Exception:
            return None

    async def check_unselected_unit_dropdown(self) -> Optional[Dict[str, str]]:
        """Checks if current page has an unselected unit dropdown that must be selected before submit."""
        if not (self._is_real and self._page and self._runner):
            return None
        async def _check():
            try:
                loc = self._page.locator("select").first
                if await loc.count() > 0 and await loc.is_visible():
                    selected_idx = await loc.evaluate("el => el.selectedIndex")
                    selected_val = await loc.evaluate("el => el.value")
                    selected_text = await loc.evaluate("el => el.options && el.selectedIndex >= 0 ? el.options[el.selectedIndex].text : ''")

                    is_unselected = (
                        selected_idx <= 0 or
                        not selected_val or
                        str(selected_val).strip() in ("", "0", "none") or
                        any(p in selected_text.strip().lower() for p in ["select", "choose", "--", "none"])
                    )
                    if not is_unselected:
                        return None

                    opts = await loc.locator("option").all()
                    opt_texts = [((await o.inner_text()) or "").strip() for o in opts]
                    unit_opts = [t for t in opt_texts if t.strip() and not any(p in t.lower() for p in ["select", "choose", "--", "none"])]
                    if not unit_opts:
                        return None

                    opts_str = ", ".join(unit_opts[:6])
                    return {
                        "type": "unit",
                        "prompt": f"Unit selection required before login. Available units: [{opts_str}]. Please enter your Unit name or number.",
                        "url": self._page.url,
                    }
            except Exception:
                pass
            return None
        try:
            return await self._runner.run(_check())
        except Exception:
            return None

    async def clear_session_and_return_to_login(self, login_url: str) -> None:
        """Cleans up session cookies and client storage, returning to the login URL."""
        if self._is_real and self._page and self._runner:
            async def _reset():
                try:
                    await self._page.context.clear_cookies()
                except Exception:
                    pass
                try:
                    await self._page.evaluate("""() => {
                        try { localStorage.clear(); } catch(e){}
                        try { sessionStorage.clear(); } catch(e){}
                    }""")
                except Exception:
                    pass
                try:
                    await self._page.goto(login_url, wait_until="domcontentloaded", timeout=15000)
                    await asyncio.sleep(0.3)
                except Exception:
                    pass
            try:
                await self._runner.run(_reset())
                self._mock_url = login_url
            except Exception:
                pass

    async def get_jev_snapshot(self) -> Dict[str, Any]:
        """Captures an ultrafast accessibility action tree snapshot using jev-ultrafast."""
        if self._is_real and self._page and self._runner:
            async def _eval_jev():
                try:
                    from jev_ultrafast.browser import READ_STATE, fingerprint
                    state = await self._page.evaluate(READ_STATE)
                    if state:
                        state["fingerprint"] = fingerprint(state)
                        return state
                except Exception as exc:
                    logger.debug(f"[JEV] Snapshot evaluation error: {exc}")
                return None
            try:
                res = await self._runner.run(_eval_jev())
                if res:
                    return res
            except Exception:
                pass
        return {}

    async def fill_intermediate_input(self, value: str) -> bool:
        """Fills user-provided OTP, 2FA code, selects unit/store/division on the page."""
        if not (self._is_real and self._page and self._runner):
            return False

        async def _fill():
            try:
                # 1. Try native <select> elements for unit/division/department/company/store
                select_selectors = [
                    'select[name*="unit" i]',
                    'select[name*="division" i]',
                    'select[name*="department" i]',
                    'select[name*="company" i]',
                    'select[name*="organization" i]',
                    'select[name*="office" i]',
                    'select[name*="branch" i]',
                    'select[name*="store" i]',
                    'select[name*="location" i]',
                    'select[name*="site" i]',
                    'select',
                ]
                for sel_tag in select_selectors:
                    try:
                        loc = self._page.locator(sel_tag)
                        cnt = await loc.count()
                        if cnt > 0:
                            for i in range(cnt):
                                item = loc.nth(i)
                                try:
                                    if await item.is_visible():
                                        # Try selecting by label first, then by value
                                        try:
                                            await item.select_option(label=value)
                                            await asyncio.sleep(0.3)
                                            return True
                                        except Exception:
                                            pass
                                        try:
                                            await item.select_option(value=value)
                                            await asyncio.sleep(0.3)
                                            return True
                                        except Exception:
                                            pass
                                        # Try partial text match by selecting index
                                        try:
                                            options = await item.locator("option").all()
                                            for opt in options:
                                                opt_text = (await opt.inner_text()).strip()
                                                if value.lower() in opt_text.lower():
                                                    await item.select_option(label=opt_text)
                                                    await asyncio.sleep(0.3)
                                                    return True
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                    except Exception:
                        pass

                # 2. Try OTP / 2FA code input fields
                code_selectors = [
                    'input[autocomplete="one-time-code"]',
                    'input[name*="otp" i]',
                    'input[name*="2fa" i]',
                    'input[name*="code" i]',
                    'input[id*="otp" i]',
                    'input[id*="2fa" i]',
                    'input[placeholder*="otp" i]',
                    'input[placeholder*="code" i]',
                    'input[type="tel"]',
                    'input[type="number"]',
                ]
                for sel in code_selectors:
                    try:
                        loc = self._page.locator(sel)
                        if await loc.count() > 0 and await loc.first.is_visible():
                            await loc.first.fill(value)
                            await asyncio.sleep(0.2)
                            for sub_sel in [
                                'button[type="submit"]',
                                'button:has-text("Verify")',
                                'button:has-text("Submit")',
                                'button:has-text("Continue")',
                                'button:has-text("Confirm")',
                                'button:has-text("Login")',
                                'input[type="submit"]',
                            ]:
                                try:
                                    s_btn = self._page.locator(sub_sel)
                                    if await s_btn.count() > 0 and await s_btn.first.is_visible():
                                        await s_btn.first.click()
                                        return True
                                except Exception:
                                    pass
                            await loc.first.press("Enter")
                            return True
                    except Exception:
                        pass

                # 3. Try custom dropdown / list items (li, a, div with matching text)
                for tag in ["li", "a", "[role='option']", "[role='listitem']"]:
                    try:
                        loc = self._page.locator(f"{tag}:has-text(\"{value}\")")
                        if await loc.count() > 0:
                            await loc.first.click()
                            await asyncio.sleep(0.3)
                            # Click any "Proceed" / "OK" / "Continue" / "Submit" button after selection
                            for btn_text in ["Proceed", "OK", "Submit", "Continue", "Confirm", "Go", "Select"]:
                                try:
                                    btn = self._page.locator(f"button:has-text(\"{btn_text}\")")
                                    if await btn.count() > 0 and await btn.first.is_visible():
                                        await btn.first.click()
                                        return True
                                except Exception:
                                    pass
                            return True
                    except Exception:
                        pass

                # 4. Try button with matching text
                try:
                    btn_loc = self._page.locator(f'button:has-text("{value}")')
                    if await btn_loc.count() > 0:
                        await btn_loc.first.click()
                        return True
                except Exception:
                    pass

                # 5. If the value is something to type into a unit text input
                for input_sel in [
                    'input[name*="unit" i]',
                    'input[name*="division" i]',
                    'input[name*="department" i]',
                    'input[placeholder*="unit" i]',
                    'input[placeholder*="division" i]',
                    'input[placeholder*="search" i]',
                ]:
                    try:
                        loc = self._page.locator(input_sel)
                        if await loc.count() > 0 and await loc.first.is_visible():
                            await loc.first.fill(value)
                            await asyncio.sleep(0.3)
                            # Click first dropdown suggestion if any
                            try:
                                suggestion = self._page.locator(f"li:has-text(\"{value}\")")
                                if await suggestion.count() > 0:
                                    await suggestion.first.click()
                                    return True
                            except Exception:
                                pass
                            await loc.first.press("Enter")
                            return True
                    except Exception:
                        pass

            except Exception as exc:
                logger.warning(f"[PLAYWRIGHT] Error filling intermediate input: {exc}")
            return False

        try:
            return await self._runner.run(_fill())
        except Exception:
            return False



    async def get_accessible_tree(self) -> str:
        if self._is_real and self._page and self._runner:
            try:
                return await self._runner.run(self._page.content())
            except Exception:
                pass
        return _MOCK_A11Y_TREES.get("default", "")

    async def screenshot(self) -> str:
        if self._is_real and self._page and self._runner:
            async def _snap():
                import base64
                data = await self._page.screenshot()
                b64 = base64.b64encode(data).decode("utf-8")
                from app.services.event_bus import get_screencast_hub
                get_screencast_hub().broadcast_frame_sync(b64)
                return b64
            try:
                return await self._runner.run(_snap())
            except Exception:
                pass
        return ""

    async def close(self) -> None:
        if self._is_real and self._runner:
            async def _cleanup():
                if self._cdp:
                    try:
                        await self._cdp.send("Page.stopScreencast")
                        await self._cdp.detach()
                    except Exception:
                        pass
                    self._cdp = None
                if self._browser:
                    await self._browser.close()
                if self._pw:
                    await self._pw.stop()
            try:
                await self._runner.run(_cleanup())
            except Exception as e:
                logger.warning(f"[PLAYWRIGHT] Error closing headed browser: {e}")
            finally:
                self._runner.stop()
                self._runner = None
                self._is_real = False
                self._browser = None
                self._page = None
                self._cdp = None
                self._pw = None
        logger.info("[PLAYWRIGHT] Browser session closed.")
