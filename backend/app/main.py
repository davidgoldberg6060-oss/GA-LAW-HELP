"""GA.LAW.HELP API entrypoint with verified motion-screen routing."""
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from . import legacy_main as _legacy_main
from .legacy_main import *
from .legacy_main import audit
from .motion_screen_service import motion_screen_response
from .innocence_analysis_service import innocence_analysis_response
from .case_chat_service import analyze_case_conversation, case_summary_from_case, parse_history
from .internal_legal_search import search_internal
from .loophole_analysis_service import SUGGESTED_TOPICS, analyze_loopholes
from .charge_check_service import analyze_charge_check, charge_check_note_text
from .civil_check_service import analyze_civil_check, civil_check_note_text
from .civil_topics import HELP_LINKS, follow_ups
from . import answer_cache
from .ai_assistant import ask_fast
from . import ai_assistant as _ai
def _model_used():
    return getattr(_ai.last_model_used,'value',None)
from .authority_search_service import persisted_authority_hits, public_law_search, search_georgia_authorities
from .grounded_legal_assistant import grounded_legal_response
from .public_case_service import EXCLUDED_PUBLIC_STATUSES, public_case_payload, safe_public_source_url
from .ingestion.coverage import corpus_coverage
from .encounter_prompt import encounter_prompt_block
from .public_rights import official_indexes, router as public_rights_router

def _delegated_ask_openai(prompt: str):
    return ask_openai(prompt)

_legacy_main.ask_openai = _delegated_ask_openai
app.include_router(public_rights_router)
from .anonymous_access import router as anonymous_router, ai_rate_limit_middleware
app.include_router(anonymous_router)
app.middleware('http')(ai_rate_limit_middleware)

@app.middleware('http')
async def crawler_policy_headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive, nosnippet'
    return response

@app.get('/robots.txt', include_in_schema=False)
def robots_policy():
    return PlainTextResponse('User-agent: *\nDisallow: /\n')

@app.get('/internal/corpus/coverage')
def internal_corpus_coverage(user=Depends(require_paid),db:Session=Depends(get_db)):
    report=corpus_coverage(db,jurisdiction='GA')
    report['release_ready_for_complete_corpus_claim']=False
    report['release_note']='Coverage is an inventory, not a completeness certification. Missing authority must never be fabricated.'
    return report

def _public_georgia_case_query(db: Session):
    return db.query(models.LegalAuthority).filter(
        models.LegalAuthority.jurisdiction.ilike('%Georgia%'),
        or_(models.LegalAuthority.authority_type.ilike('%case%'),models.LegalAuthority.authority_type.ilike('%opinion%')),
        func.lower(models.LegalAuthority.status).notin_(EXCLUDED_PUBLIC_STATUSES),
    )

@app.get('/public/georgia-cases')
def public_georgia_cases(q:str='',page:int=1,page_size:int=25,db:Session=Depends(get_db)):
    q=q.strip()
    if len(q)>500: raise HTTPException(400,'Search query is too long.')
    if page<1 or page_size<1 or page_size>50: raise HTTPException(400,'page must be at least 1 and page_size must be between 1 and 50.')
    filters = (
        or_(models.LegalAuthority.authority_type.ilike('%case%'), models.LegalAuthority.authority_type.ilike('%opinion%')),
        func.lower(models.LegalAuthority.status).notin_(EXCLUDED_PUBLIC_STATUSES),
    )
    if q:
        # Keyword / full-text retrieval (Postgres FTS or portable keyword fallback).
        # Ranked results are paginated in memory for the requested window.
        ranked = search_georgia_authorities(db, q, limit=page * page_size, filters=filters)
        start = (page - 1) * page_size
        page_hits = ranked[start:start + page_size]
        total = len(ranked)
        ids = [hit.id for hit in page_hits]
        if ids:
            fetched = db.query(models.LegalAuthority).filter(models.LegalAuthority.id.in_(ids)).all()
            by_id = {row.id: row for row in fetched}
            rows = [by_id[i] for i in ids if i in by_id]
        else:
            rows = []
    else:
        query = _public_georgia_case_query(db)
        total = query.count()
        rows = query.order_by(models.LegalAuthority.retrieved_at.desc(), models.LegalAuthority.id.desc()).offset((page-1)*page_size).limit(page_size).all()
    notice = (
        'These are indexed public Georgia case-law records. Private user workspaces are never searched. '
        'Sealed, juvenile, expunged, restricted, private, and unavailable records are excluded. '
        'A missing case means it has not yet been indexed or cannot lawfully be displayed. '
        'Search uses keywords and full-text retrieval, not a whole-question substring match.'
    )
    if q and not rows:
        notice += ' No matching indexed authority was found for this query. Missing authority is not invented.'
    return {'query':q,'page':page,'page_size':page_size,'total':total,'cases':[public_case_payload(row) for row in rows],'coverage_notice':notice}

