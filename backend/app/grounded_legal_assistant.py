"""Grounded legal-assistant response construction."""
from __future__ import annotations
import logging
import os
import re
import time
from .internal_legal_search import search_internal
from .authority_search_service import persisted_authority_hits, exact_citation_results, authority_hit, with_as_of, AMENDMENT_NOTE
from . import citation_proposer
from .encounter_prompt import encounter_prompt_block

VERIFIED={"verified","official","validated","confirmed"}
NEGATIVE={"overruled","vacated","superseded","withdrawn","repealed"}
SUPPORTED_MODES={"case_analysis","talk_to_me","rights","motions","general"}
GENERAL_SECTIONS=(("short_answer","SHORT ANSWER"),("how_it_works_in_georgia","HOW IT WORKS IN GEORGIA"),("steps_you_can_take","STEPS YOU CAN TAKE"),("deadlines_and_costs_to_check","DEADLINES AND COSTS TO CHECK"),("where_to_get_help","WHERE TO GET HELP"),("verified_georgia_authority","VERIFIED GEORGIA AUTHORITY"),("important_limitations","IMPORTANT LIMITATIONS"))
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
CONTEXT_MAX_SECTIONS=int(__import__("os").getenv("AI_CONTEXT_MAX_SECTIONS","8"))
CONTEXT_EXCERPT_CHARS=int(__import__("os").getenv("AI_CONTEXT_EXCERPT_CHARS","600"))
def _excerpt(text,limit=None):
 limit=limit or CONTEXT_EXCERPT_CHARS;text=re.sub(r"\s+"," ",str(text or "")).strip()
 return text if len(text)<=limit else text[:limit].rsplit(" ",1)[0]+" …"
_SECTION_RE=re.compile(r"\b\d{1,2}-\d{1,3}-\d+(?:\.\d+)?\b")
def _cite_keys(citation):
 c=str(citation or "");secs=_SECTION_RE.findall(c)
 return secs or ([c.strip().lower()] if c.strip() else [])
def used_in_text(hit,text):
 """True when the answer text actually cites this authority (by Code section number or full citation)."""
 low=str(text or "").lower()
 for k in _cite_keys(hit.get("citation")):
  if re.search(r"(?<![\d.-])"+re.escape(k.lower())+r"(?![\d]|\.\d)",low):return True
 return False
def _authority_context(hits,limit=None,excerpt_chars=None):
 hits=list(hits)[:limit or CONTEXT_MAX_SECTIONS]
 return "\n\n".join(f"[{i}] {h.get('title') or 'Legal authority'}\nCitation: {h.get('citation')}\nText as of: {h.get('as_of') or 'not recorded'}\nVerification: {h.get('verification_status')}{(' (' + h['verification_source'] + ')') if h.get('verification_source') else ''}\nCurrency: {h.get('currency_status') or 'unknown'}\nPrecedential status: {h.get('precedential_status') or 'unknown'}\nStatus checked at: {h.get('status_checked_at') or 'not recorded'}\nStatus source: {h.get('status_source_url') or 'not recorded'}\nStored official/source URL: {h.get('source_url')}\nStored excerpt: {_excerpt(h.get('excerpt'),excerpt_chars)}" for i,h in enumerate(hits,1))

_log=logging.getLogger(__name__)

def _bounded_persisted_hits(db,query,limit):
 """Run the persisted-authority search under a hard Postgres statement_timeout.
 On timeout or DB error, return [] so callers fall back to no-citation guidance."""
 try:dialect=db.get_bind().dialect.name
 except Exception:dialect=""
 if dialect!="postgresql":return persisted_authority_hits(db,query,limit=limit)
 ms=int(os.getenv("RETRIEVAL_TIMEOUT_MS","4000"))
 from sqlalchemy import text
 try:
  with db.begin_nested():
   db.execute(text(f"SET LOCAL statement_timeout = {ms}"))
   hits=persisted_authority_hits(db,query,limit=limit)
   db.execute(text("SET LOCAL statement_timeout = 0"))
  return hits
 except Exception as exc:
  _log.warning("Persisted authority retrieval skipped (timeout or DB error): %s",type(exc).__name__)
  try:db.execute(text("SET LOCAL statement_timeout = 0"))
  except Exception:pass
  return []

