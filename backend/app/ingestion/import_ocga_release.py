"""Operator-run, resumable import of the OCGA from a Public.Resource.Org release.

Source: Public.Resource.Org's "Bulk Access to Official Code of Georgia Annotated" item on the
Internet Archive (``gov.ga.ocga.2018``; public-domain mark), release folders such as
``release86.2022.11``: one OpenDocument (``.odt``) file per title, as released by the State.
*Georgia v. Public.Resource.Org, Inc.*, 590 U.S. 255 (2020): the OCGA, annotations included, is not
copyrightable. See docs/LEGAL_SOURCES_AND_PROVENANCE.md.

Each Code section becomes one ``legal_authorities`` row (``O.C.G.A. § 16-11-131``) with its
title/chapter/article/part hierarchy, section text, and, kept separately, its history line and
editorial annotations. Every stored version records the release, file URL and file SHA-1
(checked against the archive's published metadata; a mismatch aborts the title).

A release's date is an as-of date, not an effective date, and the release is not evidence that a
section is still current: records stay ``unverified`` with ``unknown`` currency. Sections whose
heading in the release is only "Repealed." or "Reserved." are counted and not stored.

Preview by default; ``--commit`` persists. ``--state-file`` checkpoints finished titles and the
section position inside the current title (commit mode only).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator
from urllib.parse import urlparse

from .models import LegalStatus, SourceDocument
from .persistence import upsert_authority_document

SOURCE_KEY = "pro_ocga_release"
ITEM = "gov.ga.ocga.2018"
DEFAULT_RELEASE = "release86.2022.11"
METADATA_URL = f"https://archive.org/metadata/{ITEM}"
DOWNLOAD_BASE = f"https://archive.org/download/{ITEM}/"
USER_AGENT = "GA.LAW.HELP-corpus-import/1.0 (+https://github.com/davidgoldberg6060-oss/GA-LAW-HELP)"
MAX_FILE_BYTES = 200 * 1024 * 1024
RELEASE = re.compile(r"^release\d+\.(\d{4})\.(\d{2})$")
TITLES = [f"{n:02d}" for n in range(1, 54)]

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
}
T = "{%s}" % NS["text"]
SECTION = re.compile(r"^(\d+[A-Z]?-\d+[A-Z]?-\d+(?:\.\d+)?)\.\s+(.*)$", re.S)
LEVELS = (("TITLE", "Title"), ("CHAPTER", "Chapter"), ("ARTICLE", "Article"), ("PART", "Part"), ("SUBPART", "Subpart"))
HEADING = re.compile(r"^(TITLE|CHAPTER|ARTICLE|PART|SUBPART)\s+(\d+[A-Z]?)\b\s*(.*)$", re.I | re.S)
MARKERS = {"Text": "text", "History": "history", "Annotations": "annotations"}
PLACEHOLDER = re.compile(r"^\[?(?:Repealed|Reserved|Redesignated)\b", re.I)


def _allowed(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return parsed.scheme == "https" and (host == "archive.org" or host.endswith(".archive.org"))


class _NoOffsiteRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _allowed(newurl):
            raise ValueError(f"Refusing redirect off archive.org: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_bytes(url: str) -> bytes:
    if not _allowed(url):
        raise ValueError(f"Refusing non-archive.org URL: {url}")
    opener = urllib.request.build_opener(_NoOffsiteRedirect)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(request, timeout=120) as response:
        body = response.read(MAX_FILE_BYTES + 1)
    if len(body) > MAX_FILE_BYTES:
        raise ValueError("file exceeds size limit")
    return body


def release_as_of(release: str) -> str:
    match = RELEASE.match(release)
    if not match:
        raise ValueError("release must look like release86.2022.11")
    return f"{match.group(1)}-{match.group(2)}"


def title_file(title: str) -> str:
    return f"gov.ga.ocga.title.{int(title):02d}.odt"


def release_manifest(release: str, fetch: Callable[[str], bytes] = fetch_bytes) -> dict[str, dict]:
    """Published name -> {sha1, size} for the release's ODT files (provenance check)."""
    meta = json.loads(fetch(METADATA_URL))
    prefix = release + "/"
    return {f["name"][len(prefix):]: {"sha1": f.get("sha1"), "size": f.get("size")}
            for f in meta.get("files", []) if f.get("name", "").startswith(prefix)}