@app.get('/public/georgia-cases/{authority_id}')
def public_georgia_case(authority_id:int,db:Session=Depends(get_db)):
    row=_public_georgia_case_query(db).filter(models.LegalAuthority.id==authority_id).first()
    if not row: raise HTTPException(404,'Public Georgia case not found.')
    return {'case':public_case_payload(row,include_text=True),'coverage_notice':'Verify the opinion and current precedential status against the linked official source before legal reliance.'}

@app.get('/public/georgia-laws/search')
def public_georgia_law_search(kind:str='statutes',q:str='',title:str='',chapter:str='',limit:int=25,db:Session=Depends(get_db)):
    """Guest Georgia Laws screen: statutes/regulations, case law, or court rules from the persisted corpus."""
    q=q.strip()
    if len(q)>400: raise HTTPException(400,'Search keyword is too long.')
    if not q and not title.strip(): raise HTTPException(400,'Enter a keyword or choose a title.')
    try: rows=public_law_search(db,kind=kind,keyword=q,title=title,chapter=chapter,limit=limit)
    except ValueError as error: raise HTTPException(400,str(error))
    items=[{'id':r.id,'citation':r.citation,'title':r.title,'record_type':r.authority_type,'type_label':{'statute':'Statute','court_rule':'Court rule','regulation':'Regulation'}.get((r.authority_type or '').lower(),'Case law' if r.authority_type else ''),'status':r.status,'currency_status':r.currency_status,'precedential_status':r.precedential_status,'source_url':safe_public_source_url(r.source_url),'excerpt':r.text[:600],'usable_as_support':r.usable_as_support} for r in rows]
    return {'kind':kind,'query':q,'title':title,'chapter':chapter,'items':items,'coverage_notice':'Indexed public Georgia authorities. Verify currency against the official source before relying on any result. Missing authority is not invented.'}

def _guest_rights_without_corpus(query:str, mode:str) -> dict:
    """Encounter-pack fallback. Does not invent citations or claim current Georgia law."""
    guidance = encounter_prompt_block(mode, query) or (
        'GA.LAW.HELP could not reach its AI assistant just now, so here is general guidance. '
        'For Georgia civil and criminal questions, free help is available from Georgia Legal Services Program (https://www.glsp.org/), '
        'Atlanta Legal Aid (https://atlantalegalaid.org/), Georgia Courts self-help (https://georgiacourts.gov/a2j/) and the '
        'State Bar of Georgia (https://www.gabar.org/public/find-a-lawyer). Do not miss any court date or deadline on papers you received. '
        'Please try again in a minute.')
    notice = (
        'No indexed Georgia authority was available for this guest request. '
        'This is general encounter information, not a verified citation and not a claim that any rule is current Georgia law. '
        'Stay calm. Do not resist, lie, or destroy evidence.'
    )
    return {
        'guest': True,
        'mode': mode,
        'analysis': guidance,
        'answer': guidance,
        'authorities': [],
        'grounded_authority_count': 0,
        'coverage_notice': notice,
        'official_indexes': official_indexes(),
        'login_required': False,
    }

PUBLIC_ASSISTANT_MODES={'rights','talk_to_me','general'}

def _decorate_public(response:dict,query:str,mode:str)->dict:
    response['guest']=True
    response['login_required'] = False
    response.setdefault('official_indexes',official_indexes())
    if not response.get('answer') and response.get('analysis'): response['answer']=response['analysis']
    response.setdefault('follow_ups',follow_ups(query))
    response.setdefault('help_links',HELP_LINKS)
    return response