def _proposed_hits(db,sections,have):
 """Exact-citation lookup of model-proposed sections; anything not in the database is dropped."""
 if not sections:return []
 cites=[f"O.C.G.A. \u00a7 {s}" for s in sections]
 try:
  with db.begin_nested():rows=exact_citation_results(db,cites)
 except Exception as exc:
  _log.warning("Proposed-citation lookup skipped: %s",type(exc).__name__);return []
 return [authority_hit(r) for r in rows if (r.citation or "").lower() not in have]

def _hybrid_retrieval(query,mode,db=None,limit=12):
 result=search_internal(query,mode,limit)
 if db is None:return result
 # (a) indexed DB search and (b) a quick model step proposing O.C.G.A. sections run in parallel.
 future=None;pool=None
 if citation_proposer.enabled():
  from concurrent.futures import ThreadPoolExecutor
  pool=ThreadPoolExecutor(max_workers=1);future=pool.submit(citation_proposer.propose_sections,query)
 started=time.monotonic()
 persisted=_bounded_persisted_hits(db,query,limit)
 proposed=[]
 if future is not None:
  budget=max(0.0,citation_proposer.timeout_seconds()-(time.monotonic()-started))
  try:sections=future.result(timeout=budget+0.2)
  except Exception:sections=[]
  pool.shutdown(wait=False,cancel_futures=True)
  proposed=_proposed_hits(db,sections,{str(h.get('citation') or '').lower() for h in persisted})
 if proposed:
  room=max(1,limit//3);primary=[h for h in persisted if str(h.get('record_type') or '').lower() in ('statute','court_rule','regulation')]
  others=[h for h in persisted if h not in primary]
  persisted=(primary+proposed[:room]+others)[:limit]
 if not persisted:return result
 seen={(str(h.get('citation') or '').lower(),str(h.get('source_url') or '')) for h in persisted}
 file_hits=[h for h in result.get('hits',[]) if (str(h.get('citation') or '').lower(),str(h.get('source_url') or '')) not in seen]
 result['hits']=(persisted+file_hits)[:limit]
 result['coverage_notice']='Grounding includes verified authorities persisted by the internal Georgia ingestion pipeline plus indexed corpus records. Missing authority is not invented; unknown currency or precedential status remains explicitly unknown.'
 return result

def _mode_instructions(mode):
 if mode=="talk_to_me":return """Use exact headings: WHAT APPEARS TO BE HAPPENING; SAFEST IMMEDIATE STEPS; YOUR RIGHTS; WHAT LAW ENFORCEMENT MAY / MAY NOT DO; WHAT TO SAY OR DO; VERIFIED GEORGIA AUTHORITY; IMPORTANT LIMITATIONS. Prioritize safety. For a live police encounter, do not encourage resistance, evasion, obstruction, evidence destruction, interference, or deception. Treat speech-to-text transcription errors as possible and never claim to have heard facts not supplied. Do not claim recording is lawful unless supplied authority establishes it. Use the in-app encounter pack scripts when the situation matches."""
 if mode=="general":return "Answer a general Georgia legal question (criminal or civil: record restriction/expungement, landlord-tenant, divorce/custody/child support, small claims, debt and garnishment, contracts, injury, wages, consumer, property, name change, wills/probate, etc.). This is NOT a police encounter unless the user says so. Be concise (about 250-400 words). Use exact headings: SHORT ANSWER; HOW IT WORKS IN GEORGIA; STEPS YOU CAN TAKE; DEADLINES AND COSTS TO CHECK; WHERE TO GET HELP; VERIFIED GEORGIA AUTHORITY; IMPORTANT LIMITATIONS. Under WHERE TO GET HELP mention Georgia Legal Services Program / Georgia Legal Aid (glsp.org), Atlanta Legal Aid (atlantalegalaid.org), Georgia Courts self-help (georgiacourts.gov/a2j) and the State Bar of Georgia lawyer referral where relevant. State a deadline, fee, or dollar limit only if a supplied authority's excerpt states it. Never suggest lying, hiding assets, or destroying evidence."
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
 retrieval=_hybrid_retrieval(query,mode,db,12)
 if mode=="general" and db is not None:
  from .civil_topics import topic_hits
  retrieval=topic_hits(db,query,retrieval)
 verified=_verified_hits(retrieval);context=_authority_context(verified) if verified else "No matching traceable verified indexed Georgia authority was retrieved for this question."
 grounding="Base every material Georgia-law conclusion only on supplied authorities." if verified else "No verified indexed Georgia authority is available. You may give clearly labeled general legal information and issue-spotting, but MUST NOT present a Georgia-specific proposition as verified and MUST NOT invent a citation, case, statute, rule, deadline, sentence, or procedure."
 pack=encounter_prompt_block(mode, query)
 prompt=f"""GA.LAW.HELP legal analysis request.\nMode: {mode}\n\nUSER-SUPPLIED FACTS OR QUESTION (not independently verified; may include speech-to-text transcription errors):\n{query}\n\n{pack}\n\nTRACEABLE VERIFIED INDEXED AUTHORITIES:\n{context}\n\nRules:\n- Treat the user's narrative as allegations/facts to be verified, not established facts.\n- {grounding}\n- Cite only supplied authorities, and only those that directly address the question (ignore off-topic ones); never create a citation, case, statute, rule, deadline, sentence, or procedural requirement.\n- When citing an authority that has a 'Text as of' date, write the citation followed by that date in parentheses, e.g. "O.C.G.A. § 44-7-34 (text as of 2022 edition)"; Georgia Code text may have been amended since that edition, so never call it current.\n- Never call authority current, binding, controlling, or precedential unless supplied status metadata establishes it.\n- If Currency or Precedential status is unknown, explicitly label that limitation; do not fill it from memory.\n- Do not predict or guarantee outcomes.\n- Never claim to observe or hear facts not provided.\n- Keep the whole answer under about 350 words and always finish your last sentence.\n\nFORMAT:\n{_mode_instructions(mode)}"""
 analysis=ask_ai(prompt);notice=retrieval.get("coverage_notice")
 if not verified:notice="No matching traceable verified indexed Georgia authority was found. General legal information may be shown, but GA.LAW.HELP will not invent or present an unverified citation as governing Georgia law."
 used=[h for h in verified if used_in_text(h,analysis)]
 # Only list verified authorities the answer actually cites, so the citation list stays on topic.
 # If the answer cites none, show just the top few retrieved records (verified or labeled unverified).
 shown=used or retrieval.get("hits",[])[:3]
 amendment=None
 if any(h.get("as_of") for h in shown if h in verified):
  amendment=AMENDMENT_NOTE
  # Added server-side after the AI text so it always shows, even if the model's answer was trimmed.
  if analysis and AMENDMENT_NOTE not in analysis:analysis=f"{analysis.rstrip()}\n\nNote: {AMENDMENT_NOTE}"
  notice=f"{notice} {AMENDMENT_NOTE}".strip() if notice else AMENDMENT_NOTE
 authorities=[{**h,"citation":h.get("display_citation") or with_as_of(h.get("citation"),h.get("as_of")),"citation_raw":h.get("citation")} if h.get("as_of") else h for h in shown]
 response={"mode":mode,"analysis":analysis,"authorities":authorities,"amendment_note":amendment,"grounded_authority_count":len(verified),"cited_authority_count":len(used),"coverage_notice":notice,"used_encounter_pack":bool(pack)}
 specs={"talk_to_me":TALK_SECTIONS,"case_analysis":CASE_ANALYSIS_SECTIONS,"rights":RIGHTS_SECTIONS,"motions":MOTIONS_SECTIONS,"general":GENERAL_SECTIONS}
 response["sections"]=_extract_sections(analysis,specs[mode])
 return response
