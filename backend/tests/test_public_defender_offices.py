from app import public_defender_offices as offices
from app import language as lang


def test_bundled_directory_covers_every_gpdc_circuit_page():
    data = offices.catalog()
    assert data["checked_on"] == "2026-11-13"
    assert data["source_url"] == "https://gapubdef.org/_data/circuits.json"
    rows = offices.offices()
    assert len(rows) == 51
    assert sum(1 for o in rows if o["opt_out"]) == 6
    assert all(o["address"] and o["phone"] and o["page_url"] and o["circuit"] and o["counties"] for o in rows)
    assert all(o["page_url"].startswith("https://gapubdef.org/local-offices/") for o in rows)
    # Do not invent a circuit public defender name when GPDC did not publish one.
    gwinnett = next(o for o in rows if "gwinnett" in o["id"])
    assert gwinnett["opt_out"] is True and gwinnett["defender"] is None
    # Fulton is the Atlanta Circuit.
    atlanta = offices.search(county="Fulton")
    assert len(atlanta) == 1 and atlanta[0]["circuit"] == "Atlanta Circuit"
    assert atlanta[0]["defender"]


def test_search_and_pack_include_bar_directory_and_no_ratings():
    hits = offices.search(query="Snellville")  # city is not a county; may be empty
    gwin = offices.search(query="Gwinnett")
    assert gwin and gwin[0]["opt_out"] is True
    pack = offices.pack(query="Brunswick", language="en")
    assert pack["office_count"] == 51
    assert pack["offices"] and pack["offices"][0]["phone"]
    assert pack["bar_directory"]["url"] == "https://www.gabar.org/member-directory/"
    assert "does not show win/loss" in pack["bar_directory"]["explainer"].lower() or "win/loss" in pack["bar_directory"]["explainer"]
    assert "does not publish an official per-attorney" in pack["outcome_note"]
    assert "star" not in pack["outcome_note"].lower() or "does not" in pack["outcome_note"]
    assert pack["notice"] == lang.NOTICE_EN
    es = offices.pack(language="es")
    assert es["language"] == "es" and "no califica abogados" in es["outcome_note"]
