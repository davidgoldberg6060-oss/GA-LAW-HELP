"""A question typed in Spanish gets a Spanish answer, even when the app's language is still English (Nov 21 audit)."""
from fastapi.testclient import TestClient

from app import language as L
from app.civil_topics import current_question
from app.main import app


def test_detects_spanish_questions_and_leaves_english_alone():
    for q in ("Me arrestaron por DUI en Atlanta anoche. Que hago?", "Mi casero me quiere desalojar. Tengo derechos?", "¿Qué hago?"):
        assert L.detect(q) == "es", q
    for q in ("I was arrested for DUI in Atlanta", "Can I get a DUI dismissed?", "My landlord wants to evict me, que hago", "No", ""):
        assert L.detect(q) == "en", q


def test_with_language_adds_instruction_and_english_key_words():
    out = L.with_language("Mi casero me quiere desalojar. Tengo derechos?")
    assert out.startswith("Respond in Spanish.") and L.NOTICE_ES in out
    asked = current_question(out)  # topic detection only reads the user's words
    assert asked.startswith("Mi casero") and "eviction" in asked and "landlord" in asked and "Respond" not in asked
    assert L.with_language("I got a ticket") == "I got a ticket"
    assert L.with_language("Me arrestaron anoche", "en") == "Me arrestaron anoche"  # the client asked for English
    already = L.instruction("es") + "\n\nUser: hola"
    assert L.with_language(already) == already
    assert L.with_language("I got a ticket", "es").startswith("Respond in Spanish.")
    wrapped = "Conversation so far:\nUser: hi\nAssistant: ok\n\nUser: Quiero el divorcio y la custodia de mis hijos"
    out = L.with_language(wrapped)
    assert out.startswith("Respond in Spanish.") and "User: hi" in out and current_question(out).startswith("Quiero el divorcio")
    assert "divorce" in current_question(out) and "custody" in current_question(out)


def test_rights_assistant_answers_spanish_questions_in_spanish(monkeypatch):
    seen = []

    def fake(query, mode, ask, db=None, **kw):
        seen.append(query)
        return {"analysis": "Respuesta corta\nx", "authorities": [], "mode": mode}

    monkeypatch.setattr("app.main.grounded_legal_response", fake)
    monkeypatch.setattr("app.main.answer_cache.get", lambda *a, **k: None)
    monkeypatch.setattr("app.main.answer_cache.put", lambda *a, **k: None)
    with TestClient(app) as client:
        r = client.post("/public/rights-assistant", json={"query": "Me arrestaron por DUI anoche. Que hago?", "mode": "general"})
        assert r.status_code == 200
        r = client.post("/public/rights-assistant", json={"query": "I was arrested for DUI last night", "mode": "general"})
        assert r.status_code == 200
    assert seen[0].startswith("Respond in Spanish.") and "arrested" in current_question(seen[0])
    assert seen[1] == "I was arrested for DUI last night"


def test_spanish_answers_get_the_spanish_footnote():
    en = ("Quick answer\nx\n\nEsto es información legal, no asesoramiento jurídico.\n\n"
          "Note: This is legal information, not legal advice. Georgia Code text is from the 2022 edition; some sections may "
          "have changed since. Check with a lawyer before relying on it.")
    out = L.localize_note(en, "es")
    assert out.endswith("Nota: Esta es información legal, no asesoramiento legal. El texto del Código de Georgia es de la "
                        "edición de 2022; algunas secciones pueden haber cambiado. Consulte con un abogado antes de confiar en él.")
    assert "Note:" not in out and "not legal advice" not in out and "asesoramiento jurídico" not in out and "x\n\nNota:" in out
    assert L.localize_note("Respuesta corta\ny", "es").endswith("\n\nNota: " + L.NOTE_ES)
    assert L.localize_note(en, "en") == en


def test_spanish_plan_answer_ends_with_nota(monkeypatch):
    from app import grounded_legal_assistant as service
    monkeypatch.setattr(service, "_hybrid_retrieval", lambda q, m, db, l: {"hits": []})
    q = L.with_language("Me arrestaron por DUI anoche en Atlanta. Que hago?")
    r = service.grounded_legal_response(q, "general", lambda p: "Quick answer\nLlame a un abogado.\n\nWhere to get help\n- x")
    last = r["analysis"].rstrip().splitlines()[-1]
    assert last.startswith("Nota: Esta es información legal, no asesoramiento legal.") and "Note:" not in r["analysis"]


