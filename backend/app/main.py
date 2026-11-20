"""
momus404 — app.main
FastAPI Application Factory with modern lifespan management, CORS,
exception handling, and OpenAPI documentation.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints import websocket
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import MomusBaseException
from app.core.logging import get_logger, setup_logging

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for startup and shutdown hooks."""
    settings = get_settings()
    setup_logging()
    settings.ensure_directories()

    logger.info("=" * 60)
    logger.info(f"  {settings.PROJECT_NAME} v{settings.VERSION} — PRODUCTION ENGINE STARTED")
    logger.info(
        f"  MOCK_LLM={settings.MOCK_LLM}  MOCK_MCP={settings.MOCK_MCP}  "
        f"MOCK_LAYA={settings.MOCK_LAYA}  MOCK_VAULT={settings.MOCK_VAULT}"
    )
    logger.info("=" * 60)

    yield

    logger.info(f"  {settings.PROJECT_NAME} — Engine shutting down.")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global Domain Exception Handler
    @app.exception_handler(MomusBaseException)
    async def momus_exception_handler(request: Request, exc: MomusBaseException):
        logger.error(f"[DOMAIN ERROR] {exc.message}: {exc.detail}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": exc.message, "detail": exc.detail},
        )

    # Include API Routers under /api
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Also include root-level /ws/logs so direct ws://host:8000/ws/logs works seamlessly
    app.include_router(websocket.router)

    return app
