"""OCGA (Public.Resource.Org release) importer, using a tiny synthetic ODT in the release's layout."""
import hashlib
import io
import json
import zipfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ingestion import import_ocga_release as ocga
from app.models import AuthorityAnnotation, AuthorityVersion, LegalAuthority

STYLES = """<office:automatic-styles>
<style:style style:name="P1" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-size="16.0pt"/></style:style>
<style:style style:name="P2" style:family="paragraph"><style:paragraph-properties fo:margin-left="0.25in"/><style:text-properties fo:font-size="12.0pt"/></style:style>
<style:style style:name="P3" style:family="paragraph"><style:paragraph-properties fo:text-align="justify"/><style:text-properties fo:font-size="4.0pt"/></style:style>
<style:style style:name="P4" style:family="paragraph"><style:text-properties fo:font-size="10.0pt"/></style:style>
<style:style style:name="P5" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-size="14.0pt"/></style:style>
<style:style style:name="P6" style:family="paragraph"><style:paragraph-properties fo:text-align="justify"/><style:text-properties fo:font-size="12.0pt"/></style:style>
<style:style style:name="P7" style:family="paragraph"><style:text-properties fo:font-size="12.0pt"/></style:style>
</office:automatic-styles>"""

PARAS = [
    ("P1", "TITLE 99 Test Offenses"),
    ("P2", "CHAPTER 1 General Provisions"),
    ("P2", "99-1-1.<text:s/> Short title."),
    ("P2", "99-1-2.<text:s/> Definitions."),
    ("P3", "Annotations"),              # chapter-level notes right after the TOC
    ("P4", "Cross references."),
    ("P5", "CHAPTER 1 General Provisions"),
    ("P6", "99-1-1.<text:s/> Short title."),
    ("P3", "Text"),
    ("P7", "This title shall be known as the <text:span>“Test Code.”</text:span>"),
    ("P3", "History"),
    ("P7", "History.<text:line-break/>Ga. L. 2020, p. 1, § 1."),
    ("P3", "Annotations"),
    ("P4", "Editor’s notes."),
    ("P4", "See Smith v. State, 300 Ga. 1 (2016)."),
    ("P6", "99-1-2.<text:s/> [Repealed] Definitions."),
    ("P3", "History"),
    ("P7", "History.<text:line-break/>Repealed by Ga. L. 2021, p. 2."),
    ("P5", "CHAPTER 2 Weapons"),
    ("P5", "Article 1 General"),
    ("P6", "99-2-1.<text:s/> Carrying."),
    ("P3", "Text"),
    ("P7", "(a) No person shall carry."),
    ("P7", "(b) Exceptions apply."),
    ("P3", "History"),
    ("P7", "History.<text:line-break/>Ga. L. 2022, p. 3."),
    ("P5", "CHAPTER 3 Other"),
    ("P6", "99-3-1.1.<text:s/> Later section."),
    ("P3", "Text"),
    ("P7", "Text of 99-3-1.1."),
]


def make_odt(paras=PARAS):
    body = "".join(f'<text:p text:style-name="{s}">{t}</text:p>' for s, t in paras)
    xml = ('<?xml version="1.0" encoding="UTF-8"?><office:document-content '
           'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
           'xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" '
           'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" '
           'xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0">'
           f"{STYLES}<office:body><office:text>{body}</office:text></office:body></office:document-content>")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        archive.writestr("content.xml", xml)
    return buf.getvalue()


ODT = make_odt()
FILE_URL = "https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.16.odt"


def fake_fetch(body=ODT, sha1=None, seen=None):
    def fetch(url):
        if seen is not None:
            seen.append(url)
        if url == ocga.METADATA_URL:
            return json.dumps({"files": [{"name": "release86.2022.11/gov.ga.ocga.title.16.odt",
                                          "sha1": sha1 or hashlib.sha1(body).hexdigest()}]}).encode()
        assert url == FILE_URL
        return body
    return fetch


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(ocga.time, "sleep", lambda seconds: None)


def _lines(capsys):
    return [json.loads(line) for line in capsys.readouterr().out.splitlines()]


def _session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def no_db():
    raise AssertionError("preview must not open a database session")


def test_parser_builds_sections_with_hierarchy_text_history_and_annotations():
    sections = list(ocga.parse_title(ocga.odt_paragraphs(ODT)))
    assert [s.number for s in sections] == ["99-1-1", "99-1-2", "99-2-1", "99-3-1.1"]
    first, repealed, carrying, later = sections
    assert first.citation == "O.C.G.A. § 99-1-1" and first.heading == "Short title."
    assert first.hierarchy == ["Title 99 Test Offenses", "Chapter 1 General Provisions"]
    assert first.body_text == "This title shall be known as the “Test Code.”"
    assert first.history_text == "Ga. L. 2020, p. 1, § 1."
    assert first.annotations_text == "History. Ga. L. 2020, p. 1, § 1.\n\nEditor’s notes.\nSee Smith v. State, 300 Ga. 1 (2016)."
    assert repealed.placeholder and not first.placeholder
    assert carrying.hierarchy == ["Title 99 Test Offenses", "Chapter 2 Weapons", "Article 1 General"]
    assert carrying.body_text == "(a) No person shall carry.\n(b) Exceptions apply."
    # A new chapter drops the previous chapter's article.
    assert later.hierarchy == ["Title 99 Test Offenses", "Chapter 3 Other"]


