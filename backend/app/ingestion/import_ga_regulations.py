"""Operator-run, resumable import of the Rules and Regulations of the State of Georgia.

Source: the Secretary of State's official portal, rules.sos.ga.gov (operated by Fastcase, the
designated publisher). Its robots.txt allows the per-department PDF downloads on
``/Download_pdf.aspx`` and asks for ``Crawl-delay: 2``, while it disallows the per-rule HTML pages
(``/gac/*-.*``) and search. So this importer reads only the download page and one PDF per
department, checks every URL against robots.txt before fetching, and waits at least the crawl
delay (default 5 s) between requests. It identifies itself with an honest User-Agent.

Each PDF holds a department's rules in order: ``Chapter``/``Subject`` headings, then each
``Rule N. Heading``, the rule text, and ``Cite as Ga. Comp. R. & Regs. R. N``, followed by its
``Authority:`` and ``History.`` notes. Every rule becomes one ``legal_authorities`` row keyed by
that printed citation. Authority/history notes and the Department > Chapter > Subject hierarchy go
to ``authority_annotations``. The effective date of the latest change printed in the rule's
history ("eff. <date>") is stored as the version's effective date. The compilation's "current
through" date and the PDF's SHA-256 are recorded in the version label. Records are
``official`` (acquired from the State's portal) with ``unknown`` currency. Rules printed only as
"Repealed."/"Reserved." are counted and not stored.

Preview by default; ``--commit`` persists. ``--state-file`` checkpoints finished departments and
the rule position in the current department (commit mode only).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .models import LegalStatus, SourceDocument
from .persistence import upsert_authority_document
from .security import assert_public_official_url

SOURCE_KEY = "ga_rules_regulations"
BASE = "https://rules.sos.ga.gov"
DOWNLOAD_PAGE = f"{BASE}/Download_pdf.aspx"
ROBOTS_URL = f"{BASE}/robots.txt"
USER_AGENT = "GA.LAW.HELP-corpus-import/1.0 (+https://github.com/davidgoldberg6060-oss/GA-LAW-HELP)"
MAX_PDF_BYTES = 150 * 1024 * 1024
MAX_PAGE_BYTES = 2 * 1024 * 1024

RULE_NO = r"\d+(?:-\d+)*-\.\d+(?:\.\d+)?[A-Za-z]?"
CITE = re.compile(rf"^Cite as Ga\. Comp\. R\. & Regs\. R\. ({RULE_NO})\s*$")
HEAD = re.compile(rf"^Rule ({RULE_NO})\.\s*(.*)$")
LEVEL = re.compile(r"^(Chapter|Subject) (\d+(?:-\d+)*)\.\s*(.*)$")
PLACEHOLDER = re.compile(r"^(?:Repealed|Reserved|Renumbered)\b", re.I)
EFF = re.compile(r"\beff\.\s+([A-Z][a-z]{2,8})\.?\s+(\d{1,2}),\s+(\d{4})")
MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
CURRENT_THROUGH = re.compile(r"Current through Rules and Regulations filed through ([A-Z][a-z]+ \d{1,2}, \d{4})")


# ---------------------------------------------------------------- polite fetching
class _OfficialRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        assert_public_official_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


@dataclass
class Fetched:
    url: str
    content_type: str
    body: bytes


def http_fetch(url: str, limit: int) -> Fetched:
    assert_public_official_url(url)
    opener = urllib.request.build_opener(_OfficialRedirect)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(request, timeout=180) as response:
        body = response.read(limit + 1)
        final = assert_public_official_url(response.geturl())
        ctype = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    if len(body) > limit:
        raise ValueError("document exceeds size limit")
    return Fetched(final, ctype, body)


class Robots:
    """robots.txt rules for one user agent, with ``*``/``$`` wildcards (RFC 9309).

    The standard library parser treats ``*`` literally, which would miss this site's
    ``Disallow: /gac/*-.*`` rule for per-rule pages.
    """

    def __init__(self, text: str, agent: str = USER_AGENT):
        groups: list[tuple[list[str], list[tuple[bool, str]], float | None]] = []
        agents: list[str] = []
        rules: list[tuple[bool, str]] = []
        delay: float | None = None
        last_was_agent = False
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            key, value = (part.strip() for part in line.split(":", 1))
            key = key.lower()
            if key == "user-agent":
                if not last_was_agent and agents:
                    groups.append((agents, rules, delay))
                    agents, rules, delay = [], [], None
                agents.append(value.lower())
                last_was_agent = True
                continue
            last_was_agent = False
            if key in ("allow", "disallow") and value:
                rules.append((key == "allow", value))
            elif key == "crawl-delay":
                try:
                    delay = float(value)
                except ValueError:
                    pass
        if agents:
            groups.append((agents, rules, delay))
        token = agent.split("/", 1)[0].lower()
        named = [g for g in groups if any(a != "*" and a in token for a in g[0])]
        chosen = named or [g for g in groups if "*" in g[0]]
        self.rules = [r for g in chosen for r in g[1]]
        delays = [g[2] for g in chosen if g[2] is not None]
        self.crawl_delay = max(delays) if delays else 0.0

    @staticmethod
    def _pattern(path: str) -> re.Pattern:
        anchored = path.endswith("$")
        body = re.escape(path[:-1] if anchored else path).replace(r"\*", ".*")
        return re.compile(body + ("$" if anchored else ""))

    def allowed(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        target = urllib.parse.unquote(parsed.path or "/") + (f"?{parsed.query}" if parsed.query else "")
        best: tuple[int, bool] | None = None
        for allow, path in self.rules:
            if self._pattern(path).match(target):
                candidate = (len(path), allow)
                if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and allow):
                    best = candidate
        return True if best is None else best[1]


class PoliteClient:
    """robots.txt-checked, crawl-delayed fetches from rules.sos.ga.gov."""

    def __init__(self, pause: float, fetch: Callable[[str, int], Fetched] = http_fetch, sleep=time.sleep):
        self._fetch, self._sleep = fetch, sleep
        self.robots = Robots(fetch(ROBOTS_URL, MAX_PAGE_BYTES).body.decode("utf-8", errors="replace"))
        self.pause = max(pause, self.robots.crawl_delay)
        self._last = time.monotonic()

    def get(self, url: str, limit: int) -> Fetched:
        if not self.robots.allowed(url):
            raise PermissionError(f"robots.txt disallows {url}")
        wait = self.pause - (time.monotonic() - self._last)
        if wait > 0:
            self._sleep(wait)
        try:
            return self._fetch(url, limit)
        finally:
            self._last = time.monotonic()


# ---------------------------------------------------------------- download page
@dataclass(frozen=True)
class Department:
    number: str
    name: str
    url: str


def parse_download_page(page: str) -> tuple[list[Department], str | None]:
    departments: dict[str, Department] = {}
    for href in re.findall(r'href="(\?st=GASOS[^"]*)"', page):
        query = urllib.parse.parse_qs(html.unescape(href)[1:])
        if query.get("dept") != ["Departments"] or not query.get("pdf"):
            continue
        label = query["pdf"][0]
        match = re.match(r"^Department (\d+) (.+)$", label)
        if not match:
            continue
        url = DOWNLOAD_PAGE + "?" + urllib.parse.urlencode(
            {k: v[0] for k, v in query.items()}, quote_via=urllib.parse.quote)
        departments.setdefault(match.group(1), Department(match.group(1), match.group(2).strip(), url))
    through = CURRENT_THROUGH.search(re.sub(r"\s+", " ", page))
    as_of = datetime.strptime(through.group(1), "%B %d, %Y").date().isoformat() if through else None
    return sorted(departments.values(), key=lambda d: int(d.number)), as_of


# ---------------------------------------------------------------- PDF parsing
@dataclass
class Rule:
    number: str
    heading: str
    hierarchy: list[str]
    text: str
    notes: str
    effective: str | None = None

    @property
    def citation(self) -> str:
        return f"Ga. Comp. R. & Regs. R. {self.number}"

    @property
    def placeholder(self) -> bool:
        return bool(PLACEHOLDER.match(self.heading.strip())) and not self.text.strip()


def pdf_text(body: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(body))
    if reader.is_encrypted:
        raise ValueError("encrypted PDF")
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def latest_effective(notes: str) -> str | None:
    dates = []
    for month, day, year in EFF.findall(notes):
        number = MONTHS.get(month[:3].lower())
        if number:
            try:
                dates.append(datetime(int(year), number, int(day)).date())
            except ValueError:
                continue
    return max(dates).isoformat() if dates else None


def parse_rules(text: str, department: Department) -> tuple[list[Rule], int]:
    """Rules in document order and the number of citation lines that had no matching heading."""
    lines = [line.rstrip() for line in text.splitlines()]
    cites = [(i, m.group(1)) for i, line in enumerate(lines) if (m := CITE.match(line.strip()))]
    # (chapter, subject) in force at each line, from the nearest preceding headings.
    levels_at: list[tuple[str | None, str | None]] = []
    chapter = subject = None
    for line in lines:
        level = LEVEL.match(line.strip())
        if level:
            label = f"{level.group(1)} {level.group(2)}. {level.group(3).strip()}".strip()
            if level.group(1) == "Chapter":
                chapter, subject = label, None
            else:
                subject = label
        levels_at.append((chapter, subject))
    rules: list[Rule] = []
    unmatched = 0
    previous_end = 0
    for position, (ci, number) in enumerate(cites):
        hi = next((i for i in range(ci - 1, previous_end - 1, -1)
                   if (h := HEAD.match(lines[i].strip())) and h.group(1) == number), None)
        next_cite = cites[position + 1][0] if position + 1 < len(cites) else len(lines)
        # Notes run from the cite line to the next heading line (rule, chapter or subject).
        end = next((i for i in range(ci + 1, next_cite)
                    if HEAD.match(lines[i].strip()) or LEVEL.match(lines[i].strip())), next_cite)
        if hi is None:
            unmatched += 1
            previous_end = end
            continue
        heading_lines = [HEAD.match(lines[hi].strip()).group(2).strip()]
        body_start = hi + 1
        while not heading_lines[-1].endswith(".") and body_start < ci and len(heading_lines) < 3 and lines[body_start].strip():
            heading_lines.append(lines[body_start].strip())
            body_start += 1
        hierarchy = [f"Department {department.number}. {department.name}"] + [x for x in levels_at[hi] if x]
        body = "\n".join(line.strip() for line in lines[body_start:ci]).strip()
        notes = "\n".join(line.strip() for line in lines[ci + 1:end]).strip()
        rules.append(Rule(number, " ".join(heading_lines), hierarchy, re.sub(r"\n{3,}", "\n\n", body), notes,
                          latest_effective(notes)))
        previous_end = end
    return rules, unmatched


# ---------------------------------------------------------------- persistence
def rule_document(rule: Rule, *, pdf_url: str, pdf_sha256: str, as_of: str | None, checked_at: datetime) -> SourceDocument:
    payload = json.dumps({"citation": rule.citation, "heading": rule.heading, "hierarchy": rule.hierarchy,
                          "text": rule.text, "notes": rule.notes}, ensure_ascii=False, sort_keys=True)
    effective = datetime.fromisoformat(rule.effective).replace(tzinfo=timezone.utc) if rule.effective else None
    return SourceDocument(
        source_key=SOURCE_KEY,
        url=f"{pdf_url}#{rule.number}",
        title=f"{rule.citation}. {rule.heading}",
        body=payload.encode("utf-8"),
        retrieved_at=checked_at,
        effective_at=effective,
        external_id=f"GA SOS Rules and Regulations current through {as_of or 'unknown'}; pdf sha256 {pdf_sha256}",
        content_type="application/json",
        metadata={"authority_type": "regulation", "jurisdiction": "Georgia",
                  "rule_page": f"{BASE}/gac/{rule.number}"},
        legal_status=LegalStatus(verification_status="official", status_checked_at=checked_at,
                                 status_source_url=pdf_url),
        extracted_text=rule.text,
    )


def persist_rule(db, rule: Rule, **kwargs) -> int:
    from ..models import AuthorityAnnotation

    document = rule_document(rule, **kwargs)
    saved = upsert_authority_document(db, document=document, jurisdiction="Georgia",
                                      authority_type="regulation", citation=rule.citation)
    digest = hashlib.sha256(document.body).hexdigest()
    if db.query(AuthorityAnnotation).filter_by(authority_id=saved.id, content_sha256=digest).one_or_none() is None:
        db.add(AuthorityAnnotation(authority_id=saved.id, content_sha256=digest,
                                   release=f"GA SOS R&R through {kwargs.get('as_of') or 'unknown'}",
                                   hierarchy=" > ".join(rule.hierarchy)[:1000], annotations=rule.notes or None,
                                   source_url=document.url))
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


def main(argv: list[str] | None = None, *, fetch: Callable[[str, int], Fetched] = http_fetch,
         sleep=time.sleep, session_factory=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--department", default="all", help="Comma list of department numbers (e.g. 40,111) or 'all'")
    parser.add_argument("--limit", type=int, default=500, help="Max rules this run (1-200000)")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many rules first")
    parser.add_argument("--state-file", help="JSON checkpoint for resuming (commit mode only)")
    parser.add_argument("--pause", type=float, default=5.0, help="Seconds between requests (>= robots crawl-delay)")
    parser.add_argument("--commit", action="store_true", help="Persist rules (default: preview only)")
    parser.add_argument("--quiet", action="store_true", help="Only print per-department and summary lines")
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 200000 or args.offset < 0 or not 2 <= args.pause <= 60:
        parser.error("limit must be 1-200000, offset nonnegative, pause 2-60 seconds")
    if args.offset and args.state_file:
        parser.error("use either --offset or --state-file, not both")
    wanted = None if args.department == "all" else {d.strip() for d in args.department.split(",") if d.strip()}
    if wanted is not None and not all(d.isdigit() for d in wanted):
        parser.error("--department must be numbers or 'all'")

    if args.commit and session_factory is None:
        from ..database import SessionLocal
        session_factory = SessionLocal
    if args.commit:
        require_annotation_table(session_factory)

    client = PoliteClient(args.pause, fetch=fetch, sleep=sleep)
    page = client.get(DOWNLOAD_PAGE, MAX_PAGE_BYTES)
    if page.content_type != "text/html":
        raise SystemExit("download page did not return HTML")
    departments, as_of = parse_download_page(page.body.decode("utf-8", errors="replace"))
    if not departments:
        raise SystemExit("no department PDFs found on the download page; inspect its layout")
    selected = [d for d in departments if wanted is None or d.number in wanted]
    if wanted and len(selected) != len(wanted):
        parser.error(f"unknown department(s): {sorted(wanted - {d.number for d in selected})}")

    state = _load_state(args.state_file)
    if state.get("as_of") not in (None, as_of):
        print(json.dumps({"mode": "notice", "message": f"compilation moved from {state['as_of']} to {as_of}; restarting"}))
        state = {}
    state["as_of"] = as_of
    done = set(state.get("departments_done", []))
    checked_at = datetime.now(timezone.utc)
    seen = handled = failed = 0
    totals = {"rules": 0, "placeholders_skipped": 0, "unmatched_citations": 0, "text_chars": 0, "with_effective_date": 0}
    started = time.time()
    for department in selected:
        if department.number in done or handled >= args.limit:
            continue
        try:
            pdf = client.get(department.url, MAX_PDF_BYTES)
            if pdf.content_type != "application/pdf" or not pdf.body.startswith(b"%PDF"):
                raise ValueError(f"expected a PDF, got {pdf.content_type or 'unknown'}")
            rules, unmatched = parse_rules(pdf_text(pdf.body), department)
        except Exception as exc:
            failed += 1
            print(json.dumps({"mode": "error", "department": department.number, "error_type": type(exc).__name__,
                              "error": str(exc)[:200]}), flush=True)
            continue
        sha = hashlib.sha256(pdf.body).hexdigest()
        totals["unmatched_citations"] += unmatched
        position = int(state.get("position", 0)) if state.get("current") == department.number else 0
        state["current"] = department.number
        counts = {"rules": len(rules), "placeholders": 0, "unmatched_citations": unmatched}
        for idx, rule in enumerate(rules):
            if idx < position:
                continue
            if rule.placeholder:
                counts["placeholders"] += 1
                totals["placeholders_skipped"] += 1
                continue
            seen += 1
            if seen <= args.offset:
                continue
            if handled >= args.limit:
                break
            line = {"mode": "committed" if args.commit else "preview", "citation": rule.citation,
                    "heading": rule.heading[:120], "hierarchy": rule.hierarchy, "effective": rule.effective,
                    "text_chars": len(rule.text)}
            try:
                if args.commit:
                    with session_factory() as db:
                        try:
                            line["authority_id"] = persist_rule(db, rule, pdf_url=pdf.url, pdf_sha256=sha,
                                                                as_of=as_of, checked_at=checked_at)
                            db.commit()
                        except Exception:
                            db.rollback()
                            raise
                    state["position"] = idx + 1
                    _save_state(args.state_file, state)
            except Exception as exc:
                failed += 1
                line = {"mode": "error", "citation": rule.citation, "error_type": type(exc).__name__}
            handled += 1
            totals["rules"] += 1
            totals["text_chars"] += len(rule.text)
            totals["with_effective_date"] += bool(rule.effective)
            if not args.quiet:
                print(json.dumps(line, ensure_ascii=False), flush=True)
        else:
            state.setdefault("departments_done", []).append(department.number)
            state["current"], state["position"] = None, 0
            if args.commit:
                _save_state(args.state_file, state)
        print(json.dumps({"mode": "department", "department": department.number, "name": department.name,
                          "pdf_url": pdf.url, "sha256": sha, "bytes": len(pdf.body), **counts}), flush=True)
    print(json.dumps({"summary": True, "source": BASE, "current_through": as_of,
                      "departments_available": len(departments), "departments_selected": len(selected),
                      "handled": handled, "failed": failed, **totals, "pause_seconds": client.pause,
                      "committed": args.commit, "seconds": round(time.time() - started, 1)}), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
