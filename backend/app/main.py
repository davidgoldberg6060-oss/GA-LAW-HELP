import hashlib, os, uuid
from contextlib import asynccontextmanager
from .storage import MAX_EVIDENCE_BYTES, save_chunk, finalize_chunks, store_stream, hash_stored
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from .database import Base, engine, get_db, database_health, verify_production_schema
from . import models, schemas
from .auth import hash_password, verify_password, create_token, current_user, owned_case, require_admin
from .token_service import (issue_refresh, rotate_refresh, revoke_refresh, issue_reset, consume_reset,
    issue_email_verification, consume_email_verification, revoke_all_user_refresh_tokens)
from .email_delivery import deliver_verification, deliver_password_reset, deliver_encounter_notice
from .ai_assistant import ask_openai

def validate_production_config():
    if os.getenv('ENVIRONMENT','development').lower() == 'production':
        if os.getenv('JWT_SECRET','CHANGE-ME-IN-PRODUCTION') == 'CHANGE-ME-IN-PRODUCTION':
            raise RuntimeError('JWT_SECRET must be configured in production')
        if len(os.getenv('JWT_SECRET','')) < 32:
            raise RuntimeError('JWT_SECRET must contain at least 32 characters')
        if os.getenv('DATABASE_URL','').startswith('sqlite') or not os.getenv('DATABASE_URL'):
            raise RuntimeError('A production PostgreSQL DATABASE_URL is required')
        if 'sslmode=' not in os.getenv('DATABASE_URL',''):
            raise RuntimeError('Production DATABASE_URL must explicitly enable SSL with sslmode=require or verify-full')
        if os.getenv('DEV_EXPOSE_RESET_TOKEN','false').lower() == 'true' or os.getenv('DEV_EXPOSE_VERIFICATION_TOKEN','false').lower() == 'true':
            raise RuntimeError('Development token exposure must be disabled in production')
        if os.getenv('STORAGE_BACKEND','local').lower() != 's3':
            raise RuntimeError('Production evidence storage must use STORAGE_BACKEND=s3')
        storage_required=('S3_BUCKET','S3_ENDPOINT_URL','AWS_REGION','AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY')
        storage_missing=[name for name in storage_required if not os.getenv(name)]
        if storage_missing:
            raise RuntimeError('Production S3 storage configuration is incomplete: '+', '.join(storage_missing))
        if not os.getenv('ALLOWED_HOSTS','').strip():
            raise RuntimeError('ALLOWED_HOSTS must list the production API hostname')
        if os.getenv('REQUIRE_VERIFIED_EMAIL','true').lower() == 'true':
            required=('PUBLIC_APP_URL','SMTP_HOST','SMTP_FROM')
            missing=[name for name in required if not os.getenv(name)]
            if os.getenv('MAIL_DELIVERY_MODE','disabled').lower() != 'smtp' or missing:
                raise RuntimeError('Verified-email production mode requires SMTP delivery: '+', '.join(missing))
            if not os.getenv('PUBLIC_APP_URL','').startswith('https://'):
                raise RuntimeError('PUBLIC_APP_URL must use HTTPS in production')

@asynccontextmanager
async def lifespan(_app:FastAPI):
    validate_production_config()
    if os.getenv('ENVIRONMENT','development').lower() == 'production':
        verify_production_schema()
    else:
        Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title='STANDALONE ASSISTANT GA.LAW.HELP', version='1.3.0', lifespan=lifespan)
EVIDENCE_DIR = os.getenv('EVIDENCE_DIR', './evidence_store'); os.makedirs(EVIDENCE_DIR, exist_ok=True)
origins=[x.strip() for x in os.getenv('CORS_ALLOWED_ORIGINS','').split(',') if x.strip()]
# Railway assigns HTTPS subdomains to services. Permit those browser origins by default
# while retaining CORS_ALLOWED_ORIGINS for exact custom domains.
origin_regex=os.getenv('CORS_ALLOWED_ORIGIN_REGEX',r'^https://[a-zA-Z0-9-]+\\.up\\.railway\\.app$').strip() or None
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_origin_regex=origin_regex,allow_credentials=False,allow_methods=['GET','POST','PUT','PATCH','DELETE'],allow_headers=['Authorization','Content-Type','X-Request-ID'])
allowed_hosts=[x.strip() for x in os.getenv('ALLOWED_HOSTS','').split(',') if x.strip()]
if allowed_hosts:
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=allowed_hosts)

@app.middleware('http')
async def security_headers(request:Request,call_next):
    request_id=request.headers.get('X-Request-ID') or uuid.uuid4().hex
    response=await call_next(request)
    response.headers['X-Request-ID']=request_id
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='no-referrer'
    response.headers['Cache-Control']='no-store'
    if os.getenv('ENVIRONMENT','development').lower() == 'production':
        response.headers['Strict-Transport-Security']='max-age=31536000; includeSubDomains'
    return response

def audit(db, user_id, action, obj, oid=None):
    db.add(models.AuditLog(user_id=user_id, action=action, object_type=obj, object_id=str(oid) if oid else None))

@app.get('/health')
def health(): return {'status':'ok','service':'GA.LAW.HELP','version':'1.3.0'}

@app.get('/health/live')
def liveness(): return {'status':'ok'}

@app.get('/health/ready')
def readiness():
    try:
        return {'status':'ready',**database_health()}
    except Exception:
        raise HTTPException(503,'Database unavailable')

