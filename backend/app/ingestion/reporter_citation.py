"""Conservative Georgia reporter-citation extraction.

This module recognizes only explicit reporter citations present in trusted
source text. It never derives a citation from a docket number, title, URL,
decision date, or model output.
"""
from __future__ import annotations

import re

# Georgia Reports citations. A parallel South Eastern citation alone is not
# treated as a Georgia reporter citation for admission to the Georgia index.
_GA_REPORTER = re.compile(r"(?<![A-Za-z0-9])(?P<vol>[1-9]\d{0,3})\s+Ga\.\s+(?P<page>[1-9]\d{0,4})(?!\d)")


def explicit_georgia_reporter_citations(text: str) -> tuple[str, ...]:
    """Return unique explicit ``N Ga. N`` citations in source order."""
    if not text:
        return ()
    seen: set[str] = set()
    citations: list[str] = []
    for match in _GA_REPORTER.finditer(text):
        citation = f"{int(match.group('vol'))} Ga. {int(match.group('page'))}"
        if citation not in seen:
            seen.add(citation)
            citations.append(citation)
    return tuple(citations)


def resolve_single_georgia_reporter_citation(text: str) -> str | None:
    """Resolve only unambiguous source evidence; ambiguity remains unresolved."""
    citations = explicit_georgia_reporter_citations(text)
    return citations[0] if len(citations) == 1 else None
