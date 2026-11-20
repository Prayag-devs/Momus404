"""
momus404 — backend/opendots_vault.py (Backward Compatibility Facade)
Re-exports from app.services.vault_service and app.core.security.
"""

from app.core.security import redact, mask_email
from app.services.vault_service import OpenDotsVault, get_vault

# Module-level singleton
vault = get_vault()

__all__ = ["OpenDotsVault", "vault", "redact", "mask_email"]
