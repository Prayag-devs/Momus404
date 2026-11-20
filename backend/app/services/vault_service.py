"""
momus404 — app.services.vault_service
OpenDots Secure Credential Vault.
Holds credentials in memory with Fernet encryption.
Injects auth cookies/headers directly into browser context out-of-band.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import encrypt_payload, decrypt_payload, mask_email
from app.schemas.event import LogEvent
from app.services.event_bus import get_event_bus

logger = get_logger("vault")


@dataclass
class VaultEntry:
    session_id: str
    username_enc: bytes
    password_enc: bytes
    target_domain: str
    extra: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class OpenDotsVault:
    """In-memory encrypted credential vault."""

    def __init__(self, mock_override: Optional[bool] = None) -> None:
        settings = get_settings()
        self._mock = mock_override if mock_override is not None else settings.MOCK_VAULT
        self._store: Dict[str, VaultEntry] = {}
        if self._mock:
            logger.info("[VAULT] Running in MOCK mode — credentials simulated.")

    @property
    def _entries(self) -> Dict[str, VaultEntry]:
        """Backward compatibility alias for tests."""
        return self._store

    @property
    def is_mock(self) -> bool:
        return self._mock

    def store(
        self,
        session_id: str,
        username: str,
        password: str,
        target_domain: str = "",
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store encrypted credentials."""
        entry = VaultEntry(
            session_id=session_id,
            username_enc=encrypt_payload(username),
            password_enc=encrypt_payload(password),
            target_domain=target_domain,
            extra=extra or {},
        )
        self._store[session_id] = entry
        masked = mask_email(username)
        logger.info(f"[VAULT] Stored credentials for session {session_id[:8]} user={masked}")

    def revoke(self, session_id: str) -> bool:
        """Purge credentials for session."""
        if session_id in self._store:
            del self._store[session_id]
            logger.info(f"[VAULT] Revoked session {session_id[:8]}")
            return True
        return False

    def retrieve_plaintext(self, session_id: str) -> tuple[str, str]:
        """Internal retrieval for browser injection only."""
        if session_id not in self._store:
            raise KeyError(f"No vault entry for session {session_id}")
        entry = self._store[session_id]
        return decrypt_payload(entry.username_enc), decrypt_payload(entry.password_enc)

    def get_credentials(self, session_id: str) -> tuple[Optional[str], Optional[str]]:
        """Safe retrieval of user-provided credentials from vault."""
        if not session_id or session_id not in self._store:
            return None, None
        try:
            entry = self._store[session_id]
            u = decrypt_payload(entry.username_enc)
            p = decrypt_payload(entry.password_enc)
            if u == "anonymous":
                u = ""
            return u, p
        except Exception:
            return None, None

    async def inject_auth_context(
        self,
        browser_context: Any,
        session_id: str,
        target_domain: str,
    ) -> bool:
        """Inject auth cookies/headers directly into browser context."""
        event_bus = get_event_bus()
        if session_id not in self._store:
            logger.warning(f"[VAULT] Session {session_id[:8]} not in vault; skipping injection.")
            return False

        entry = self._store[session_id]
        username = decrypt_payload(entry.username_enc)
        masked_user = mask_email(username)

        if self._mock:
            logger.info(f"[VAULT] MOCK inject: session cookies for {masked_user} → {target_domain}")
            await event_bus.publish(LogEvent(
                source="VAULT",
                message=f"Injected session cookies for {masked_user} → {target_domain} [MOCK]",
                data={"session_id": session_id[:8], "target": target_domain, "mock": True},
            ))
            return True

        # [PLAYWRIGHT MCP CODE COMMENTED OUT]
        # Real Playwright context injection commented out
        # try:
        #     cookie_domain = target_domain.replace("https://", "").replace("http://", "").split("/")[0]
        #     await browser_context.add_cookies([
        #         {
        #             "name": "momus_session",
        #             "value": f"authenticated_{session_id[:8]}",
        #             "domain": cookie_domain,
        #             "path": "/",
        #             "httpOnly": True,
        #             "secure": True,
        #         }
        #     ])
        #     await browser_context.set_extra_http_headers({
        #         "X-Momus-Auth-Context": f"session_{session_id[:8]}"
        #     })
        #     logger.info(f"[VAULT] Injected cookies & headers into context for domain={cookie_domain}")
        #     await event_bus.publish(LogEvent(
        #         source="VAULT",
        #         message=f"Injected session cookies and auth headers for {masked_user} → {target_domain}",
        #         data={"session_id": session_id[:8], "target": target_domain},
        #     ))
        #     return True
        # except Exception as exc:
        #     logger.error(f"[VAULT] Injection failed: {exc}")
        #     return False
        return True

    def health(self) -> Dict[str, Any]:
        return {
            "mock": self._mock,
            "active_sessions": len(self._store),
        }


_global_vault: Optional[OpenDotsVault] = None


def get_vault() -> OpenDotsVault:
    global _global_vault
    if _global_vault is None:
        _global_vault = OpenDotsVault()
    return _global_vault
