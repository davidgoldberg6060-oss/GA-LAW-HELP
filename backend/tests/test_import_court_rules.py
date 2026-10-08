"""Georgia court rules importer: Court of Appeals HTML, robots-blocked PDFs, operator copies."""
import json
import urllib.error

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ingestion import import_court_rules as cr
from app.ingestion.import_ga_regulations import Fetched
from app.models import AuthorityAnnotation, AuthorityVersion, LegalAuthority

GS_ROBOTS = "User-agent: *\nDisallow: /wp-content/uploads/\nDisallow: /readme.html\n"
COA_ROBOTS = "User-agent: *\nDisallow: /wp-admin/\nAllow: /wp-admin/admin-ajax.php\n"
COA_INDEX = """<div class="entry-content"><a href="https://www.gaappeals.gov/rules-1-8/">Rules 1-8</a>
<a href="https://www.gaappeals.gov/rule-16/">Rule 16</a><a href="https://www.gaappeals.gov/rule-22/">Rule 22</a></div>"""
COA_1_8 = """<html><body><h3>Full Rules Menu</h3><div class="entry-content">
<p>These rules are effective on March 26, 2026.</p>
<h1 class="wp-block-heading">I. General</h1>
<h2 class="wp-block-heading">Rule 1. Clerk&#8217;s Office Hours and Location.</h2>
<p>The Clerk&#8217;s office shall be open Monday through Friday.</p>
<h2 class="wp-block-heading">Rule 2. Documents.</h2>
<p>(a) Requirement for Written Documents.</p><div class="inner"><p>All filings shall be in writing.</p></div>
</div><footer><p>Rule 99. Not a rule.</p></footer></body></html>"""
COA_16 = """<div class="entry-content"><h1>IV. Extension of Time for Filing</h1>
<h2>Rule 16. Extension of Time for Filing.</h2><p>(a) Notices of Appeal.</p></div>"""
COA_22 = """<div class="entry-content"><h2>Rule 22. Reserved.</h2></div>"""
OTHER = """<a href="/wp-content/uploads/2025/01/UNIFORM-SUPERIOR-COURT-RULES-2025_01_01.pdf">Old</a>
<a href="/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf">Rules</a>
<a href="/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf">Municipal Court</a>
<a href="/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf">Rules</a>"""
USC_TEXT = """UNIFORM RULES
TABLE OF CONTENTS
Rule 1. PREAMBLE ............................................ 1
Rule 2. DEFINITIONS .......................................... 3
Rule 6.4. Failure to Make Discovery
and Motion to Compel ......................................... 17
i
Rule 1. PREAMBLE
These rules are promulgated.
Amended effective September 19, 1986; October 7, 2010.
Rule 2. DEFINITIONS
Rule 2.1. Attorney
"Attorney" means a member of the State Bar.
17
Rule 6.4. Failure to Make Discovery and Motion to Compel Discovery
(A) Motions to compel shall quote the request. See
Rule 25 of these rules.
Rule 36.16 applies to records.
Amended effective November 28, 1996; amended effective May 15, 2014.
Rule 7. Reserved
"""
USC_PDF = b"%PDF-1.7 usc"


def make_fetch(seen=None, gs_robots=GS_ROBOTS, robots_error=None):
    pages = {
        "https://www.gaappeals.gov/robots.txt": COA_ROBOTS,
        "https://www.gasupreme.us/robots.txt": gs_robots,
        "https://www.gaappeals.gov/court-rules/": COA_INDEX,
        "https://www.gaappeals.gov/rules-1-8/": COA_1_8,
        "https://www.gaappeals.gov/rule-16/": COA_16,
        "https://www.gaappeals.gov/rule-22/": COA_22,
        cr.OTHER_RULES: OTHER,
    }

    def fetch(url, limit):
        if seen is not None:
            seen.append(url)
        if robots_error and url.endswith("/robots.txt") and "gasupreme" in url:
            raise urllib.error.HTTPError(url, robots_error, "x", {}, None)
        if url.endswith(".pdf"):
            return Fetched(url, "application/pdf", USC_PDF)
        return Fetched(url, "text/html", pages[url].encode())
    return fetch


@pytest.fixture(autouse=True)
def _fake_pdf(monkeypatch):
    monkeypatch.setattr(cr, "pdf_text", lambda body: USC_TEXT if body == USC_PDF else "")


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


def test_court_of_appeals_html_rules_parse_with_parts_and_set_effective_date():
    rules, effective = cr.parse_html_rules(COA_1_8, cr.RULE_SETS["coa"])
    assert effective == "2026-03-26"
    assert [(r.number, r.heading) for r in rules] == [("1", "Clerk’s Office Hours and Location."), ("2", "Documents.")]
    assert rules[1].text == "(a) Requirement for Written Documents.\nAll filings shall be in writing."
    assert rules[0].hierarchy == ["Rules of the Court of Appeals of the State of Georgia", "I. General"]
    assert rules[0].effective == "2026-03-26" and rules[0].citation(cr.RULE_SETS["coa"]) == "Ga. Ct. App. R. 1"


def test_pdf_rules_skip_the_table_of_contents_and_line_initial_cross_references():
    rules = cr.parse_pdf_rules(USC_TEXT, cr.RULE_SETS["superior"])
    assert [r.number for r in rules] == ["1", "2", "2.1", "6.4", "7"]
    first, parent, attorney, discovery, reserved = rules
    assert first.text == "These rules are promulgated." and first.effective == "2010-10-07"
    assert parent.placeholder and reserved.placeholder and not attorney.placeholder
    assert discovery.text.endswith("Rule 36.16 applies to records.")
    assert discovery.notes == "Amended effective November 28, 1996; amended effective May 15, 2014."
    assert discovery.effective == "2014-05-15"


