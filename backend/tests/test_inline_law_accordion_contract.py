from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "android/app/src/main/java/help/galaw/standalone"


def test_android_citations_expand_inline_instead_of_opening_downloads():
    acc = (SRC / "LawAccordion.kt").read_text(encoding="utf-8")
    assert "collapse()" in acc and "if (wasOpen) return" in acc  # one open at a time; tap again closes
    assert "Loading full text" in acc and "View official source" in acc
    screens = (SRC / "GaScreens.kt").read_text(encoding="utf-8")
    assert screens.count("LawAccordion.toggle(") >= 2 and "Open official source ›" not in screens
    assert "LawAccordion.toggle(widget, cite)" in (SRC / "AnswerFormat.kt").read_text(encoding="utf-8")
    assert "LawAccordion.toggle(" in (SRC / "InternalLegalSearchActivity.kt").read_text(encoding="utf-8")


def test_web_citations_use_the_accordion():
    app = (ROOT / "src/App.tsx").read_text(encoding="utf-8")
    acc = (ROOT / "src/LawAccordion.tsx").read_text(encoding="utf-8")
    assert "/public/georgia-laws/law" in acc and "View official source" in acc and "aria-expanded" in acc
    assert app.count("<LawAccordion") >= 4
    assert "href={c.citation.source_url}" not in app