@app.post('/public/rights-assistant')
def public_rights_assistant(body:dict,db:Session=Depends(get_db)):
    """Guest grounded assistant. ``rights``/``talk_to_me`` = police encounter help; ``general`` = any
    Georgia criminal or civil legal question (Talk to Me). Answers use the fast model and are cached
    by normalized question + mode for 24 h (guest answers contain no account data)."""
    query=str(body.get('query','')).strip();mode=str(body.get('mode','rights')).strip()
    if not query: raise HTTPException(400,'Describe the encounter or rights question.')
    if len(query)>4000: raise HTTPException(400,'Question is too long.')
    if mode not in PUBLIC_ASSISTANT_MODES: raise HTTPException(400,'Guest mode is limited to rights, live-encounter and general Georgia legal help.')
    cached=answer_cache.get(query,mode,db=db)
    if cached is not None:
        cached['cached']=True
        return cached
    _ai.last_model_used.value=None
    try:
        response = grounded_legal_response(query, mode, ask_fast, db=db)
    except RuntimeError:
        # AI provider unavailable: return the static encounter pack instead of failing the guest.
        fallback = _guest_rights_without_corpus(query, mode)
        fallback['ai_unavailable'] = True
        return _decorate_public(fallback,query,mode)
    except SQLAlchemyError:
        db.rollback()
        return _decorate_public(_guest_rights_without_corpus(query, mode),query,mode)
    response['login_required'] = False
    response['model_used']=_model_used()
    response=_decorate_public(response,query,mode)
    if response.get('answer'): answer_cache.put(query,mode,response,db=db)
    return response

for _route in list(app.router.routes):
    if getattr(_route,'path',None)=='/cases/{case_id}/motion-screen' and 'POST' in getattr(_route,'methods',set()): app.router.routes.remove(_route)

