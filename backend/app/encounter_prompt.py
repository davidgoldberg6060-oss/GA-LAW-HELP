"""Format the in-app encounter pack for the grounded assistant."""
from __future__ import annotations
import json
from .encounter_rights import encounter_pack

def encounter_prompt_block(mode: str, query: str) -> str:
    if mode not in {"rights", "talk_to_me"}:
        return ""
    pack = encounter_pack()
    text = (query or "").lower()
    chosen = []
    for item in pack["encounters"]:
        keys = {item["id"], item["title"].lower()}
        if item["id"] == "traffic_stop" and any(w in text for w in ("traffic", "stop", "pulled", "car", "dui")):
            chosen.append(item)
        elif item["id"] == "at_home" and any(w in text for w in ("home", "house", "door", "warrant")):
            chosen.append(item)
        elif item["id"] == "interrogation" and any(w in text for w in ("interrogat", "question", "miranda", "station", "custody")):
            chosen.append(item)
        elif item["id"] == "street" and any(w in text for w in ("street", "sidewalk", "walking")):
            chosen.append(item)
        elif any(k in text for k in keys):
            chosen.append(item)
    if not chosen:
        chosen = pack["encounters"]
    payload = {"disclaimer": pack["disclaimer"], "encounters": chosen, "landmarks": pack["landmarks"], "courts": pack["courts"]}
    return "IN-APP ENCOUNTER PACK (educational; label as general information unless a verified indexed authority also supports it):\n" + json.dumps(payload, ensure_ascii=False)
