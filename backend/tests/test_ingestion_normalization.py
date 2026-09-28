from datetime import datetime, timezone

import pytest

from app.ingestion.models import SourceDocument
from app.ingestion.normalization import normalize_authority


def doc(body: bytes, content_type: str = "text/html") -> SourceDocument:
    return SourceDocument(
        source_key="ga_code",
        url="https://www.legis.ga.gov/example",
        title="Official material",
        body=body,
        retrieved_at=datetime.now(timezone.utc),
        content_type=content_type,
        metadata={"authority_type": "statute", "jurisdiction": "Georgia"},
    )


def test_normalization_extracts_only_source_present_citation_candidates():
    item = normalize_authority(doc(b"<h1>Search</h1><p>O.C.G.A. 17-5-30 applies here.</p>"))
    assert item.citation_candidates == ("O.C.G.A. § 17-5-30",)
    assert item.authority_type == "statute"
    assert item.jurisdiction == "Georgia"


def test_normalization_deduplicates_candidates_and_strips_scripts():
    item = normalize_authority(doc(b"<script>O.C.G.A. 99-9-99</script> O.C.G.A. 16-11-126; O.C.G.A. 16-11-126"))
    assert item.citation_candidates == ("O.C.G.A. § 16-11-126",)
    assert "99-9-99" not in item.text


def test_normalization_keeps_unknown_citation_unknown():
    item = normalize_authority(doc(b"Official page with no citation in its text."))
    assert item.citation_candidates == ()


def test_pdf_requires_separate_trusted_extraction_stage():
    with pytest.raises(ValueError, match="trusted PDF extraction"):
        normalize_authority(doc(b"%PDF fake", "application/pdf"))


def test_normalization_accepts_common_ocga_formatting_without_inventing_values():
    item = normalize_authority(doc("OCGA section 16 - 7 - 1; O.C.G.A. &sect; 16-7-1".encode()))
    assert item.citation_candidates == ("O.C.G.A. § 16-7-1",)


def test_normalization_canonicalizes_georgia_appellate_case_numbers():
    item = normalize_authority(doc(b"Supreme Court case S 26 A 0123 and Court of Appeals A 26 A 0456."))
    assert item.citation_candidates == ("S26A0123", "A26A0456")


def test_content_type_parameters_do_not_break_official_html_ingestion():
    item = normalize_authority(doc(b"O.C.G.A. 17-5-30", "text/html; charset=utf-8"))
    assert item.citation_candidates == ("O.C.G.A. § 17-5-30",)
