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
GENERAL_SECTIONS=(("short_answer","Short answer"),("how_it_works_in_georgia","How it works in Georgia"),("questions_to_ask_your_lawyer","Questions to ask your lawyer"),("deadlines_and_costs_to_check","Deadlines and costs"),("where_to_get_help","Where to get help"))
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

_STYLE=("Write in plain, friendly English a non-lawyer understands, at about an 8th-grade reading level (about 150-260 words; people read this on a phone with little time). Use short everyday words and short sentences (under 15 words). Under the first heading write only 1-3 short sentences: the most useful answer first. Every bullet is one short line (under about 15 words), optionally followed by one short sentence of detail; put at most 4 bullets under any heading or group label. Be direct and concrete: lead with what helps most for this exact question, and for each law or option you mention say plainly how it can help and when it applies instead of just restating it; cut filler and anything off the question. Answer only the question asked and stay neutral about who is asking: do not assume the user, or anyone else, is arrested, in custody, charged, convicted, a family member, or a caregiver unless the user's own words say so. Use 'you' generally, or 'the person charged' when the user describes a charge without saying whose. If the user clearly says it is about a family member or friend who is in jail, then talk about 'your loved one' and add practical family tips. The text before the user's latest 'User:' line is app instructions and earlier conversation, not facts about the user. Plain text only: no markdown, "
 "no '#', no '**'. Put each heading on its own line exactly as written, then short sentences or bullet lines starting with '- '. "
 "Do not add a list of sources at the end; the app shows the laws cited separately.")

_PRACTICAL=("Always give concrete, practical help even when no law section fits. Common situations: "
 "SELF-DEFENSE / FIGHT CHARGES: Georgia law recognizes self-defense and allows a pretrial hearing to ask for immunity from prosecution; get a criminal defense lawyer or public defender right away; don't discuss the incident with police or anyone else without your lawyer; save evidence (photos of injuries, witnesses, video). "
 "JAIL OR PRISON CONDITIONS (only when the user says someone is in jail or prison; no water, food, bed, medical care): if the user is family or a friend on the outside, lead with what THEY can do: call or write the facility (the counselor, then the warden) and ask for a medical check, contact the Georgia Department of Corrections Ombudsman, contact the person's lawyer or public defender, and keep notes of every call; the person in custody can put in a written sick-call request and a grievance and keep copies; contact the Southern Center for Human Rights, ACLU of Georgia, or legal aid; in general terms, the U.S. Constitution's Eighth Amendment protects against inhumane conditions and federal civil-rights law (42 U.S.C. § 1983) can allow a lawsuit; in an emergency tell staff right away and have family call the facility. "
 "You may mention these general federal protections by name, but never quote or number Georgia sections that are not listed.")

def _headings(spec):return "; ".join(label for _,label in spec)

def _defense_block(question):
 from .defense_help import prompt_block
 return prompt_block(retrieval_question(question))

def _plan_instructions(plan,motions=None):
 from . import defense_plan as _dp
 style=_STYLE.replace("(about 150-260 words; people read this on a phone with little time)","(about 450-620 words for this plan; people read it on a phone, so keep every line short)").replace("Under the first heading write only 1-3 short sentences: the most useful answer first. ","")
 return f"{style} If the user asked a specific question, answer it directly in the Quick answer first. {_dp.prompt_block(plan,motions)}"

def _mode_instructions(mode,question="",plan=None,motions=None):
 if mode=="general" and plan:return _plan_instructions(plan,motions)
 if mode=="talk_to_me":return f"""{_STYLE} Use these headings in order: {_headings(TALK_SECTIONS)}. Prioritize safety. For a live police encounter, do not encourage resistance, evasion, obstruction, evidence destruction, interference, or deception. Speech-to-text errors are possible; never claim to have heard facts not given. Do not claim recording is lawful unless a listed law says so. Use the encounter scripts when the situation matches."""
 if mode=="general":return f"{_STYLE} {_PRACTICAL} Answer a Georgia legal question (criminal or civil: arrests, fights and self-defense, DUI, drugs, theft, probation, warrants and bond, record restriction/expungement, landlord-tenant, divorce/custody/child support, small claims, debt and garnishment, contracts, injury, wages, consumer, property, wills/probate, etc.). This is NOT a police encounter unless the user says so. Use these headings in order: {_headings(GENERAL_SECTIONS)}. {_defense_block(question)} Under Questions to ask your lawyer write 3-5 short questions (under about 15 words each), each ending with '?', that this person could ask a lawyer about THIS topic (for example whether an option or defense applies to their facts, what evidence matters, what the process and deadlines are, what it may cost, and what risks to weigh); do not write action steps there, do not assume they already have a lawyer, and do not state rules or deadlines inside the questions. Under Where to get help write one short line only; the app replaces it with verified, topic-matched resources. Do not name organizations, phone numbers, or websites there. State a deadline, fee, or dollar limit only if a listed law's text states it. Never suggest lying, hiding assets, or destroying evidence."
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