@app.get('/public/research')
def public_research(q:str=''):
    query=q.strip()
    if not query:
        raise HTTPException(400,'Enter a Georgia legal question')
    lower=query.lower()
    resources=[
        {'title':'Georgia General Assembly — Georgia Code','url':'https://www.legis.ga.gov/legislation/georgia-code','kind':'Statutes','official':True},
        {'title':'Supreme Court of Georgia — Opinions','url':'https://www.gasupreme.us/opinions/','kind':'Court opinions','official':True},
        {'title':'Court of Appeals of Georgia — Opinions','url':'https://www.gaappeals.us/opinions/','kind':'Court opinions','official':True},
    ]
    topic='Georgia legal research'
    guidance='Start with the current Georgia Code, then check controlling Georgia appellate decisions and the rule in effect on the relevant date.'
    if any(x in lower for x in ('criminal','arrest','warrant','search','felony','misdemeanor','sentence','probation')):
        topic='Georgia criminal law and procedure'
        guidance='Identify the exact charge or police action, incident date, county, and case stage. Check the statute text, effective date, and later appellate interpretations.'
    elif any(x in lower for x in ('custody','divorce','child support','family','marriage')):
        topic='Georgia family law'
        guidance='Identify the county, existing orders, filing stage, and dates. Court forms and local rules may matter in addition to the Georgia Code.'
        resources.append({'title':'Georgia Judicial Council — Self-Help Resources','url':'https://georgiacourts.gov/a2j/self-help-resources-highlighted-by-a2j/','kind':'Court resources','official':True})
    elif any(x in lower for x in ('appeal','habeas','conviction','ineffective','plea')):
        topic='Georgia appeal or post-conviction research'
        guidance='Deadlines and procedural history are critical. Gather the docket, judgment, transcripts, motions, appellate decisions, and earlier habeas filings before relying on a remedy.'
    elif any(x in lower for x in ('tenant','landlord','eviction','rent','lease')):
        topic='Georgia landlord-tenant law'
        guidance='Identify the lease terms, notices, filing county, dates, and whether a court case has begun. Verify current statutes and local court procedures.'
    return {
        'query':query,
        'topic':topic,
        'guidance':guidance,
        'resources':resources,
        'notice':'This is a research starting point, not legal advice. Verify the current text, dates, court rules, and case-specific facts before relying on it.'
    }

@app.post('/cases/{case_id}/motion-screen')
def private_motion_screen(case_id:int,body:dict,user=Depends(current_user),db:Session=Depends(get_db)):
    case=owned_case(case_id,user,db)
    supplied=str(body.get('facts','')).strip()
    if len(supplied)>12000: raise HTTPException(400,'Case summary is too long.')
    facts=supplied or ('Case title: '+(case.title or '')+'\nCase number: '+(case.case_number or 'Not entered')+'\nGeorgia county: '+(case.county or 'Not entered')+'\nCase type: '+(case.case_type or 'Not entered')+'\nCurrent stage: '+(case.stage or 'Not entered')+'\nCase narrative: '+(case.narrative or 'Not entered'))
    prompt='GEORGIA CRIMINAL CASE MOTION SCREEN. Analyze only supplied case facts. Identify potentially relevant procedural options, motions, or post-conviction remedies without predicting outcomes. For each relevant option explain why it may apply, missing facts or records, timing issues to verify, authority that must be verified before filing, likely State counterarguments, and the next record to obtain. Never invent statutes, cases, deadlines, judges, or local filing rules. Distinguish pretrial, trial, direct review, and post-conviction procedures. End with a prioritized verification checklist. CASE INFORMATION:\n'+facts
    try: answer=ask_openai(prompt)
    except RuntimeError: raise HTTPException(503,'The motion screening assistant is temporarily unavailable.')
    audit(db,user.id,'RUN_MOTION_SCREEN','case',case_id);db.commit()
    return {'analysis':answer,'notice':'AI-generated legal information, not legal advice. Verify current authority, deadlines, record facts, and local filing requirements before filing.'}

@app.post('/admin/legal/sources/bootstrap-georgia')
def bootstrap_georgia_sources(admin=Depends(require_admin),db:Session=Depends(get_db)):
    sources=[
      {'name':'Supreme Court of Georgia — Opinions','jurisdiction':'Georgia','base_url':'https://www.gasupreme.us/opinions/','source_type':'COURT_OPINIONS','official':True,'enabled':True},
      {'name':'Court of Appeals of Georgia — Opinions','jurisdiction':'Georgia','base_url':'https://www.gaappeals.us/opinions/','source_type':'COURT_OPINIONS','official':True,'enabled':True},
      {'name':'Georgia General Assembly — Georgia Code','jurisdiction':'Georgia','base_url':'https://www.legis.ga.gov/legislation/georgia-code','source_type':'STATUTES','official':True,'enabled':True},
      {'name':'Judicial Council of Georgia','jurisdiction':'Georgia','base_url':'https://georgiacourts.gov/','source_type':'COURT_RESOURCES','official':True,'enabled':True},
    ]
    created=0
    for item in sources:
        row=db.query(models.LegalSource).filter_by(name=item['name']).first()
        if row:
            row.base_url=item['base_url'];row.source_type=item['source_type'];row.official=True;row.enabled=True
        else:
            db.add(models.LegalSource(**item));created+=1
    audit(db,admin.id,'BOOTSTRAP_GEORGIA_SOURCES','legal_source');db.commit()
    return {'created':created,'configured':len(sources),'notice':'Official-source registry configured. This does not claim all opinions have been ingested; coverage stats show actual indexed material.'}

