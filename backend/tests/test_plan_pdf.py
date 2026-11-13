from app import language as lang
from app import plan_pdf


def test_pdf_starts_with_header_and_contains_notice_and_questions():
    body = (
        "Your Defense Plan: DUI\n\nQuick answer\nChallenge the stop.\n\n"
        "Questions to ask your lawyer\n• Can the blood test be challenged?\n\n"
        "Laws cited\n• O.C.G.A. § 40-6-391"
    )
    data = plan_pdf.build_pdf("Your Defense Plan: DUI", body)
    assert data.startswith(b"%PDF-1.4")
    assert b"%%EOF" in data
    # Times-Roman text is stored as literal strings in the content stream.
    assert b"Your Defense Plan: DUI" in data or b"STANDALONE ASSISTANT" in data
    assert lang.NOTICE_EN.encode() in data or b"not legal advice" in data
    assert b"Questions to ask your lawyer" in data
    assert b"O.C.G.A." in data


def test_build_text_appends_notice_once():
    text = plan_pdf.build_text("Plan", "Hello.\n\n" + lang.NOTICE_EN)
    assert text.count(lang.NOTICE_EN) == 1
    assert "not a court filing" in text.lower()


def test_spanish_pdf_uses_spanish_notice():
    data = plan_pdf.build_pdf("Su plan de defensa", "Respuesta r\\u00e1pida\\nVaya a la corte.".encode().decode("unicode_escape"), "es")
    assert data.startswith(b"%PDF-1.4")
    assert "asesoramiento".encode("latin-1", "replace") in data or lang.NOTICE_ES.encode("latin-1", "replace") in data