def retrieval_question(query):
 """App clients wrap the user's latest message in instructions plus history ('... User: <message>').
 Law retrieval uses only that latest message so instruction words (e.g. 'incarceration' as an in-scope
 topic) are never treated as facts. The full text still goes to the model as conversation context."""
 from .civil_topics import current_question
 return current_question(query) or str(query or "")

_ANY_SECTION_RE=re.compile(r"(?:O\.?\s?C\.?\s?G\.?\s?A\.?|OCGA|Code Section|Code §|§)\s*§?\s*(\d{1,2}-\d{1,3}-\d+(?:\.\d+)?)",re.I)
_DEADLINE_RE=re.compile(r"\b(\d{1,3})\s*(?:\(\w+\)\s*)?(?:calendar |business |court )?days?\b",re.I)
def citation_check(analysis,verified):
 """Every Georgia Code section the answer cites must be one of the retrieved, verified sources."""
 allowed=set()
 for h in verified:allowed.update(_cite_keys(h.get("citation")))
 cited=[]
 for m in _ANY_SECTION_RE.finditer(str(analysis or "")):
  if m.group(1) not in cited:cited.append(m.group(1))
 return {"cited":cited,"unsupported":[c for c in cited if c not in allowed]}
def source_limited_answer(verified):
 """Fail-closed reply when the model cited law we could not match to retrieved sources."""
 lines=["We couldn't verify the legal citations in the generated answer against our stored Georgia sources, so we are not showing it. Deadlines and rules can decide a case, so please don't rely on a guessed answer."]
 if verified:
  lines.append("Sources that may be relevant (stored text; may be out of date; check the current official version):")
  lines+=["• "+str(h.get("citation"))+(" — "+str(h.get("title")) if h.get("title") else "") for h in verified[:5]]
 lines.append("For exact deadlines, read the paperwork you received, ask the court clerk, or talk to a lawyer, public defender, or legal aid. This is general legal information, not legal advice.")
 return "\n".join(lines)
def unsupported_deadline_warning(analysis,verified):
 """Warn when the answer states a day count that does not appear in any retrieved source excerpt (e.g. the
 relevant subsection was truncated out of the stored excerpt). No legal day counts are hardcoded here."""
 counts={m.group(1) for m in _DEADLINE_RE.finditer(str(analysis or ""))}
 if not counts:return None
 evidence=" ".join(str(h.get("excerpt") or "") for h in verified)
 have={m.group(1) for m in _DEADLINE_RE.finditer(evidence)}
 missing=sorted(counts-have,key=int)
 if not missing:return None
 return "Deadline check: the day count(s) above ("+", ".join(missing)+") could not be confirmed in the stored source text we retrieved. Confirm the exact deadline from your paperwork, the court clerk, or a lawyer before relying on it."

def search_text_for(query):
 """The user's words plus plain legal terms implied by slang (retrieval only)."""
 from .slang import plain_terms
 extra=plain_terms(query)
 return f"{query}\n{extra}" if extra else query

SICK_CALL_STEP="• Ask the facility for a medical check (call the counselor, then the warden), and have the person in custody put in a written sick-call request and keep a copy. If nobody responds, contact the GDC Ombudsman and file a grievance."
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
 search=search_text_for(retrieval_question(query))
 retrieval=(retrieve or _hybrid_retrieval)(search,mode,db,limit)
 search=f"{search}\n{retrieval.get('rewrite_terms') or ''}".strip()
 if db is not None:retrieval=topic_hits(db,search,retrieval)
 trusted=set(topic_sections(search,limit=40))
 for c in build_query_plan(search).pinned_citations:trusted.add(c);trusted.update(_SECTION_RE.findall(c))
 return _verified_hits({"hits":relevant_hits(retrieval.get("hits",[]),search,trusted)})