@app.post('/admin/legal/authorities/{authority_id}/versions/import')
def import_authority_version(authority_id:int,body:schemas.AuthorityVersionCreate,admin=Depends(require_admin),db:Session=Depends(get_db)):
    authority=db.get(models.LegalAuthority,authority_id)
    if not authority: raise HTTPException(404,'Authority not found')
    source=body.source_url.strip()
    if not source.startswith('https://'): raise HTTPException(400,'Authority source must use HTTPS')
    digest=hashlib.sha256(body.text.encode('utf-8')).hexdigest()
    existing=db.query(models.AuthorityVersion).filter_by(authority_id=authority_id,content_sha256=digest).first()
    if existing: return {'id':existing.id,'created':False,'sha256':digest,'verification_status':existing.verification_status}
    row=models.AuthorityVersion(authority_id=authority_id,content_sha256=digest,**body.model_dump());db.add(row);db.flush();audit(db,admin.id,'IMPORT_AUTHORITY_VERSION','authority_version',row.id);db.commit();db.refresh(row)
    return {'id':row.id,'created':True,'sha256':digest,'verification_status':row.verification_status,'source_url':row.source_url}

@app.post('/admin/legal/authorities/import')
def import_authority(body:schemas.AuthorityCreate,admin=Depends(require_admin),db:Session=Depends(get_db)):
    citation=body.citation.strip(); source=(body.source_url or '').strip()
    if not citation: raise HTTPException(400,'Citation is required')
    if source and not source.startswith('https://'): raise HTTPException(400,'Authority source must use HTTPS')
    existing=db.query(models.LegalAuthority).filter(models.LegalAuthority.jurisdiction==body.jurisdiction,models.LegalAuthority.citation==citation).first()
    if existing:
        return {'id':existing.id,'created':False,'citation':existing.citation,'status':existing.status,'notice':'Existing authority retained; add a separately sourced version rather than silently overwriting legal text.'}
    row=models.LegalAuthority(**body.model_dump()); row.citation=citation; row.retrieved_at=models.utcnow(); db.add(row);db.flush();audit(db,admin.id,'IMPORT_AUTHORITY','legal_authority',row.id);db.commit();db.refresh(row)
    return {'id':row.id,'created':True,'citation':row.citation,'status':row.status,'source_url':row.source_url}

@app.get('/admin/legal/sources')
def legal_sources(admin=Depends(require_admin),db:Session=Depends(get_db)):
    rows=db.query(models.LegalSource).order_by(models.LegalSource.official.desc(),models.LegalSource.name).all()
    return [{'id':x.id,'name':x.name,'jurisdiction':x.jurisdiction,'base_url':x.base_url,'source_type':x.source_type,'official':x.official,'enabled':x.enabled} for x in rows]

@app.get('/legal/authorities/stats')
def authority_stats(user=Depends(current_user),db:Session=Depends(get_db)):
    total=db.query(models.LegalAuthority).count()
    versions=db.query(models.AuthorityVersion).count()
    verified_versions=db.query(models.AuthorityVersion).filter(models.AuthorityVersion.verification_status.in_(['VERIFIED','OFFICIAL','CURRENT'])).count()
    ga_cases=db.query(models.LegalAuthority).filter(models.LegalAuthority.jurisdiction.ilike('%Georgia%'),models.LegalAuthority.authority_type.ilike('%case%')).count()
    official_sources=db.query(models.LegalSource).filter_by(official=True,enabled=True).count()
    return {'authorities':total,'authority_versions':versions,'verified_versions':verified_versions,'georgia_cases':ga_cases,'enabled_official_sources':official_sources,'notice':'Coverage counts describe what GA.LAW.HELP has actually indexed; they do not imply every public Georgia court record is present.'}

@app.get('/cases/{case_id}/similar-authorities')
def similar_authorities(case_id:int,q:str='',user=Depends(current_user),db:Session=Depends(get_db)):
    case=owned_case(case_id,user,db)
    raw=q.strip() or ' '.join(filter(None,[case.case_type,case.stage,case.narrative or '']))
    stop={'case','court','georgia','criminal','civil','with','from','that','this','have','were','been','into','your','their','about','not','entered','current'}
    terms=[]
    for token in raw.replace('\\n',' ').replace(',',' ').replace('.',' ').split():
        term=''.join(ch for ch in token.lower() if ch.isalnum() or ch in ('-','/'))
        if len(term)>=4 and term not in stop and term not in terms: terms.append(term)
        if len(terms)>=12: break
    query=db.query(models.LegalAuthority).filter(models.LegalAuthority.jurisdiction.ilike('%Georgia%'))
    if terms:
        from sqlalchemy import or_
        filters=[]
        for term in terms:
            like='%'+term+'%'; filters.extend([models.LegalAuthority.title.ilike(like),models.LegalAuthority.citation.ilike(like),models.LegalAuthority.text.ilike(like)])
        query=query.filter(or_(*filters))
    rows=query.limit(40).all(); ranked=[]
    for authority in rows:
        hay=' '.join(filter(None,[authority.title,authority.citation,authority.text])).lower()
        score=sum(1 for term in terms if term in hay)
        versions=db.query(models.AuthorityVersion).filter_by(authority_id=authority.id).all()
        verified=[v for v in versions if str(v.verification_status or '').upper() in ('VERIFIED','OFFICIAL','CURRENT')]
        ranked.append((score,authority,verified))
    ranked.sort(key=lambda item:(item[0],len(item[2])),reverse=True)
    results=[{'id':a.id,'citation':a.citation,'title':a.title,'status':a.status,'source_url':a.source_url,'match_score':score,'verified_versions':[{'id':v.id,'source_url':v.source_url,'effective_from':v.effective_from,'effective_to':v.effective_to,'verification_status':v.verification_status} for v in verified]} for score,a,verified in ranked[:25]]
    return {'case_id':case_id,'query_terms':terms,'results':results,'notice':'Results are ranked research leads from the indexed Georgia authority corpus, not a determination that an authority controls this case. Verify facts, procedural posture, dates, authority status, and current law.'}

