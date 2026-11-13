from app import language as lang
from app import read_aloud


def test_spanish_instruction_keeps_citations_and_english_headings():
    inst = lang.instruction("es")
    assert "Respond in Spanish" in inst
    assert "O.C.G.A." in inst
    assert "Quick answer" in inst
    assert lang.NOTICE_ES in inst
    assert lang.normalize_language("Español") == "es"
    assert lang.normalize_language("en-US") == "en"


def test_translation_notice_says_english_original_counts():
    note = lang.translation_notice("es")
    assert "inglés" in note or "ingles" in note.replace("é", "e")
    assert "corte" in note
    assert "entiend" in note or "entender" in note


def test_read_aloud_voices_are_original_and_speak_the_notice():
    ids = [v["id"] for v in read_aloud.catalog()]
    assert ids == ["off", "butler", "nanny"]
    butler = read_aloud.voice("The Butler")
    nanny = read_aloud.voice("nanny")
    assert butler["label"] == "The Butler" and butler["locale"] == "en-GB"
    assert nanny["label"] == "The Nanny" and nanny["locale"] == "en-US"
    assert butler["rate"] < nanny["rate"]
    assert "original" in butler["description"].lower() and "not based on any person" in butler["description"].lower()
    # No trademarked or actor names in the catalog.
    blob = " ".join(str(v) for v in read_aloud.catalog()).lower()
    for banned in ("alfred", "batman", "drescher", "fran ", "wayne"):
        assert banned not in blob
    spoken = read_aloud.spoken_text("Challenge the stop. Ask about O.C.G.A. § 40-6-391.", "butler")
    assert spoken.startswith(butler["intro_en"])
    assert "Challenge the stop" in spoken and "O.C.G.A. § 40-6-391" in spoken
    assert spoken.endswith(lang.NOTICE_EN)
    spanish = read_aloud.spoken_text("Impugne la parada.", "nanny", "es")
    assert spanish.startswith(nanny["intro_es"])
    assert lang.NOTICE_ES in spanish
    assert read_aloud.spoken_text("", "butler") == ""
    assert read_aloud.normalize("off") == "off"
