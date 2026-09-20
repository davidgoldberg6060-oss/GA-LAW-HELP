import re
from dataclasses import dataclass
from typing import Iterable

TOKEN = re.compile(r"[a-z0-9§.-]+", re.I)

def terms(text: str) -> set[str]:
    return {x.lower() for x in TOKEN.findall(text) if len(x) > 2}

@dataclass(frozen=True)
class SearchDocument:
    id: str
    citation: str
    title: str
    text: str
    verified: bool = False
    current_status: str = "unknown"

@dataclass(frozen=True)
class SearchResult:
    document: SearchDocument
    score: float
    matched_terms: tuple[str, ...]

def search(query: str, documents: Iterable[SearchDocument], limit: int = 10) -> list[SearchResult]:
    q = terms(query)
    out = []
    for d in documents:
        body = terms(f"{d.citation} {d.title} {d.text}")
        overlap = q & body
        if not overlap:
            continue
        score = len(overlap) / max(1, len(q))
        if d.verified:
            score += .15
        if d.current_status.lower() in {"current", "good_law", "active"}:
            score += .1
        out.append(SearchResult(d, round(score, 4), tuple(sorted(overlap))))
    return sorted(out, key=lambda r: r.score, reverse=True)[:limit]
