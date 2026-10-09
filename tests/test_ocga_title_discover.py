"""OCGA title inventory must stay on the archive manifest."""
import json

from backend.app.ingestion.import_ocga_release import discover_release, main


def test_discover_release_lists_title_checksums_without_downloading_odt():
    seen = []

    def fetch(url):
        seen.append(url)
        return json.dumps({
            "files": [
                {"name": "release86.2022.11/gov.ga.ocga.title.16.odt", "sha1": "a" * 40, "size": 10},
                {"name": "release86.2022.11/gov.ga.ocga.title.01.odt", "sha1": "b" * 40, "size": 11},
            ]
        }).encode()

    report = discover_release("release86.2022.11", fetch)
    assert seen == ["https://archive.org/metadata/gov.ga.ocga.2018"]
    assert report["committed"] is False
    assert report["title_files"] == 2
    assert report["titles"][0]["file"] == "gov.ga.ocga.title.01.odt"
    assert report["titles"][0]["url"].endswith("/gov.ga.ocga.title.01.odt")
    assert "not downloaded" in report["note"].lower() or "not stored" in report["note"].lower()


def test_discover_only_cannot_commit():
    try:
        main(["--discover-only", "--commit"], fetch=lambda url: b"{}")
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("discover-only --commit should fail")