@app.post('/cases/{case_id}/defense-analysis')
def defense_analysis(case_id:int,body:dict,user=Depends(current_user),db:Session=Depends(get_db)):
    case=owned_case(case_id,user,db)
    supplied=str(body.get('facts','')).strip()
    facts=supplied or ('Case title: '+(case.title or '')+'\nCase number: '+(case.case_number or 'Not entered')+'\nGeorgia county: '+(case.county or 'Not entered')+'\nCase type: '+(case.case_type or 'Not entered')+'\nCurrent stage: '+(case.stage or 'Not entered')+'\nCase narrative: '+(case.narrative or 'Not entered'))
    if len(facts)>16000: raise HTTPException(400,'Case summary is too long.')
    linked=[]
    for link in db.query(models.CaseAuthorityLink).filter_by(case_id=case_id).all():
        authority=db.get(models.LegalAuthority,link.authority_id)
        version=db.get(models.AuthorityVersion,link.authority_version_id) if link.authority_version_id else None
        if authority:
            linked.append({'citation':authority.citation,'title':authority.title,'verified':bool(link.verified),'status':authority.status,'proposition':link.proposition,'relevance':link.relevance,'source_url':(version.source_url if version else authority.source_url)})
    authority_context='\n'.join([('VERIFIED' if x['verified'] else 'UNVERIFIED')+' | '+str(x['citation'])+' | '+str(x['title'])+' | proposition: '+str(x['proposition'])+' | relevance: '+str(x['relevance']) for x in linked]) or 'No case authorities have been linked and verified yet.'
    prompt='DEFENSE-SIDE GEORGIA CASE ANALYSIS. Ask: What lawful arguments could defense counsel reasonably have investigated or raised? Do not assume innocence or guilt and do not predict an outcome. Separate allegations, established record facts, disputed facts, and unknowns. Screen suppression, admissibility, identification, searches, statements/interrogations, discovery, expert evidence, charging defects, jury instructions, sufficiency, alternative explanations, impeachment, plea/sentencing issues, appeals, and post-conviction remedies when relevant. For each potential strategy explain factual prerequisites, legal authority that must be verified, likely State response, evidence that strengthens or weakens it, and procedural timing. Never invent a case, citation, holding, deadline, fact, or court action. If the record is insufficient say so. End with records to obtain and issues to research in authoritative Georgia sources. You may specifically cite only authorities shown below as VERIFIED; otherwise describe the legal issue without inventing a citation. VERIFIED/LINKED AUTHORITIES:\n'+authority_context+'\nCASE INFORMATION:\n'+facts
    try: answer=ask_openai(prompt)
    except RuntimeError: raise HTTPException(503,'The defense analysis assistant is temporarily unavailable.')
    audit(db,user.id,'RUN_DEFENSE_ANALYSIS','case',case_id);db.commit()
    return {'analysis':answer,'linked_authorities':linked,'notice':'Defense-side research analysis only. It does not establish innocence or guilt and is not legal advice. Verify the record, current authority, deadlines, and local rules.'}

@app.post('/public/ask')
def public_ask(body: dict):
    question=str(body.get('question','')).strip()
    if not question:
        raise HTTPException(400,'Enter a Georgia legal question')
    if len(question) > 6000:
        raise HTTPException(400,'Question is too long')
    try:
        answer=ask_openai(question)
    except RuntimeError:
        raise HTTPException(503,'The AI assistant is temporarily unavailable. Please try again shortly.')
    return {
        'question':question,
        'answer':answer,
        'notice':'AI-generated legal information can be wrong or incomplete. Verify important points against current official law and consult a licensed attorney for advice about your situation.'
    }

@app.post('/auth/register')
def register(body: schemas.UserCreate, db: Session=Depends(get_db)):
    email=body.email.lower()
    if db.query(models.User).filter_by(email=email).first(): raise HTTPException(409,'Email exists')
    admin_emails={x.strip().lower() for x in os.getenv('ADMIN_EMAILS','').split(',') if x.strip()}
    u=models.User(email=email,password_hash=hash_password(body.password),role='admin' if email in admin_emails else 'user'); db.add(u); db.flush(); audit(db,u.id,'REGISTER','user',u.id)
    verification=issue_email_verification(db,u.id); db.commit()
    delivered=deliver_verification(u.email,verification)
    response={'verification_required':os.getenv('REQUIRE_VERIFIED_EMAIL','false').lower()=='true','user':{'id':u.id,'email':u.email}}
    response['verification_delivery']='sent' if delivered else 'unavailable'
    if os.getenv('DEV_EXPOSE_VERIFICATION_TOKEN','false').lower()=='true': response['dev_verification_token']=verification
    if not response['verification_required']:
        refresh=issue_refresh(db,u.id); db.commit(); response.update({'access_token':create_token(u.id),'refresh_token':refresh,'token_type':'bearer'})
    return response

