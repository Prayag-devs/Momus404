"""
momus404 — backend/log_bus.py (Backward Compatibility Facade)
Re-exports from app.services.event_bus.
"""

from app.services.event_bus import EventBus, get_event_bus

# Module-level singleton and class alias
LogBus = EventBus
bus = get_event_bus()

__all__ = ["LogBus", "EventBus", "bus"]
