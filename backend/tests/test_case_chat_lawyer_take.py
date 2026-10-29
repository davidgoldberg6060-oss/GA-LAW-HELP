import json

from app import case_chat_service

HITS = [{"citation": "O.C.G.A. § 9-3-33", "title": "Injuries to the person", "source_url": "https://law.example/9-3-33",
         "verification_status": "verified", "record_type": "statute"}]


def _grounded(payload):
    return lambda query, mode, ask_ai, db=None: dict(payload)


def _ai(payload, calls):
    def ask(prompt):
        calls.append(prompt)
        return json.dumps(payload)
    return ask


def _run(monkeypatch, grounded, ai_payload, message="What deadline applies to my injury claim?"):
    calls = []
    monkeypatch.setattr(case_chat_service, "grounded_legal_response", _grounded(grounded))
    result = case_chat_service.analyze_case_conversation(user_message=message, history=[], case_summary=None, ask_ai=_ai(ai_payload, calls))
    return result, calls


GROUNDED = {"analysis": "answer", "sections": {}, "authorities": HITS, "grounded_authority_count": 1}


def test_lawyer_take_grounded_in_verified_authorities(monkeypatch):
    result, calls = _run(monkeypatch, GROUNDED, {"lawyer_take": {"text": "Write down dates. Talk to a Georgia attorney soon.", "citations": ["O.C.G.A. § 9-3-33"]}})
    take = result["lawyer_take"]
    assert take["label"] == "If I Was Your Lawyer, I Would Say"
    assert take["disclaimer"] == "Not legal advice \u2014 this app is not your lawyer."
    assert take["citations"][0]["source_url"] == "https://law.example/9-3-33"
    assert len(calls) == 1 and "O.C.G.A. § 9-3-33" in calls[0]


def test_lawyer_take_dropped_when_citation_not_retrieved(monkeypatch):
    result, _ = _run(monkeypatch, GROUNDED, {"lawyer_take": {"text": "File now.", "citations": ["O.C.G.A. § 99-9-99"]}})
    assert result["lawyer_take"] is None


def test_no_lawyer_take_without_verified_sources(monkeypatch):
    unverified = {**GROUNDED, "authorities": [{**HITS[0], "verification_status": "unverified"}], "grounded_authority_count": 0}
    result, calls = _run(monkeypatch, unverified, {"lawyer_take": {"text": "x", "citations": ["O.C.G.A. § 9-3-33"]}})
    assert result["lawyer_take"] is None and calls == []
    result, calls = _run(monkeypatch, {**GROUNDED, "authorities": [], "grounded_authority_count": 0}, {})
    assert result["lawyer_take"] is None and calls == []


def test_no_lawyer_take_for_evasion_requests(monkeypatch):
    result, calls = _run(monkeypatch, GROUNDED, {"lawyer_take": {"text": "x", "citations": ["O.C.G.A. § 9-3-33"]}},
                         message="How do I avoid getting caught by police?")
    assert result["lawyer_take"] is None and calls == []


def test_lawyer_take_failure_never_breaks_answer(monkeypatch):
    monkeypatch.setattr(case_chat_service, "grounded_legal_response", _grounded(GROUNDED))
    def boom(prompt):
        raise RuntimeError("ai down")
    result = case_chat_service.analyze_case_conversation(user_message="What now?", history=[], case_summary=None, ask_ai=boom)
    assert result["analysis"] == "answer" and result["lawyer_take"] is None
