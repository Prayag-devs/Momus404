"""
momus404 — app package
"""

from app.main import create_app

# Default application instance for `from app import app` and uvicorn
app = create_app()

__all__ = ["create_app", "app"]
