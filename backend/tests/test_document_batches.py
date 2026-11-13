from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import document_batches as batches
from app import document_reader as dr
from app import ai_assistant, ai_models


def _db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def setup_function():
    batches._table_ready = False


def test_prior_context_empty():
    text, summarized = batches.prior_context([])
    assert text == "" and summarized is False


def test_prior_context_keeps_full_text_when_short():
    text, summarized = batches.prior_context([
        {"page_count": 3, "extracted_text": "Citation for speeding in Gwinnett.", "summary": "A traffic citation."},
    ])
    assert "Citation for speeding in Gwinnett." in text
    assert "same case" in text
    assert summarized is False


def test_prior_context_summarizes_when_too_long():
    long_text = "COUNT " + ("word " * 8000)
    text, summarized = batches.prior_context(
        [{"page_count": 10, "extracted_text": long_text, "summary": "First ten pages are a discovery packet."}],
        max_chars=2000,
    )
    assert summarized is True
    assert "First ten pages are a discovery packet." in text
    assert "summarized" in text
    assert long_text not in text
    assert len(text) <= 4000


def test_snapshot_merges_fields_in_order():
    snap = batches.snapshot_fields([
        {"page_count": 10, "document_type": "Citation", "case_number": "21-CR-1", "court": "Gwinnett State Court",
         "charges_or_claims": ["DUI"], "key_dates": ["Nov 1 arraignment"]},
        {"page_count": 4, "document_type": "Discovery", "charges_or_claims": ["DUI", "Open container"],
         "key_dates": ["Nov 1 arraignment", "Blood test date"]},
    ])
    assert snap["pages_earlier"] == 14
    assert snap["case_number"] == "21-CR-1"
    assert snap["charges_or_claims"] == ["DUI", "Open container"]
    assert snap["key_dates"] == ["Nov 1 arraignment", "Blood test date"]


def test_store_round_trip_is_scoped_to_user():
    db = _db()
    sid = batches.new_session_id()
    assert batches.load(db, 1, sid) == []
    assert batches.append(db, 1, sid, 3, {"extracted_text": "page one", "summary": "A citation"}) == 1
    assert batches.append(db, 1, sid, 2, {"extracted_text": "page four", "summary": "More papers"}) == 2
    rows = batches.load(db, 1, sid)
    assert [r["page_count"] for r in rows] == [3, 2]
    assert [r["extracted_text"] for r in rows] == ["page one", "page four"]
    assert batches.load(db, 99, sid) == []


def test_read_documents_includes_earlier_batch_context(monkeypatch):
    ai_models.reset()
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_VISION_MODEL_CHAIN", "gemini-3.5-flash")
    seen = {}
    good = (
        '{"readable": true, "document_type": "Discovery", "extracted_text": "Page 11 bodycam log",'
        ' "summary": "More discovery.", "key_dates": [], "charges_or_claims": [],'
        ' "case_number": "21-CR-1", "court": "Gwinnett State Court", "field_explanations": {},'
        ' "next_steps": [], "questions_for_lawyer": [], "photo_tips": ""}'
    )

    def fake(provider, model, url, payload, headers, timeout):
        seen["prompt"] = payload["contents"][0]["parts"][0]["text"]
        return {"candidates": [{"content": {"parts": [{"text": good}]}}]}

    monkeypatch.setattr(ai_assistant, "_http_post_json", fake)
    jpeg = b"\xff\xd8\xff\xe0" + b"0" * 100
    prior, _ = batches.prior_context([{"page_count": 10, "extracted_text": "First batch: DUI citation.", "summary": "A DUI citation."}])
    out = dr.read_documents([("image/jpeg", jpeg)], prior_context=prior)
    assert "First batch: DUI citation." in seen["prompt"]
    assert "same case" in seen["prompt"]
    assert out["pages"] == 1
    assert out["case_number"] == "21-CR-1"
