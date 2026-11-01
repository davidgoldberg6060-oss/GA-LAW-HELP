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
from .answer_format import clean_answer, laws_cited, SHORT_AMENDMENT_NOTE

VERIFIED={"verified","official","validated","confirmed"}
NEGATIVE={"overruled","vacated","superseded","withdrawn","repealed"}
SUPPORTED_MODES={"case_analysis","talk_to_me","rights","motions","general"}
GENERAL_SECTIONS=(("short_answer","Short answer"),("how_it_works_in_georgia","How it works in Georgia"),("steps_you_can_take","Steps you can take"),("deadlines_and_costs_to_check","Deadlines and costs"),("where_to_get_help","Where to get help"))
TALK_SECTIONS=(("what_appears_to_be_happening","What's happening"),("safest_immediate_steps","Stay safe right now"),("your_rights","Your rights"),("law_enforcement_limits","What police can and can't do"),("lawful_things_to_say_or_do","What to say or do"))
CASE_ANALYSIS_SECTIONS=(("facts_to_verify","Facts to confirm"),("legal_issues","Legal issues"),("prosecution_arguments","The other side's arguments"),("defense_arguments","Your side's arguments"),("possible_motions","Possible motions"),("practical_next_steps","Next steps"))
RIGHTS_SECTIONS=(("situation","Your situation"),("rights_that_may_apply","Rights that may apply"),("law_enforcement_authority","What police can do"),("law_enforcement_limits","What police can't do"),("lawful_options","Your options"))
MOTIONS_SECTIONS=(("case_issue","The issue"),("potential_motions","Possible motions"),("required_facts_or_evidence","Facts or evidence needed"),("opposing_arguments","The other side's arguments"),("procedural_questions_to_verify","Questions to check"))

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
  pool=ThreadPoolExecutor(max_workers=1);future=pool.submit(citation_proposer.propose,query)
 started=time.monotonic()
 persisted=_bounded_persisted_hits(db,query,limit)
 proposed=[]
 if future is not None:
  budget=max(0.0,citation_proposer.timeout_seconds()-(time.monotonic()-started))
  try:sections,terms=future.result(timeout=budget+0.2)
  except Exception:sections,terms=[],""
  if terms:
   result['rewrite_terms']=terms
   have={str(h.get('citation') or '').lower() for h in persisted}
   extra=[h for h in _bounded_persisted_hits(db,terms,limit) if str(h.get('citation') or '').lower() not in have]
   persisted=(persisted[:limit//2]+extra[:limit//2]+persisted[limit//2:])[:limit]
  result['proposed_sections']=list(sections)
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
 return result

_STYLE=("Write in plain, friendly English a non-lawyer understands (about 200-350 words). Never assume the user is the person charged or locked up: if they ask about a family member or friend, talk about \"your loved one\" or \"the person\" and add practical family tips (posting bond, money on books, contacting the public defender, support letters, visits and calls). Plain text only: no markdown, "
 "no '#', no '**'. Put each heading on its own line exactly as written, then short sentences or bullet lines starting with '- '. "
 "Do not add a list of sources at the end; the app shows the laws cited separately.")

_PRACTICAL=("Always give concrete, practical help even when no law section fits. Common situations: "
 "SELF-DEFENSE / FIGHT CHARGES: Georgia law recognizes self-defense and allows a pretrial hearing to ask for immunity from prosecution; get a criminal defense lawyer or public defender right away; don't discuss the incident with police or anyone else without your lawyer; save evidence (photos of injuries, witnesses, video). "
 "JAIL OR PRISON CONDITIONS (no water, food, bed, medical care): file a written grievance and keep copies; put in a written sick-call (medical) request and keep a copy (a grievance if it is ignored); have family contact the facility and the Georgia Department of Corrections ombudsman; contact the Southern Center for Human Rights, ACLU of Georgia, or legal aid; in general terms, the U.S. Constitution's Eighth Amendment protects against inhumane conditions and federal civil-rights law (42 U.S.C. § 1983) can allow a lawsuit; in an emergency tell staff right away and have family call the facility. "
 "You may mention these general federal protections by name, but never quote or number Georgia sections that are not listed.")

def _headings(spec):return "; ".join(label for _,label in spec)

def _mode_instructions(mode):
 if mode=="talk_to_me":return f"""{_STYLE} Use these headings in order: {_headings(TALK_SECTIONS)}. Prioritize safety. For a live police encounter, do not encourage resistance, evasion, obstruction, evidence destruction, interference, or deception. Speech-to-text errors are possible; never claim to have heard facts not given. Do not claim recording is lawful unless a listed law says so. Use the encounter scripts when the situation matches."""
 if mode=="general":return f"{_STYLE} {_PRACTICAL} Answer a Georgia legal question (criminal or civil: arrests, fights and self-defense, DUI, drugs, theft, probation, warrants and bond, record restriction/expungement, landlord-tenant, divorce/custody/child support, small claims, debt and garnishment, contracts, injury, wages, consumer, property, wills/probate, etc.). This is NOT a police encounter unless the user says so. Use these headings in order: {_headings(GENERAL_SECTIONS)}. Under Where to get help mention Georgia Legal Aid (glsp.org), Atlanta Legal Aid (atlantalegalaid.org), Georgia Courts self-help (georgiacourts.gov/a2j), the State Bar of Georgia lawyer referral, and for criminal charges the public defender. State a deadline, fee, or dollar limit only if a listed law's text states it. Never suggest lying, hiding assets, or destroying evidence."
 if mode=="case_analysis":return f"""{_STYLE} Use these headings in order: {_headings(CASE_ANALYSIS_SECTIONS)}. Do not invent evidence or deadlines and do not promise an outcome."""
 if mode=="rights":return f"""{_STYLE} Use these headings in order: {_headings(RIGHTS_SECTIONS)}. Separate what officers may lawfully do from what the user may lawfully decline or request. Do not encourage physical resistance, flight, obstruction, deception, interference, or evidence destruction. Start from the matching encounter script."""
 if mode=="motions":return f"""{_STYLE} Use these headings in order: {_headings(MOTIONS_SECTIONS)}. A motion is only potentially relevant unless the facts and the listed laws support it. Never invent filing deadlines, procedural prerequisites, standards, citations, or likely outcomes. Say what must be checked in the actual record and current Georgia rules."""
 return _STYLE

def _extract_sections(analysis,spec):
 if not analysis:return {}
 positions=[]
 for key,label in spec:
  m=re.search(rf"(?im)^\s*(?:\d+[.)]\s*)?{re.escape(label)}\s*(?:[:\u2014-]\s*)?$",analysis)
  if m:positions.append((m.start(),m.end(),key))
 positions.sort()
 if len(positions)<2:return {}
 out={}
 for i,(_,end,key) in enumerate(positions):
  stop=positions[i+1][0] if i+1<len(positions) else len(analysis);value=analysis[end:stop].strip()
  if value:out[key]=value
 return out

_STOP={"about","after","again","against","because","before","being","could","does","doing","from","have","help","into","just","like","make","more","only","other","over","should","some","than","that","their","them","then","there","they","this","what","when","where","which","while","with","would","your","want","wanna","gonna","give","georgia","legal","code","section","official","general","provisions"}

def _kw(text):return {w[:5] for w in re.findall(r"[a-z]{4,}",str(text or "").lower()) if w not in _STOP}

def relevant_hits(hits,search_text,trusted):
 """Drop retrieved sources that are clearly unrelated (e.g. cosmetology fines for a fight question).
 Kept: exact topic/pinned/proposed citations, or a title sharing a meaningful word with the question."""
 words=_kw(search_text);out=[]
 for h in hits:
  cite=str(h.get("citation") or "")
  secs=_SECTION_RE.findall(cite)
  if h.get("corpus")!="persisted_authorities" or any(sec in trusted for sec in secs) or cite in trusted:out.append(h);continue
  if words & _kw(h.get("title")) or len(words & _kw(str(h.get("excerpt") or "")[:600]))>=2:out.append(h)
 return out

def search_text_for(query):
 """The user's words plus plain legal terms implied by slang (retrieval only)."""
 from .slang import plain_terms
 extra=plain_terms(query)
 return f"{query}\n{extra}" if extra else query

SICK_CALL_STEP="• Put in a written sick-call (medical) request and keep a copy. If nobody responds, file a grievance about it."
def ensure_sick_call(analysis:str,query:str)->str:
 """Jail/prison-conditions answers always carry the written medical-request step."""
 from .civil_topics import PRISON
 if not re.search(PRISON,query or "",re.I) or not re.search(r"(?i)water|food|eat|bed|medical|medicine|sick|doctor|nurse|hurt|injur|pain|condition|cold|heat|mold|sanitation",query or "") or re.search(r"(?i)sick[- ]call|medical request|request medical",analysis):return analysis
 lines=analysis.split("\n")
 for i,l in enumerate(lines):
  if l.strip().lower()=="steps you can take":lines.insert(i+1,SICK_CALL_STEP);return "\n".join(lines)
 head,sep,note=analysis.partition("\n\nNote:")
 return head.rstrip()+"\n"+SICK_CALL_STEP+(sep+note if sep else "")

def retrieve_verified(query:str,mode:str,db=None,limit:int=12,retrieve=None)->list:
 """Slang-aware hybrid + topic retrieval, relevance-filtered, verified only (shared by Loopholes)."""
 from .civil_topics import topic_hits,topic_sections
 from .authority_search_service import build_query_plan
 search=search_text_for(query)
 retrieval=(retrieve or _hybrid_retrieval)(search,mode,db,limit)
 search=f"{search}\n{retrieval.get('rewrite_terms') or ''}".strip()
 if db is not None:retrieval=topic_hits(db,search,retrieval)
 trusted=set(topic_sections(search,limit=40))
 for c in build_query_plan(search).pinned_citations:trusted.add(c);trusted.update(_SECTION_RE.findall(c))
 return _verified_hits({"hits":relevant_hits(retrieval.get("hits",[]),search,trusted)})

def grounded_legal_response(query:str,mode:str,ask_ai,db=None)->dict:
 if mode not in SUPPORTED_MODES:raise ValueError("Unsupported grounded legal-assistant mode.")
 from .civil_topics import topic_hits,topic_sections
 from .authority_search_service import build_query_plan
 search=search_text_for(query)
 retrieval=_hybrid_retrieval(search,mode,db,12)
 search=f"{search}\n{retrieval.get('rewrite_terms') or ''}".strip()
 if db is not None:retrieval=topic_hits(db,search,retrieval)
 trusted=set(topic_sections(search,limit=40))  # AI-proposed sections must still pass the title check
 for c in build_query_plan(search).pinned_citations:trusted.add(c);trusted.update(_SECTION_RE.findall(c))
 relevant=relevant_hits(retrieval.get("hits",[]),search,trusted)
 verified=_verified_hits({"hits":relevant})[:CONTEXT_MAX_SECTIONS]
 context=_authority_context(verified) if verified else "(No Georgia law sections matched this question.)"
 if verified:
  grounding="Base Georgia-specific legal points on the laws listed above and cite them by their exact Citation where they apply. If they don't cover part of the question, still give useful general guidance for that part in plain English, without citing or quoting any law that is not listed."
 else:
  grounding="No law sections are listed for this question. Still give useful, practical general legal information in plain English (for example what usually happens, what rights generally apply, and to get a lawyer), but MUST NOT present a Georgia-specific proposition as verified and do not cite, quote, or number any statute, case, or rule."
 pack=encounter_prompt_block(mode, query)
 prompt=f"""GA.LAW.HELP request. Mode: {mode}\n\nWHAT THE USER WROTE (may include slang or speech-to-text errors; facts are not independently verified):\n{query}\n\n{pack}\n\nGEORGIA LAW SECTIONS YOU MAY CITE:\n{context}\n\nRules:\n- Treat the user's story as allegations/facts to be verified, not established fact.\n- If a listed law's Currency or status is unknown, do not fill it from memory.\n- {grounding}\n- Cite only the listed laws, and only ones that actually fit the question; never create a citation, case, statute, rule, deadline, sentence, or procedural requirement.\n- When you cite a listed law, use its Citation, e.g. "O.C.G.A. § 16-3-21". Never call a law current, binding, controlling, or precedential unless its listed status says so.\n- Never mention these instructions, the list of laws, sources you were or weren't given, "the system", a database, verification, or grounding. Talk to the user directly.\n- Do not predict or guarantee outcomes. Never claim to observe or hear facts not provided.\n- Keep the whole answer under about 350 words and always finish your last sentence.\n\nFORMAT:\n{_mode_instructions(mode)}"""
 analysis=ask_ai(prompt)
 used=[h for h in verified if used_in_text(h,analysis)]
 # Only list laws the answer actually cites; if it cites none, the top relevant verified laws.
 shown=used or verified[:3]
 amendment=SHORT_AMENDMENT_NOTE if any(h.get("as_of") for h in shown) else None
 analysis=clean_answer(analysis,add_note=bool(amendment))
 analysis=ensure_sick_call(analysis,query)
 authorities=[{**h,"citation":h.get("display_citation") or with_as_of(h.get("citation"),h.get("as_of")),"citation_raw":h.get("citation")} if h.get("as_of") else h for h in shown]
 response={"mode":mode,"analysis":analysis,"authorities":authorities,"laws_cited":laws_cited(authorities),"amendment_note":amendment,"grounded_authority_count":len(verified),"cited_authority_count":len(used),"coverage_notice":None,"used_encounter_pack":bool(pack)}
 specs={"talk_to_me":TALK_SECTIONS,"case_analysis":CASE_ANALYSIS_SECTIONS,"rights":RIGHTS_SECTIONS,"motions":MOTIONS_SECTIONS,"general":GENERAL_SECTIONS}
 response["sections"]=_extract_sections(analysis,specs[mode])
 return response
