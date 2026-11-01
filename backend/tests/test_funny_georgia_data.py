"""Funny & Weird Georgia Laws data: every entry must be sourced (never invented)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANDROID = ROOT / "android/app/src/main/assets/funny_georgia.json"
WEB = ROOT / "src/funnyGeorgia.json"


def _data():
    return json.loads(ANDROID.read_text(encoding="utf-8"))


def test_android_and_web_copies_are_identical():
    assert json.loads(WEB.read_text(encoding="utf-8")) == _data()


def test_every_law_has_citation_and_https_source():
    laws = _data()["laws"]
    assert len(laws) >= 60
    for law in laws:
        for key in ("title", "summary", "citation", "jurisdiction", "category", "status"):
            assert law[key].strip(), (key, law)
        assert law["source_url"].startswith("https://"), law
    statutes = [l for l in laws if l["citation"].startswith("O.C.G.A. § ")]
    assert all("codes.findlaw.com/ga/" in l["source_url"] for l in statutes)
    assert len({l["citation"] for l in statutes}) == len(statutes)


def test_every_case_has_court_year_citation_and_https_source():
    cases = _data()["cases"]
    assert len(cases) >= 10
    for c in cases:
        assert c["name"].strip() and c["court"].strip() and c["citation"].strip() and c["summary"].strip()
        assert c["court"] in {"Court of Appeals of Georgia", "Supreme Court of Georgia"}
        assert 1800 < int(c["year"]) <= 2026
        assert c["source_url"].startswith("https://"), c


def test_known_myths_are_not_presented_as_law():
    text = json.dumps(_data()).lower()
    for myth in ("donkey", "bathtub", "ice cream cone", "ice-cream cone", "back pocket"):
        assert myth not in text


def test_android_screen_loads_asset_and_is_wired_for_guests():
    src = ROOT / "android/app/src/main/java/help/galaw/standalone"
    activity = (src / "FunnyLawsActivity.kt").read_text(encoding="utf-8")
    assert 'assets.open("funny_georgia.json")' in activity
    assert "Funny Cases" in activity and "Funny Laws" in activity
    assert "FunnyLawsActivity" in (src / "AuthActivity.kt").read_text(encoding="utf-8")
    assert "FunnyLawsActivity" in (ROOT / "android/app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
