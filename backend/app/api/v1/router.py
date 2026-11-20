"""
momus404 — app.api.v1.router
Consolidates all v1 REST routes and WebSocket routes.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    health,
    judge,
    playground,
    runs,
    specs,
    telemetry,
    websocket,
)

api_router = APIRouter()

# API prefix routes
api_router.include_router(auth.router)
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(telemetry.router, tags=["Telemetry"])
api_router.include_router(specs.router, tags=["Specs"])
api_router.include_router(runs.router, tags=["Runs"])
api_router.include_router(judge.router, tags=["Judge"])
api_router.include_router(websocket.router, tags=["WebSocket"])
api_router.include_router(playground.router)
