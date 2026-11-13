"""Live 2026-11-12: the fast model hit MAX_TOKENS on the broad defense answer and the trim cut inside 'O.C.G.A.'."""
from app.ai_assistant import trim_to_last_sentence, _gemini_profile
from app.defense_help import drop_empty_group_labels


def test_trim_drops_unfinished_bullet_instead_of_cutting_inside_citation():
    text = ("How it works in Georgia\nChallenging the evidence:\n• A motion to suppress under O.C.G.A. § 17-5-30 may help.\n\n"
            "Ways to lessen the outcome:\n• First Offender sentencing may apply for eligible defendants under O.C.G")
    out = trim_to_last_sentence(text)
    assert out.endswith("may help.\n\nWays to lessen the outcome:") or out.endswith("may help.")
    assert "under O." not in out.splitlines()[-1]


def test_trim_never_ends_on_an_abbreviation():
    out = trim_to_last_sentence("This is one full sentence that is long enough. It cites O.C.G.A.")
    assert out == "This is one full sentence that is long enough."
    assert trim_to_last_sentence("Complete.") == "Complete."


def test_empty_group_label_removed():
    a = "Challenging the evidence:\n• x.\n\nWays to lessen the outcome:\n\nMotions that could help\n• y"
    out = drop_empty_group_labels(a)
    assert "Ways to lessen the outcome:" not in out and "Challenging the evidence:" in out and "Motions that could help" in out


def test_fast_budget_leaves_room_for_thinking(monkeypatch):
    monkeypatch.delenv("GEMINI_FAST_MAX_OUTPUT_TOKENS", raising=False)
    assert _gemini_profile("q", "m", "fast")["max_output_tokens"] >= 4000
