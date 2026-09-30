from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCREEN = ROOT / "android/app/src/main/java/help/galaw/standalone/CaseLookupScreenModel.kt"
MAIN = ROOT / "android/app/src/main/java/help/galaw/standalone/MainActivity.kt"


def test_case_lookup_screen_uses_internal_corpus_controller_and_renderer():
    text = SCREEN.read_text(encoding="utf-8")
    assert "CaseLookupController.lookup(api, rawQuery)" in text
    assert "CaseLookupRenderer.render(result)" in text
    assert "searchAuthorities(" not in text
    assert "publicAsk(" not in text
    assert "groundedLegalAssistant(" not in text


def test_visible_law_search_legacy_path_is_tracked_until_replaced():
    """Release guard: this should be inverted when MainActivity is migrated.

    Keeping this explicit prevents anyone from mistaking the new screen model for completed
    UI wiring. The next native migration must remove searchAuthorities from showLawSearch.
    """
    text = MAIN.read_text(encoding="utf-8")
    start = text.index("private fun showLawSearch()")
    end = text.index("private fun showGuide", start)
    law_search = text[start:end]
    assert "searchAuthorities(" in law_search
    assert "CaseLookupScreenModel.search" not in law_search
