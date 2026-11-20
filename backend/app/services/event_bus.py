"""
momus404 — app.services.event_bus
In-process asynchronous pub/sub event bus with ring-buffer history.
"""

from __future__ import annotations

import asyncio
from collections import deque
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from app.schemas.event import LogEvent

if TYPE_CHECKING:
    from fastapi import WebSocket

RING_BUFFER_CAPACITY = 1000


class EventBus:
    """Central async pub/sub bus for event broadcasting and buffering."""

    def __init__(self, capacity: int = RING_BUFFER_CAPACITY) -> None:
        self._capacity = capacity
        self._run_buffers: Dict[str, deque[LogEvent]] = {}
        self._ws_clients: Set[WebSocket] = set()
        self._global_buffer: deque[LogEvent] = deque(maxlen=capacity)
        self._lock = asyncio.Lock()

    async def subscribe(self, ws: WebSocket) -> None:
        async with self._lock:
            self._ws_clients.add(ws)

    async def unsubscribe(self, ws: WebSocket) -> None:
        async with self._lock:
            self._ws_clients.discard(ws)

    async def publish(self, event: LogEvent) -> None:
        self._global_buffer.append(event)
        if event.run_id:
            if event.run_id not in self._run_buffers:
                self._run_buffers[event.run_id] = deque(maxlen=self._capacity)
            self._run_buffers[event.run_id].append(event)

        payload = event.model_dump_json()
        async with self._lock:
            clients = set(self._ws_clients)

        dead: Set[WebSocket] = set()
        for ws in clients:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)

        if dead:
            async with self._lock:
                self._ws_clients -= dead

    def publish_sync(self, event: LogEvent) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(event))
        except RuntimeError:
            self._global_buffer.append(event)

    def get_recent(self, run_id: Optional[str] = None, limit: int = 100) -> List[LogEvent]:
        if run_id and run_id in self._run_buffers:
            buf = self._run_buffers[run_id]
        else:
            buf = self._global_buffer
        return list(buf)[-limit:]

    def clear_run(self, run_id: str) -> None:
        self._run_buffers.pop(run_id, None)


_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


class ScreencastHub:
    """Manages active WebSocket connections for live browser CDP screencasting."""

    def __init__(self) -> None:
        self._clients: Dict[str, Set[WebSocket]] = {}
        self._global_clients: Set[WebSocket] = set()
        self._last_frames: Dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, ws: WebSocket, run_id: Optional[str] = None) -> None:
        async with self._lock:
            if run_id:
                if run_id not in self._clients:
                    self._clients[run_id] = set()
                self._clients[run_id].add(ws)
                last = self._last_frames.get(run_id) or self._last_frames.get("global")
                if last:
                    try:
                        await ws.send_text(last)
                    except Exception:
                        pass
            else:
                self._global_clients.add(ws)
                last = self._last_frames.get("global")
                if last:
                    try:
                        await ws.send_text(last)
                    except Exception:
                        pass

    async def unsubscribe(self, ws: WebSocket, run_id: Optional[str] = None) -> None:
        async with self._lock:
            if run_id and run_id in self._clients:
                self._clients[run_id].discard(ws)
            self._global_clients.discard(ws)

    async def broadcast_frame(self, frame_base64: str, run_id: Optional[str] = None) -> None:
        if run_id:
            self._last_frames[run_id] = frame_base64
        self._last_frames["global"] = frame_base64

        async with self._lock:
            targets = set(self._global_clients)
            if run_id and run_id in self._clients:
                targets.update(self._clients[run_id])

        dead = set()
        for ws in targets:
            try:
                await ws.send_text(frame_base64)
            except Exception:
                dead.add(ws)

        if dead:
            async with self._lock:
                self._global_clients -= dead
                if run_id and run_id in self._clients:
                    self._clients[run_id] -= dead

    def broadcast_frame_sync(self, frame_base64: str, run_id: Optional[str] = None) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.broadcast_frame(frame_base64, run_id))
        except RuntimeError:
            if run_id:
                self._last_frames[run_id] = frame_base64
            self._last_frames["global"] = frame_base64


_global_screencast_hub: Optional[ScreencastHub] = None


def get_screencast_hub() -> ScreencastHub:
    global _global_screencast_hub
    if _global_screencast_hub is None:
        _global_screencast_hub = ScreencastHub()
    return _global_screencast_hub

