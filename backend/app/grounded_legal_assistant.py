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
CASE_ANALYSIS_SECTIONS=(
    ("facts_to_verify","FACTS TO VERIFY"),
    ("legal_issues","LEGAL ISSUES"),
    ("prosecution_arguments","PROSECUTION ARGUMENTS"),
    ("defense_arguments","DEFENSE ARGUMENTS"),
    ("possible_motions","POSSIBLE MOTIONS"),
    ("practical_next_steps","PRACTICAL NEXT STEPS"),
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
2. SAFEST IMMEDIATE STEPS — short, calm actions focused on physical safety and lawful de-escalation. If this is a live police encounter, do not encourage resistance, evasion, obstruction, evidence destruction, interference, or deception.
3. YOUR RIGHTS — explain supported rights. If no verified indexed authority was supplied, clearly label legal details as general information that still requires Georgia-authority verification.
4. WHAT LAW ENFORCEMENT MAY / MAY NOT DO — separate supported powers or restrictions and avoid categorical claims when authority is unavailable.
5. WHAT TO SAY OR DO — lawful, non-confrontational options only.
6. VERIFIED GEORGIA AUTHORITY — only supplied authorities actually relied on. If none were supplied, say that no matching verified indexed authority was found; never invent one.
7. IMPORTANT LIMITATIONS — missing facts, uncertain transcription, unknown legal status, or authority that still needs verification.
Keep urgent guidance concise enough to read during a live encounter. Do not tell the user that recording is lawful unless supplied authority establishes it for the described circumstances."""
    if mode=="case_analysis": return """Use these exact response sections in this order:
1. FACTS TO VERIFY — separate the user's allegations from facts/documents that should be confirmed. Do not assume disputed facts are true.
2. LEGAL ISSUES — identify legal issues reasonably raised by the supplied facts. When verified indexed authority is unavailable, label legal details as general information requiring Georgia-authority verification.
3. PROSECUTION ARGUMENTS — strongest reasonable prosecution positions; do not invent evidence.
4. DEFENSE ARGUMENTS — strongest reasonable defense positions; distinguish factual defenses from legal defenses.
5. POSSIBLE MOTIONS — identify motions that may be relevant to the described facts, but do not say a motion should be filed or is legally supported unless verified authority and the record support it.
6. PRACTICAL NEXT STEPS — evidence/documents to preserve or obtain, questions for counsel, deadlines/issues to verify, and lawful preparation steps. Never invent a deadline.
7. VERIFIED GEORGIA AUTHORITY — only supplied [number] authorities actually relied on. If none were supplied, explicitly say so; never invent a citation.
8. IMPORTANT LIMITATIONS — missing facts, unresolved conflicts, unknown currency/precedential status, and matters requiring Georgia counsel or court-record review.
Do not promise dismissal, suppression, acquittal, sentence reduction, or any other outcome."""
    return "Clearly separate user facts, general legal information, verified authority-backed conclusions, counterarguments/limitations, and practical next steps. Never invent a citation or legal authority."

def _extract_sections(analysis:str,spec:tuple)->dict:
    if not analysis:return {}
    positions=[]
    for key,label in spec:
        match=re.search(rf"(?im)^\s*(?:\d+[.)]\s*)?{re.escape(label)}\s*(?:[:—-]\s*)?",analysis)
        if match:positions.append((match.start(),match.end(),key))
    positions.sort()
    if len(positions)<2:return {}
    sections={}
    for i,(_,end,key) in enumerate(positions):
        stop=positions[i+1][0] if i+1<len(positions) else len(analysis);value=analysis[end:stop].strip()
        if value:sections[key]=value
    return sections

def _talk_sections(analysis:str)->dict:return _extract_sections(analysis,TALK_SECTIONS)
def _case_analysis_sections(analysis:str)->dict:return _extract_sections(analysis,CASE_ANALYSIS_SECTIONS)

def grounded_legal_response(query:str,mode:str,ask_ai)->dict:
    if mode not in SUPPORTED_MODES:raise ValueError("Unsupported grounded legal-assistant mode.")
    retrieval=search_internal(query,mode,12);verified=_verified_hits(retrieval)
    authority_context=_authority_context(verified) if verified else "No matching traceable verified indexed Georgia authority was retrieved for this question."
    grounding_rule=(
        "Base every material Georgia-law conclusion only on the authorities supplied above."
        if verified else
        "No verified indexed Georgia authority is available for this response. You may still answer the user's ordinary legal question with useful general legal information, issue-spotting, and practical questions to discuss with counsel, but you MUST NOT present a Georgia-specific legal proposition as verified, MUST NOT invent a citation/case/statute/rule/deadline/sentence, and MUST clearly identify what requires Georgia-authority verification."
    )
    prompt=f"""GA.LAW.HELP legal analysis request.
Mode: {mode}

USER-SUPPLIED FACTS OR QUESTION (not independently verified; may include speech-to-text transcription errors):
{query}

TRACEABLE VERIFIED INDEXED AUTHORITIES AVAILABLE FOR THIS RESPONSE:
{authority_context}

Rules for this response:
- Treat the user's narrative as allegations/facts to be verified, not established facts.
- {grounding_rule}
- Cite only supplied authorities by [number] and stored citation; never create a citation, case, statute, rule, deadline, sentence, or procedural requirement that is not supplied.
- Never describe an authority as current, binding, controlling, or precedential unless its supplied status metadata establishes that proposition.
- If Currency or Precedential status is unknown, explicitly label that limitation; do not fill it from memory.
- Do not predict or guarantee an outcome.
- For a live police encounter, prioritize physical safety and do not encourage resistance, evasion, obstruction, evidence destruction, interference, or deception.
- Never claim to observe, hear, identify, or infer facts that were not actually provided.

MODE-SPECIFIC FORMAT:
{_mode_instructions(mode)}
"""
    analysis=ask_ai(prompt)
    coverage_notice=retrieval.get("coverage_notice")
    if not verified:
        coverage_notice="No matching traceable verified indexed Georgia authority was found. The AI may provide clearly labeled general legal information and issue-spotting, but GA.LAW.HELP will not invent or present an unverified citation as governing Georgia law."
    response={"mode":mode,"analysis":analysis,"authorities":retrieval.get("hits",[]),"grounded_authority_count":len(verified),"coverage_notice":coverage_notice}
    if mode=="talk_to_me":response["sections"]=_talk_sections(analysis)
    elif mode=="case_analysis":response["sections"]=_case_analysis_sections(analysis)
    return response