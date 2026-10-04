"""Georgia Rules and Regulations importer (rules.sos.ga.gov department PDFs), with synthetic fixtures."""
import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ingestion import import_ga_regulations as regs
from app.models import AuthorityAnnotation, AuthorityVersion, LegalAuthority

ROBOTS = """User-agent: GPTBot
Disallow: /

User-agent: *
Crawl-delay: 2
Disallow: /gac/*-.*
Disallow: /loadthedata.aspx
Disallow: /search/
"""

PAGE = """<html><body><span>Current through Rules and Regulations filed through
 September 2, 2026</span>
<a href="?st=GASOS&amp;year=2026&amp;dept=Departments&amp;pdf=Department 41 AGRICULTURAL COMMODITY COMMISSION FOR BEEF">Download</a>
<a href="?st=GASOS&amp;year=2026&amp;dept=Departments&amp;pdf=Department 41 AGRICULTURAL COMMODITY COMMISSION FOR BEEF">Download</a>
<a href="?st=GASOS&amp;year=2026&amp;dept=Departments&amp;pdf=Department 40 RULES OF GEORGIA DEPARTMENT OF AGRICULTURE">Download</a>
<a href="?st=GASOS&amp;dept=Bulletins&amp;pdf=2026-08 Georgia Monthly Bulletin for August 2026">Bulletin</a>
</body></html>"""

DEPT41 = """Rules and Regulations of the State of Georgia
Department 41 AGRICULTURAL
COMMODITY COMMISSION FOR BEEF
Table of Contents
Chapter 41-1. MARKETING ORDER FOR BEEF.
Rule 41-1-.01. Definitions.
Rule 41-1-.02. Product Affected.
Rule 41-1-.03. Repealed.
Chapter 41-1 entitled "Marketing Order for Beef" adopted. F. Jun. 16, 2014; eff. Jul. 6, 2014.
Cite as Ga. Comp. R. & Regs. R. dept. 41, ADMINISTRATIVE HISTORY
Chapter 41-1. MARKETING ORDER FOR BEEF.
Rule 41-1-.01. Definitions.
For the purpose of this Marketing Order, "Beef" means any bovine animal.
Cite as Ga. Comp. R. & Regs. R. 41-1-.01
Authority: O.C.G.A § 2-8-13.
History. Original Rule entitled "Definitions" adopted. F. Jun. 16, 2014; eff. July 6, 2014.
Amended: F. Jan. 3, 2020; eff. Jan. 23, 2020.
Rule 41-1-.02. Product Affected and Area of
Production Covered.
(1) Beef.
(2) The entire State of Georgia.
Cite as Ga. Comp. R. & Regs. R. 41-1-.02
Authority: O.C.G.A § 2-8-13.
History. Original Rule entitled "Product Affected" adopted. F. Jun. 16, 2014; eff. July 6, 2014.
Rule 41-1-.03. Repealed.
Cite as Ga. Comp. R. & Regs. R. 41-1-.03
History. Repealed: F. Feb. 1, 2016; eff. Feb. 21, 2016.
Chapter 41-2. ASSESSMENTS.
Subject 41-2-1. RATES.
Rule 41-2-1-.01. Rate.
One dollar per head.
Cite as Ga. Comp. R. & Regs. R. 41-2-1-.01
Authority: O.C.G.A § 2-8-15.
History. Original Rule entitled "Rate" adopted. F. and eff. June 30, 1965.
Cite as Ga. Comp. R. & Regs. R. 41-9-.99
"""

PDF41 = b"%PDF-1.7 dept41"


def make_fetch(seen=None, robots=ROBOTS, pdf=PDF41, ctype="application/pdf"):
    def fetch(url, limit):
        if seen is not None:
            seen.append(url)
        if url == regs.ROBOTS_URL:
            return regs.Fetched(url, "text/plain", robots.encode())
        if url == regs.DOWNLOAD_PAGE:
            return regs.Fetched(url, "text/html", PAGE.encode())
        assert url.startswith(regs.DOWNLOAD_PAGE + "?") and "Department%2041" in url, url
        return regs.Fetched(url, ctype, pdf)
    return fetch


