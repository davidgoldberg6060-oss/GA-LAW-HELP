"""Grounded Case Analysis / Talk to Me response construction."""
from __future__ import annotations
from .internal_legal_search import search_internal

VERIFIED={"verified","official","validated","confirmed"}
NEGATIVE={"overruled","vacated","superseded","withdrawn","repealed"}
SUPPORTED_MODES={"case_analysis","talk_to_me","rights","motions"}

def _is_traceable(hit:dict)->bool:
    status=str(hit.get("verification_status") or "").strip().lower()
    citation=str(hit.get("citation") or "").strip()
    source_url=str(hit.get("source_url") or "").strip()
    return status in VERIFIED and bool(citation) and source_url.startswith("https://")

def _is_negatively_treated(hit:dict)->bool:
    currency=str(hit.get("currency_status") or "unknown").strip().lower()
    precedent=str(hit.get("precedential_status") or "unknown").strip().lower()
    treatment=hit.get("negative_treatment") or []
    if isinstance(treatment,str): treatment=[treatment]
    words={str(x).strip().lower() for x in treatment}
    return currency in NEGATIVE or precedent in NEGATIVE or bool(words & NEGATIVE)

def _verified_hits(result:dict)->list[dict]:
    # Unknown currency remains usable only as a traceable research authority; an
    # explicit negative status is never sent to AI as affirmative governing law.
    return [h for h in result.get("hits",[]) if _is_traceable(h) and not _is_negatively_treated(h)]

def _authority_context(hits:list[dict])->str:
    blocks=[]
    for index,hit in enumerate(hits,1):
        blocks.append(
            f"[{index}] {hit.get('title') or 'Legal authority'}\n"
            f"Citation: {hit.get('citation')}\nCorpus: {hit.get('corpus') or 'unknown'}\n"
            f"Verification: {hit.get('verification_status')}\nCurrency: {hit.get('currency_status') or 'unknown'}\n"
            f"Precedential status: {hit.get('precedential_status') or 'unknown'}\n"
            f"Status checked at: {hit.get('status_checked_at') or 'not recorded'}\n"
            f"Status source: {hit.get('status_source_url') or 'not recorded'}\n"
            f"Stored official/source URL: {hit.get('source_url')}\nStored excerpt: {hit.get('excerpt') or ''}"
        )
    return "\n\n".join(blocks)

def grounded_legal_response(query:str,mode:str,ask_ai)->dict:
    if mode not in SUPPORTED_MODES: raise ValueError("Unsupported grounded legal-assistant mode.")
    retrieval=search_internal(query,mode,12);verified=_verified_hits(retrieval)
    if not verified:
        return {"mode":mode,"analysis":None,"authorities":retrieval.get("hits",[]),"grounded_authority_count":0,"coverage_notice":"No traceable, non-negatively-treated indexed authority matched strongly enough for AI legal analysis. GA.LAW.HELP will not invent authority or use an authority explicitly marked overruled, vacated, superseded, withdrawn, or repealed as affirmative governing law."}
    prompt=f"""GA.LAW.HELP grounded legal analysis request.
Mode: {mode}

USER-SUPPLIED FACTS OR QUESTION (not independently verified):
{query}

TRACEABLE VERIFIED INDEXED AUTHORITIES AVAILABLE FOR THIS RESPONSE:
{_authority_context(verified)}

Rules for this response:
- Treat the user's narrative as allegations/facts to be verified, not established facts.
- Base every material legal conclusion only on the authorities supplied above.
- Cite supplied authorities by [number] and stored citation; never create a citation, case, statute, rule, deadline, sentence, or procedural requirement that is not supplied.
- Never describe an authority as current, binding, controlling, or precedential unless its supplied status metadata establishes that proposition.
- If Currency or Precedential status is unknown, explicitly label that limitation; do not fill it from memory.
- Clearly separate user facts, legal issues, authority-backed analysis, counterarguments/limitations, and practical next steps.
- Do not predict or guarantee an outcome.
- For a live police encounter, prioritize physical safety and do not encourage resistance, evasion, obstruction, evidence destruction, or deception.
"""
    analysis=ask_ai(prompt)
    return {"mode":mode,"analysis":analysis,"authorities":retrieval.get("hits",[]),"grounded_authority_count":len(verified),"coverage_notice":retrieval.get("coverage_notice")}