@app.post('/auth/login')
def login(body: schemas.Login, db: Session=Depends(get_db)):
    u=db.query(models.User).filter_by(email=body.email.lower()).first()
    if not u or not verify_password(body.password,u.password_hash): raise HTTPException(401,'Invalid credentials')
    if not u.is_active: raise HTTPException(401,'Invalid credentials')
    if os.getenv('REQUIRE_VERIFIED_EMAIL','false').lower()=='true' and not u.verified_at:
        raise HTTPException(403,'Email verification required')
    audit(db,u.id,'LOGIN','user',u.id); refresh=issue_refresh(db,u.id); db.commit()
    return {'access_token':create_token(u.id),'refresh_token':refresh,'token_type':'bearer'}


@app.post('/auth/refresh')
def refresh(body: schemas.RefreshRequest, db: Session=Depends(get_db)):
    rotated=rotate_refresh(db,body.refresh_token)
    if not rotated: raise HTTPException(401,'Invalid or expired refresh token')
    uid,new_refresh=rotated; db.commit()
    return {'access_token':create_token(uid),'refresh_token':new_refresh,'token_type':'bearer'}

@app.post('/auth/logout')
def logout(body: schemas.LogoutRequest, db: Session=Depends(get_db)):
    revoked=revoke_refresh(db,body.refresh_token)
    if revoked: db.commit()
    return {'logged_out':True}

@app.post('/auth/forgot-password')
def forgot_password(body: schemas.ForgotPasswordRequest, db: Session=Depends(get_db)):
    u=db.query(models.User).filter_by(email=body.email.lower()).first()
    # Enumeration-safe response. Delivery adapter can send the reset token by email/SMS.
    if u:
        token=issue_reset(db,u.id); audit(db,u.id,'PASSWORD_RESET_REQUEST','user',u.id); db.commit(); deliver_password_reset(u.email,token)
        if os.getenv('DEV_EXPOSE_RESET_TOKEN','false').lower()=='true': return {'accepted':True,'dev_reset_token':token}
    return {'accepted':True}

@app.post('/auth/reset-password')
def reset_password(body: schemas.ResetPasswordRequest, db: Session=Depends(get_db)):
    uid=consume_reset(db,body.token)
    if not uid: raise HTTPException(400,'Invalid or expired reset token')
    u=db.get(models.User,uid); u.password_hash=hash_password(body.new_password)
    revoke_all_user_refresh_tokens(db,uid)
    audit(db,uid,'PASSWORD_RESET_COMPLETE','user',uid); db.commit()
    return {'reset':True}

@app.post('/auth/verify-email')
def verify_email(body: schemas.VerifyEmailRequest, db: Session=Depends(get_db)):
    uid=consume_email_verification(db,body.token)
    if not uid: raise HTTPException(400,'Invalid or expired verification token')
    u=db.get(models.User,uid)
    u.verified_at=models.utcnow()
    audit(db,uid,'EMAIL_VERIFIED','user',uid); db.commit()
    return {'verified':True}

@app.post('/auth/resend-verification')
def resend_verification(body: schemas.ResendVerificationRequest, db: Session=Depends(get_db)):
    u=db.query(models.User).filter_by(email=body.email.lower()).first()
    response={'accepted':True}
    if u and not u.verified_at:
        token=issue_email_verification(db,u.id); audit(db,u.id,'EMAIL_VERIFICATION_REQUEST','user',u.id); db.commit(); deliver_verification(u.email,token)
        if os.getenv('DEV_EXPOSE_VERIFICATION_TOKEN','false').lower()=='true': response['dev_verification_token']=token
    return response

@app.get('/me')
def me(user=Depends(current_user)): return {'id':user.id,'email':user.email,'role':user.role,'verified_at':user.verified_at,'created_at':user.created_at}

@app.get('/cases')
def list_cases(user=Depends(current_user), db:Session=Depends(get_db)):
    rows=db.query(models.Case).filter_by(owner_id=user.id).order_by(models.Case.created_at.desc()).all()
    return [{'id':c.id,'title':c.title,'case_number':c.case_number,'county':c.county,'case_type':c.case_type,'stage':c.stage} for c in rows]

@app.post('/cases')
def create_case(body:schemas.CaseCreate,user=Depends(current_user),db:Session=Depends(get_db)):
    c=models.Case(owner_id=user.id,**body.model_dump()); db.add(c); db.flush(); audit(db,user.id,'CREATE_CASE','case',c.id); db.commit(); db.refresh(c)
    return {'id':c.id,'title':c.title,'stage':c.stage}

