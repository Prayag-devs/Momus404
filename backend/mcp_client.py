"""
momus404 — backend/mcp_client.py (Backward Compatibility Facade)
Re-exports from app.services.mcp_service.
"""

from app.services.mcp_service import PlaywrightMCPClient

__all__ = ["PlaywrightMCPClient"]
