"""Two-level TTL cache (in-process + small shared Postgres table) for for public (non-personal) AI answers, keyed by normalized question + mode.

Only the guest endpoints use it. Per-user case chat and case tools are never cached.
"""
from __future__ import annotations
import copy
import hashlib
import os
import re
import threading
import json
import logging
import time

from sqlalchemy import text

_log = logging.getLogger(__name__)
DB_MAX_ROWS = int(os.getenv("ANSWER_CACHE_DB_MAX_ROWS", "500"))
_table_ready = False

TTL_SECONDS = int(os.getenv("ANSWER_CACHE_TTL_SECONDS", str(24 * 3600)))
MAX_ENTRIES = int(os.getenv("ANSWER_CACHE_MAX_ENTRIES", "2000"))
_lock = threading.Lock()
_store: dict[str, tuple[float, dict]] = {}


def normalize(question: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", re.sub(r"\s+", " ", (question or "").lower())).strip()


def key(question: str, mode: str) -> str:
    return hashlib.sha256(f"v4\x00{mode}\x00{normalize(question)}".encode()).hexdigest()  # v2: plain-text answers


def _ensure_table(db) -> None:
    global _table_ready
    if _table_ready:
        return
    with db.begin_nested():
        db.execute(text("CREATE TABLE IF NOT EXISTS public_answer_cache (cache_key VARCHAR(64) PRIMARY KEY, "
                        "created_at DOUBLE PRECISION NOT NULL, payload TEXT NOT NULL)"))
    db.commit()
    _table_ready = True


def _db_get(db, k: str, now: float) -> dict | None:
    try:
        _ensure_table(db)
        row = db.execute(text("SELECT created_at, payload FROM public_answer_cache WHERE cache_key=:k"), {"k": k}).first()
        db.commit()
    except Exception as exc:  # cache must never break answers
        db.rollback(); _log.warning("answer cache read skipped: %s", type(exc).__name__)
        return None
    if not row or now - float(row[0]) > TTL_SECONDS:
        return None
    value = json.loads(row[1])
    with _lock:
        _store[k] = (float(row[0]), copy.deepcopy(value))
    return value


def _db_put(db, k: str, value: dict, now: float) -> None:
    try:
        _ensure_table(db)
        payload = json.dumps(value, default=str)
        db.execute(text("DELETE FROM public_answer_cache WHERE cache_key=:k OR created_at < :old"), {"k": k, "old": now - TTL_SECONDS})
        db.execute(text("INSERT INTO public_answer_cache (cache_key, created_at, payload) VALUES (:k, :t, :p)"), {"k": k, "t": now, "p": payload})
        db.execute(text("DELETE FROM public_answer_cache WHERE cache_key IN (SELECT cache_key FROM public_answer_cache "
                        "ORDER BY created_at DESC LIMIT -1 OFFSET :n)" if db.get_bind().dialect.name == "sqlite" else
                        "DELETE FROM public_answer_cache WHERE cache_key IN (SELECT cache_key FROM public_answer_cache "
                        "ORDER BY created_at DESC OFFSET :n)"), {"n": DB_MAX_ROWS})
        db.commit()
    except Exception as exc:
        db.rollback(); _log.warning("answer cache write skipped: %s", type(exc).__name__)


def get(question: str, mode: str, now: float | None = None, db=None) -> dict | None:
    now = time.time() if now is None else now
    k = key(question, mode)
    with _lock:
        item = _store.get(k)
        if item and now - item[0] <= TTL_SECONDS:
            return copy.deepcopy(item[1])
        _store.pop(k, None)
    return _db_get(db, k, now) if db is not None else None


def put(question: str, mode: str, value: dict, now: float | None = None, db=None) -> None:
    now = time.time() if now is None else now
    if db is not None:
        _db_put(db, key(question, mode), value, now)
    with _lock:
        if len(_store) >= MAX_ENTRIES:
            for k in sorted(_store, key=lambda x: _store[x][0])[: max(1, MAX_ENTRIES // 10)]:
                _store.pop(k, None)
        _store[key(question, mode)] = (now, copy.deepcopy(value))


def clear() -> None:
    with _lock:
        _store.clear()
