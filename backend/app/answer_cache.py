"""In-memory TTL cache for public (non-personal) AI answers, keyed by normalized question + mode.

Only the guest endpoints use it. Per-user case chat and case tools are never cached.
"""
from __future__ import annotations
import copy
import hashlib
import os
import re
import threading
import time

TTL_SECONDS = int(os.getenv("ANSWER_CACHE_TTL_SECONDS", str(24 * 3600)))
MAX_ENTRIES = int(os.getenv("ANSWER_CACHE_MAX_ENTRIES", "2000"))
_lock = threading.Lock()
_store: dict[str, tuple[float, dict]] = {}


def normalize(question: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", re.sub(r"\s+", " ", (question or "").lower())).strip()


def key(question: str, mode: str) -> str:
    return hashlib.sha256(f"{mode}\x00{normalize(question)}".encode()).hexdigest()


def get(question: str, mode: str, now: float | None = None) -> dict | None:
    now = time.time() if now is None else now
    k = key(question, mode)
    with _lock:
        item = _store.get(k)
        if not item:
            return None
        if now - item[0] > TTL_SECONDS:
            _store.pop(k, None)
            return None
        return copy.deepcopy(item[1])


def put(question: str, mode: str, value: dict, now: float | None = None) -> None:
    now = time.time() if now is None else now
    with _lock:
        if len(_store) >= MAX_ENTRIES:
            for k in sorted(_store, key=lambda x: _store[x][0])[: max(1, MAX_ENTRIES // 10)]:
                _store.pop(k, None)
        _store[key(question, mode)] = (now, copy.deepcopy(value))


def clear() -> None:
    with _lock:
        _store.clear()
