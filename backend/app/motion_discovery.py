"""Discover motion/remedy concepts from indexed legal authority text.

Discovery creates research candidates only. It never upgrades a candidate to
verified law without the authority/source verification layer.
"""
import re
from dataclasses import dataclass, asdict
from .motion_registry import normalize_motion_name

# Conservative legal-procedure phrases. Keep the noun phrase bounded so a
# whole sentence is not accidentally treated as a motion name.
_PATTERNS = (
    re.compile(r"\b(motion\s+(?:to|for)\s+[a-z][a-z\- ]{2,70}?)(?=[,.;:)\n]|\s+(?:was|is|be|should|may|must|filed|seeking|requesting)\b)", re.I),
    re.compile(r"\b(extraordinary\s+motion\s+for\s+[a-z][a-z\- ]{2,60}?)(?=[,.;:)\n]|\s+(?:was|is|be|filed)\b)", re.I),
    re.compile(r"\b(petition\s+for\s+(?:writ\s+of\s+)?[a-z][a-z\- ]{2,60}?)(?=[,.;:)\n]|\s+(?:was|is|be|filed)\b)", re.I),
    re.compile(r"\b(application\s+for\s+[a-z][a-z\- ]{2,60}?)(?=[,.;:)\n]|\s+(?:was|is|be|filed)\b)", re.I),
)

@dataclass(frozen=True)
class DiscoveredProcedure:
    display_name: str
    normalized_name: str
    authority_id: int | None = None
    citation: str = ""
    source_url: str = ""
    authority_status: str = "UNVERIFIED"
    currency_status: str = "unknown"
    precedential_status: str = "unknown"
    negative_treatment: str = ""
    occurrence_count: int = 1


def _clean(value: str) -> str:
    return " ".join(value.strip(" \t\r\n,.;:()[]").split())


def discover_procedures(text: str, *, authority_id: int | None = None, citation: str = "", source_url: str = "", authority_status: str = "UNVERIFIED", currency_status: str = "unknown", precedential_status: str = "unknown", negative_treatment: str = "") -> list[dict]:
    found: dict[str, DiscoveredProcedure] = {}
    for pattern in _PATTERNS:
        for match in pattern.finditer(text or ""):
            display = _clean(match.group(1))
            normalized = normalize_motion_name(display)
            if len(normalized) < 8:
                continue
            previous = found.get(normalized)
            found[normalized] = DiscoveredProcedure(
                display_name=display,
                normalized_name=normalized,
                authority_id=authority_id,
                citation=citation,
                source_url=source_url,
                authority_status=authority_status,
                currency_status=currency_status,
                precedential_status=precedential_status,
                negative_treatment=negative_treatment,
                occurrence_count=(previous.occurrence_count + 1) if previous else 1,
            )
    return [asdict(item) for item in sorted(found.values(), key=lambda item: item.normalized_name)]


def discover_from_authorities(authorities) -> list[dict]:
    """Aggregate procedure candidates across LegalAuthority-like objects."""
    aggregated: dict[str, dict] = {}
    ref_fields = (
        "authority_id", "citation", "source_url", "authority_status",
        "currency_status", "precedential_status", "negative_treatment",
    )
    for authority in authorities:
        rows = discover_procedures(
            getattr(authority, "text", "") or "",
            authority_id=getattr(authority, "id", None),
            citation=getattr(authority, "citation", "") or "",
            source_url=getattr(authority, "source_url", "") or "",
            authority_status=getattr(authority, "status", "UNVERIFIED") or "UNVERIFIED",
            currency_status=getattr(authority, "currency_status", "unknown") or "unknown",
            precedential_status=getattr(authority, "precedential_status", "unknown") or "unknown",
            negative_treatment=getattr(authority, "negative_treatment", "") or "",
        )
        for row in rows:
            key = row["normalized_name"]
            current = aggregated.get(key)
            if current:
                current["occurrence_count"] += row["occurrence_count"]
                current["authority_refs"].append({k: row[k] for k in ref_fields})
            else:
                row["authority_refs"] = [{k: row[k] for k in ref_fields}]
                aggregated[key] = row
    return sorted(aggregated.values(), key=lambda row: (-row["occurrence_count"], row["normalized_name"]))
