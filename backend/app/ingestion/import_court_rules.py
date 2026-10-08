"""Operator-run, resumable import of Georgia court rules from the courts' official sites.

Rule sets (``--set``):
- ``coa``: Rules of the Court of Appeals of Georgia, HTML pages on www.gaappeals.gov.
- ``supreme``: Rules of the Supreme Court of Georgia, PDF linked from www.gasupreme.us/rules/.
- ``superior``, ``state``, ``juvenile``, ``probate``, ``magistrate``, ``municipal``,
  ``business``: Uniform Rules and Statewide Business Court Rules, PDFs linked from
  www.gasupreme.us/other-court-rules/.

robots.txt is checked (with ``*`` wildcards) for every URL before it is fetched, and requests are
spaced at least ``--pause`` seconds apart (default 3 s). www.gasupreme.us disallows
``/wp-content/uploads/``, which is where the Supreme Court and Uniform Rules PDFs live, so those
PDFs are never fetched automatically: the importer reports them as ``blocked_by_robots`` with
their official URL. An operator may download them by hand and pass ``--pdf-dir``; a local file
with the official file name is then parsed, and the official URL is recorded as provenance next
to the local file's SHA-256.

Each rule becomes one ``legal_authorities`` row (``Ga. Ct. App. R. 16``, ``Unif. Super. Ct. R.
6.4``, ...), ``authority_type`` ``court_rule``, ``official`` with ``unknown`` currency. The
"Amended effective ..." history lines and the rule-set/part hierarchy go to
``authority_annotations``; the latest effective date printed for the rule (or the rule set's
stated effective date) becomes the version's effective date. "Reserved"/"Repealed" placeholders
are counted, not stored. Preview by default; ``--commit`` persists; ``--state-file`` resumes.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable

from .import_ga_regulations import Fetched, Robots, pdf_text, require_annotation_table
from .models import LegalStatus, SourceDocument
from .persistence import upsert_authority_document
from .security import assert_public_official_url

SOURCE_KEY = "ga_court_rules"
USER_AGENT = "GA.LAW.HELP-corpus-import/1.0 (+https://github.com/davidgoldberg6060-oss/GA-LAW-HELP)"
MAX_BYTES = 60 * 1024 * 1024
ALLOWED = {"www.gaappeals.gov", "gaappeals.gov", "www.gasupreme.us", "gasupreme.us"}
OTHER_RULES = "https://www.gasupreme.us/other-court-rules/"
OTHER_CODES = "https://www.gasupreme.us/other-codes-rules/"


@dataclass(frozen=True)
class RuleSet:
    key: str
    title: str
    prefix: str
    index: str
    pdf_pattern: str | None = None  # None: HTML rule pages (Court of Appeals)


RULE_SETS = {
    "coa": RuleSet("coa", "Rules of the Court of Appeals of the State of Georgia", "Ga. Ct. App. R.",
                   "https://www.gaappeals.gov/court-rules/"),
    "supreme": RuleSet("supreme", "Rules of the Supreme Court of the State of Georgia", "Ga. Sup. Ct. R.",
                       "https://www.gasupreme.us/rules/", r"SupremeCourtRules[^\"'/]*\.pdf"),
    "superior": RuleSet("superior", "Uniform Superior Court Rules", "Unif. Super. Ct. R.", OTHER_RULES,
                        r"UNIFORM-SUPERIOR-COURT-RULES[^\"'/]*\.pdf"),
    "state": RuleSet("state", "Uniform State Court Rules", "Unif. State Ct. R.", OTHER_RULES,
                     r"UNIFORM-STATE-COURT-RULES[^\"'/]*\.pdf"),
    "juvenile": RuleSet("juvenile", "Uniform Juvenile Court Rules", "Unif. Juv. Ct. R.", OTHER_RULES,
                        r"UNIFORM-JUVENILE-COURT-RULES[^\"'/]*\.pdf"),
    "probate": RuleSet("probate", "Uniform Probate Court Rules", "Unif. Prob. Ct. R.", OTHER_RULES,
                       r"UNIFORM-PROBATE-COURT-RULES[^\"'/]*\.pdf"),
    "magistrate": RuleSet("magistrate", "Uniform Magistrate Court Rules", "Unif. Mag. Ct. R.", OTHER_RULES,
                          r"UNIFORM-MAGISTRATE-COURT-RULES[^\"'/]*\.pdf"),
    "municipal": RuleSet("municipal", "Uniform Municipal Court Rules", "Unif. Mun. Ct. R.", OTHER_RULES,
                         r"UNIFORM-MUNICIPAL-COURT-RULES[^\"'/]*\.pdf"),
    "business": RuleSet("business", "Statewide Business Court Rules", "Statewide Bus. Ct. R.", OTHER_RULES,
                        r"State-wide-Business-Court-Rules[^\"'/]*\.pdf"),
}

DATE = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})"
NOTE_LINE = re.compile(r"^(?:Amended|Adopted|Effective|Renumbered|Repealed|Revised|Approved)\b.*\b\d{4}\b", re.I)
PLACEHOLDER = re.compile(r"^\[?(?:Reserved|Repealed)\b", re.I)
PDF_HEAD = re.compile(r"^Rule (\d+(?:\.\d+)*[A-Z]?)\.?(?:\s+(.*\S))?\s*$")
TOC_LINE = re.compile(r"\.{5,}\s*[0-9ivxlc]+\s*$", re.I)
FURNITURE = re.compile(r"^(?:[0-9]+|[ivxlc]+|_{5,})$", re.I)


# ---------------------------------------------------------------- polite multi-host client
def http_fetch(url: str, limit: int) -> Fetched:
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if host not in ALLOWED:
        raise ValueError(f"host not allowed: {host}")
    assert_public_official_url(url)

    class _Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if (urllib.parse.urlsplit(newurl).hostname or "").lower() not in ALLOWED:
                raise ValueError(f"redirect off official hosts: {newurl}")
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(_Redirect)
    with opener.open(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=120) as response:
        body = response.read(limit + 1)
        ctype = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        final = response.geturl()
    if len(body) > limit:
        raise ValueError("document exceeds size limit")
    return Fetched(final, ctype, body)


class Client:
    def __init__(self, pause: float, fetch=http_fetch, sleep=time.sleep):
        self._fetch, self._sleep, self.pause = fetch, sleep, pause
        self._robots: dict[str, Robots] = {}
        self._last = 0.0

    def _wait(self, host_pause: float):
        wait = max(self.pause, host_pause) - (time.monotonic() - self._last)
        if self._last and wait > 0:
            self._sleep(wait)

    def robots(self, url: str) -> Robots:
        parts = urllib.parse.urlsplit(url)
        host = parts.hostname or ""
        if host not in self._robots:
            self._wait(0)
            try:
                text = self._fetch(f"https://{host}/robots.txt", 512 * 1024).body.decode("utf-8", "replace")
            except urllib.error.HTTPError as exc:
                # RFC 9309: 4xx means no restrictions; anything else means stay away.
                text = "" if 400 <= exc.code < 500 else "User-agent: *\nDisallow: /\n"
            finally:
                self._last = time.monotonic()
            self._robots[host] = Robots(text)
        return self._robots[host]

    def allowed(self, url: str) -> bool:
        return self.robots(url).allowed(url)

    def get(self, url: str, limit: int = MAX_BYTES) -> Fetched:
        robots = self.robots(url)
        if not robots.allowed(url):
            raise PermissionError(f"robots.txt disallows {url}")
        self._wait(robots.crawl_delay)
        try:
            return self._fetch(url, limit)
        finally:
            self._last = time.monotonic()


# ---------------------------------------------------------------- parsing
@dataclass
class CourtRule:
    number: str
    heading: str
    hierarchy: list[str]
    text: str
    notes: str
    effective: str | None
    source_url: str | None = None

    def citation(self, rule_set: RuleSet) -> str:
        return f"{rule_set.prefix} {self.number}"

    @property
    def placeholder(self) -> bool:
        # Reserved/repealed rules, and parent headings with no text of their own ("Rule 24. DOMESTIC RELATIONS").
        return not self.text.strip() or (bool(PLACEHOLDER.match(self.heading.strip())) and len(self.text.strip()) < 40)


def latest_date(text: str) -> str | None:
    found = []
    for month, day, year in re.findall(DATE, text):
        try:
            found.append(datetime.strptime(f"{month} {day} {year}", "%B %d %Y").date())
        except ValueError:
            continue
    return max(found).isoformat() if found else None


def _key(number: str) -> tuple:
    return tuple(int(p) if p.isdigit() else p for p in re.findall(r"\d+|[A-Z]", number))


def _plausible_next(candidate: tuple, last: tuple, heading: str) -> bool:
    """A real heading continues the numbering; line-initial cross references usually do not."""
    if heading[:1].islower():
        return False  # "Rule 25 of these rules ..." wrapped onto a new line
    if not last:
        return True
    if candidate[0] == last[0]:
        return candidate > last
    return isinstance(candidate[0], int) and isinstance(last[0], int) and 0 < candidate[0] - last[0] <= 5


def parse_pdf_rules(text: str, rule_set: RuleSet) -> list[CourtRule]:
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln and not FURNITURE.match(ln)]
    toc_end = max((i for i, ln in enumerate(lines) if TOC_LINE.search(ln)), default=-1)
    rules: list[CourtRule] = []
    current: dict | None = None
    last_key: tuple = ()
    for line in lines[toc_end + 1:]:
        head = PDF_HEAD.match(line)
        if head and _plausible_next(_key(head.group(1)), last_key, head.group(2) or ""):
            if current:
                rules.append(_finish(current, rule_set))
            last_key = _key(head.group(1))
            current = {"number": head.group(1), "heading": (head.group(2) or "").strip(), "lines": []}
            continue
        if current:
            current["lines"].append(line)
    if current:
        rules.append(_finish(current, rule_set))
    return rules


def _finish(raw: dict, rule_set: RuleSet, default_effective: str | None = None) -> CourtRule:
    body = list(raw["lines"])
    notes: list[str] = []
    while body and NOTE_LINE.match(body[-1]):
        notes.insert(0, body.pop())
    note_text = "\n".join(notes)
    return CourtRule(raw["number"], raw["heading"], [rule_set.title] + raw.get("parts", []),
                     "\n".join(body).strip(), note_text, latest_date(note_text) or default_effective)


class _Blocks(HTMLParser):
    """(tag, text) blocks inside the WordPress ``entry-content`` div."""

    BLOCK = {"h1", "h2", "h3", "h4", "p", "li", "td", "blockquote", "pre"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.inside = False
        self.blocks: list[tuple[str, str]] = []
        self._tag: str | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            if self.inside:
                self.depth += 1
            elif "entry-content" in (dict(attrs).get("class") or "").split():
                self.inside, self.depth = True, 1
        if self.inside and tag in self.BLOCK:
            self._flush()
            self._tag = tag
        if self.inside and tag == "br":
            self._buf.append("\n")

    def handle_endtag(self, tag):
        if self.inside and tag in self.BLOCK:
            self._flush()
        if tag == "div" and self.inside:
            self.depth -= 1
            if self.depth == 0:
                self._flush()
                self.inside = False

    def handle_data(self, data):
        if self.inside:
            self._buf.append(data)

    def _flush(self):
        text = re.sub(r"[ \t\xa0]+", " ", "".join(self._buf)).strip()
        if text:
            self.blocks.append((self._tag or "p", text))
        self._buf, self._tag = [], None


HTML_HEAD = re.compile(r"^Rule (\d+(?:\.\d+)*[A-Z]?)\.?\s*(.*)$")


def parse_html_rules(page: str, rule_set: RuleSet) -> tuple[list[CourtRule], str | None]:
    parser = _Blocks()
    parser.feed(page)
    effective = None
    for _, text in parser.blocks:
        m = re.search(rf"These rules are effective on {DATE}", text)
        if m:
            effective = datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y").date().isoformat()
            break
    rules: list[CourtRule] = []
    part: list[str] = []
    current: dict | None = None
    for tag, text in parser.blocks:
        if tag == "h1":
            part = [text]
            continue
        head = HTML_HEAD.match(text) if tag in ("h2", "h3") else None
        if head:
            if current:
                rules.append(_finish(current, rule_set, effective))
            current = {"number": head.group(1), "heading": head.group(2).strip(), "lines": [], "parts": list(part)}
            continue
        if current:
            current["lines"].append(text)
    if current:
        rules.append(_finish(current, rule_set, effective))
    return rules, effective


def coa_pages(index_html: str) -> list[str]:
    pages = re.findall(r'href="(https://www\.gaappeals\.gov/rules?-[0-9][0-9-]*/)"', index_html)
    return sorted(set(pages), key=lambda u: [int(n) for n in re.findall(r"\d+", u)])


def find_pdf(index_html: str, rule_set: RuleSet, base: str) -> str | None:
    hrefs = [html.unescape(h) for h in re.findall(r'href="([^"]+\.pdf)"', index_html, re.I)]
    matches = [h for h in hrefs if re.search(rule_set.pdf_pattern, h)]
    return urllib.parse.urljoin(base, sorted(matches)[-1]) if matches else None


# ---------------------------------------------------------------- persistence
def rule_document(rule: CourtRule, rule_set: RuleSet, *, url: str, sha256: str, provenance: str,
                  checked_at: datetime) -> SourceDocument:
    payload = json.dumps({"citation": rule.citation(rule_set), "heading": rule.heading, "hierarchy": rule.hierarchy,
                          "text": rule.text, "notes": rule.notes}, ensure_ascii=False, sort_keys=True)
    effective = datetime.fromisoformat(rule.effective).replace(tzinfo=timezone.utc) if rule.effective else None
    return SourceDocument(
        source_key=SOURCE_KEY, url=f"{rule.source_url or url}#rule-{rule.number}",
        title=f"{rule.citation(rule_set)}. {rule.heading}".strip(), body=payload.encode("utf-8"),
        retrieved_at=checked_at, effective_at=effective,
        external_id=f"{rule_set.title}; {provenance}; sha256 {sha256}"[:255],
        content_type="application/json",
        metadata={"authority_type": "court_rule", "jurisdiction": "Georgia", "rule_set": rule_set.key},
        legal_status=LegalStatus(verification_status="official", status_checked_at=checked_at,
                                 status_source_url=rule.source_url or url),
        extracted_text=rule.text)


def persist_rule(db, rule: CourtRule, rule_set: RuleSet, **kwargs) -> int:
    from ..models import AuthorityAnnotation

    document = rule_document(rule, rule_set, **kwargs)
    saved = upsert_authority_document(db, document=document, jurisdiction="Georgia", authority_type="court_rule",
                                      citation=rule.citation(rule_set))
    digest = hashlib.sha256(document.body).hexdigest()
    if db.query(AuthorityAnnotation).filter_by(authority_id=saved.id, content_sha256=digest).one_or_none() is None:
        db.add(AuthorityAnnotation(authority_id=saved.id, content_sha256=digest, release=kwargs["provenance"][:100],
                                   hierarchy=" > ".join(rule.hierarchy)[:1000], annotations=rule.notes or None,
                                   source_url=document.url))
    db.flush()
    return saved.id




def discover_other_codes(index_html: str, *, source_url: str, fetched_at: str, sha256: str,
                         index_bytes: int, robots_disallow_uploads: bool) -> dict:
    """Inventory the official other-codes-rules page without downloading PDFs.

    PDF links under /wp-content/uploads/ stay blocked when robots.txt disallows that path.
    Filenames are index labels, not effective dates and not stored rule text.
    """
    hrefs = [html.unescape(h) for h in re.findall(r'href="([^"]+\.pdf)"', index_html, re.I)]
    pdfs = []
    seen: set[str] = set()
    for href in hrefs:
        url = urllib.parse.urljoin(source_url, href)
        if url in seen:
            continue
        seen.add(url)
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
        if host not in {"www.gasupreme.us", "gasupreme.us"}:
            continue
        pdfs.append({
            "url": url,
            "file": urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1]),
            "downloaded": False,
            "gap": (
                "Named on the other-codes-rules index only. PDF not downloaded because "
                "robots.txt disallows /wp-content/uploads/. Filename is not an effective date "
                "and not stored rule text."
            ),
        })
    return {
        "mode": "discover-only",
        "source": source_url,
        "fetched_at": fetched_at,
        "index_sha256": sha256,
        "index_bytes": index_bytes,
        "pdf_links": len(pdfs),
        "pdfs": pdfs,
        "robots_disallow_uploads": robots_disallow_uploads,
        "committed": False,
        "note": "Index inventory only. No PDFs downloaded and no authority rows written.",
    }


# ---------------------------------------------------------------- CLI
def load_set(rule_set: RuleSet, client: Client, pdf_dir: str | None) -> dict:
    """Rules of one set plus provenance, or a ``blocked``/``error`` description."""
    index = client.get(rule_set.index)
    page = index.body.decode("utf-8", "replace")
    if rule_set.pdf_pattern is None:
        rules: list[CourtRule] = []
        effective = None
        sha = hashlib.sha256()
        pages = coa_pages(page)
        if not pages:
            return {"status": "error", "error": "no rule pages linked from the index"}
        for url in pages:
            fetched = client.get(url)
            sha.update(fetched.body)
            found, eff = parse_html_rules(fetched.body.decode("utf-8", "replace"), rule_set)
            effective = effective or eff
            for rule in found:
                rule.source_url = url  # the page the text came from
            rules.extend(found)
        return {"status": "ok", "rules": rules, "url": rule_set.index, "sha256": sha.hexdigest(),
                "provenance": f"official HTML pages, effective {effective or 'unknown'}", "pages": len(pages)}
    pdf_url = find_pdf(page, rule_set, rule_set.index)
    if not pdf_url:
        return {"status": "error", "error": "rules PDF not linked from the index"}
    name = urllib.parse.unquote(pdf_url.rsplit("/", 1)[-1])
    if client.allowed(pdf_url):
        body, how = client.get(pdf_url).body, "fetched"
    elif pdf_dir and (Path(pdf_dir) / name).is_file():
        body, how = (Path(pdf_dir) / name).read_bytes(), "operator-supplied copy"
    else:
        return {"status": "blocked_by_robots", "pdf_url": pdf_url,
                "hint": f"download by hand and pass --pdf-dir containing {name}"}
    if not body.startswith(b"%PDF"):
        return {"status": "error", "error": "not a PDF", "pdf_url": pdf_url}
    rules = parse_pdf_rules(pdf_text(body), rule_set)
    return {"status": "ok", "rules": rules, "url": pdf_url, "sha256": hashlib.sha256(body).hexdigest(),
            "provenance": f"{how} of {name}"}


def main(argv: list[str] | None = None, *, fetch=http_fetch, sleep=time.sleep, session_factory=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--set", default="all", help="Comma list of: " + ", ".join(RULE_SETS) + " (or 'all')")
    parser.add_argument("--discover-other-codes", action="store_true",
                        help="Inventory https://www.gasupreme.us/other-codes-rules/ only. Do not download PDFs or open a database.")
    parser.add_argument("--pdf-dir", help="Folder with hand-downloaded official PDFs (robots-blocked sets)")
    parser.add_argument("--limit", type=int, default=2000, help="Max rules this run (1-20000)")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many rules first")
    parser.add_argument("--state-file", help="JSON checkpoint for resuming (commit mode only)")
    parser.add_argument("--pause", type=float, default=3.0, help="Seconds between requests (2-60)")
    parser.add_argument("--commit", action="store_true", help="Persist rules (default: preview only)")
    parser.add_argument("--quiet", action="store_true", help="Only print per-set and summary lines")
    args = parser.parse_args(argv)
    if args.discover_other_codes and args.commit:
        parser.error("--discover-other-codes cannot be combined with --commit")
    if args.discover_other_codes:
        client = Client(args.pause, fetch=fetch, sleep=sleep)
        if not client.allowed(OTHER_CODES):
            print(json.dumps({"mode": "discover-only", "source": OTHER_CODES, "status": "blocked_by_robots",
                              "committed": False}), flush=True)
            return 1
        fetched = client.get(OTHER_CODES)
        robots = client.robots(OTHER_CODES)
        sample = "https://www.gasupreme.us/wp-content/uploads/other-codes-rules.pdf"
        report = discover_other_codes(
            fetched.body.decode("utf-8", "replace"),
            source_url=OTHER_CODES,
            fetched_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            sha256=hashlib.sha256(fetched.body).hexdigest(),
            index_bytes=len(fetched.body),
            robots_disallow_uploads=not robots.allowed(sample),
        )
        print(json.dumps(report), flush=True)
        return 0
    keys = list(RULE_SETS) if args.set == "all" else [k.strip() for k in args.set.split(",") if k.strip()]
    if not keys or any(k not in RULE_SETS for k in keys):
        parser.error("--set must list known rule sets: " + ", ".join(RULE_SETS))
    if not 1 <= args.limit <= 20000 or args.offset < 0 or not 2 <= args.pause <= 60:
        parser.error("limit must be 1-20000, offset nonnegative, pause 2-60 seconds")
    if args.offset and args.state_file:
        parser.error("use either --offset or --state-file, not both")
    if args.commit and session_factory is None:
        from ..database import SessionLocal
        session_factory = SessionLocal
    if args.commit:
        require_annotation_table(session_factory)

    state = json.loads(Path(args.state_file).read_text()) if args.state_file and Path(args.state_file).exists() else {}

    def save():
        if args.commit and args.state_file:
            Path(args.state_file).write_text(json.dumps(state))

    client = Client(args.pause, fetch=fetch, sleep=sleep)
    checked_at = datetime.now(timezone.utc)
    seen = handled = failed = 0
    blocked: list[str] = []
    totals = {"rules": 0, "placeholders_skipped": 0, "text_chars": 0}
    for key in keys:
        rule_set = RULE_SETS[key]
        if key in state.get("sets_done", []) or handled >= args.limit:
            continue
        try:
            loaded = load_set(rule_set, client, args.pdf_dir)
        except Exception as exc:
            loaded = {"status": "error", "error": f"{type(exc).__name__}: {str(exc)[:200]}"}
        if loaded["status"] != "ok":
            if loaded["status"] == "blocked_by_robots":
                blocked.append(key)
            else:
                failed += 1
            print(json.dumps({"mode": "set", "set": key, **loaded}), flush=True)
            continue
        rules = loaded["rules"]
        position = state.get("position", 0) if state.get("current") == key else 0
        state["current"] = key
        counts = {"rules": len(rules), "placeholders": 0}
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
            line = {"mode": "committed" if args.commit else "preview", "citation": rule.citation(rule_set),
                    "heading": rule.heading[:120], "effective": rule.effective, "text_chars": len(rule.text)}
            try:
                if args.commit:
                    with session_factory() as db:
                        try:
                            line["authority_id"] = persist_rule(db, rule, rule_set, url=loaded["url"],
                                                                sha256=loaded["sha256"], provenance=loaded["provenance"],
                                                                checked_at=checked_at)
                            db.commit()
                        except Exception:
                            db.rollback()
                            raise
                    state["position"] = idx + 1
                    save()
            except Exception as exc:
                failed += 1
                line = {"mode": "error", "citation": rule.citation(rule_set), "error_type": type(exc).__name__}
            handled += 1
            totals["rules"] += 1
            totals["text_chars"] += len(rule.text)
            if not args.quiet:
                print(json.dumps(line, ensure_ascii=False), flush=True)
        else:
            state.setdefault("sets_done", []).append(key)
            state["current"], state["position"] = None, 0
            save()
        print(json.dumps({"mode": "set", "set": key, "status": "ok", "url": loaded["url"], "sha256": loaded["sha256"],
                          "provenance": loaded["provenance"], **counts}), flush=True)
    print(json.dumps({"summary": True, "sets": keys, "handled": handled, "failed": failed,
                      "blocked_by_robots": blocked, **totals, "committed": args.commit}), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
