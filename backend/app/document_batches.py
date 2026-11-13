"""Multi-batch paper reading: up to 10 pages per request, later batches append to the same session/case.

Raw photos are not stored (disk is tight). Each batch keeps extracted text, a short summary, and
key fields so a later batch can be read together with everything already sent. If earlier text is
too long, only the summaries are sent to the model.
"""
from __future__ import annotations

import json
import logging
import time
import uuid

from sqlalchemy import text

from . import document_reader as dr

logger = logging.getLogger(__name__)

MAX_PAGES_PER_BATCH = dr.MAX_FILES
MAX_PRIOR_CHARS = int(__import__("os").getenv("DOC_READ_MAX_PRIOR_CHARS", "20000"))
_table_ready = False


def new_session_id() -> str:
    return uuid.uuid4().hex


def _ensure_table(db) -> None:
    global _table_ready
    if _table_ready:
        return
    with db.begin_nested():
        db.execute(text(
            "CREATE TABLE IF NOT EXISTS document_read_batches ("
            "session_id VARCHAR(64) NOT NULL, "
            "user_id INTEGER NOT NULL, "
            "batch_index INTEGER NOT NULL, "
            "case_id INTEGER, "
            "created_at DOUBLE PRECISION NOT NULL, "
            "page_count INTEGER NOT NULL, "
            "payload TEXT NOT NULL, "
            "PRIMARY KEY (session_id, batch_index))"
        ))
        db.execute(text(
            "CREATE INDEX IF NOT EXISTS document_read_batches_user_session "
            "ON document_read_batches (user_id, session_id)"
        ))
    db.commit()
    _table_ready = True


def _safe(db, fn, default=None):
    try:
        return fn()
    except Exception as exc:
        db.rollback()
        logger.warning("document batch store skipped: %s", type(exc).__name__)
        return default


def load(db, user_id: int, session_id: str | None) -> list[dict]:
    sid = (session_id or "").strip()
    if not sid or not user_id:
        return []

    def _go():
        _ensure_table(db)
        rows = db.execute(text(
            "SELECT batch_index, case_id, page_count, payload FROM document_read_batches "
            "WHERE session_id=:s AND user_id=:u ORDER BY batch_index"
        ), {"s": sid, "u": int(user_id)}).fetchall()
        db.commit()
        out = []
        for row in rows:
            item = json.loads(row[3])
            item["batch_index"] = int(row[0])
            item["case_id"] = row[1]
            item["page_count"] = int(row[2])
            out.append(item)
        return out

    return _safe(db, _go, []) or []


def append(db, user_id: int, session_id: str, page_count: int, payload: dict, case_id: int | None = None) -> int:
    """Save this batch and return its 1-based index."""
    sid = (session_id or "").strip() or new_session_id()
    slim = {
        "extracted_text": (payload.get("extracted_text") or "")[:80000],
        "summary": (payload.get("summary") or "")[:8000],
        "answer": (payload.get("answer") or "")[:16000],
        "document_type": payload.get("document_type") or "",
        "case_number": payload.get("case_number") or "",
        "court": payload.get("court") or "",
        "charges_or_claims": payload.get("charges_or_claims") or [],
        "key_dates": payload.get("key_dates") or [],
        "pages": page_count,
    }

    def _go():
        _ensure_table(db)
        current = db.execute(text(
            "SELECT COALESCE(MAX(batch_index), 0) FROM document_read_batches "
            "WHERE session_id=:s AND user_id=:u"
        ), {"s": sid, "u": int(user_id)}).scalar() or 0
        idx = int(current) + 1
        db.execute(text(
            "INSERT INTO document_read_batches (session_id, user_id, batch_index, case_id, created_at, page_count, payload) "
            "VALUES (:s, :u, :i, :c, :t, :p, :b)"
        ), {"s": sid, "u": int(user_id), "i": idx, "c": case_id, "t": time.time(), "p": int(page_count), "b": json.dumps(slim, default=str)})
        db.commit()
        return idx

    return _safe(db, _go, 1) or 1


def prior_context(batches: list[dict], max_chars: int = MAX_PRIOR_CHARS) -> tuple[str, bool]:
    """Text the model should treat as already-read pages. (text, was_summarized)."""
    if not batches:
        return "", False
    full_parts, summary_parts = [], []
    total_pages = 0
    for i, batch in enumerate(batches, 1):
        pages = int(batch.get("page_count") or batch.get("pages") or 0)
        total_pages += pages
        text = (batch.get("extracted_text") or "").strip()
        summary = (batch.get("summary") or batch.get("answer") or "").strip()
        heading = f"--- Earlier batch {i} ({pages or '?'} page(s)) ---"
        full_parts.append(heading + "\n" + (text or summary))
        summary_parts.append(heading + ", summary ---\n" + (summary or text[:1500]))
    full = "\n\n".join(full_parts)
    prefix = (
        f"The person already sent {len(batches)} earlier batch(es) ({total_pages} page(s)) "
        "for this same case. Read the new pages together with that earlier material. "
        "Your answer should cover the whole set, not only the new pages.\n\n"
    )
    if len(full) <= max_chars:
        return prefix + full, False
    summarized = "\n\n".join(summary_parts)
    return (
        prefix
        + "The earlier pages were summarized because the full text is long:\n\n"
        + summarized[:max_chars]
    ), True


def snapshot_fields(batches: list[dict]) -> dict:
    """Merge key fields from earlier batches so a later plan still sees them."""
    charges, dates = [], []
    case_number = ""
    court = ""
    types = []
    pages = 0
    for batch in batches:
        pages += int(batch.get("page_count") or batch.get("pages") or 0)
        types.append(batch.get("document_type") or "")
        case_number = case_number or (batch.get("case_number") or "")
        court = court or (batch.get("court") or "")
        charges.extend(batch.get("charges_or_claims") or [])
        dates.extend(batch.get("key_dates") or [])
    # de-dupe, keep order
    def uniq(items):
        seen, out = set(), []
        for item in items:
            key = (item or "").strip()
            if key and key not in seen:
                seen.add(key)
                out.append(item)
        return out
    return {
        "pages_earlier": pages,
        "document_type": ", ".join(uniq(types)),
        "case_number": case_number,
        "court": court,
        "charges_or_claims": uniq(charges),
        "key_dates": uniq(dates),
    }
