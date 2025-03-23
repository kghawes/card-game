"""Centralized event system to broadcast events between game and GUI."""

class EventManager:
    """Class to manage subscribing to and dispatching events."""
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, callback):
        """Register a callback function for an event."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def dispatch(self, event_type, *args, **kwargs):
        """Notify all listeners of an event."""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(*args, **kwargs)