# ---------------------------------------------------------------- ODT parsing
@dataclass
class Paragraph:
    text: str
    centered: bool
    tiny: bool


def _style_map(root) -> dict[str, tuple[bool, bool]]:
    styles: dict[str, tuple[bool, bool]] = {}
    auto = root.find("office:automatic-styles", NS)
    for style in (auto if auto is not None else []):
        name = style.get("{%s}name" % NS["style"])
        para = style.find("style:paragraph-properties", NS)
        textp = style.find("style:text-properties", NS)
        centered = para is not None and para.get("{%s}text-align" % NS["fo"]) == "center"
        size = textp.get("{%s}font-size" % NS["fo"]) if textp is not None else None
        tiny = bool(size and size.endswith("pt") and float(size[:-2]) <= 6)
        styles[name] = (centered, tiny)
    return styles


def _text(element) -> str:
    parts: list[str] = []

    def walk(node):
        if node.text:
            parts.append(node.text)
        for child in node:
            tag = child.tag
            if tag == T + "s":
                parts.append(" " * int(child.get(T + "c", "1")))
            elif tag == T + "tab":
                parts.append("\t")
            elif tag == T + "line-break":
                parts.append("\n")
            else:
                walk(child)
            if child.tail:
                parts.append(child.tail)

    walk(element)
    return "".join(parts)


def odt_paragraphs(odt: bytes) -> list[Paragraph]:
    with zipfile.ZipFile(io.BytesIO(odt)) as archive:
        root = ET.fromstring(archive.read("content.xml"))
    styles = _style_map(root)
    body = root.find("office:body/office:text", NS)
    out: list[Paragraph] = []
    for node in body.iter():
        if node.tag not in (T + "p", T + "h"):
            continue
        centered, tiny = styles.get(node.get(T + "style-name", ""), (False, False))
        out.append(Paragraph(re.sub(r"[ \t]+", " ", _text(node)).strip(), centered, tiny))
    return out


@dataclass
class Section:
    number: str
    heading: str
    hierarchy: list[str]
    text: list[str] = field(default_factory=list)
    history: list[str] = field(default_factory=list)
    annotations: list[str] = field(default_factory=list)

    @property
    def citation(self) -> str:
        return f"O.C.G.A. § {self.number}"

    @property
    def placeholder(self) -> bool:
        return bool(PLACEHOLDER.match(self.heading)) and not "".join(self.text).strip()

    @property
    def body_text(self) -> str:
        return "\n".join(p for p in self.text if p).strip()

    @property
    def history_text(self) -> str:
        return re.sub(r"^History\.\s*", "", "\n".join(p for p in self.history if p).strip())

    @property
    def annotations_text(self) -> str:
        parts = []
        if self.history_text:
            parts.append("History. " + self.history_text)
        notes = "\n".join(p for p in self.annotations if p).strip()
        if notes:
            parts.append(notes)
        return "\n\n".join(parts)


def parse_title(paragraphs: list[Paragraph]) -> Iterator[Section]:
    """Walk the release's paragraphs into Code sections with their hierarchy."""
    levels: dict[str, str] = {}
    current: Section | None = None
    mode = None
    for i, para in enumerate(paragraphs):
        if para.tiny and para.text in MARKERS:
            mode = MARKERS[para.text]
            continue
        heading = HEADING.match(para.text) if para.centered else None
        if heading:
            if current:
                yield current
                current, mode = None, None
            kind = heading.group(1).upper()
            names = [k for k, _ in LEVELS]
            label = dict(LEVELS)[kind]
            levels[kind] = f"{label} {heading.group(2)} {heading.group(3).strip()}".strip()
            for lower in names[names.index(kind) + 1:]:
                levels.pop(lower, None)
            continue
        section = SECTION.match(para.text)
        if section and not para.centered and _next_is_marker(paragraphs, i):
            if current:
                yield current
            hierarchy = [levels[k] for k, _ in LEVELS if k in levels]
            current, mode = Section(section.group(1), section.group(2).strip(), hierarchy), None
            continue
        if current is None or not para.text:
            continue
        if mode == "text":
            current.text.append(para.text)
        elif mode == "history":
            current.history.append(para.text)
        elif mode == "annotations":
            current.annotations.append(para.text)
    if current:
        yield current


