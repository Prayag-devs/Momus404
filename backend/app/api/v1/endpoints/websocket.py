"""
momus404 — app.api.v1.endpoints.websocket
Real-time WebSocket event streaming endpoint.
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logging import get_logger
from app.services.event_bus import get_event_bus

logger = get_logger("websocket")
router = APIRouter()


@router.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket) -> None:
    """Streams live execution logs, verdicts, and telemetry events."""
    bus = get_event_bus()
    await websocket.accept()
    await bus.subscribe(websocket)

    try:
        # Buffer replay on initial connect
        for event in bus.get_recent(limit=100):
            await websocket.send_text(event.model_dump_json())

        # Heartbeat loop
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if msg == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "heartbeat"}))
    except (WebSocketDisconnect, ConnectionResetError):
        pass
    except Exception as exc:
        logger.debug(f"[WS] WebSocket logs connection terminated: {exc}")
    finally:
        await bus.unsubscribe(websocket)


from app.services.event_bus import get_screencast_hub

@router.websocket("/ws/screencast")
@router.websocket("/ws/screencast/{run_id}")
async def websocket_screencast_endpoint(websocket: WebSocket, run_id: str = "") -> None:
    """Streams real-time CDP browser screencast frames (JPEG) to frontend canvas."""
    hub = get_screencast_hub()
    await websocket.accept()
    await hub.subscribe(websocket, run_id=run_id or None)

    try:
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if msg == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                pass
    except (WebSocketDisconnect, ConnectionResetError):
        pass
    except Exception as exc:
        logger.debug(f"[WS] Screencast WebSocket connection terminated: {exc}")
    finally:
        await hub.unsubscribe(websocket, run_id=run_id or None)

