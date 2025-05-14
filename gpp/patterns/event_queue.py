\
import collections

class Event:
    """A generic event."""
    def __init__(self, type, **payload):
        self.type = type
        self.payload = payload

    def __repr__(self):
        return f"Event(type='{self.type}', payload={self.payload})"

class EventQueue:
    """
    A singleton event queue to decouple event sending from processing.
    Events are queued and processed typically in a central game loop.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventQueue, cls).__new__(cls)
            # Initialize the queue only once
            cls._instance._queue = collections.deque()
        return cls._instance

    def queue_event(self, event_type, **payload):
        """Adds an event to the queue."""
        event = Event(event_type, **payload)
        self._queue.append(event)
        # print(f"DEBUG: Event queued: {event}") # Uncomment for debugging

    def get_event(self):
        """Retrieves and removes the next event from the queue. Returns None if empty."""
        if self._queue:
            return self._queue.popleft()
        return None

    def peek_event(self):
        """Looks at the next event without removing it. Returns None if empty."""
        if self._queue:
            return self._queue[0]
        return None

    def has_events(self):
        """Checks if there are any events in the queue."""
        return bool(self._queue)

# Global singleton instance of the event queue
global_event_queue = EventQueue()
