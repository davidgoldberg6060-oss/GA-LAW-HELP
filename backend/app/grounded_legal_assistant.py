"""Grounded Case Analysis / Talk to Me response construction."""
from __future__ import annotations
import re
from .internal_legal_search import search_internal

VERIFIED={"verified","official","validated","confirmed"}
NEGATIVE={"overruled","vacated","superseded","withdrawn","repealed"}
SUPPORTED_MODES={"case_analysis","talk_to_me","rights","motions"}
TALK_SECTIONS=(
    ("what_appears_to_be_happening","WHAT APPEARS TO BE HAPPENING"),
    ("safest_immediate_steps","SAFEST IMMEDIATE STEPS"),
    ("your_rights","YOUR RIGHTS"),
    ("law_enforcement_limits","WHAT LAW ENFORCEMENT MAY / MAY NOT DO"),
    ("lawful_things_to_say_or_do","WHAT TO SAY OR DO"),
    ("verified_georgia_authority","VERIFIED GEORGIA AUTHORITY"),
    ("important_limitations","IMPORTANT LIMITATIONS"),
)

def _is_traceable(hit:dict)->bool:
    status=str(hit.get("verification_status") or "").strip().lower();citation=str(hit.get("citation") or "").strip();source_url=str(hit.get("source_url") or "").strip()
    return status in VERIFIED and bool(citation) and source_url.startswith("https://")

def _is_negatively_treated(hit:dict)->bool:
    currency=str(hit.get("currency_status") or "unknown").strip().lower();precedent=str(hit.get("precedential_status") or "unknown").strip().lower();treatment=hit.get("negative_treatment") or []
    if isinstance(treatment,str): treatment=[treatment]
    words={str(x).strip().lower() for x in treatment};return currency in NEGATIVE or precedent in NEGATIVE or bool(words & NEGATIVE)

def _verified_hits(result:dict)->list[dict]: return [h for h in result.get("hits",[]) if _is_traceable(h) and not _is_negatively_treated(h)]
def _authority_context(hits:list[dict])->str:
    blocks=[]
    for index,hit in enumerate(hits,1):
        blocks.append(f"[{index}] {hit.get('title') or 'Legal authority'}\nCitation: {hit.get('citation')}\nCorpus: {hit.get('corpus') or 'unknown'}\nVerification: {hit.get('verification_status')}\nCurrency: {hit.get('currency_status') or 'unknown'}\nPrecedential status: {hit.get('precedential_status') or 'unknown'}\nStatus checked at: {hit.get('status_checked_at') or 'not recorded'}\nStatus source: {hit.get('status_source_url') or 'not recorded'}\nStored official/source URL: {hit.get('source_url')}\nStored excerpt: {hit.get('excerpt') or ''}")
    return "\n\n".join(blocks)

def _mode_instructions(mode:str)->str:
    if mode=="talk_to_me": return """Use these exact response sections in this order:
1. WHAT APPEARS TO BE HAPPENING — summarize the user's account without presenting allegations or speech recognition as established fact.
2. SAFEST IMMEDIATE STEPS — short, calm actions focused on physical safety and lawful de-escalation. If the facts indicate immediate danger, say to move to a safe place if possible and contact emergency services; do not imply the app itself can summon help.
3. YOUR RIGHTS — explain only rights supported by the supplied authority and clearly state when the indexed authority is insufficient.
4. WHAT LAW ENFORCEMENT MAY / MAY NOT DO — separate supported powers or restrictions; do not make categorical claims that the supplied authority does not establish.
5. WHAT TO SAY OR DO — give lawful, non-confrontational options; never coach resistance, obstruction, flight, deception, evidence destruction, or interference with officers.
6. VERIFIED GEORGIA AUTHORITY — list only supplied [number] authorities actually relied on, with their stored citations and any unknown currency/precedential limitation.
7. IMPORTANT LIMITATIONS — identify missing facts, uncertain transcription, unknown legal status, or issues requiring a Georgia lawyer/court record review.
Keep urgent guidance concise enough to read during a live encounter. Do not tell the user that recording is lawful unless supplied authority establishes it for the described circumstances."""
    return "Clearly separate user facts, legal issues, authority-backed analysis, counterarguments/limitations, and practical next steps."

def _talk_sections(analysis:str)->dict:
    """Convert the model's required headings into a stable API contract for native clients."""
    if not analysis: return {}
    positions=[]
    for key,label in TALK_SECTIONS:
        match=re.search(rf"(?im)^\s*(?:\d+[.)]\s*)?{re.escape(label)}\s*(?:[:—-]\s*)?",analysis)
        if match: positions.append((match.start(),match.end(),key))
    positions.sort()
    if len(positions)<2: return {}
    sections={}
    for i,(_,end,key) in enumerate(positions):
        stop=positions[i+1][0] if i+1<len(positions) else len(analysis);value=analysis[end:stop].strip()
        if value: sections[key]=value
    return sections

def grounded_legal_response(query:str,mode:str,ask_ai)->dict:
    if mode not in SUPPORTED_MODES: raise ValueError("Unsupported grounded legal-assistant mode.")
    retrieval=search_internal(query,mode,12);verified=_verified_hits(retrieval)
    if not verified: return {"mode":mode,"analysis":None,"sections":{} if mode=="talk_to_me" else None,"authorities":retrieval.get("hits",[]),"grounded_authority_count":0,"coverage_notice":"No traceable, non-negatively-treated indexed authority matched strongly enough for AI legal analysis. GA.LAW.HELP will not invent authority or use an authority explicitly marked overruled, vacated, superseded, withdrawn, or repealed as affirmative governing law."}
    prompt=f"""GA.LAW.HELP grounded legal analysis request.
Mode: {mode}

USER-SUPPLIED FACTS OR QUESTION (not independently verified; may include speech-to-text transcription errors):
{query}

TRACEABLE VERIFIED INDEXED AUTHORITIES AVAILABLE FOR THIS RESPONSE:
{_authority_context(verified)}

Rules for this response:
- Treat the user's narrative as allegations/facts to be verified, not established facts.
- Base every material legal conclusion only on the authorities supplied above.
- Cite supplied authorities by [number] and stored citation; never create a citation, case, statute, rule, deadline, sentence, or procedural requirement that is not supplied.
- Never describe an authority as current, binding, controlling, or precedential unless its supplied status metadata establishes that proposition.
- If Currency or Precedential status is unknown, explicitly label that limitation; do not fill it from memory.
- Do not predict or guarantee an outcome.
- For a live police encounter, prioritize physical safety and do not encourage resistance, evasion, obstruction, evidence destruction, interference, or deception.
- Never claim to observe, hear, identify, or infer facts that were not actually provided in the user's text/transcript.

MODE-SPECIFIC FORMAT:
{_mode_instructions(mode)}
"""
    analysis=ask_ai(prompt)
    response={"mode":mode,"analysis":analysis,"authorities":retrieval.get("hits",[]),"grounded_authority_count":len(verified),"coverage_notice":retrieval.get("coverage_notice")}
    if mode=="talk_to_me": response["sections"]=_talk_sections(analysis)
    return response