@pytest.fixture(autouse=True)
def _fake_pdf_text(monkeypatch):
    monkeypatch.setattr(regs, "pdf_text", lambda body: DEPT41 if body == PDF41 else "")


def _lines(capsys):
    return [json.loads(line) for line in capsys.readouterr().out.splitlines()]


def _session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def no_db():
    raise AssertionError("preview must not open a database session")


def no_sleep(seconds):
    pass


def test_download_page_lists_departments_once_and_reads_the_current_through_date():
    departments, as_of = regs.parse_download_page(PAGE)
    assert [d.number for d in departments] == ["40", "41"]
    assert as_of == "2026-09-02"
    assert departments[1].url == (regs.DOWNLOAD_PAGE + "?st=GASOS&year=2026&dept=Departments&pdf="
                                  "Department%2041%20AGRICULTURAL%20COMMODITY%20COMMISSION%20FOR%20BEEF")


def test_parser_splits_rules_notes_hierarchy_and_latest_effective_date():
    dept = regs.Department("41", "AGRICULTURAL COMMODITY COMMISSION FOR BEEF", "u")
    rules, unmatched = regs.parse_rules(DEPT41, dept)
    assert unmatched == 1  # the stray cite line with no heading is reported, not guessed
    assert [r.number for r in rules] == ["41-1-.01", "41-1-.02", "41-1-.03", "41-2-1-.01"]
    first, second, repealed, rate = rules
    assert first.citation == "Ga. Comp. R. & Regs. R. 41-1-.01" and first.heading == "Definitions."
    assert first.text == 'For the purpose of this Marketing Order, "Beef" means any bovine animal.'
    assert first.notes.startswith("Authority: O.C.G.A § 2-8-13.\nHistory.")
    assert first.effective == "2020-01-23"
    assert first.hierarchy == ["Department 41. AGRICULTURAL COMMODITY COMMISSION FOR BEEF", "Chapter 41-1. MARKETING ORDER FOR BEEF."]
    assert second.heading == "Product Affected and Area of Production Covered."
    assert second.text == "(1) Beef.\n(2) The entire State of Georgia."
    assert repealed.placeholder and not first.placeholder
    assert rate.hierarchy[1:] == ["Chapter 41-2. ASSESSMENTS.", "Subject 41-2-1. RATES."]
    assert rate.effective == "1965-06-30"


def test_preview_is_default_respects_robots_crawl_delay_and_never_touches_the_database(capsys):
    seen, sleeps = [], []
    rc = regs.main(["--department", "41", "--pause", "2"], fetch=make_fetch(seen), sleep=sleeps.append, session_factory=no_db)
    lines = _lines(capsys)
    assert rc == 0
    assert [l["citation"] for l in lines if l.get("mode") == "preview"] == [
        "Ga. Comp. R. & Regs. R. 41-1-.01", "Ga. Comp. R. & Regs. R. 41-1-.02", "Ga. Comp. R. & Regs. R. 41-2-1-.01"]
    assert seen[0] == regs.ROBOTS_URL and seen[1] == regs.DOWNLOAD_PAGE and len(seen) == 3
    assert all(1.0 < s <= 2.0 for s in sleeps) and len(sleeps) == 2
    summary = lines[-1]
    assert summary["current_through"] == "2026-09-02" and summary["placeholders_skipped"] == 1
    assert summary["unmatched_citations"] == 1 and summary["committed"] is False


def test_robots_disallow_is_honoured_and_pause_is_raised_to_the_crawl_delay():
    client = regs.PoliteClient(2, fetch=make_fetch(robots=ROBOTS.replace("Crawl-delay: 2", "Crawl-delay: 9")), sleep=no_sleep)
    assert client.pause == 9
    with pytest.raises(PermissionError):
        client.get(regs.BASE + "/gac/41-1-.01", 100)
    with pytest.raises(PermissionError):
        client.get(regs.BASE + "/search/?q=beef", 100)
    blocked = regs.PoliteClient(2, fetch=make_fetch(robots="User-agent: *\nDisallow: /\n"), sleep=no_sleep)
    with pytest.raises(PermissionError):
        blocked.get(regs.DOWNLOAD_PAGE, 100)


