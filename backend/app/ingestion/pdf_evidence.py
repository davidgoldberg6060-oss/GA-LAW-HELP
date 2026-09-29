"""Trusted text-evidence boundary for official Georgia legal PDFs.

PDF text is extracted only from a SourceDocument already acquired through the
approved official-source transport. Extraction does not itself make a citation
valid: the resulting text is passed through the same conservative Georgia
Reports citation resolver and official-verification gate.
"""
from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

from .models import SourceDocument
from .pipeline import source_for
from .reporter_citation import resolve_single_georgia_reporter_citation

MAX_PDF_PAGES_FOR_CITATION_EVIDENCE = 12
MAX_EXTRACTED_CHARS = 250_000


def extract_official_pdf_text(document: SourceDocument) -> str | None:
    """Extract bounded text from a verified official Georgia PDF.

    Returns None when provenance, verification, parsing, encryption, or text
    availability is insufficient. This function never performs OCR and never
    derives a citation from a docket number, filename, title, or URL.
    """
    if document.content_type != "application/pdf":
        return None
    source = source_for(document.source_key)
    if source.jurisdiction.strip().lower() != "georgia":
        return None
    if document.legal_status is None or document.legal_status.verification_status != "official":
        return None
    try:
        reader = PdfReader(BytesIO(document.body), strict=True)
        if reader.is_encrypted:
            return None
        chunks: list[str] = []
        size = 0
        for page in reader.pages[:MAX_PDF_PAGES_FOR_CITATION_EVIDENCE]:
            text = page.extract_text() or ""
            if not text:
                continue
            remaining = MAX_EXTRACTED_CHARS - size
            if remaining <= 0:
                break
            text = text[:remaining]
            chunks.append(text)
            size += len(text)
        result = "\n".join(chunks).strip()
        return result or None
    except Exception:
        # Malformed/unparseable PDFs are evidence failures, not ingestion data.
        return None


def resolve_official_pdf_georgia_citation(document: SourceDocument) -> str | None:
    """Resolve one explicit Georgia Reports citation from trusted PDF text."""
    text = extract_official_pdf_text(document)
    if not text:
        return None
    return resolve_single_georgia_reporter_citation(text)
