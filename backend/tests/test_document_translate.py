import json
from app import document_translate as tr
from app import language as lang


RAW = json.dumps({
    "translated_text": "ESTADO DE GEORGIA vs. JORDAN LEE\nCase No. SAMPLE-1\nCargo: Driving While License Suspended\nComparecencia: 9 de diciembre de 2026 a las 9:00 a.m. en Gwinnett State Court.",
    "plain_language": {
        "document_type": "Aviso de acusación formal",
        "summary": "Este papel le avisa de una fecha de corte por conducir con la licencia suspendida.",
        "charges_or_claims": [{"text": "Driving While License Suspended", "explanation": "Es el cargo escrito en el papel; es lo que el Estado dice que ocurrió."}],
        "key_dates": [{"text": "December 9, 2026 9:00 AM", "explanation": "Es la fecha y hora en que debe presentarse en la corte."}],
        "case_number": "SAMPLE-1",
        "case_number_explanation": "Así identifica el tribunal su caso.",
        "court": "Gwinnett State Court",
        "court_explanation": "Es el tribunal que aparece en el papel.",
        "next_steps": ["Llegue a tiempo el día de la corte."],
        "questions_for_lawyer": ["¿Se puede reducir el cargo?"],
        "helpful_flags": [],
    },
})


def test_spanish_translation_includes_full_text_breakdown_and_court_notice():
    parsed = tr.parse_translation(RAW)
    answer = tr.format_spanish(parsed, {"extracted_text": "STATE OF GEORGIA v. JORDAN LEE\nCase No. SAMPLE-1"})
    assert "Traducción al español" in answer
    assert "ESTADO DE GEORGIA" in answer
    assert "Explicación en palabras sencillas" in answer
    assert "Driving While License Suspended" in answer
    assert "lo que el Estado dice" in answer
    assert "December 9, 2026" in answer
    assert "SAMPLE-1" in answer
    assert "Gwinnett State Court" in answer
    assert "Preguntas para su abogado" in answer
    assert lang.TRANSLATION_NOTICE_ES in answer
    assert "documento original en inglés es el que cuenta" in answer
    assert lang.NOTICE_ES in answer
    assert "Original en inglés" in answer


def test_keeps_citations_and_case_numbers_as_written():
    parsed = tr.parse_translation(RAW)
    assert parsed["case_number"] == "SAMPLE-1"
    assert parsed["court"] == "Gwinnett State Court"
    assert parsed["charges_or_claims"][0]["text"] == "Driving While License Suspended"