def test_non_pdf_responses_fail_closed(capsys):
    rc = regs.main(["--department", "41"], fetch=make_fetch(ctype="text/html", pdf=b"<html>"), sleep=no_sleep, session_factory=no_db)
    lines = _lines(capsys)
    assert rc == 1 and lines[0]["mode"] == "error" and lines[-1]["rules"] == 0


def test_commit_persists_official_unknown_currency_rules_with_notes_and_is_idempotent(capsys):
    Session = _session()
    for _ in range(2):
        assert regs.main(["--department", "41", "--commit"], fetch=make_fetch(), sleep=no_sleep, session_factory=Session) == 0
    with Session() as db:
        assert db.query(LegalAuthority).count() == 3
        assert db.query(AuthorityVersion).count() == 3 and db.query(AuthorityAnnotation).count() == 3
        row = db.query(LegalAuthority).filter_by(citation="Ga. Comp. R. & Regs. R. 41-1-.01").one()
        assert row.authority_type == "regulation" and row.status == "OFFICIAL" and row.currency_status == "unknown"
        assert row.source_url.endswith("Department%2041%20AGRICULTURAL%20COMMODITY%20COMMISSION%20FOR%20BEEF#41-1-.01")
        assert "Authority:" not in row.text
        version = db.query(AuthorityVersion).filter_by(authority_id=row.id).one()
        assert str(version.effective_from) == "2020-01-23"
        assert version.version_label.startswith("GA SOS Rules and Regulations current through 2026-09-02; pdf sha256 ")
        note = db.query(AuthorityAnnotation).filter_by(authority_id=row.id).one()
        assert note.hierarchy.endswith("Chapter 41-1. MARKETING ORDER FOR BEEF.")
        assert note.annotations.startswith("Authority: O.C.G.A § 2-8-13.")


def test_state_file_resumes_and_preview_does_not_write_it(tmp_path, capsys):
    state = tmp_path / "state.json"
    Session = _session()
    regs.main(["--department", "41", "--state-file", str(state)], fetch=make_fetch(), sleep=no_sleep, session_factory=no_db)
    assert not state.exists()
    regs.main(["--department", "41", "--commit", "--limit", "1", "--state-file", str(state)],
              fetch=make_fetch(), sleep=no_sleep, session_factory=Session)
    capsys.readouterr()
    regs.main(["--department", "41", "--commit", "--state-file", str(state)], fetch=make_fetch(), sleep=no_sleep, session_factory=Session)
    assert [l["citation"] for l in _lines(capsys) if l.get("mode") == "committed"] == [
        "Ga. Comp. R. & Regs. R. 41-1-.02", "Ga. Comp. R. & Regs. R. 41-2-1-.01"]
    assert json.loads(state.read_text())["departments_done"] == ["41"]


def test_cli_guards():
    for argv in (["--pause", "1"], ["--department", "abc"], ["--offset", "2", "--state-file", "x"]):
        with pytest.raises(SystemExit):
            regs.main(argv, fetch=make_fetch(), sleep=no_sleep, session_factory=no_db)
    with pytest.raises(SystemExit):
        regs.main(["--department", "999"], fetch=make_fetch(), sleep=no_sleep, session_factory=no_db)
    with pytest.raises(ValueError):
        regs.http_fetch("https://example.com/Download_pdf.aspx", 10)


def test_robots_wildcards_follow_rfc9309():
    robots = regs.Robots(ROBOTS)
    assert robots.crawl_delay == 2
    assert not robots.allowed(regs.BASE + "/gac/40-1-1-.01")
    assert robots.allowed(regs.BASE + "/gac/40-1-1")
    assert robots.allowed(regs.DOWNLOAD_PAGE + "?st=GASOS&pdf=Department%2040%20X")
    assert not robots.allowed(regs.BASE + "/loadthedata.aspx")
    named = regs.Robots("User-agent: GA.LAW.HELP-corpus-import\nDisallow: /x$\n\nUser-agent: *\nDisallow: /\n")
    assert named.allowed(regs.BASE + "/xy") and not named.allowed(regs.BASE + "/x")
    tie = regs.Robots("User-agent: *\nDisallow: /a\nAllow: /a\n")
    assert tie.allowed(regs.BASE + "/a")