def _next_is_marker(paragraphs: list[Paragraph], i: int) -> bool:
    for para in paragraphs[i + 1:i + 4]:
        if para.text:
            # Chapter-level notes also open with "Annotations", so only Text/History start a section.
            return para.tiny and para.text in ("Text", "History")
    return False


# ---------------------------------------------------------------- records + persistence
def section_document(section: Section, *, release: str, file_url: str, file_sha1: str,
                     retrieved_at: datetime) -> SourceDocument:
    payload = json.dumps({"citation": section.citation, "heading": section.heading,
                          "hierarchy": section.hierarchy, "text": section.body_text,
                          "annotations": section.annotations_text}, ensure_ascii=False, sort_keys=True)
    return SourceDocument(
        source_key=SOURCE_KEY,
        url=f"{file_url}#{section.number}",
        title=f"{section.citation}. {section.heading}",
        body=payload.encode("utf-8"),
        retrieved_at=retrieved_at,
        external_id=f"Public.Resource.Org OCGA {release} (as of {release_as_of(release)}); file sha1 {file_sha1}",
        content_type="application/json",
        metadata={"authority_type": "statute", "jurisdiction": "Georgia", "release": release},
        legal_status=LegalStatus(),  # currency unknown: a release date is not proof of currency
        extracted_text=section.body_text,
    )


def persist_section(db, section: Section, **kwargs) -> int:
    from ..models import AuthorityAnnotation

    document = section_document(section, **kwargs)
    saved = upsert_authority_document(db, document=document, jurisdiction="Georgia", authority_type="statute",
                                      citation=section.citation)
    digest = hashlib.sha256(document.body).hexdigest()
    exists = (db.query(AuthorityAnnotation)
              .filter_by(authority_id=saved.id, content_sha256=digest).one_or_none())
    if exists is None:
        db.add(AuthorityAnnotation(authority_id=saved.id, content_sha256=digest, release=kwargs["release"],
                                   hierarchy=" > ".join(section.hierarchy)[:1000] or None,
                                   annotations=section.annotations_text or None, source_url=document.url))
    db.flush()
    return saved.id


def require_annotation_table(session_factory) -> None:
    from sqlalchemy import inspect

    with session_factory() as db:
        if not inspect(db.get_bind()).has_table("authority_annotations"):
            raise SystemExit("authority_annotations table missing: apply "
                             "backend/migrations/20261004_authority_annotations.sql before --commit")


# ---------------------------------------------------------------- CLI
def _load_state(path):
    return json.loads(Path(path).read_text(encoding="utf-8")) if path and Path(path).exists() else {}


def _save_state(path, state):
    if path:
        tmp = Path(path).with_suffix(".tmp")
        tmp.write_text(json.dumps(state), encoding="utf-8")
        tmp.replace(path)


