"""Court of Appeals importer: official-source discovery, conservative filtering, preview default."""
import json
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ingestion import import_appeals_opinions as coa
from app.ingestion.acquisition import FetchResponse
from app.models import LegalAuthority


def _row(docket, style, ruling, pdf, when="September 29, 2026", cls="link-pdf"):
    return f"""<tr><td>{docket}</td><td>{style}</td><td>{when}</td><td>{ruling}</td>
    <td><a href='../results_one_record.php?docr_case_num={docket}' target='_blank'>Open Record</a></td>
    <td><a class='{cls}' href='{pdf}' target='_blank'>View PDF File</a></td></tr>"""


PDF = "https://efast.gaappeals.gov/download?filingId="
RESULTS = ("<h2>8 Results for dates 09-28-2026 thru 10-02-2026</h2><table><tr><th>Case Number</th></tr>"
           + _row("A26A1522", "DOE v. THE STATE", "AFFIRMED", PDF + "1")
           + _row("A26A1522", "DOE v. THE STATE", "AFFIRMED", PDF + "1")  # repeated identical row
           + _row("A26A1558", "ROE v. SMITH", "VACATED & CASE REMANDED", PDF + "2")
           + _row("A26A1559", "ROE v. SMITH", "AFFIRMED IN PART", PDF + "2")  # consolidated, same PDF
           + _row("A26A1108", "POE v. STATE", "REVERSED", PDF + "3")
           + _row("A26A1108", "POE v. STATE", "REVERSED", PDF + "4")  # ambiguous
           + _row("A27D0133", "APPLICANT v. CO", "DISCRETIONARY APPLICATION DENIED", PDF + "5")
           + _row("A27A0313", "INS CO v. EBY", "WITHDRAWN", PDF + "6")
           + _row("A27A0238", "X v. Y", "DISMISSED", PDF + "7")
           + _row("A26A0001", "EVIL v. LINK", "AFFIRMED", "https://example.com/fake.pdf")
           + "</table>").encode()


def _transport(calls, *, results=RESULTS, final_url=None):
    def transport(url):
        calls.append(url)
        if url.startswith(coa.SEARCH_URL):
            return FetchResponse(final_url or url, 200, {"Content-Type": "text/html; charset=UTF-8"}, results)
        assert url.startswith(PDF)
        return FetchResponse(url, 200, {"Content-Type": "application/pdf;charset=UTF-8"}, b"%PDF-1.4 opinion " + url.encode())
    return transport


def test_search_url_uses_the_official_get_form():
    url = coa.search_url(date(2026, 9, 28), date(2026, 10, 2))
    assert url == coa.SEARCH_URL + "?OPstartDate=2026-09-28&OPendDate=2026-10-02&submit=Start+Opinions+Search"


def test_discovery_filters_orders_merges_consolidated_and_skips_ambiguous():
    calls = []
    opinions, ambiguous = coa.discover(date(2026, 9, 28), date(2026, 10, 2), transport=_transport(calls))
    assert ambiguous == ["A26A1108"]
    by_docket = {o.docket: o for o in opinions}
    assert set(by_docket) == {"A26A1522", "A26A1558, A26A1559"}
    assert by_docket["A26A1558, A26A1559"].ruling == "VACATED & CASE REMANDED; AFFIRMED IN PART"
    assert all(o.url.startswith(PDF) for o in opinions)  # external link ignored
    with_orders, _ = coa.discover(date(2026, 9, 28), date(2026, 10, 2), include_orders=True, transport=_transport([]))
    assert {"A27D0133", "A27A0313", "A27A0238"} <= {o.docket for o in with_orders}


def test_long_ranges_are_split_into_bounded_windows():
    assert list(coa.windows(date(2026, 1, 1), date(2026, 3, 5))) == [
        (date(2026, 1, 1), date(2026, 1, 31)), (date(2026, 2, 1), date(2026, 3, 3)), (date(2026, 3, 4), date(2026, 3, 5)),
    ]
    with pytest.raises(ValueError):
        coa.discover_window(date(2026, 1, 1), date(2026, 3, 1), _transport([]))


def test_fails_closed_on_redirect_off_host_or_unexpected_layout():
    with pytest.raises(ValueError, match="redirected outside"):
        coa.discover_window(date(2026, 9, 28), date(2026, 10, 2), _transport([], final_url="https://www.gaappeals.us/x"))
    with pytest.raises(ValueError, match="Unexpected opinion search layout"):
        coa.discover_window(date(2026, 9, 28), date(2026, 10, 2), _transport([], results=b"<p>maintenance</p>"))


def test_preview_is_default_and_never_touches_the_database(capsys, monkeypatch):
    monkeypatch.setattr(coa.time, "sleep", lambda s: None)
    def no_db():
        raise AssertionError("preview must not open a database session")
    rc = coa.main(["--start", "2026-09-28", "--end", "2026-10-02", "--pause", "0.5"], transport=_transport([]), session_factory=no_db)
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert rc == 0
    assert {l["mode"] for l in lines if "mode" in l} == {"skipped", "preview"}
    assert all(l["citation"].endswith("[UNVERIFIED DOCUMENT ID]") for l in lines if l.get("mode") == "preview")
    assert lines[-1]["committed"] is False and lines[-1]["succeeded"] == 2


def test_commit_persists_unverified_records_with_unknown_status(monkeypatch):
    monkeypatch.setattr(coa.time, "sleep", lambda s: None)
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    rc = coa.main(["--start", "2026-09-28", "--end", "2026-10-02", "--commit"], transport=_transport([]), session_factory=Session)
    assert rc == 0
    with Session() as db:
        rows = db.query(LegalAuthority).order_by(LegalAuthority.citation).all()
        assert [r.citation for r in rows] == ["A26A1522 [UNVERIFIED DOCUMENT ID]", "A26A1558, A26A1559 [UNVERIFIED DOCUMENT ID]"]
        assert all(r.jurisdiction == "Georgia" and r.authority_type == "case_law" for r in rows)
        assert all(r.currency_status == "unknown" and r.precedential_status == "unknown" for r in rows)
        assert all(r.source_url.startswith(PDF) for r in rows)
    # Re-running is idempotent (upsert by citation).
    coa.main(["--start", "2026-09-28", "--end", "2026-10-02", "--commit"], transport=_transport([]), session_factory=Session)
    with Session() as db:
        assert db.query(LegalAuthority).count() == 2
