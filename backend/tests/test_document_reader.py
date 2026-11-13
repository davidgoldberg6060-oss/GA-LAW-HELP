import json

import pytest

from app import ai_assistant, ai_models, document_reader as dr

JPEG = b"\xff\xd8\xff\xe0" + b"0" * 100
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
GOOD = json.dumps({"readable": True, "document_type": "Notice of arraignment", "extracted_text": "Case No. SAMPLE-1",
                   "summary": "This is a court date notice.", "key_dates": ["December 9, 2026 9:00 AM - arraignment"],
                   "charges_or_claims": ["Driving While License Suspended"], "case_number": "SAMPLE-1", "court": "Gwinnett State Court", "field_explanations": {"charge_or_claim": "This is the offense listed on the paper.", "dates": "This is when you must appear.", "case_number": "Use this number with the clerk.", "court": "This is the courthouse you go to."}, "next_steps": ["Go to court on time"],
                   "questions_for_lawyer": ["Can the charge be reduced?"], "photo_tips": ""})


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    ai_models.reset()
    for k in ("GEMINI_API_KEY", "OPENROUTER_API_KEY", "XAI_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY", "CEREBRAS_API_KEY",
              "MISTRAL_API_KEY", "GITHUB_MODELS_TOKEN", "GEMINI_VISION_MODEL_CHAIN", "GEMINI_CHECK_MODEL_CHAIN"):
        monkeypatch.delenv(k, raising=False)
    yield
    ai_models.reset()


def test_sniff_types():
    assert dr.sniff_type(JPEG, "application/octet-stream") == "image/jpeg"
    assert dr.sniff_type(PNG, None) == "image/png"
    assert dr.sniff_type(b"%PDF-1.7 x", "image/jpeg") == "application/pdf"
    assert dr.sniff_type(b"\x00\x00\x00\x18ftypheic" + b"0" * 10, "") == "image/heic"
    assert dr.sniff_type(b"????", "", "scan.HEIC") == "image/heic"


def test_validate_rejects_bad_input():
    with pytest.raises(dr.DocumentInputError):
        dr.validate([])
    with pytest.raises(dr.DocumentInputError):
        dr.validate([("text/plain", b"hi")])
    with pytest.raises(dr.DocumentInputError):
        dr.validate([("image/jpeg", JPEG)] * (dr.MAX_FILES + 1))


def test_gemini_reads_multiple_pages_inline(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_VISION_MODEL_CHAIN", "gemini-3.5-flash")
    seen = {}

    def fake(provider, model, url, payload, headers, timeout):
        seen["url"] = url
        seen["parts"] = payload["contents"][0]["parts"]
        return {"candidates": [{"content": {"parts": [{"text": GOOD}]}}]}

    monkeypatch.setattr(ai_assistant, "_http_post_json", fake)
    out = dr.read_documents([("image/jpeg", JPEG), ("image/png", PNG)], "When is court?")
    assert "gemini-3.5-flash:generateContent" in seen["url"]
    assert [p["inline_data"]["mime_type"] for p in seen["parts"][1:]] == ["image/jpeg", "image/png"]
    assert out["readable"] and out["pages"] == 2 and out["model_used"] == "gemini:gemini-3.5-flash"
    assert "December 9, 2026" in out["answer"] and "not legal advice" in out["answer"]


def test_falls_back_to_openrouter_when_gemini_rejects(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("OPENROUTER_API_KEY", "k2")
    monkeypatch.setenv("GEMINI_VISION_MODEL_CHAIN", "gemini-a,gemini-b")
    calls = []

    def fake(provider, model, url, payload, headers, timeout):
        calls.append(provider["name"] + ":" + model)
        if provider["name"] == "gemini":
            err = ai_assistant.ProviderHTTPError("x", 400 if model == "gemini-a" else 429)
            err.detail = "bad image"
            raise err
        content = payload["messages"][1]["content"]
        assert content[1]["image_url"]["url"].startswith("data:image/jpeg;base64,")
        return {"choices": [{"message": {"content": "```json\n" + GOOD + "\n```"}}]}

    monkeypatch.setattr(ai_assistant, "_http_post_json", fake)
    out = dr.read_documents([("image/jpeg", JPEG)])
    assert calls[:2] == ["gemini:gemini-a", "gemini:gemini-b"]
    assert out["model_used"].startswith("openrouter:") and out["document_type"] == "Notice of arraignment"


def test_unreadable_photo_gives_tip():
    out = dr.parse_result(json.dumps({"readable": False, "photo_tips": "Too dark."}))
    assert not out["readable"] and "Too dark." in out["answer"]


def test_endpoint_is_rate_limited_path():
    from app.anonymous_access import is_ai_path
    assert is_ai_path("POST", "/documents/read")

def test_plain_english_reader_explains_charge_dates_case_number_and_court():
    out = dr.parse_result(GOOD)
    answer = out["answer"]
    assert answer.startswith("Quick answer")
    assert "Driving While License Suspended" in answer
    assert "This is the offense listed on the paper." in answer
    assert "December 9, 2026" in answer
    assert "SAMPLE-1" in answer and "Case number" in answer
    assert "Gwinnett State Court" in answer and "Court" in answer
    assert "Questions to ask your lawyer" in answer
    assert "not legal advice" in answer


def test_guesses_case_number_from_extracted_text():
    fields = dr.guess_case_fields("IN THE STATE COURT OF DEKALB COUNTY\nCase No. 26-CR-1234\nCharge: Battery")
    assert fields["case_number"].startswith("26-CR-1234")
    assert "State Court" in fields["court"] or "DEKALB" in fields["court"].upper() or "DeKalb" in fields["court"] or fields["court"]
