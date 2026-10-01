"""Unauthenticated encounter and rights endpoints for free guest use."""
from fastapi import APIRouter, Query
from .encounter_rights import encounter_pack
from .encounter_prompt import encounter_prompt_block

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/encounter")
def public_encounter(situation: str = Query("", max_length=400)):
    pack = encounter_pack()
    if situation.strip():
        return {
            "guest": True,
            "disclaimer": pack["disclaimer"],
            "prompt": encounter_prompt_block("rights", situation),
            "landmarks": pack["landmarks"],
        }
    return {"guest": True, **pack}


@router.get("/courts")
def public_courts():
    pack = encounter_pack()
    return {"guest": True, "courts": pack["courts"], "disclaimer": pack["disclaimer"]}
