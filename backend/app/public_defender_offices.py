"""Official Georgia circuit public defender office directory.

Bundled from the Georgia Public Defender Council's published circuit dataset
(https://gapubdef.org/_data/circuits.json), checked 2026-11-13. This is contact
information only: no ratings, no win/loss records, no scraped commentary.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from . import language as lang

_HERE = Path(__file__).resolve().parent
_CANDIDATES = (
    _HERE / "data" / "public_defender_offices.json",
    _HERE.parents[1] / "config" / "public_defender_offices.json",
    _HERE.parents[2] / "config" / "public_defender_offices.json",
    _HERE.parents[2] / "src" / "publicDefenderOfficesData.json",
)

_WORD = re.compile(r"[a-z0-9]+")


def _path() -> Path:
    for p in _CANDIDATES:
        if p.is_file():
            return p
    raise FileNotFoundError("public_defender_offices.json was not found")


@lru_cache(maxsize=1)
def catalog() -> dict:
    return json.loads(_path().read_text(encoding="utf-8"))


def offices() -> list[dict]:
    return list(catalog()["offices"])


def _hay(office: dict) -> str:
    parts = [
        office.get("circuit") or "",
        office.get("defender") or "",
        office.get("address") or "",
        office.get("phone") or "",
        office.get("email") or "",
        " ".join(office.get("counties") or []),
        office.get("opt_out_note") or "",
        office.get("region") or "",
    ]
    for extra in office.get("additional_offices") or []:
        parts.extend([extra.get("location") or "", extra.get("address") or "", extra.get("phone") or ""])
    juv = office.get("juvenile") or {}
    if isinstance(juv, dict):
        parts.extend([juv.get("name") or "", juv.get("phone") or ""])
    return " ".join(parts).lower()


def search(query: str = "", county: str = "") -> list[dict]:
    """Filter official offices by county name or free-text (circuit, city, defender, phone)."""
    q = (query or "").strip().lower()
    county_q = (county or "").strip().lower().removesuffix(" county").strip()
    out = []
    for office in offices():
        counties = [c.lower() for c in (office.get("counties") or [])]
        if county_q and not any(county_q == c or county_q in c or c in county_q for c in counties):
            continue
        if q:
            blob = _hay(office)
            tokens = _WORD.findall(q)
            if tokens and not all(tok in blob for tok in tokens):
                # allow a single phrase / county match
                if q not in blob:
                    continue
        out.append(office)
    return out


def pack(query: str = "", county: str = "", language: str = "en") -> dict:
    data = catalog()
    code = lang.normalize_language(language)
    spanish = code == "es"
    bar = data["bar_directory"]
    return {
        "title": "Defensores públicos" if spanish else "Public Defenders",
        "language": code,
        "checked_on": data["checked_on"],
        "source_url": data["source_url"],
        "find_tool_url": data["find_tool_url"],
        "source_name": data["source_name"],
        "office_count": len(data["offices"]),
        "offices": search(query, county),
        "outcome_note": data["outcome_note_es"] if spanish else data["outcome_note_en"],
        "bar_directory": {
            "label": bar["label_es"] if spanish else bar["label_en"],
            "url": bar["url"],
            "discipline_url": bar["discipline_url"],
            "terms_url": bar["terms_url"],
            "explainer": bar["explainer_es"] if spanish else bar["explainer_en"],
        },
        "notice": lang.notice(code),
        "problems_heading": "Problem with my public defender?",
    }