@app.post('/cases/{case_id}/motion-screen')
def private_motion_screen(case_id:int,body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    case=owned_case(case_id,user,db);additional=str(body.get('additional_facts','')).strip()
    if len(additional)>4000: raise HTTPException(400,'Additional case facts are too long.')
    facts=('Case title: '+(case.title or '')+'\nCase number: '+(case.case_number or 'Not entered')+'\nGeorgia county: '+(case.county or 'Not entered')+'\nCase type: '+(case.case_type or 'Not entered')+'\nCurrent stage: '+(case.stage or 'Not entered')+'\nCase narrative: '+(case.narrative or 'Not entered'))
    if additional:facts+='\nAdditional user-supplied facts (not independently verified): '+additional
    if len(facts)>12000:facts=facts[:12000]+'\n[Case text truncated for analysis]'
    try:
        response=motion_screen_response(db, facts, ask_openai)
    except RuntimeError: raise HTTPException(503,'The motion screening assistant is temporarily unavailable.')
    audit(db,user.id,'RUN_MOTION_SCREEN','case',case_id);db.commit();return response

@app.post('/cases/{case_id}/innocence-analysis')
def private_innocence_analysis(case_id:int,body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    case=owned_case(case_id,user,db);additional=str(body.get('additional_facts','')).strip()
    if len(additional)>8000: raise HTTPException(400,'Additional case facts are too long.')
    try: response=innocence_analysis_response(db,case,additional,ask_openai)
    except RuntimeError: raise HTTPException(503,'The case analysis assistant is temporarily unavailable.')
    audit(db,user.id,'RUN_INNOCENCE_ANALYSIS','case',case_id);db.commit();return response

@app.post('/cases/{case_id}/chat')
def private_case_chat(case_id:int,body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    """Conversational grounded Case Analysis: case file + recent turns + current message."""
    case=owned_case(case_id,user,db)
    try:
        response=analyze_case_conversation(user_message=str(body.get('message','')),history=parse_history(body.get('history')),case_summary=case_summary_from_case(case),ask_ai=ask_fast,db=db)
    except ValueError as error: raise HTTPException(400,str(error))
    except RuntimeError: raise HTTPException(503,'The case analysis assistant is temporarily unavailable.')
    audit(db,user.id,'RUN_CASE_CHAT','case',case_id);db.commit();return response

@app.post('/loopholes/analyze')
def loopholes_analyze(body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    """Legal Loopholes: grounded contradictions, gaps, ambiguities and exceptions for a topic."""
    try: response=analyze_loopholes(str(body.get('topic','')),ask_openai,db=db)
    except ValueError as error: raise HTTPException(400,str(error))
    except RuntimeError: raise HTTPException(503,'The legal analysis assistant is temporarily unavailable.')
    audit(db,user.id,'RUN_LOOPHOLE_ANALYSIS','topic',None);db.commit();return response

def save_charge_check_note(db,case_id,user_id,text):
    db.add(models.CaseNote(case_id=case_id,owner_id=user_id,note_type='CHARGE_CHECK',title='Charge Check',content=text,language='en'))

@app.post('/charge-check')
def charge_check(body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    """Charge Check: likely Georgia charges, defenses and lawful lowest-outcome paths for a situation.

    Attaches to ``case_id`` when given (must be owned); otherwise creates a new criminal case
    unless ``save_case`` is false. Refused or empty-input requests never create a case.
    """
    case=None; raw_id=body.get('case_id')
    if raw_id not in (None,''):
        try: case=owned_case(int(raw_id),user,db)
        except (TypeError,ValueError): raise HTTPException(400,'Invalid case id.')
    situation=str(body.get('situation','')).strip() or (str(case.narrative or '').strip() if case is not None else '')
    _ai.last_model_used.value=None
    try: response=analyze_charge_check(situation,ask_openai,db=db,case_summary=case_summary_from_case(case) if case else None)
    except ValueError as error: raise HTTPException(400,str(error))
    except RuntimeError: raise HTTPException(503,'GA.LAW.HELP is busy right now. Your question wasn’t lost — please tap Retry in a minute.')
    response['model_used']=_model_used()
    if not response.get('refused'):
        if case is None and body.get('save_case',True) is not False:
            case=models.Case(owner_id=user.id,title=('Charge Check: '+situation)[:120],case_type='criminal',stage='Pre-charge / investigation',narrative=situation)
            db.add(case);db.flush();audit(db,user.id,'CREATE_CASE','case',case.id)
        if case is not None:
            save_charge_check_note(db,case.id,user.id,charge_check_note_text(response))
    response['case_id']=case.id if case is not None else None
    audit(db,user.id,'RUN_CHARGE_CHECK','case',case.id if case is not None else None);db.commit();return response

@app.post('/cases/{case_id}/charge-check')
def case_charge_check(case_id:int,body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    return charge_check({**body,'case_id':case_id},user,db)

def save_civil_check_note(db,case_id,user_id,text):
    db.add(models.CaseNote(case_id=case_id,owner_id=user_id,note_type='CIVIL_CHECK',title='Civil Case Check',content=text,language='en'))

@app.post('/civil-check')
def civil_check(body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    """Civil Case Check: likely claims/defenses, court, deadlines, evidence and low-cost paths for a dispute.

    Attaches to ``case_id`` when given (must be owned); otherwise creates a new civil case unless
    ``save_case`` is false. Refused requests never create a case."""
    case=None; raw_id=body.get('case_id')
    if raw_id not in (None,''):
        try: case=owned_case(int(raw_id),user,db)
        except (TypeError,ValueError): raise HTTPException(400,'Invalid case id.')
    situation=str(body.get('situation','')).strip() or (str(case.narrative or '').strip() if case is not None else '')
    _ai.last_model_used.value=None
    try: response=analyze_civil_check(situation,ask_openai,db=db,case_summary=case_summary_from_case(case) if case else None)
    except ValueError as error: raise HTTPException(400,str(error))
    except RuntimeError: raise HTTPException(503,'GA.LAW.HELP is busy right now. Your question wasn’t lost — please tap Retry in a minute.')
    response['model_used']=_model_used()
    if not response.get('refused'):
        if case is None and body.get('save_case',True) is not False:
            case=models.Case(owner_id=user.id,title=('Civil Case Check: '+situation)[:120],case_type='civil',stage='Dispute / pre-filing',narrative=situation)
            db.add(case);db.flush();audit(db,user.id,'CREATE_CASE','case',case.id)
        if case is not None:
            save_civil_check_note(db,case.id,user.id,civil_check_note_text(response))
    response['case_id']=case.id if case is not None else None
    audit(db,user.id,'RUN_CIVIL_CHECK','case',case.id if case is not None else None);db.commit();return response

@app.post('/cases/{case_id}/civil-check')
def case_civil_check(case_id:int,body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    return civil_check({**body,'case_id':case_id},user,db)

@app.get('/loopholes/topics')
def loopholes_topics():
    return {'suggested_topics':list(SUGGESTED_TOPICS)}

@app.post('/internal/legal-search')
def internal_legal_search(body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    query=str(body.get('query','')).strip();mode=str(body.get('mode','case_analysis')).strip()
    if len(query)>12000: raise HTTPException(400,'Search text is too long.')
    if mode not in {'case_lookup','case_analysis','rights','motions','talk_to_me','general'}: raise HTTPException(400,'Unsupported legal-search mode.')
    try: limit=int(body.get('limit',12))
    except (TypeError,ValueError): raise HTTPException(400,'Invalid result limit.')
    result=search_internal(query,mode,limit)
    persisted=persisted_authority_hits(db,query,limit=max(1,min(limit,25)))
    if persisted:
        seen={(str(h.get('citation') or '').lower(),str(h.get('source_url') or '')) for h in persisted}
        file_hits=[h for h in result.get('hits',[]) if (str(h.get('citation') or '').lower(),str(h.get('source_url') or '')) not in seen]
        result['hits']=(persisted+file_hits)[:max(1,min(limit,50))]
        result['coverage_notice']='Results include verified authorities persisted by the internal Georgia ingestion pipeline plus indexed corpus records. Missing authority is not invented; unknown currency or precedential status remains explicitly unknown.'
    return result

@app.post('/internal/legal-assistant')
def internal_grounded_legal_assistant(body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    """AI analysis grounded only in verified records from the internal legal corpus."""
    query=str(body.get('query','')).strip();mode=str(body.get('mode','case_analysis')).strip()
    if not query: raise HTTPException(400,'Enter case facts, an encounter description, or a legal question.')
    if len(query)>12000: raise HTTPException(400,'Analysis text is too long.')
    if mode not in {'case_analysis','rights','motions','talk_to_me','general'}: raise HTTPException(400,'Unsupported grounded legal-assistant mode.')
    try: return {**grounded_legal_response(query,mode,ask_openai,db=db),'model_used':_model_used()}
    except RuntimeError: raise HTTPException(503,'The grounded legal assistant is temporarily unavailable.')


# ---------- Privacy policy and account deletion (Google Play requirements) ----------
from pathlib import Path as _Path
import html as _html
from fastapi.responses import HTMLResponse
from .account_deletion import CONFIRM_WORD, delete_account
from .auth import verify_password as _verify_password

PRIVACY_POLICY_MD = (_Path(__file__).with_name('privacy_policy.md')).read_text(encoding='utf-8')

def _inline(text: str) -> str:
    out = _html.escape(text)
    parts = out.split('**')
    return ''.join(f'<strong>{p}</strong>' if i % 2 else p for i, p in enumerate(parts))

def render_policy_html(md: str) -> str:
    body, in_list = [], False
    for line in md.splitlines():
        if line.startswith('- '):
            if not in_list: body.append('<ul>'); in_list = True
            body.append(f'<li>{_inline(line[2:])}</li>'); continue
        if in_list: body.append('</ul>'); in_list = False
        if line.startswith('### '): body.append(f'<h3>{_inline(line[4:])}</h3>')
        elif line.startswith('## '): body.append(f'<h2>{_inline(line[3:])}</h2>')
        elif line.startswith('# '): body.append(f'<h1>{_inline(line[2:])}</h1>')
        elif line.strip(): body.append(f'<p>{_inline(line)}</p>')
    if in_list: body.append('</ul>')
    style = 'body{font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;line-height:1.5;color:#e8f0f8;background:#04121f}h1,h2,h3{color:#d4af37}'
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GA.LAW.HELP Privacy Policy</title><style>{style}</style></head><body>{"".join(body)}</body></html>'

@app.get('/privacy', include_in_schema=False, response_class=HTMLResponse)
def privacy_policy_page():
    return HTMLResponse(render_policy_html(PRIVACY_POLICY_MD))

@app.get('/privacy.md', include_in_schema=False)
def privacy_policy_markdown():
    return PlainTextResponse(PRIVACY_POLICY_MD, media_type='text/markdown; charset=utf-8')

@app.post('/me/delete')
def delete_my_account(body: schemas.AccountDeleteRequest, user=Depends(current_user), db: Session=Depends(get_db)):
    if body.confirm.strip().upper() != CONFIRM_WORD: raise HTTPException(422, f'Type {CONFIRM_WORD} to confirm account deletion')
    if not _verify_password(body.password, user.password_hash): raise HTTPException(403, 'Password is incorrect')
    return delete_account(db, user)


# ---------- AI free-model rotation status ----------
from . import ai_models as _ai_models
import threading as _threading
import os

@app.get('/health/ai')
def health_ai():
    """Cooldown / probe state of each model in the free rotation (no secrets, no prompts)."""
    return {"status": "ok", "last_probe_note": "1-token probe runs once per process at startup", **_ai_models.status()}

# The app uses a lifespan handler (on_event hooks never fire), so start the probe at import time.
if os.getenv('AI_STARTUP_PROBE','1')!='0' and os.getenv('GEMINI_API_KEY','').strip():
    _threading.Thread(target=_ai.probe_models,daemon=True,name='ai-probe').start()