@app.get('/cases/{case_id}')
def get_case(case_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    c=owned_case(case_id,user,db)
    return {'id':c.id,'title':c.title,'case_number':c.case_number,'county':c.county,'case_type':c.case_type,'stage':c.stage,'narrative':c.narrative,'created_at':c.created_at}

@app.patch('/cases/{case_id}')
def update_case(case_id:int,body:schemas.CaseUpdate,user=Depends(current_user),db:Session=Depends(get_db)):
    c=owned_case(case_id,user,db)
    changes=body.model_dump(exclude_unset=True)
    for key,value in changes.items(): setattr(c,key,value)
    audit(db,user.id,'UPDATE_CASE','case',c.id); db.commit(); db.refresh(c)
    return {'id':c.id,'title':c.title,'case_number':c.case_number,'county':c.county,'case_type':c.case_type,'stage':c.stage,'narrative':c.narrative,'updated_at':c.updated_at}

@app.post('/cases/{case_id}/timeline')
def add_timeline(case_id:int,body:schemas.TimelineCreate,user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db); e=models.TimelineEvent(case_id=case_id,**body.model_dump()); db.add(e); db.flush(); audit(db,user.id,'ADD_TIMELINE_EVENT','timeline_event',e.id); db.commit(); db.refresh(e)
    return {'id':e.id,'source_label':e.source_label}

@app.get('/cases/{case_id}/timeline')
def timeline(case_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db); rows=db.query(models.TimelineEvent).filter_by(case_id=case_id).order_by(models.TimelineEvent.occurred_at).all()
    return [{'id':x.id,'occurred_at':x.occurred_at,'type':x.event_type,'title':x.title,'details':x.details,'source_label':x.source_label,'source_ref':x.source_ref} for x in rows]

@app.post('/cases/{case_id}/evidence')
def upload_evidence(case_id:int,file:UploadFile=File(...),user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db); safe=os.path.basename(file.filename or 'evidence'); key=f'{user.id}/{case_id}/{uuid.uuid4().hex}_{safe}'
    try: digest,size=store_stream(file.file,key)
    except ValueError as exc: raise HTTPException(413,str(exc))
    media_type=file.content_type or 'application/octet-stream'
    ev=models.Evidence(case_id=case_id,filename=safe,media_type=media_type,sha256=digest,storage_key=key,size_bytes=size); db.add(ev); db.flush()
    job_types=['PROBE_MEDIA','TRANSCRIBE_DEEP_LISTENING']
    if media_type.startswith('video/'): job_types += ['FRAME_ANALYSIS','REFLECTION_ANALYSIS','OFF_CAMERA_RECONSTRUCTION']
    for jt in job_types: db.add(models.AnalysisJob(evidence_id=ev.id,job_type=jt,status='QUEUED'))
    audit(db,user.id,'UPLOAD_EVIDENCE','evidence',ev.id); db.commit(); db.refresh(ev)
    notice_sent=deliver_encounter_notice(user.email,ev.filename,ev.sha256,size) if media_type.startswith(('audio/','video/')) else False
    return {'id':ev.id,'filename':ev.filename,'bytes':size,'sha256':ev.sha256,'original_preserved':True,'jobs_queued':job_types,'owner_email_notice_sent':notice_sent}

@app.get('/cases/{case_id}/evidence')
def evidence(case_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db); rows=db.query(models.Evidence).filter_by(case_id=case_id).all()
    return [{'id':e.id,'filename':e.filename,'media_type':e.media_type,'bytes':e.size_bytes,'sha256':e.sha256,'uploaded_at':e.uploaded_at,'verified_at':e.verified_at,'original_preserved':e.original_preserved} for e in rows]

@app.post('/cases/{case_id}/evidence/{evidence_id}/verify')
def verify_evidence_integrity(case_id:int,evidence_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    ev=db.query(models.Evidence).filter_by(id=evidence_id,case_id=case_id).first()
    if not ev: raise HTTPException(404,'Evidence not found')
    try: digest,size=hash_stored(ev.storage_key)
    except FileNotFoundError: raise HTTPException(409,'Stored original is unavailable')
    verified=digest==ev.sha256 and size==ev.size_bytes
    if verified: ev.verified_at=models.utcnow()
    audit(db,user.id,'VERIFY_EVIDENCE_INTEGRITY','evidence',ev.id); db.commit()
    return {'id':ev.id,'verified':verified,'expected_sha256':ev.sha256,'actual_sha256':digest,'expected_bytes':ev.size_bytes,'actual_bytes':size,'verified_at':ev.verified_at}


@app.post('/cases/{case_id}/uploads/init')
def init_upload(case_id:int, body:schemas.UploadInit, user=Depends(current_user), db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    if body.total_bytes and body.total_bytes > MAX_EVIDENCE_BYTES: raise HTTPException(413,'evidence exceeds MAX_EVIDENCE_BYTES')
    uid=str(uuid.uuid4())
    row=models.UploadSession(id=uid,case_id=case_id,user_id=user.id,filename=os.path.basename(body.filename),media_type=body.media_type,total_chunks=body.total_chunks,total_bytes=body.total_bytes)
    db.add(row); audit(db,user.id,'INIT_RESUMABLE_UPLOAD','upload_session',uid); db.commit()
    return {'upload_id':uid,'chunk_size_recommended':8*1024*1024,'total_chunks':body.total_chunks}

@app.put('/cases/{case_id}/uploads/{upload_id}/chunks/{index}')
def put_chunk(case_id:int, upload_id:str, index:int, file:UploadFile=File(...), user=Depends(current_user), db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    row=db.query(models.UploadSession).filter_by(id=upload_id,case_id=case_id,user_id=user.id).first()
    if not row: raise HTTPException(404,'Upload session not found')
    if row.status != 'UPLOADING': raise HTTPException(409,'Upload session is not active')
    if index < 0 or index >= row.total_chunks: raise HTTPException(400,'Invalid chunk index')
    data=file.file.read()
    try: n=save_chunk(user.id,case_id,upload_id,index,data)
    except ValueError as exc: raise HTTPException(413,str(exc))
    return {'upload_id':upload_id,'chunk':index,'bytes':n,'accepted':True}

@app.post('/cases/{case_id}/uploads/{upload_id}/complete')
def complete_upload(case_id:int, upload_id:str, user=Depends(current_user), db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    row=db.query(models.UploadSession).filter_by(id=upload_id,case_id=case_id,user_id=user.id).first()
    if not row: raise HTTPException(404,'Upload session not found')
    if row.status != 'UPLOADING': raise HTTPException(409,'Upload session is not active')
    try: key,digest,size=finalize_chunks(user.id,case_id,upload_id,row.filename,row.total_chunks,row.total_bytes)
    except FileNotFoundError as e: raise HTTPException(409,str(e))
    except ValueError as e: raise HTTPException(409,str(e))
    ev=models.Evidence(case_id=case_id,filename=row.filename,media_type=row.media_type,sha256=digest,storage_key=key,size_bytes=size)
    db.add(ev); db.flush()
    job_types=['PROBE_MEDIA','TRANSCRIBE_DEEP_LISTENING']
    if row.media_type.startswith('video/'): job_types += ['FRAME_ANALYSIS','REFLECTION_ANALYSIS','OFF_CAMERA_RECONSTRUCTION']
    for jt in job_types: db.add(models.AnalysisJob(evidence_id=ev.id,job_type=jt,status='QUEUED'))
    row.status='COMPLETE'; audit(db,user.id,'COMPLETE_RESUMABLE_UPLOAD','evidence',ev.id); db.commit(); db.refresh(ev)
    return {'evidence_id':ev.id,'bytes':size,'sha256':digest,'original_preserved':True,'jobs_queued':job_types}

@app.get('/cases/{case_id}/evidence/{evidence_id}/jobs')
def evidence_jobs(case_id:int,evidence_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    ev=db.query(models.Evidence).filter_by(id=evidence_id,case_id=case_id).first()
    if not ev: raise HTTPException(404,'Evidence not found')
    rows=db.query(models.AnalysisJob).filter_by(evidence_id=evidence_id).all()
    return [{'id':j.id,'type':j.job_type,'status':j.status,'progress':j.progress,'error':j.error} for j in rows]


@app.post('/legal/authorities')
def create_authority(body:schemas.AuthorityCreate,user=Depends(require_admin),db:Session=Depends(get_db)):
    row=models.LegalAuthority(**body.model_dump()); db.add(row); db.flush(); audit(db,user.id,'CREATE_AUTHORITY','legal_authority',row.id); db.commit(); db.refresh(row)
    return {'id':row.id,'citation':row.citation,'status':row.status}

@app.post('/legal/authorities/{authority_id}/versions')
def add_authority_version(authority_id:int,body:schemas.AuthorityVersionCreate,user=Depends(require_admin),db:Session=Depends(get_db)):
    if not db.get(models.LegalAuthority,authority_id): raise HTTPException(404,'Authority not found')
    digest=hashlib.sha256(body.text.encode()).hexdigest(); row=models.AuthorityVersion(authority_id=authority_id,content_sha256=digest,**body.model_dump()); db.add(row); db.flush(); audit(db,user.id,'ADD_AUTHORITY_VERSION','authority_version',row.id); db.commit(); db.refresh(row)
    return {'id':row.id,'sha256':digest,'verification_status':row.verification_status}

@app.get('/legal/authorities/search')
def search_authorities(q:str='',as_of:str|None=None,user=Depends(current_user),db:Session=Depends(get_db)):
    from datetime import date as D
    query=db.query(models.LegalAuthority); like=f'%{q}%'; query=query.filter((models.LegalAuthority.citation.ilike(like)) | (models.LegalAuthority.title.ilike(like))) if q else query
    target=D.fromisoformat(as_of) if as_of else None; out=[]
    for a in query.limit(50).all():
        vv=db.query(models.AuthorityVersion).filter_by(authority_id=a.id).all(); vv=[v for v in vv if not target or ((not v.effective_from or v.effective_from<=target) and (not v.effective_to or v.effective_to>=target))]
        out.append({'id':a.id,'citation':a.citation,'title':a.title,'status':a.status,'versions':[{'id':v.id,'effective_from':v.effective_from,'effective_to':v.effective_to,'verification_status':v.verification_status,'source_url':v.source_url} for v in vv]})
    return {'as_of':as_of,'results':out,'warning':'Verify authority status and historical applicability against the official source before legal reliance.'}

@app.post('/cases/{case_id}/authorities')
def link_authority(case_id:int,body:schemas.AuthorityLinkCreate,user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    authority=db.get(models.LegalAuthority,body.authority_id)
    if not authority: raise HTTPException(404,'Authority not found')
    if body.authority_version_id:
        version=db.get(models.AuthorityVersion,body.authority_version_id)
        if not version or version.authority_id != body.authority_id: raise HTTPException(400,'Authority version does not belong to authority')
    row=models.CaseAuthorityLink(case_id=case_id,**body.model_dump()); db.add(row); db.flush(); audit(db,user.id,'LINK_AUTHORITY','case_authority_link',row.id); db.commit(); return {'id':row.id}

@app.get('/cases/{case_id}/why')
def why(case_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db); out=[]
    for l in db.query(models.CaseAuthorityLink).filter_by(case_id=case_id).all():
        a=db.get(models.LegalAuthority,l.authority_id); v=db.get(models.AuthorityVersion,l.authority_version_id) if l.authority_version_id else None
        out.append({'proposition':l.proposition,'relevance':l.relevance,'verified':l.verified,'citation':a.citation,'authority_status':a.status,'source_url':v.source_url if v else a.source_url,'pinpoint':l.pinpoint,'source_location':l.source_location,'effective_from':v.effective_from if v else a.effective_from,'effective_to':v.effective_to if v else a.effective_to,'version_verification':v.verification_status if v else None})
    return {'case_id':case_id,'why':out}

# --- v0.9 case-workspace intelligence endpoints ---
def _issue_payload(x):
    return {'id':x.id,'issue':x.issue,'category':x.category,'favors':x.favors,'analysis':x.analysis,
            'counterargument':x.counterargument,'facts_needed':x.facts_needed,'confidence':x.confidence}

@app.get('/cases/{case_id}/analysis')
def get_case_analysis(case_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    rows=db.query(models.IssueAnalysis).filter_by(case_id=case_id).order_by(models.IssueAnalysis.id.desc()).all()
    return {'case_id':case_id,'findings':[_issue_payload(x) for x in rows],
            'notice':'Screening findings are research leads, not legal conclusions. Verify facts, deadlines, authority status, and procedural posture.'}

@app.post('/cases/{case_id}/analysis/run')
def run_case_analysis(case_id:int,body:schemas.CaseAnalysisRequest,user=Depends(current_user),db:Session=Depends(get_db)):
    c=owned_case(case_id,user,db)
    # v0.9 deliberately creates issue-screening leads from case posture/narrative. It does not invent case law.
    text=((c.stage or '')+' '+(c.narrative or '')).lower()
    candidates=[]
    def add(issue,category,favors,analysis,counter,facts,confidence='NEEDS_REVIEW'):
        candidates.append(models.IssueAnalysis(case_id=case_id,issue=issue,category=category,favors=favors,
            analysis=analysis,counterargument=counter,facts_needed=facts,confidence=confidence))
    if any(k in text for k in ['search','warrant','traffic stop','seized','police entered']):
        add('Search / seizure review','constitutional','USER','Facts suggest Fourth Amendment / Georgia search-and-seizure review may be relevant.','Government may argue a warrant, consent, probable cause, an exception, standing limits, or harmlessness.','Warrant and affidavit; bodycam; inventory/return; suppression filings; exact search and seizure timeline.')
    if any(k in text for k in ['plea','guilty','pleaded']):
        add('Plea validity review','plea','USER','The case narrative indicates a plea, so voluntariness, advice, plea terms, and the plea colloquy should be reviewed.','The record may show a knowing and voluntary plea and valid waiver.','Plea transcript; plea form; counsel file; plea offer; sentencing transcript; dates and advice given.')
    if any(k in text for k in ['sentence','sentenced','years','merger']):
        add('Sentence / merger review','sentencing','USER','The record should be checked for statutory sentencing limits, merger, and sentence structure.','The counts may involve distinct conduct/elements and the sentence may fall within authorized limits.','Indictment/accusation; verdict or plea; sentencing transcript; written sentence; offense dates; count-by-count sentence.')
    if any(k in text for k in ['appeal','habeas','ineffective','lawyer','attorney']):
        add('Preservation / post-conviction review','post_conviction','MIXED','The procedural posture suggests review of preservation, deadlines, prior rulings, and potentially available appellate or post-conviction issues.','Claims may be waived, defaulted, untimely, previously decided, insufficiently preserved, or unavailable in the present vehicle.','Complete docket; notices of appeal; motion-for-new-trial record; appellate opinions; habeas petitions/orders; transcripts; counsel records.')
    if not candidates:
        add('Complete-record issue screening','case_review','MIXED','There is not enough structured information yet to responsibly identify a specific legal issue.','Incomplete facts can make an apparently favorable issue disappear once the full record is reviewed.','Charging document; docket; stage; offense/incident date; key motions/orders; plea or trial record; sentence; appeal history.')
    # Replace prior auto-screening rows while preserving manually created/non-auto rows in future versions.
    db.query(models.IssueAnalysis).filter_by(case_id=case_id).delete()
    db.add_all(candidates); audit(db,user.id,'RUN_CASE_SCREENING','case',case_id); db.commit()
    return {'case_id':case_id,'focus':body.focus,'findings':[_issue_payload(x) for x in candidates],
            'authority_rule':'No citation is treated as supporting authority unless it is separately linked to the case and verified against a source.'}

@app.get('/cases/{case_id}/red-team')
def case_red_team(case_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    owned_case(case_id,user,db)
    rows=db.query(models.IssueAnalysis).filter_by(case_id=case_id).all()
    return {'case_id':case_id,'items':[{'issue':x.issue,'user_position':x.analysis,'counterargument':x.counterargument,
        'facts_needed':x.facts_needed,'risk':'Needs source and record verification before reliance.'} for x in rows]}

@app.get('/cases/{case_id}/second-look')
def second_look(case_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    c=owned_case(case_id,user,db)
    rows=db.query(models.IssueAnalysis).filter_by(case_id=case_id).all()
    categories=['sentencing','plea','post_conviction','constitutional']
    matches=[_issue_payload(x) for x in rows if x.category in categories]
    return {'case_id':case_id,'stage':c.stage,'screening':matches,
        'required_record':['charging document','plea or trial transcript','sentencing transcript/order','motion-for-new-trial record','appellate opinions/orders','prior habeas filings/orders'],
        'notice':'This is a second-look screening workspace. Remedy availability depends on dates, preservation, prior litigation, retroactivity, and the complete record.'}