def test_preview_is_default_verifies_sha1_and_never_touches_the_database(capsys):
    assert ocga.main(["--title", "16"], fetch=fake_fetch(), session_factory=no_db) == 0
    lines = _lines(capsys)
    assert [l["citation"] for l in lines if l.get("mode") == "preview"] == [
        "O.C.G.A. § 99-1-1", "O.C.G.A. § 99-2-1", "O.C.G.A. § 99-3-1.1"]
    summary = lines[-1]
    assert summary["placeholders_skipped"] == 1 and summary["committed"] is False and summary["as_of"] == "2022-11"


def test_sha1_mismatch_fails_closed(capsys):
    assert ocga.main(["--title", "16"], fetch=fake_fetch(sha1="0" * 40), session_factory=no_db) == 1
    lines = _lines(capsys)
    assert lines[0]["error"] == "sha1 mismatch" and lines[-1]["sections"] == 0


def test_commit_stores_text_and_separate_annotations_with_provenance_and_is_idempotent(capsys):
    Session = _session()
    assert ocga.main(["--title", "16", "--commit"], fetch=fake_fetch(), session_factory=Session) == 0
    assert ocga.main(["--title", "16", "--commit"], fetch=fake_fetch(), session_factory=Session) == 0
    with Session() as db:
        assert db.query(LegalAuthority).count() == 3
        assert db.query(AuthorityVersion).count() == 3 and db.query(AuthorityAnnotation).count() == 3
        row = db.query(LegalAuthority).filter_by(citation="O.C.G.A. § 99-1-1").one()
        assert row.text == "This title shall be known as the “Test Code.”"
        assert "Editor’s notes" not in row.text
        assert row.authority_type == "statute" and row.status == "UNVERIFIED" and row.currency_status == "unknown"
        assert row.source_url == FILE_URL + "#99-1-1"
        version = db.query(AuthorityVersion).filter_by(authority_id=row.id).one()
        assert version.version_label == ("Public.Resource.Org OCGA release86.2022.11 (as of 2022-11); "
                                         f"file sha1 {hashlib.sha1(ODT).hexdigest()}")
        assert version.effective_from is None  # a release date is not an effective date
        note = db.query(AuthorityAnnotation).filter_by(authority_id=row.id).one()
        assert note.release == "release86.2022.11" and note.content_sha256 == version.content_sha256
        assert note.hierarchy == "Title 99 Test Offenses > Chapter 1 General Provisions"
        assert note.annotations.startswith("History. Ga. L. 2020")


def test_state_file_resumes_and_preview_does_not_write_it(tmp_path, capsys):
    state = tmp_path / "state.json"
    Session = _session()
    ocga.main(["--title", "16", "--state-file", str(state)], fetch=fake_fetch(), session_factory=no_db)
    assert not state.exists()
    ocga.main(["--title", "16", "--commit", "--limit", "1", "--state-file", str(state)], fetch=fake_fetch(), session_factory=Session)
    assert json.loads(state.read_text())["current_title"] == "16"
    capsys.readouterr()
    ocga.main(["--title", "16", "--commit", "--state-file", str(state)], fetch=fake_fetch(), session_factory=Session)
    assert [l["citation"] for l in _lines(capsys) if l.get("mode") == "committed"] == [
        "O.C.G.A. § 99-2-1", "O.C.G.A. § 99-3-1.1"]
    assert json.loads(state.read_text())["titles_done"] == ["16"]
    seen = []
    ocga.main(["--title", "16", "--commit", "--state-file", str(state)], fetch=fake_fetch(seen=seen), session_factory=Session)
    assert seen == [ocga.METADATA_URL]  # finished titles are not downloaded again


def test_commit_requires_the_annotations_migration():
    engine = create_engine("sqlite://")
    LegalAuthority.__table__.create(engine)
    with pytest.raises(SystemExit, match="20261004_authority_annotations.sql"):
        ocga.main(["--title", "16", "--commit"], fetch=fake_fetch(), session_factory=sessionmaker(bind=engine))


def test_only_archive_org_and_valid_releases_are_accepted():
    with pytest.raises(ValueError):
        ocga.fetch_bytes("https://example.com/gov.ga.ocga.title.16.odt")
    with pytest.raises(ValueError):
        ocga.fetch_bytes("http://archive.org/metadata/gov.ga.ocga.2018")
    assert ocga._allowed("https://dn710803.ca.archive.org/0/items/gov.ga.ocga.2018/x.odt")
    assert not ocga._allowed("https://archive.org.evil.example/x")
    with pytest.raises(ValueError):
        ocga._NoOffsiteRedirect().redirect_request(None, None, 302, "", {}, "https://evil.example/x")
    with pytest.raises(SystemExit):
        ocga.main(["--release", "latest"], fetch=fake_fetch(), session_factory=no_db)
    with pytest.raises(SystemExit):
        ocga.main(["--title", "54"], fetch=fake_fetch(), session_factory=no_db)


def test_migration_matches_the_model():
    from pathlib import Path
    sql = (Path(__file__).resolve().parents[1] / "migrations/20261004_authority_annotations.sql").read_text()
    for column in AuthorityAnnotation.__table__.columns:
        assert column.name in sql
    assert "uq_authority_annotations_version UNIQUE (authority_id, content_sha256)" in sql
