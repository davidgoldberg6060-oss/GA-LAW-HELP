"""GA.LAW.HELP API entrypoint with verified motion-screen routing."""
from . import legacy_main as _legacy_main
from .legacy_main import *
from .legacy_main import audit
from .motion_screen_service import motion_screen_response

# Keep legacy route call sites testable through app.main.ask_openai while the
# endpoint migration is incremental.
def _delegated_ask_openai(prompt: str):
    return ask_openai(prompt)

_legacy_main.ask_openai = _delegated_ask_openai

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
