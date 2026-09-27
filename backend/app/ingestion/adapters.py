import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin
from .models import LegalStatus
from .security import assert_public_official_url

@dataclass(frozen=True)
class DiscoveredItem:
    external_id: str
    title: str
    url: str
    status_hint: str | None = None

# Status extraction is intentionally conservative. It records only explicit
# source statements and never treats publication on an official site as proof
# that an authority is current, binding, or precedential.
_NEGATIVE_PATTERNS = {
    "overruled": re.compile(r"\boverruled\b", re.I),
    "vacated": re.compile(r"\bvacated\b", re.I),
    "superseded": re.compile(r"\bsuperseded\b", re.I),
    "withdrawn": re.compile(r"\bwithdrawn\b", re.I),
    "repealed": re.compile(r"\brepealed\b", re.I),
}
_CURRENT_PATTERNS = (
    re.compile(r"\bcurrent(?:ly)? effective\b", re.I),
    re.compile(r"\beffective\s+(?:on|as of)\b", re.I),
)


def legal_status_from_official_text(text: str, source_url: str, *, checked_at: datetime | None = None) -> LegalStatus:
    """Capture explicit legal-status evidence from an approved official page.

    This function does not perform citator inference. If an official page does
    not explicitly establish currency or treatment, those fields remain unknown.
    """
    official_url = assert_public_official_url(source_url)
    checked = checked_at or datetime.now(timezone.utc)
    treatments = tuple(name for name, pattern in _NEGATIVE_PATTERNS.items() if pattern.search(text or ""))
    if treatments:
        currency = treatments[0]
    elif any(pattern.search(text or "") for pattern in _CURRENT_PATTERNS):
        currency = "current"
    else:
        currency = "unknown"
    return LegalStatus(
        verification_status="official",
        currency_status=currency,
        precedential_status="unknown",
        status_checked_at=checked,
        status_source_url=official_url,
        negative_treatment=treatments,
    )

class SupremeCourtOpinionIndexAdapter:
    BASE = "https://www.gasupreme.us/"
    CASE_NO = re.compile(r"\bS\d{2}[A-Z]\d{4}\b")

    def year_url(self, year: int) -> str:
        if year < 1900 or year > 2100:
            raise ValueError("invalid year")
        return assert_public_official_url(urljoin(self.BASE, f"{year}-opinions/"))

    def discover_from_html(self, html: str, year: int) -> list[DiscoveredItem]:
        seen, out = set(), []
        for m in self.CASE_NO.finditer(html):
            case_no = m.group(0)
            if case_no in seen:
                continue
            seen.add(case_no)
            out.append(DiscoveredItem(case_no, case_no, self.year_url(year), "index-discovered"))
        return out

    def status_from_official_page(self, text: str, year: int, checked_at: datetime | None = None) -> LegalStatus:
        return legal_status_from_official_text(text, self.year_url(year), checked_at=checked_at)

class CourtOfAppealsOpinionIndexAdapter:
    """Conservative discovery for public Georgia Court of Appeals opinion indexes."""
    BASE = "https://www.gaappeals.us/"
    CASE_NO = re.compile(r"\bA\d{2}A\d{4}\b")

    def opinions_url(self) -> str:
        return assert_public_official_url(urljoin(self.BASE, "opinions/"))

    def discover_from_html(self, html: str) -> list[DiscoveredItem]:
        seen, out = set(), []
        for m in self.CASE_NO.finditer(html):
            case_no = m.group(0)
            if case_no in seen:
                continue
            seen.add(case_no)
            out.append(DiscoveredItem(case_no, case_no, self.opinions_url(), "index-discovered"))
        return out

    def status_from_official_page(self, text: str, checked_at: datetime | None = None) -> LegalStatus:
        return legal_status_from_official_text(text, self.opinions_url(), checked_at=checked_at)

class GeorgiaCourtsAdapter:
    ROOT = "https://georgiacourts.gov/"
    def rules_index(self) -> str:
        return assert_public_official_url(urljoin(self.ROOT, "tag/court-rules/"))
    def supreme_rules(self) -> str:
        return assert_public_official_url(urljoin(self.ROOT, "georgia-supreme-court-rules/"))
    def court_directory(self) -> str:
        return assert_public_official_url(urljoin(self.ROOT, "find-a-court/"))
    def self_help(self) -> str:
        return assert_public_official_url(urljoin(self.ROOT, "a2j/"))
    def status_from_official_page(self, text: str, source_url: str, checked_at: datetime | None = None) -> LegalStatus:
        return legal_status_from_official_text(text, source_url, checked_at=checked_at)

class GeneralAssemblyAdapter:
    ROOT = "https://www.legis.ga.gov/"
    def code_index(self) -> str:
        return assert_public_official_url(urljoin(self.ROOT, "legislation/georgia-code"))
    def validate_document_url(self, url: str) -> str:
        return assert_public_official_url(url)
    def status_from_official_page(self, text: str, source_url: str, checked_at: datetime | None = None) -> LegalStatus:
        return legal_status_from_official_text(text, self.validate_document_url(source_url), checked_at=checked_at)