def test_preview_imports_coa_and_reports_robots_blocked_pdfs_without_fetching_them(capsys):
    seen = []
    assert cr.main(["--set", "coa,superior"], fetch=make_fetch(seen), sleep=no_sleep, session_factory=no_db) == 0
    lines = _lines(capsys)
    assert [l["citation"] for l in lines if l.get("mode") == "preview"] == [
        "Ga. Ct. App. R. 1", "Ga. Ct. App. R. 2", "Ga. Ct. App. R. 16"]
    blocked = next(l for l in lines if l.get("set") == "superior")
    assert blocked["status"] == "blocked_by_robots"
    assert blocked["pdf_url"] == "https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf"
    assert not any(url.endswith(".pdf") for url in seen)
    assert lines[-1]["blocked_by_robots"] == ["superior"] and lines[-1]["placeholders_skipped"] == 1



def test_municipal_and_business_indexes_name_official_pdfs_without_fetching_them(capsys):
    seen = []
    assert cr.main(["--set", "municipal,business"], fetch=make_fetch(seen), sleep=no_sleep, session_factory=no_db) == 0
    lines = _lines(capsys)
    blocked = {l["set"]: l for l in lines if l.get("status") == "blocked_by_robots"}
    assert blocked["municipal"]["pdf_url"].endswith("/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf")
    assert blocked["business"]["pdf_url"].endswith("/State-wide-Business-Court-Rules-2026_06_11.pdf")
    assert not any(url.endswith(".pdf") for url in seen)
    assert lines[-1]["blocked_by_robots"] == ["municipal", "business"]
    assert lines[-1]["committed"] is False

def test_operator_supplied_pdf_is_used_with_the_official_url_as_provenance(tmp_path, capsys):
    (tmp_path / "UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf").write_bytes(USC_PDF)
    Session = _session()
    assert cr.main(["--set", "superior", "--pdf-dir", str(tmp_path), "--commit"], fetch=make_fetch(),
                   sleep=no_sleep, session_factory=Session) == 0
    with Session() as db:
        rows = {r.citation: r for r in db.query(LegalAuthority).all()}
        assert set(rows) == {"Unif. Super. Ct. R. 1", "Unif. Super. Ct. R. 2.1", "Unif. Super. Ct. R. 6.4"}
        rule = rows["Unif. Super. Ct. R. 6.4"]
        assert rule.authority_type == "court_rule" and rule.status == "OFFICIAL" and rule.currency_status == "unknown"
        assert rule.source_url == ("https://www.gasupreme.us/wp-content/uploads/2026/04/"
                                   "UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf#rule-6.4")
        version = db.query(AuthorityVersion).filter_by(authority_id=rule.id).one()
        assert str(version.effective_from) == "2014-05-15"
        assert "operator-supplied copy of UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf" in version.version_label
        note = db.query(AuthorityAnnotation).filter_by(authority_id=rule.id).one()
        assert note.annotations.startswith("Amended effective November 28, 1996")


def test_robots_404_allows_and_5xx_blocks(capsys):
    cr.main(["--set", "superior"], fetch=make_fetch(robots_error=404), sleep=no_sleep, session_factory=no_db)
    assert [l["citation"] for l in _lines(capsys) if l.get("mode") == "preview"][0] == "Unif. Super. Ct. R. 1"
    with pytest.raises(PermissionError):
        cr.Client(3, fetch=make_fetch(robots_error=503), sleep=no_sleep).get(cr.OTHER_RULES)


def test_commit_is_idempotent_and_state_file_resumes(tmp_path, capsys):
    Session = _session()
    state = tmp_path / "state.json"
    cr.main(["--set", "coa", "--state-file", str(state)], fetch=make_fetch(), sleep=no_sleep, session_factory=no_db)
    assert not state.exists()
    cr.main(["--set", "coa", "--commit", "--limit", "1", "--state-file", str(state)], fetch=make_fetch(),
            sleep=no_sleep, session_factory=Session)
    capsys.readouterr()
    cr.main(["--set", "coa", "--commit", "--state-file", str(state)], fetch=make_fetch(), sleep=no_sleep, session_factory=Session)
    assert [l["citation"] for l in _lines(capsys) if l.get("mode") == "committed"] == ["Ga. Ct. App. R. 2", "Ga. Ct. App. R. 16"]
    cr.main(["--set", "coa", "--commit"], fetch=make_fetch(), sleep=no_sleep, session_factory=Session)
    with Session() as db:
        assert db.query(LegalAuthority).count() == 3 and db.query(AuthorityVersion).count() == 3
        row = db.query(LegalAuthority).filter_by(citation="Ga. Ct. App. R. 16").one()
        assert row.source_url == "https://www.gaappeals.gov/rule-16/#rule-16"


def test_pause_is_respected_and_hosts_are_allowlisted():
    sleeps = []
    client = cr.Client(3, fetch=make_fetch(), sleep=sleeps.append)
    client.get("https://www.gaappeals.gov/court-rules/")
    client.get("https://www.gaappeals.gov/rule-16/")
    assert sleeps and all(0 < s <= 3 for s in sleeps)
    with pytest.raises(ValueError):
        cr.http_fetch("https://example.com/rules/", 10)
    for argv in (["--set", "nope"], ["--pause", "1"], ["--offset", "1", "--state-file", "x"]):
        with pytest.raises(SystemExit):
            cr.main(argv, fetch=make_fetch(), sleep=no_sleep, session_factory=no_db)
