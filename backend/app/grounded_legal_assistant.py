"""Grounded legal-assistant response construction."""
from __future__ import annotations
import re
from .internal_legal_search import search_internal
from .authority_search_service import persisted_authority_hits
from .encounter_prompt import encounter_prompt_block

VERIFIED={"verified","official","validated","confirmed"}
NEGATIVE={"overruled","vacated","superseded","withdrawn","repealed"}
SUPPORTED_MODES={"case_analysis","talk_to_me","rights","motions"}
TALK_SECTIONS=(("what_appears_to_be_happening","WHAT APPEARS TO BE HAPPENING"),("safest_immediate_steps","SAFEST IMMEDIATE STEPS"),("your_rights","YOUR RIGHTS"),("law_enforcement_limits","WHAT LAW ENFORCEMENT MAY / MAY NOT DO"),("lawful_things_to_say_or_do","WHAT TO SAY OR DO"),("verified_georgia_authority","VERIFIED GEORGIA AUTHORITY"),("important_limitations","IMPORTANT LIMITATIONS"))
CASE_ANALYSIS_SECTIONS=(("facts_to_verify","FACTS TO VERIFY"),("legal_issues","LEGAL ISSUES"),("prosecution_arguments","PROSECUTION ARGUMENTS"),("defense_arguments","DEFENSE ARGUMENTS"),("possible_motions","POSSIBLE MOTIONS"),("practical_next_steps","PRACTICAL NEXT STEPS"),("verified_georgia_authority","VERIFIED GEORGIA AUTHORITY"),("important_limitations","IMPORTANT LIMITATIONS"))
RIGHTS_SECTIONS=(("situation","SITUATION"),("rights_that_may_apply","RIGHTS THAT MAY APPLY"),("law_enforcement_authority","LAW ENFORCEMENT AUTHORITY"),("law_enforcement_limits","LAW ENFORCEMENT LIMITS"),("lawful_options","LAWFUL OPTIONS"),("verified_georgia_authority","VERIFIED GEORGIA AUTHORITY"),("important_limitations","IMPORTANT LIMITATIONS"))
MOTIONS_SECTIONS=(("case_issue","CASE ISSUE"),("potential_motions","POTENTIAL MOTIONS"),("required_facts_or_evidence","REQUIRED FACTS OR EVIDENCE"),("opposing_arguments","OPPOSING ARGUMENTS"),("procedural_questions_to_verify","PROCEDURAL QUESTIONS TO VERIFY"),("verified_georgia_authority","VERIFIED GEORGIA AUTHORITY"),("important_limitations","IMPORTANT LIMITATIONS"))

def _is_traceable(hit:dict)->bool:
 if hit.get("usable_as_support") is False:return False
 status=str(hit.get("verification_status") or "").strip().lower();citation=str(hit.get("citation") or "").strip();url=str(hit.get("source_url") or "").strip();return status in VERIFIED and bool(citation) and url.startswith("https://")
def _is_negatively_treated(hit:dict)->bool:
 currency=str(hit.get("currency_status") or "unknown").strip().lower();precedent=str(hit.get("precedential_status") or "unknown").strip().lower();treatment=hit.get("negative_treatment") or []
 if isinstance(treatment,str):treatment=[treatment]
 return currency in NEGATIVE or precedent in NEGATIVE or bool({str(x).strip().lower() for x in treatment}&NEGATIVE)
def _verified_hits(result):return [h for h in result.get("hits",[]) if _is_traceable(h) and not _is_negatively_treated(h)]
def _authority_context(hits):
 return "\n\n".join(f"[{i}] {h.get('title') or 'Legal authority'}\nCitation: {h.get('citation')}\nVerification: {h.get('verification_status')}\nCurrency: {h.get('currency_status') or 'unknown'}\nPrecedential status: {h.get('precedential_status') or 'unknown'}\nStatus checked at: {h.get('status_checked_at') or 'not recorded'}\nStatus source: {h.get('status_source_url') or 'not recorded'}\nStored official/source URL: {h.get('source_url')}\nStored excerpt: {h.get('excerpt') or ''}" for i,h in enumerate(hits,1))

def _hybrid_retrieval(query,mode,db=None,limit=12):
 result=search_internal(query,mode,limit)
 if db is None:return result
 persisted=persisted_authority_hits(db,query,limit=limit)
 if not persisted:return result
 seen={(str(h.get('citation') or '').lower(),str(h.get('source_url') or '')) for h in persisted}
 file_hits=[h for h in result.get('hits',[]) if (str(h.get('citation') or '').lower(),str(h.get('source_url') or '')) not in seen]
 result['hits']=(persisted+file_hits)[:limit]
 result['coverage_notice']='Grounding includes verified authorities persisted by the internal Georgia ingestion pipeline plus indexed corpus records. Missing authority is not invented; unknown currency or precedential status remains explicitly unknown.'
 return result

