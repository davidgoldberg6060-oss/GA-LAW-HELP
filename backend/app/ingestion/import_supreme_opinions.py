"""Operator-run, resumable import of Supreme Court of Georgia opinion PDFs.

The court's annual opinion pages are the discovery source. Reporter citations
are used when deterministically found in the official PDF. For corpus expansion,
an opinion without a reporter citation is still retained under a clearly marked
UNVERIFIED DOCUMENT ID based on the court docket; it must not be represented as
verified/current authority until later evidence upgrades it.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
import json
import os
import re
import time
from urllib.parse import urljoin, urlparse

from .http_transport import production_transport
from .pdf_evidence import resolve_official_pdf_georgia_citation
from .security import assert_public_official_url
from .source_acquisition import OfficialDocumentRequest, acquire_ingestion_item
from ..database import SessionLocal
from .pipeline import persist_item

CASE_NO = re.compile(r"\bS\d{2}[A-Z]\d{4}\b", re.I)
INDEX_LIMIT = 3 * 1024 * 1024


@dataclass(frozen=True)
define_unused = None
