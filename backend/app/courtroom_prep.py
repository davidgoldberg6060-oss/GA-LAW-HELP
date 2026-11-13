"""Courtroom prep checklists for Georgia courts, tailored by case type.

General day-before and day-of guidance, plus extras for each defense-plan case type.
Content is bilingual (English and Spanish). This is legal information, not legal advice.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from . import defense_plan, language as lang

SECTION_IDS = (
    "day_before", "day_of", "bring", "wear", "arrive", "address_judge", "say", "dont_say",
)

_HERE = Path(__file__).resolve().parent
_CANDIDATES = (
    _HERE / "data" / "courtroom_prep.json",  # shipped inside the API image (backend/app/data)
    _HERE.parents[1] / "config" / "courtroom_prep.json",  # /app/config in Docker, backend/config fallback
    _HERE.parents[2] / "config" / "courtroom_prep.json",  # repo root when running from backend/app
    _HERE.parents[2] / "src" / "courtroomPrepData.json",
)


def _path() -> Path:
    for p in _CANDIDATES:
        if p.is_file():
            return p
    raise FileNotFoundError("courtroom_prep.json was not found")


@lru_cache(maxsize=1)
def catalog() -> dict:
    return json.loads(_path().read_text(encoding="utf-8"))


def case_types() -> list[dict]:
    """Labels for the type picker, in catalog order, plus a general option."""
    data = catalog()
    rows = [{"id": "", "label": "Any Georgia court date", "family": "general"}]
    for key, info in data["types"].items():
        rows.append({"id": key, "label": info["label_en"], "family": info.get("family") or ""})
    return rows


def detect_type(text: str | None) -> str | None:
    """Reuse the defense-plan detector so prep matches the plan's case type."""
    return defense_plan.detect(text or "")


def _pick(item: dict, language: str) -> str:
    key = "es" if lang.is_spanish(language) else "en"
    return str(item.get(key) or item.get("en") or "").strip()


def _items(block: dict | None, section: str, language: str) -> list[str]:
    if not block:
        return []
    out = []
    seen = set()
    for item in block.get(section) or []:
        text = _pick(item, language) if isinstance(item, dict) else str(item).strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def prep_for(case_type: str | None = None, language: str = "en", situation: str = "") -> dict:
    """A skimmable courtroom-prep pack: quick answer, then day-before and day-of sections."""
    data = catalog()
    code = lang.normalize_language(language)
    spanish = code == "es"
    kind = (case_type or "").strip()
    if kind not in data["types"]:
        kind = detect_type(situation) or ""
    info = data["types"].get(kind) or {}
    if spanish:
        label = info.get("label_es") or info.get("label_en") or ("Cualquier fecha de corte en Georgia")
        quick = info.get("quick_es") or data["quick_es"]
        disclaimer = data["disclaimer_es"]
        title = f"Preparación para la corte: {label}" if info else "Preparación para la corte"
    else:
        label = info.get("label_en") or "Any Georgia court date"
        quick = info.get("quick_en") or data["quick_en"]
        disclaimer = data["disclaimer_en"]
        title = f"Courtroom prep: {label}" if info else "Courtroom prep"
    sections = []
    for spec in data["sections"]:
        sid = spec["id"]
        # Type-specific points first, then the general Georgia-court list, de-duplicated.
        items = _items(info, sid, code) + _items(data["general"], sid, code)
        # _items already de-dupes within a block; de-dupe across both.
        dedup, seen = [], set()
        for item in items:
            if item not in seen:
                seen.add(item)
                dedup.append(item)
        sections.append({
            "id": sid,
            "title": spec["title_es"] if spanish else spec["title_en"],
            "items": dedup,
        })
    return {
        "title": title,
        "case_type": kind or None,
        "label": label,
        "family": info.get("family") or "general",
        "language": code,
        "quick": quick,
        "sections": sections,
        "disclaimer": disclaimer,
        "notice": lang.notice(code),
    }


def as_text(prep: dict) -> str:
    """Plain text for sharing, PDFs, and read-aloud (quick answer first, then sections)."""
    lines = [prep.get("title") or "Courtroom prep", "", "Quick answer" if prep.get("language") != "es" else "Respuesta rápida", prep.get("quick") or ""]
    for section in prep.get("sections") or []:
        items = section.get("items") or []
        if not items:
            continue
        lines.extend(["", section.get("title") or ""])
        lines.extend("• " + item for item in items)
    lines.extend(["", prep.get("disclaimer") or "", prep.get("notice") or lang.NOTICE_EN])
    return "\n".join(lines).strip() + "\n"
