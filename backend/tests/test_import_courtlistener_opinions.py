"""CourtListener Georgia importer: small synthetic bulk fixtures in CourtListener's CSV format."""
import bz2
import csv
import io
import json
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ingestion import import_courtlistener_opinions as cl
from app.models import AuthorityVersion, LegalAuthority

DOCKETS = [("id", "court_id", "docket_number", "case_name"),
           ("1", "ga", "S24A0001", "Smith v. State"), ("2", "gactapp", "A24A0100", "Doe v. Roe"),
           ("3", "ga", "29652", "Old v. Case"), ("4", "nc", "S24A0001", "Not Georgia")]
CLUSTERS = [("id", "docket_id", "case_name", "case_name_full", "date_filed", "slug", "precedential_status"),
            ("10", "1", "Smith v. State", "", "2024-05-01", "smith-v-state", "Published"),
            ("11", "2", "Doe v. Roe", "", "2024-06-02", "doe-v-roe", "Unpublished"),
            ("12", "3", "Old v. Case", "", "1921-01-01", "old-v-case", "Published"),
            ("13", "4", "Not Georgia", "", "2024-01-01", "nope", "Published")]
CITATIONS = [("id", "volume", "reporter", "page", "type", "cluster_id"),
             ("1", "318", "Ga.", "5", "1", "10"), ("2", "900", "S.E.2d", "1", "3", "10"),
             ("3", "150", "Ga.", "3", "1", "12"), ("4", "1", "N.C.", "1", "1", "13")]
OPINIONS = [("id", "type", "plain_text", "html", "html_with_citations", "cluster_id"),
            ("100", "020lead", "", "", '<p>The trial court\'s "ruling" is</p>\n<p>AFFIRMED.</p>', "10"),
            ("101", "040dissent", "I dissent.", "", "", "10"),
            ("102", "010combined", "Judgment reversed.", "", "", "11"),
            ("103", "010combined", "Elsewhere.", "", "", "13"),
            ("104", "010combined", "", "", "", "12"),
            ("105", "015unamimous", "Second majority.", "", "", "11")]


def _write(path, rows):
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_ALL, escapechar="\\", doublequote=False)
    writer.writerows(rows)
    path.write_bytes(bz2.compress(buf.getvalue().encode("utf-8")))
    return str(path)


@pytest.fixture
def files(tmp_path):
    paths = {name: _write(tmp_path / f"{name}.csv.bz2", rows) for name, rows in
             (("dockets", DOCKETS), ("clusters", CLUSTERS), ("citations", CITATIONS), ("opinions", OPINIONS))}
    args = []
    for name, path in paths.items():
        args += [f"--{name}-file", path]
    return args, tmp_path


def _lines(capsys):
    return [json.loads(line) for line in capsys.readouterr().out.splitlines()]


def _session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def no_db():
    raise AssertionError("preview must not open a database session")


def test_preview_is_default_filters_georgia_and_keeps_only_majority_opinions(files, capsys):
    args, _ = files
    assert cl.main(args, session_factory=no_db) == 0
    lines = _lines(capsys)
    records = [l for l in lines if l.get("mode") == "preview"]
    assert [(r["cluster_id"], r["citation"], r["court"]) for r in records] == [
        ("10", "318 Ga. 5", "ga"), ("11", "A24A0100 [UNVERIFIED DOCUMENT ID]", "gactapp")]
    assert records[0]["source_url"] == "https://www.courtlistener.com/opinion/10/smith-v-state/"
    summary = lines[-1]
    assert summary["georgia_clusters"] == 3 and summary["committed"] is False
    assert summary["skips"] == {"skipped_separate_opinions": 1, "skipped_no_text": 1, "skipped_second_majority": 1}


def test_html_is_reduced_to_text_and_escaped_quotes_survive(files):
    args, _ = files
    index = cl.build_index(args[1], args[3], args[5])
    record = next(r for r in cl.stream_bulk_opinions(args[7], index, {}, "bulk-x") if r)
    assert record.text == 'The trial court\'s "ruling" is\n\nAFFIRMED.'


def test_commit_persists_unverified_records_and_reruns_are_idempotent(files, capsys):
    args, _ = files
    Session = _session()
    assert cl.main(args + ["--commit"], session_factory=Session) == 0
    assert cl.main(args + ["--commit"], session_factory=Session) == 0
    with Session() as db:
        rows = {r.citation: r for r in db.query(LegalAuthority).all()}
        assert set(rows) == {"318 Ga. 5", "A24A0100 [UNVERIFIED DOCUMENT ID]"}
        smith = rows["318 Ga. 5"]
        assert smith.status == "UNVERIFIED" and smith.currency_status == "unknown"
        assert smith.precedential_status == "unknown" and smith.authority_type == "case_law"
        assert db.query(AuthorityVersion).count() == 2
        version = db.query(AuthorityVersion).filter_by(authority_id=smith.id).one()
        assert version.version_label == "courtlistener:bulk-local:opinion:100"
        assert version.source_url == "https://www.courtlistener.com/opinion/10/smith-v-state/"


