"""Georgia Case Analysis / Talk to Me response construction."""
from __future__ import annotations
import re
from .internal_legal_search import search_internal

VERIFIED={"verified","official","validated","confirmed"}
NEGATIVE={"overruled","vacated","superseded","withdrawn","repealed"}
SUPPORTED_MODES={"case_analysis","talk_to_me","rights","motions"}
TALK_SECTIONS=(("what_appears_to_be_happening","WHAT APPEARS TO BE HAPPENING"),("safest_immediate_steps","SAFEST IMMEDIATE STEPS"),("your_rights","YOUR RIGHTS"),("law_enforcement_limits","WHAT LAW ENFORCEMENT MAY / MAY NOT DO"),("lawful_things_to_say_or_do","WHAT TO SAY OR DO"),("verified_georgia_authority","GEORGIA LAW"),("important_limitations","IMPORTANT LIMITATIONS"))
CASE_ANALYSIS_SECTIONS=(("facts_to_verify","FACTS TO CHECK"),("legal_issues","LEGAL ISSUES"),("prosecution_arguments","PROSECUTION ARGUMENTS"),("defense_arguments","DEFENSE ARGUMENTS"),("possible_motions","POSSIBLE MOTIONS"),("practical_next_steps","PRACTICAL NEXT STEPS"),("verified_georgia_authority","GEORGIA LAW"),("important_limitations","IMPORTANT LIMITATIONS"))

def _is_traceable(hit:dict)->bool:
    status=str(hit.get("verification_status") or "").strip().lower();citation=str(hit.get("citation") or "").strip();source_url=str(hit.get("source_url") or "").strip()
    return status in VERIFIED and bool(citation) and source_url.startswith("https://")
def _is_negatively_treated(hit:dict)->bool:
    currency=str(hit.get("currency_status") or "unknown").strip().lower();precedent=str(hit.get("precedential_status") or "unknown").strip().lower();treatment=hit.get("negative_treatment") or []
    if isinstance(treatment,str):treatment=[treatment]
    words={str(x).strip().lower() for x in treatment};return currency in NEGATIVE or precedent in NEGATIVE or bool(words&NEGATIVE)
def _verified_hits(result:dict)->list[dict]:return[h for h in result.get("hits",[]) if _is_traceable(h) and not _is_negatively_treated(h)]
def _authority_context(hits:list[dict])->str:
    return "\n\n".join(f"[{i}] {h.get('title') or 'Georgia legal authority'}\nCitation: {h.get('citation')}\nSource: {h.get('source_url')}\nExcerpt: {h.get('excerpt') or ''}" for i,h in enumerate(hits,1))

def _mode_instructions(mode:str)->str:
    if mode=="talk_to_me":return """Use these exact sections in order:
1. WHAT APPEARS TO BE HAPPENING — briefly explain the situation described by the user.
2. SAFEST IMMEDIATE STEPS — calm, practical steps that prioritize physical safety and lawful de-escalation. During a live police encounter never encourage resistance, evasion, obstruction, interference, deception, or evidence destruction.
3. YOUR RIGHTS — explain the rights relevant to the situation in clear language.
4. WHAT LAW ENFORCEMENT MAY / MAY NOT DO — explain important legal limits and powers relevant to the described interaction. Avoid categorical claims when facts or law materially depend on circumstances.
5. WHAT TO SAY OR DO — give lawful, non-confrontational options and useful phrases the person can use.
6. GEORGIA LAW — explain the Georgia law relevant to the question. Use supplied authorities when available. Do not invent a statute, case, citation, deadline, sentence, or rule.
7. IMPORTANT LIMITATIONS — briefly identify only missing facts or uncertainties that could materially change the answer.
Keep urgent guidance concise enough to read during an encounter. The purpose is to help the user understand rights, law-enforcement limits, and safe lawful choices—not to refuse ordinary legal questions because the internal library lacks a matching document."""
    if mode=="case_analysis":return """Use these exact sections in order:
1. FACTS TO CHECK — identify disputed or missing facts that matter to the legal analysis.
2. LEGAL ISSUES — explain the legal issues raised by the user's facts in understandable language.
3. PROSECUTION ARGUMENTS — explain the strongest reasonable prosecution positions without inventing evidence.
4. DEFENSE ARGUMENTS — explain reasonable factual and legal defenses raised by the facts.
5. POSSIBLE MOTIONS — explain motions that may be relevant and what each would try to accomplish. Do not promise that a motion will succeed.
6. PRACTICAL NEXT STEPS — evidence to preserve or obtain, questions for counsel, court preparation, and issues/deadlines to investigate. Never invent a deadline.
7. GEORGIA LAW — explain applicable Georgia law and cite supplied authority when available. Never invent a case, statute, citation, sentence, deadline, or procedural rule.
8. IMPORTANT LIMITATIONS — briefly identify missing facts or unresolved issues that could materially change the analysis.
The purpose is to help the user understand the case and prepare: charges, elements, defenses, motions, evidence issues, constitutional issues, sentencing exposure when known, and useful questions or arguments to discuss with counsel. Do not promise dismissal, suppression, acquittal, or sentence reduction."""
    return "Answer the user's legal question directly and helpfully. Explain relevant Georgia law, rights, practical next steps, and material uncertainties. Never invent legal authority or guarantee an outcome."

