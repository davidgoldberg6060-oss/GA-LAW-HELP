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
            "coverage_limit": pack.get("coverage_limit"),
            "prompt": encounter_prompt_block("rights", situation),
            "landmarks": pack["landmarks"],
            "official_indexes": official_indexes(),
        }
    payload = {"guest": True, **pack, "official_indexes": official_indexes()}
    return payload


@router.get("/courts")
def public_courts():
    pack = encounter_pack()
    return {"guest": True, "courts": pack["courts"], "disclaimer": pack["disclaimer"]}


def official_indexes():
    """Public court index pages only. Not the Official Code of Georgia Annotated."""
    return [
        {"title": "Supreme Court of Georgia opinion index", "url": "https://www.gasupreme.us/2026-opinions/", "kind": "court index", "official": True},
        {"title": "Court of Appeals of Georgia", "url": "https://www.gaappeals.us/", "kind": "court index", "official": True},
    ]