PLAN_EN = ("Your Defense Plan: Eviction\n\nQuick answer\n• Puede ofrecer pagar la renta.\n\n"
           "How they'd build the case against you\n• Likely claim: posesión por falta de pago.\n\n"
           "How to fight back\n• Demand for possession: el aviso no fue correcto.\n\n"
           "Key deadlines\n• Revise su citación.\n\nQuestions to ask your lawyer\n• ¿Puedo pagar ahora?\n\nWhere to get help\n• x")


def test_spanish_answers_get_spanish_titles_and_headings():
    out = L.localize_headings(PLAN_EN, "es")
    lines = out.splitlines()
    assert lines[0] == "Su plan de defensa: Desalojo"
    for h in ("Respuesta rápida", "Cómo armarían el caso en su contra", "Cómo defenderse", "Plazos clave",
              "Preguntas para su abogado", "Dónde obtener ayuda"):
        assert h in lines, h
    for h in ("Quick answer", "How to fight back", "Key deadlines", "Where to get help"):
        assert h not in lines, h
    # bullets and sentences are never touched (even ones that start like a heading)
    assert "• Demand for possession: el aviso no fue correcto." in lines
    assert L.localize_headings(PLAN_EN, "en") == PLAN_EN  # English unchanged
    assert L.plan_title_es("Your Civil Plan: Insurance claim problem") == "Su plan civil: Problema con un reclamo de seguro"
    assert L.plan_title_es("Your Civil Plan: Car wreck injury") == "Su plan civil: Lesión por accidente de auto"
    assert L.plan_title_es("Your Defense Plan") == "Su plan de defensa"


def test_every_plan_label_has_a_spanish_title():
    from app import defense_plan as dp
    from app import civil_guide as cg
    labels = {label for label, _f in dp._TYPE.values()} | {c["label"] for c in cg.CATEGORIES} | {cg.OTHER["label"]}
    missing = sorted(lab for lab in labels if lab not in L.PLAN_LABELS_ES)
    assert not missing, missing


def test_every_known_heading_has_a_spanish_heading():
    from app.answer_format import _KNOWN_HEADINGS
    missing = sorted(h for h in _KNOWN_HEADINGS if h not in L.HEADINGS_ES)
    assert not missing, missing


def test_spanish_plan_route_has_spanish_title_and_headings(monkeypatch):
    from app import grounded_legal_assistant as service
    monkeypatch.setattr(service, "_hybrid_retrieval", lambda q, m, db, l: {"hits": []})
    q = L.with_language("Mi casero me dio un aviso de desalojo en Georgia. ¿Qué puedo hacer?")
    model = ("Quick answer\nPuede responder a la demanda.\n\nHow they'd build the case against you\n- Likely claim: falta de pago.\n\n"
             "How to fight back\n- Aviso: el aviso no fue correcto.\n\nWhere to get help\n- x")
    r = service.grounded_legal_response(q, "general", lambda p: model)
    lines = r["analysis"].splitlines()
    assert lines[0] == "Su plan de defensa: Desalojo", lines[:3]
    assert "Respuesta rápida" in lines and "Cómo defenderse" in lines and "Quick answer" not in lines
    assert r["defense_plan"]["title"] == "Su plan de defensa: Desalojo"
    assert lines[-1].startswith("Nota: ")


def test_english_plan_route_is_unchanged(monkeypatch):
    from app import grounded_legal_assistant as service
    monkeypatch.setattr(service, "_hybrid_retrieval", lambda q, m, db, l: {"hits": []})
    model = ("Quick answer\nYou can answer the case.\n\nHow they'd build the case against you\n- Likely claim: unpaid rent.\n\n"
             "How to fight back\n- Notice: the notice was wrong.\n\nWhere to get help\n- x")
    r = service.grounded_legal_response("My landlord gave me an eviction notice in Georgia. What can I do?", "general", lambda p: model)
    lines = r["analysis"].splitlines()
    assert lines[0] == "Your Defense Plan: Eviction" and "Quick answer" in lines and "How to fight back" in lines
    assert r["defense_plan"]["title"] == "Your Defense Plan: Eviction" and lines[-1].startswith("Note: ")
