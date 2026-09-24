import re
from dataclasses import dataclass
from urllib.parse import urljoin
from .security import assert_public_official_url

@dataclass(frozen=True)
class DiscoveredItem:
    external_id: str
    title: str
    url: str
    status_hint: str | None = None

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

class GeneralAssemblyAdapter:
    ROOT = "https://www.legis.ga.gov/"
    def code_index(self) -> str:
        return assert_public_official_url(urljoin(self.ROOT, "legislation/georgia-code"))
    def validate_document_url(self, url: str) -> str:
        return assert_public_official_url(url)