def test_official_records_win_over_courtlistener_duplicates(files, capsys):
    args, _ = files
    Session = _session()
    with Session() as db:
        db.add(LegalAuthority(jurisdiction="Georgia", authority_type="case_law",
                              citation="A24A0100 [UNVERIFIED DOCUMENT ID]", title="Doe v. Roe", text="official",
                              status="UNVERIFIED", source_url="https://efast.gaappeals.gov/download?filingId=1",
                              retrieved_at=datetime.now(timezone.utc), currency_status="unknown", precedential_status="unknown"))
        db.commit()
    cl.main(args + ["--commit"], session_factory=Session)
    outcomes = {l["cluster_id"]: l["outcome"] for l in _lines(capsys) if l.get("mode") == "committed"}
    assert outcomes == {"10": "committed", "11": "duplicate_of_official"}
    with Session() as db:
        doe = db.query(LegalAuthority).filter_by(citation="A24A0100 [UNVERIFIED DOCUMENT ID]").one()
        assert doe.text == "official" and "gaappeals" in doe.source_url


def test_state_file_resumes_and_preview_never_advances_it(files, capsys):
    args, tmp = files
    state = tmp / "state.json"
    Session = _session()
    cl.main(args + ["--state-file", str(state)], session_factory=no_db)
    assert not state.exists()
    cl.main(args + ["--commit", "--limit", "1", "--state-file", str(state)], session_factory=Session)
    saved = json.loads(state.read_text())
    assert saved["clusters_done"] == ["10"] and saved["rows_scanned"] == 1
    capsys.readouterr()
    cl.main(args + ["--commit", "--state-file", str(state)], session_factory=Session)
    assert [l["cluster_id"] for l in _lines(capsys) if l.get("mode") == "committed"] == ["11"]
    with pytest.raises(SystemExit):
        cl.main(args + ["--offset", "1", "--state-file", str(state)])


def test_index_cache_round_trips_and_is_tied_to_the_snapshot(files, tmp_path):
    args, _ = files
    cache = tmp_path / "cache" / "index.json"
    index = cl.build_index(args[1], args[3], args[5], courts=["ga"])
    cl.save_index(index, str(cache), "2026-09-30")
    loaded = cl.load_index(str(cache), "2026-09-30")
    assert set(loaded) == {"10", "12"} and loaded["10"].citations == ["318 Ga. 5"]
    assert cl.load_index(str(cache), "2026-12-31") is None
    assert cl.load_index(str(tmp_path / "missing.json"), "2026-09-30") is None


def test_main_reuses_the_index_cache(files, tmp_path, capsys, monkeypatch):
    args, _ = files
    cache = str(tmp_path / "index.json")
    cl.main(args + ["--index-cache", cache], session_factory=no_db)
    monkeypatch.setattr(cl, "build_index", lambda *a, **k: (_ for _ in ()).throw(AssertionError("rebuilt")))
    capsys.readouterr()
    cl.main(args + ["--index-cache", cache, "--court", "gactapp"], session_factory=no_db)
    assert [l["cluster_id"] for l in _lines(capsys) if l.get("mode") == "preview"] == ["11"]


def test_only_courtlistener_hosts_and_complete_snapshots_are_used():
    with pytest.raises(ValueError):
        cl.check_url("https://example.com/bulk-data/opinions-2026-09-30.csv.bz2")
    with pytest.raises(ValueError):
        cl.check_url("http://www.courtlistener.com/api/rest/v4/clusters/")
    listing = {
        "opinions": ["2026-06-30", "2026-09-30"], "opinion-clusters": ["2026-06-30", "2026-09-30"],
        "dockets": ["2026-06-30", "2026-09-30"], "citations": ["2026-06-30"]}

    def fetch(url):
        kind = next(k for k in listing if f"prefix=bulk-data%2F{k}-" in url)
        return "".join(f"<Key>bulk-data/{kind}-{d}.csv.bz2</Key>" for d in listing[kind])

    assert cl.latest_bulk_date(fetch) == "2026-06-30"
    assert cl.bulk_url("opinions", "2026-09-30") == cl.BULK_BASE + "opinions-2026-09-30.csv.bz2"


def test_api_mode_needs_token_and_checkpoints_the_cursor():
    with pytest.raises(ValueError):
        next(cl.stream_api_opinions("", ["ga"], {}, pause=1))
    pages = {
        "clusters1": {"results": [{"id": 10, "case_name": "Smith v. State", "date_filed": "2024-05-01", "docket_id": 1,
                                   "slug": "smith", "citations": [{"volume": 318, "reporter": "Ga.", "page": 5}]}],
                      "next": "https://www.courtlistener.com/api/rest/v4/clusters/?cursor=abc"},
        "clusters2": {"results": [], "next": None},
    }

    def fetch(url):
        if "clusters/?cursor=abc" in url:
            return pages["clusters2"]
        if "/clusters/" in url:
            assert "docket__court=ga" in url
            return pages["clusters1"]
        if "/dockets/1/" in url:
            return {"docket_number": "S24A0001"}
        if "/opinions/" in url:
            return {"results": [{"id": 101, "type": "040dissent", "plain_text": "x"},
                                {"id": 100, "type": "020lead", "plain_text": "Affirmed."}]}
        raise AssertionError(url)

    state = {}
    records = [r for r in cl.stream_api_opinions("tok", ["ga"], state, pause=1, fetch_json=fetch) if r]
    assert [(r.meta.citation, r.opinion_id, r.text) for r in records] == [("318 Ga. 5", "100", "Affirmed.")]
    assert state["api_next"] == {"ga": None} and state["clusters_done"] == ["10"]
