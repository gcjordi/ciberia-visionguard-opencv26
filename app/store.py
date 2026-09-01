from __future__ import annotations

from threading import Lock
from typing import Any


class TraceStore:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def put(self, trace_id: str, item: dict[str, Any]) -> None:
        with self._lock:
            self._items[trace_id] = item

    def get(self, trace_id: str) -> dict[str, Any] | None:
        with self._lock:
            item = self._items.get(trace_id)
            return None if item is None else dict(item)


store = TraceStore()