def _mode_instructions(mode):
 if mode=="talk_to_me":return """Use exact headings: WHAT APPEARS TO BE HAPPENING; SAFEST IMMEDIATE STEPS; YOUR RIGHTS; WHAT LAW ENFORCEMENT MAY / MAY NOT DO; WHAT TO SAY OR DO; VERIFIED GEORGIA AUTHORITY; IMPORTANT LIMITATIONS. Prioritize safety. For a live police encounter, do not encourage resistance, evasion, obstruction, evidence destruction, interference, or deception. Treat speech-to-text transcription errors as possible and never claim to have heard facts not supplied. Do not claim recording is lawful unless supplied authority establishes it. Use the in-app encounter pack scripts when the situation matches."""
 if mode=="case_analysis":return """Use exact headings: FACTS TO VERIFY; LEGAL ISSUES; PROSECUTION ARGUMENTS; DEFENSE ARGUMENTS; POSSIBLE MOTIONS; PRACTICAL NEXT STEPS; VERIFIED GEORGIA AUTHORITY; IMPORTANT LIMITATIONS. Do not invent evidence or deadlines and do not promise an outcome."""
 if mode=="rights":return """Use these exact headings in order: SITUATION; RIGHTS THAT MAY APPLY; LAW ENFORCEMENT AUTHORITY; LAW ENFORCEMENT LIMITS; LAWFUL OPTIONS; VERIFIED GEORGIA AUTHORITY; IMPORTANT LIMITATIONS. Separate what officers may lawfully do from what the user may lawfully decline or request. Do not encourage physical resistance, flight, obstruction, deception, interference, or evidence destruction. Start from the matching in-app encounter script. Do not state a Georgia-specific right as verified unless supplied authority supports it."""
 if mode=="motions":return """Use these exact headings in order: CASE ISSUE; POTENTIAL MOTIONS; REQUIRED FACTS OR EVIDENCE; OPPOSING ARGUMENTS; PROCEDURAL QUESTIONS TO VERIFY; VERIFIED GEORGIA AUTHORITY; IMPORTANT LIMITATIONS. A motion is only potentially relevant unless the facts and supplied authority support it. Never invent filing deadlines, procedural prerequisites, standards, citations, or likely outcomes. Identify what must be checked in the actual record and current Georgia rules."""
 return "Separate facts, legal issues, verified authority, limitations, and practical next steps."

def _extract_sections(analysis,spec):
 if not analysis:return {}
 positions=[]
 for key,label in spec:
  m=re.search(rf"(?im)^\s*(?:\d+[.)]\s*)?{re.escape(label)}\s*(?:[:\u2014-]\s*)?",analysis)
  if m:positions.append((m.start(),m.end(),key))
 positions.sort()
 if len(positions)<2:return {}
 out={}
 for i,(_,end,key) in enumerate(positions):
  stop=positions[i+1][0] if i+1<len(positions) else len(analysis);value=analysis[end:stop].strip()
  if value:out[key]=value
 return out

def grounded_legal_response(query:str,mode:str,ask_ai,db=None)->dict:
 if mode not in SUPPORTED_MODES:raise ValueError("Unsupported grounded legal-assistant mode.")
 retrieval=_hybrid_retrieval(query,mode,db,12);verified=_verified_hits(retrieval);context=_authority_context(verified) if verified else "No matching traceable verified indexed Georgia authority was retrieved for this question."
 grounding="Base every material Georgia-law conclusion only on supplied authorities." if verified else "No verified indexed Georgia authority is available. You may give clearly labeled general legal information and issue-spotting, but MUST NOT present a Georgia-specific proposition as verified and MUST NOT invent a citation, case, statute, rule, deadline, sentence, or procedure."
 pack=encounter_prompt_block(mode, query)
 prompt=f"""GA.LAW.HELP legal analysis request.\nMode: {mode}\n\nUSER-SUPPLIED FACTS OR QUESTION (not independently verified; may include speech-to-text transcription errors):\n{query}\n\n{pack}\n\nTRACEABLE VERIFIED INDEXED AUTHORITIES:\n{context}\n\nRules:\n- Treat the user's narrative as allegations/facts to be verified, not established facts.\n- {grounding}\n- Cite only supplied authorities; never create a citation, case, statute, rule, deadline, sentence, or procedural requirement.\n- Never call authority current, binding, controlling, or precedential unless supplied status metadata establishes it.\n- If Currency or Precedential status is unknown, explicitly label that limitation; do not fill it from memory.\n- Do not predict or guarantee outcomes.\n- Never claim to observe or hear facts not provided.\n\nFORMAT:\n{_mode_instructions(mode)}"""
 analysis=ask_ai(prompt);notice=retrieval.get("coverage_notice")
 if not verified:notice="No matching traceable verified indexed Georgia authority was found. General legal information may be shown, but GA.LAW.HELP will not invent or present an unverified citation as governing Georgia law."
 response={"mode":mode,"analysis":analysis,"authorities":retrieval.get("hits",[]),"grounded_authority_count":len(verified),"coverage_notice":notice,"used_encounter_pack":bool(pack)}
 specs={"talk_to_me":TALK_SECTIONS,"case_analysis":CASE_ANALYSIS_SECTIONS,"rights":RIGHTS_SECTIONS,"motions":MOTIONS_SECTIONS}
 response["sections"]=_extract_sections(analysis,specs[mode])
 return response