def _motion_lookup(db,citations,verified):
 """Verified hits for motion citations (O.C.G.A. section numbers or full court-rule citations):
 already-retrieved verified hits first, then an exact DB lookup. Anything not found and verified is dropped."""
 by={}
 def add(h):
  c=str(h.get("citation") or "");by.setdefault(c,h)
  for s in _SECTION_RE.findall(c):by.setdefault(s,h)
 for h in verified:add(h)
 missing=[c for c in citations if c not in by]
 if missing and db is not None:
  secs=[c for c in missing if _SECTION_RE.fullmatch(c)];rules=[c for c in missing if c not in secs]
  found=[]
  try:
   from .charge_check_service import lookup_sections
   with db.begin_nested():
    if secs:found+=lookup_sections(db,secs)
    if rules:found+=[authority_hit(r) for r in exact_citation_results(db,rules)]
  except Exception as exc:
   _log.warning("Motion citation lookup skipped: %s",type(exc).__name__)
  for h in found:
   h.pop("full_text",None);h["excerpt"]=(h.get("excerpt") or "")[:600]
  for h in _verified_hits({"hits":found}):add(h)
 return [by[c] for c in citations if c in by]

def _clarify_response(plan,query,mode):
 """Too vague for a plan (no charge or claim named): ask 1-2 short questions instead of guessing. No model call."""
 from . import defense_plan as _dp
 from .help_resources import replace_help_section
 analysis,help_resources=replace_help_section(_dp.clarify_text(plan),plan.get("facts") or retrieval_question(query))
 analysis=_dp.with_notice(analysis)
 return {"suggested_motions":[],"help_resources":help_resources,"citation_check":"passed","unsupported_citations":[],"deadline_warning":False,"mode":mode,
  "analysis":analysis,"authorities":[],"laws_cited":[],"amendment_note":None,"grounded_authority_count":0,"cited_authority_count":0,"coverage_notice":None,
  "used_encounter_pack":False,"defense_plan":_dp.meta(plan),"follow_ups":_dp.follow_ups(plan),"sections":{}}