def main(argv: list[str] | None = None, *, fetch: Callable[[str], bytes] = fetch_bytes, session_factory=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--release", default=DEFAULT_RELEASE)
    parser.add_argument("--title", default="all", help="Comma list of title numbers (1-53) or 'all'")
    parser.add_argument("--limit", type=int, default=1000, help="Max sections this run (1-100000)")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many sections first")
    parser.add_argument("--state-file", help="JSON checkpoint for resuming (commit mode only)")
    parser.add_argument("--pause", type=float, default=2.0, help="Seconds between file downloads")
    parser.add_argument("--commit", action="store_true", help="Persist sections (default: preview only)")
    parser.add_argument("--quiet", action="store_true", help="Only print per-title and summary lines")
    args = parser.parse_args(argv)
    try:
        as_of = release_as_of(args.release)
        titles = TITLES if args.title == "all" else [f"{int(t):02d}" for t in args.title.split(",") if t.strip()]
    except ValueError as exc:
        parser.error(str(exc))
    if any(t not in TITLES for t in titles):
        parser.error("titles must be 1-53")
    if not 1 <= args.limit <= 100000 or args.offset < 0 or not 0.5 <= args.pause <= 60:
        parser.error("limit must be 1-100000, offset nonnegative, pause 0.5-60 seconds")
    if args.offset and args.state_file:
        parser.error("use either --offset or --state-file, not both")

    state = _load_state(args.state_file)
    if state.get("release") not in (None, args.release):
        parser.error(f"state file is for {state['release']}")
    state["release"] = args.release
    if args.commit and session_factory is None:
        from ..database import SessionLocal
        session_factory = SessionLocal
    if args.commit:
        require_annotation_table(session_factory)

    manifest = release_manifest(args.release, fetch)
    retrieved_at = datetime.now(timezone.utc)
    seen = handled = failed = 0
    totals = {"sections": 0, "placeholders_skipped": 0, "text_chars": 0, "annotation_chars": 0}
    started = time.time()
    done_titles = set(state.get("titles_done", []))
    for title in titles:
        if title in done_titles or handled >= args.limit:
            continue
        name = title_file(title)
        published = manifest.get(name)
        if not published or not published.get("sha1"):
            print(json.dumps({"mode": "error", "title": title, "error": "file not in release manifest"}), flush=True)
            failed += 1
            continue
        file_url = f"{DOWNLOAD_BASE}{args.release}/{name}"
        body = fetch(file_url)
        sha1 = hashlib.sha1(body).hexdigest()  # noqa: S324 - matches the archive's published checksum
        if sha1 != published["sha1"]:
            print(json.dumps({"mode": "error", "title": title, "error": "sha1 mismatch", "file_url": file_url}), flush=True)
            failed += 1
            continue
        sections = list(parse_title(odt_paragraphs(body)))
        title_counts = {"sections": len(sections), "placeholders": 0}
        position = int(state.get("position", 0)) if state.get("current_title") == title else 0
        state["current_title"] = title
        for idx, section in enumerate(sections):
            if idx < position:
                continue
            if section.placeholder:
                title_counts["placeholders"] += 1
                totals["placeholders_skipped"] += 1
                continue
            seen += 1
            if seen <= args.offset:
                continue
            if handled >= args.limit:
                break
            line = {"mode": "committed" if args.commit else "preview", "citation": section.citation,
                    "heading": section.heading[:120], "hierarchy": section.hierarchy,
                    "text_chars": len(section.body_text), "annotation_chars": len(section.annotations_text)}
            try:
                if args.commit:
                    with session_factory() as db:
                        try:
                            line["authority_id"] = persist_section(db, section, release=args.release, file_url=file_url,
                                                                   file_sha1=sha1, retrieved_at=retrieved_at)
                            db.commit()
                        except Exception:
                            db.rollback()
                            raise
                    state["position"] = idx + 1
                    _save_state(args.state_file, state)
            except Exception as exc:
                failed += 1
                line = {"mode": "error", "citation": section.citation, "error_type": type(exc).__name__}
            handled += 1
            totals["sections"] += 1
            totals["text_chars"] += len(section.body_text)
            totals["annotation_chars"] += len(section.annotations_text)
            if not args.quiet:
                print(json.dumps(line, ensure_ascii=False), flush=True)
        else:
            state.setdefault("titles_done", []).append(title)
            state["current_title"], state["position"] = None, 0
            if args.commit:
                _save_state(args.state_file, state)
        print(json.dumps({"mode": "title", "title": title, "file_url": file_url, "sha1": sha1,
                          "bytes": len(body), **title_counts}), flush=True)
        time.sleep(args.pause)
    print(json.dumps({"summary": True, "source": f"archive.org/details/{ITEM}", "release": args.release,
                      "as_of": as_of, "titles": titles, "handled": handled, "failed": failed, **totals,
                      "committed": args.commit, "seconds": round(time.time() - started, 1)}), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
