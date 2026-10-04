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


def test_visible_law_search_no_longer_uses_legacy_authority_search():
    """Release guard (inverted after migration, PR #117).

    MainActivity's Georgia Laws entry point was migrated off the legacy, login-gated
    searchAuthorities path to the free guest rights flow (POST /public/rights-assistant and
    GET /public/encounter via openGuestRights). It must not regress to the legacy search, and
    the corpus-only CaseLookupScreenModel is still not wired here.
    """
    text = MAIN.read_text(encoding="utf-8")
    start = text.index("private fun showLawSearch()")
    end = text.index("private fun showGuide", start)
    law_search = text[start:end]
    assert "searchAuthorities(" not in law_search
    assert "openGuestRights(" in law_search
    assert "CaseLookupScreenModel.search" not in law_search