def grounded_legal_response(query:str,mode:str,ask_ai,db=None,conversation:list|None=None,plan:dict|None=None)->dict:
 """``plan``: a Defense Plan decision from ``defense_plan`` (uploaded papers pass one). In ``general`` mode it is
 otherwise decided automatically: a user describing their own situation gets "Your Defense Plan".
 ``conversation``: recent turns from conversation_memory (any screen). When given, the model sees them as
 earlier conversation, and a follow-up message ('what motion should I file first?') is retrieved and matched to
 motions together with the user's earlier words so the answer continues from the same situation."""
 if mode not in SUPPORTED_MODES:raise ValueError("Unsupported grounded legal-assistant mode.")
 from .civil_topics import topic_hits,topic_sections
 from .authority_search_service import build_query_plan
 from . import conversation_memory as _cm
 if conversation is not None and _cm.is_empty(conversation):conversation=None
 focus=_cm.focus_question(retrieval_question(query),conversation) if conversation else retrieval_question(query)
 from . import defense_plan as _dp
 if mode=="general" and plan is None:plan=_dp.plan_for(query,conversation)
 if plan and plan.get("status")=="clarify":return _clarify_response(plan,query,mode)
 if plan and plan.get("source")!="document" and len(plan.get("facts") or "")>len(focus):focus=plan["facts"]  # "Build my defense" after earlier facts
 topic_text=focus if focus!=retrieval_question(query) else query
 search=search_text_for(focus)
 retrieval=_hybrid_retrieval(search,mode,db,12)
 search=f"{search}\n{retrieval.get('rewrite_terms') or ''}".strip()
 if db is not None:retrieval=topic_hits(db,search,retrieval)
 from . import defense_help as _dh
 question=focus
 defense_mode=mode in ("general","motions")  # the Motions screen gets the same defense-first law lookup
 ctx_limit=_dh.context_limit(question,CONTEXT_MAX_SECTIONS) if defense_mode else CONTEXT_MAX_SECTIONS
 if plan:ctx_limit=max(ctx_limit,14)
 if defense_mode and db is not None:retrieval=_dh.defense_hits(db,question,retrieval,limit=max(12,ctx_limit))
 if plan and db is not None:retrieval=_dp.plan_hits(db,plan,retrieval,limit=max(14,ctx_limit))
 trusted=set(topic_sections(search,limit=40))  # AI-proposed sections must still pass the title check
 if defense_mode:trusted.update(_dh.defense_sections(question))
 if plan:trusted.update(_dp.plan_sections(plan))
 for c in build_query_plan(search).pinned_citations:trusted.add(c);trusted.update(_SECTION_RE.findall(c))
 relevant=relevant_hits(retrieval.get("hits",[]),search,trusted)
 if mode=="general":relevant=_dh.drop_off_topic(relevant,question,trusted)
 verified=_verified_hits({"hits":relevant})[:ctx_limit]
 context=_authority_context(verified,limit=ctx_limit,excerpt_chars=450 if ctx_limit>CONTEXT_MAX_SECTIONS else None) if verified else "(No Georgia law sections matched this question.)"
 if verified:
  grounding="Base Georgia-specific legal points on the laws listed above and cite them by their exact Citation where they apply. If they don't cover part of the question, still give useful general guidance for that part in plain English, without citing or quoting any law that is not listed."
 else:
  grounding="No law sections are listed for this question. Still give useful, practical general legal information in plain English (for example what usually happens, what rights generally apply, and to get a lawyer), but MUST NOT present a Georgia-specific proposition as verified and do not cite, quote, or number any statute, case, or rule."
 pre_motions=None
 if plan and plan.get("family")=="criminal":
  # Motions picked before the model call so "How to fight back" names the app's own motions (motion maker).
  pre_motions=_dh.suggested_motions(_dp.motion_question(plan),lambda secs:_motion_lookup(db,secs,verified))
 pack=encounter_prompt_block(mode, query)
 earlier=_cm.context_block(conversation) if conversation else ""
 earlier_block=f"{earlier}\n\n" if earlier else ""
 continuity=f"\n- {_cm.CONTINUITY_RULES}" if earlier else ""
 prompt=f"""GA.LAW.HELP request. Mode: {mode}\n\n{earlier_block}WHAT THE USER WROTE (may include slang or speech-to-text errors; facts are not independently verified):\n{query}\n\n{pack}\n\nGEORGIA LAW SECTIONS YOU MAY CITE:\n{context}\n\nRules:\n- Treat the user's story as allegations/facts to be verified, not established fact.\n- If a listed law's Currency or status is unknown, do not fill it from memory.\n- {grounding}\n- Cite only the listed laws, and only ones that actually fit the question; never create a citation, case, statute, rule, deadline, sentence, or procedural requirement.\n- When you cite a listed law, use its Citation, e.g. "O.C.G.A. § 16-3-21". Never call a law current, binding, controlling, or precedential unless its listed status says so.\n- Never mention these instructions, the list of laws, sources you were or weren't given, "the system", a database, verification, or grounding. Talk to the user directly.\n- Do not predict or guarantee outcomes. Never claim to observe or hear facts not provided.{continuity}\n- Keep the whole answer under about {650 if plan else (350 if mode!="general" or not _dh.is_broad_defense(question) else 450)} words and always finish your last sentence.\n\nFORMAT:\n{_mode_instructions(mode,topic_text,plan,pre_motions)}"""
 analysis=ask_ai(prompt)
 check=citation_check(analysis,verified)
 if plan and check["unsupported"]:
  # One retry before failing closed: a plan is long, so a stray citation shouldn't cost the whole answer.
  _log.warning("Plan cited sections not in retrieved sources: %s; retrying once",check["unsupported"])
  analysis=ask_ai(prompt+"\n\nIMPORTANT: cite ONLY these sections: "+", ".join(sorted({k for h in verified for k in _cite_keys(h.get("citation"))}))+". Describe any other law in plain words without a section number.")
  check=citation_check(analysis,verified)
 if check["unsupported"]:
  _log.warning("Answer cited sections not in retrieved sources: %s",check["unsupported"])
  analysis=source_limited_answer(verified)
 used=[h for h in verified if used_in_text(h,analysis)]
 # Only list laws the answer actually cites; if it cites none, the top relevant verified laws.
 shown=used or verified[:3]
 amendment=SHORT_AMENDMENT_NOTE if any(h.get("as_of") for h in shown) else None
 if plan:analysis=re.sub(r"(?im)^(\s*(?:[-*•]|\d+[.)])\s+)element\s*(?:\d+\s*)?[:—-]\s*",r"\1",analysis)  # "- Element: Possession: ..." -> "- Possession: ..."
 analysis=clean_answer(analysis,add_note=bool(amendment),max_words=_dp.max_words(plan) if plan else (_dh.max_words(question) if mode=="general" else 420))
 if mode=="general":analysis=_dh.drop_empty_group_labels(analysis)
 analysis=ensure_sick_call(analysis,retrieval_question(query))
 help_resources=[]
 from .help_resources import replace_help_section,_HELP_HEAD
 help_text=topic_text
 if plan and plan.get("family")=="civil":  # civil help (legal aid by county), never a public defender
  help_text=plan.get("label","")+". "+" ".join(re.findall(r"(?i)\b[a-z]+ county\b",plan.get("facts") or topic_text))
 if mode=="general" or _HELP_HEAD.search(analysis or ""):
  analysis,help_resources=replace_help_section(analysis,help_text)
 if mode=="general":
  from .help_resources import ensure_lawyer_questions
  analysis=ensure_lawyer_questions(analysis,topic_text)
 authorities=[{**h,"citation":h.get("display_citation") or with_as_of(h.get("citation"),h.get("as_of")),"citation_raw":h.get("citation")} if h.get("as_of") else h for h in shown]
 deadline_warning=unsupported_deadline_warning(analysis,verified)
 if deadline_warning:analysis=analysis.rstrip()+"\n\n"+deadline_warning
 # Motions from the app's motion library, only when relevant and only with verified Georgia law.
 motions=[];case_stage=None
 if mode=="general" and not (plan and plan.get("family")=="civil"):
  from .case_guide import detect_stage
  mq=_dp.motion_question(plan) if plan else question
  case_stage=detect_stage(mq) or _dh.default_stage(mq)
  motions=pre_motions if pre_motions is not None else _dh.suggested_motions(mq,lambda secs:_motion_lookup(db,secs,verified))
  if motions:
   section=_dh.motions_section(motions,bool(case_stage))
   placed=_dp.insert_before(analysis,section,("Options to lessen the outcome","Key deadlines","Evidence to gather now")) if plan else None
   analysis=placed if placed is not None else _dh.insert_motions(analysis,section)
   have={str(a.get("citation_raw") or a.get("citation") or "").lower() for a in authorities}
   for m in motions:
    for h in m["authorities"]:
     if str(h.get("citation") or "").lower() not in have:
      have.add(str(h.get("citation") or "").lower());authorities.append({**h,"citation":h.get("display_citation") or with_as_of(h.get("citation"),h.get("as_of")),"citation_raw":h.get("citation")} if h.get("as_of") else h)
 response={"suggested_motions":[{k:v for k,v in m.items() if k!="authorities"} for m in motions],"help_resources":help_resources,"citation_check":"failed_closed" if check["unsupported"] else "passed","unsupported_citations":check["unsupported"],"deadline_warning":bool(deadline_warning),"mode":mode,"analysis":analysis,"authorities":authorities,"laws_cited":laws_cited(authorities),"amendment_note":amendment,"grounded_authority_count":len(verified),"cited_authority_count":len(used),"coverage_notice":None,"used_encounter_pack":bool(pack)}
 if case_stage:response["case_stage"]=case_stage
 if plan:
  response["analysis"]=_dp.title_line(plan)+"\n\n"+_dp.with_notice(response["analysis"])
  response["defense_plan"]=_dp.meta(plan)
  if _dp.follow_ups(plan):response["follow_ups"]=_dp.follow_ups(plan)
 if conversation:response["focus_question"]=focus
 response["analysis"]=re.sub(r"\n{3,}","\n\n",response["analysis"] or "")
 specs={"talk_to_me":TALK_SECTIONS,"case_analysis":CASE_ANALYSIS_SECTIONS,"rights":RIGHTS_SECTIONS,"motions":MOTIONS_SECTIONS,"general":GENERAL_SECTIONS+(("motions_that_could_help",_dh.MOTIONS_HEADING),)}
 response["sections"]=_extract_sections(analysis,_dp.section_spec(plan) if plan else specs[mode])
 return response
