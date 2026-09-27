"""GA.LAW.HELP API entrypoint with verified motion-screen routing."""
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, or_

from . import legacy_main as _legacy_main
from .legacy_main import *
from .legacy_main import audit
from .motion_screen_service import motion_screen_response
from .innocence_analysis_service import innocence_analysis_response
from .internal_legal_search import search_internal
from .public_case_service import EXCLUDED_PUBLIC_STATUSES, public_case_payload

# Keep legacy route call sites testable through app.main.ask_openai while the
# endpoint migration is incremental.
def _delegated_ask_openai(prompt: str):
    return ask_openai(prompt)

_legacy_main.ask_openai = _delegated_ask_openai


@app.middleware('http')
async def crawler_policy_headers(request, call_next):
    """Tell cooperative crawlers not to index or archive API responses."""
    response = await call_next(request)
    response.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive, nosnippet'
    return response


@app.get('/robots.txt', include_in_schema=False)
def robots_policy():
    """Keep cooperative crawlers away from the API surface."""
    return PlainTextResponse('User-agent: *\nDisallow: /\n')


def _public_georgia_case_query(db: Session):
    """Select public case-law authorities without touching user case tables."""
    return db.query(models.LegalAuthority).filter(
        models.LegalAuthority.jurisdiction.ilike('%Georgia%'),
        or_(
            models.LegalAuthority.authority_type.ilike('%case%'),
            models.LegalAuthority.authority_type.ilike('%opinion%'),
        ),
        func.lower(models.LegalAuthority.status).notin_(EXCLUDED_PUBLIC_STATUSES),
    )


@app.get('/public/georgia-cases')
def public_georgia_cases(
    q: str = '',
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
):
    """Search indexed public Georgia cases without requiring ownership or login."""
    q = q.strip()
    if len(q) > 500:
        raise HTTPException(400, 'Search query is too long.')
    if page < 1 or page_size < 1 or page_size > 50:
        raise HTTPException(400, 'page must be at least 1 and page_size must be between 1 and 50.')

    query = _public_georgia_case_query(db)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(
            models.LegalAuthority.title.ilike(like),
            models.LegalAuthority.citation.ilike(like),
            models.LegalAuthority.text.ilike(like),
        ))

    total = query.count()
    rows = (
        query.order_by(
            models.LegalAuthority.retrieved_at.desc(),
            models.LegalAuthority.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        'query': q,
        'page': page,
        'page_size': page_size,
        'total': total,
        'cases': [public_case_payload(row) for row in rows],
        'coverage_notice': (
            'These are indexed public Georgia case-law records. Private user workspaces are never searched. '
            'Sealed, juvenile, expunged, restricted, private, and unavailable records are excluded. '
            'A missing case means it has not yet been indexed or cannot lawfully be displayed.'
        ),
    }


@app.get('/public/georgia-cases/{authority_id}')
def public_georgia_case(authority_id: int, db: Session = Depends(get_db)):
    """Return one indexed public Georgia case-law record and its stored text."""
    row = _public_georgia_case_query(db).filter(
        models.LegalAuthority.id == authority_id
    ).first()
    if not row:
        raise HTTPException(404, 'Public Georgia case not found.')
    return {
        'case': public_case_payload(row, include_text=True),
        'coverage_notice': (
            'Verify the opinion and current precedential status against the linked official source before legal reliance.'
        ),
    }


# Remove only the legacy free-form motion-screen route, preserving every other
# current route and middleware registration from legacy_main.
for _route in list(app.router.routes):
    if getattr(_route, 'path', None) == '/cases/{case_id}/motion-screen' and 'POST' in getattr(_route, 'methods', set()):
        app.router.routes.remove(_route)

@app.post('/cases/{case_id}/motion-screen')
def private_motion_screen(case_id:int,body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    case=owned_case(case_id,user,db)
    additional=str(body.get('additional_facts','')).strip()
    if len(additional)>4000:
        raise HTTPException(400,'Additional case facts are too long.')
    facts=('Case title: '+(case.title or '')+'\nCase number: '+(case.case_number or 'Not entered')+'\nGeorgia county: '+(case.county or 'Not entered')+'\nCase type: '+(case.case_type or 'Not entered')+'\nCurrent stage: '+(case.stage or 'Not entered')+'\nCase narrative: '+(case.narrative or 'Not entered'))
    if additional:
        facts+='\nAdditional user-supplied facts (not independently verified): '+additional
    if len(facts)>12000:
        facts=facts[:12000]+'\n[Case text truncated for analysis]'
    try:
        response=motion_screen_response(db, facts, ask_openai)
    except RuntimeError:
        raise HTTPException(503,'The motion screening assistant is temporarily unavailable.')
    audit(db,user.id,'RUN_MOTION_SCREEN','case',case_id);db.commit()
    return response

@app.post('/cases/{case_id}/innocence-analysis')
def private_innocence_analysis(case_id:int,body:dict,user=Depends(require_paid),db:Session=Depends(get_db)):
    """Analyze user-supplied case details for innocence/doubt issues and verified procedural avenues."""
    case=owned_case(case_id,user,db)
    additional=str(body.get('additional_facts','')).strip()
    if len(additional)>8000:
        raise HTTPException(400,'Additional case facts are too long.')
    try:
        response=innocence_analysis_response(db, case, additional, ask_openai)
    except RuntimeError:
        raise HTTPException(503,'The case analysis assistant is temporarily unavailable.')
    audit(db,user.id,'RUN_INNOCENCE_ANALYSIS','case',case_id);db.commit()
    return response

@app.post('/internal/legal-search')
def internal_legal_search(body:dict,user=Depends(require_paid)):
    """Search GA.LAW.HELP's internal indexed public-law corpus without redirecting users."""
    query=str(body.get('query','')).strip()
    mode=str(body.get('mode','case_analysis')).strip()
    if len(query)>12000:
        raise HTTPException(400,'Search text is too long.')
    if mode not in {'case_lookup','case_analysis','rights','motions','talk_to_me'}:
        raise HTTPException(400,'Unsupported legal-search mode.')
    try:
        limit=int(body.get('limit',12))
    except (TypeError,ValueError):
        raise HTTPException(400,'Invalid result limit.')
    return search_internal(query,mode,limit)
