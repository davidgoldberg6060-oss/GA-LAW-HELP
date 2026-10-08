"""Discover-only OCGA inventory must not download title text or open a database."""
import json

from backend.app.ingestion.import_ocga_release import discover_release, main


def test_discover_release_reads_metadata_only():
    calls = []

    def fetch(url):
        calls.append(url)
        return json.dumps({
            "files": [
                {"name": "release86.2022.11/gov.ga.ocga.title.16.odt", "sha1": "abc123", "size": "12"},
                {"name": "release86.2022.11/gov.ga.court.rules.odt", "sha1": "def456", "size": "9"},
            ]
        }).encode()

    report = discover_release("release86.2022.11", fetch)
    assert calls == ["https://archive.org/metadata/gov.ga.ocga.2018"]
    assert report["committed"] is False
    assert report["mode"] == "discover-only"
    assert report["title_files"] == 1
    assert report["titles"][0]["title"] == 16
    assert report["titles"][0]["sha1"] == "abc123"
    assert report["titles"][0]["url"].endswith("/release86.2022.11/gov.ga.ocga.title.16.odt")
    assert "gov.ga.court.rules.odt" in report["other_odt"]
    assert "01" in report["missing_titles"]
    assert "16" not in report["missing_titles"]


def test_discover_only_refuses_commit():
    try:
        main(["--discover-only", "--commit"], fetch=lambda url: b"{}")
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("discover-only --commit should fail")