def _extract_sections(analysis:str,spec:tuple)->dict:
    if not analysis:return{}
    positions=[]
    for key,label in spec:
        m=re.search(rf"(?im)^\s*(?:\d+[.)]\s*)?{re.escape(label)}\s*(?:[:—-]\s*)?",analysis)
        if m:positions.append((m.start(),m.end(),key))
    positions.sort()
    if len(positions)<2:return{}
    out={}
    for i,(_,end,key) in enumerate(positions):
        stop=positions[i+1][0] if i+1<len(positions) else len(analysis);value=analysis[end:stop].strip()
        if value:out[key]=value
    return out

def grounded_legal_response(query:str,mode:str,ask_ai)->dict:
    if mode not in SUPPORTED_MODES:raise ValueError("Unsupported legal-assistant mode.")
    retrieval=search_internal(query,mode,12);authorities=_verified_hits(retrieval)
    authority_context=_authority_context(authorities) if authorities else "No matching source excerpt is supplied. Answer the ordinary legal question from general legal knowledge, but do not fabricate a Georgia citation or exact rule you are unsure of."
    prompt=f"""GA.LAW.HELP assistant request.
Mode: {mode}

USER'S QUESTION OR DESCRIPTION:
{query}

GEORGIA LEGAL SOURCE MATERIAL AVAILABLE TO CITE:
{authority_context}

Core role:
- Help the user understand Georgia law and the legal system in practical, plain language.
- In case analysis, identify charges/issues, elements when known, defenses, prosecution weaknesses, evidence and constitutional issues, possible motions, court preparation, and useful matters to raise with counsel.
- During law-enforcement interactions, help the user understand rights, what officers may and may not do, and safe lawful choices.
- Answer the question directly even when the internal legal library has no matching document. Do not make source availability the focus of the response.
- Treat disputed factual allegations as the user's account rather than established fact.
- Use supplied Georgia sources when relevant. Never invent a case, statute, citation, rule, deadline, sentence, or procedural requirement.
- Do not guarantee legal outcomes.
- During a live police encounter prioritize physical safety; never encourage resistance, evasion, obstruction, interference, deception, or evidence destruction.
- Never claim to see, hear, or know facts the user did not provide.

RESPONSE FORMAT:
{_mode_instructions(mode)}
"""
    analysis=ask_ai(prompt)
    response={"mode":mode,"analysis":analysis,"authorities":retrieval.get("hits",[]),"grounded_authority_count":len(authorities),"coverage_notice":None}
    if mode=="talk_to_me":response["sections"]=_extract_sections(analysis,TALK_SECTIONS)
    elif mode=="case_analysis":response["sections"]=_extract_sections(analysis,CASE_ANALYSIS_SECTIONS)
    return response
