from collections import defaultdict
from typing import Callable
from queue import Queue
import threading
import logging

_logger = logging.getLogger(__name__)


class EventDispatcher:
    _listeners : dict[str, list[Callable]]
    _worker : threading.Thread
    _queue: Queue
    
    def __init__(self):
        self._listeners = defaultdict(list)
        self._queue = Queue()
        self._worker = threading.Thread(target=self._process_loop, daemon=True)
        self._worker.start()
        
    def on(self, event_name: str):
        def decorator(func : Callable):
            self._listeners[event_name].append(func)
            return func
        
        return decorator
    
    def emit(self, event_name: str, *args, **kwargs) -> None:
        """Empile l'event dans la queue — ne bloque pas l'appelant."""
        self._queue.put((event_name, args, kwargs))
        
    def _process_loop(self) -> None:
        while True:
            event_name, args, kwargs = self._queue.get()
            for handler in self._listeners.get(event_name, []):
                try:
                    handler(*args, **kwargs)
                except Exception:
                    _logger.exception("Handler '%s' failed for event '%s'", handler.__name__, event_name)



events = EventDispatcher()