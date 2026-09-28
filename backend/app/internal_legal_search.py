"""Internal legal-corpus retrieval used by GA.LAW.HELP API routes."""
from __future__ import annotations
import json,re
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[2]
CORPUS=ROOT/'data'/'corpus'
FILES={'cases':['georgia_supreme_opinions.jsonl','georgia_court_of_appeals.jsonl'],'statutes':['georgia_statutes.jsonl'],'motions_rules':['georgia_rules_motions.jsonl'],'law_enforcement':['law_enforcement_authorities.jsonl']}
ROUTES={'case_lookup':['cases','statutes'],'case_analysis':['cases','statutes','motions_rules','law_enforcement'],'rights':['law_enforcement','cases','statutes'],'motions':['motions_rules','cases','statutes'],'talk_to_me':['law_enforcement','cases','statutes']}
TOK=re.compile(r'[A-Za-z0-9§.-]+');STOP={'a','an','and','are','as','at','be','by','can','do','for','from','how','i','if','in','is','it','law','me','my','of','on','or','the','to','was','what','when','where','with'};NEGATIVE={'overruled','vacated','superseded','withdrawn','repealed'}
def _tokens(s):return {x.lower() for x in TOK.findall(s or '') if len(x)>1 and x.lower() not in STOP}
def _rows(path):
 if not path.exists():return
 with path.open(encoding='utf-8') as f:
  for line in f:
   try:yield json.loads(line)
   except (json.JSONDecodeError,UnicodeDecodeError):continue
def _body(r):return ' '.join(str(r.get(k) or '') for k in ('title','citation','docket_number','heading','text','authority_text','rule_text','name','topic','court','section_number','decision_date','effective_date'))
def _source_url(value):
 value=str(value or '').strip()
 if not value:return None
 try:
  parsed=urlparse(value);return value if parsed.scheme=='https' and bool(parsed.netloc) else None
 except ValueError:return None
def _verified(r):return str(r.get('verification_status') or r.get('status') or '').strip().lower() in {'verified','official','validated','confirmed'}
def _clean(r,*names):
 for name in names:
  value=str(r.get(name) or '').strip()
  if value:return value
 return None
def _legal_status(r):
 raw=r.get('legal_status') if isinstance(r.get('legal_status'),dict) else {}
 def value(name,default='unknown'):return str(raw.get(name) or r.get(name) or default).strip()
 status_source=_source_url(raw.get('status_source_url') or r.get('status_source_url'));checked=str(raw.get('status_checked_at') or r.get('status_checked_at') or '').strip() or None;negative=raw.get('negative_treatment',r.get('negative_treatment',[]))
 if isinstance(negative,str):negative=[negative]
 if not isinstance(negative,list):negative=[]
 return {'currency_status':value('currency_status'),'precedential_status':value('precedential_status'),'status_checked_at':checked,'status_source_url':status_source,'superseded_by':str(raw.get('superseded_by') or r.get('superseded_by') or '').strip() or None,'negative_treatment':[str(x) for x in negative if str(x).strip()]}
def _metadata(r,corpus):
 return {'record_type':{'cases':'case','statutes':'statute','motions_rules':'rule_or_motion','law_enforcement':'law_enforcement_authority'}.get(corpus,corpus),'court':_clean(r,'court'),'docket_number':_clean(r,'docket_number','case_number'),'decision_date':_clean(r,'decision_date','date_decided','opinion_date','filed_date'),'section_number':_clean(r,'section_number','code_section'),'effective_date':_clean(r,'effective_date'),'jurisdiction':_clean(r,'jurisdiction') or 'Georgia'}
def search_internal(query,mode='case_analysis',limit=12):
 query=(query or '').strip()
 if not query:return {'query':'','mode':mode,'hits':[],'coverage_notice':'Enter facts, a charge, statute, motion, case, or rights question.'}
 q=_tokens(query)
 if not q:return {'query':query,'mode':mode,'hits':[],'coverage_notice':'Add specific legal facts, a charge, statute, motion, case name, or rights issue.'}
 hits=[]
 for corpus in ROUTES.get(mode,ROUTES['case_analysis']):
  for fn in FILES[corpus]:
   for r in _rows(CORPUS/fn):
    body=_body(r);b=_tokens(body);matched=q&b
    if not matched:continue
    coverage=len(matched)/len(q)
    if len(q)>=4 and len(matched)<2 and coverage<0.5:continue
    phrase=1.0 if query.lower() in body.lower() else 0.0;citation=str(r.get('citation') or r.get('section_number') or '').lower();citation_match=0.45 if citation and any(t in citation for t in q) else 0.0;title=' '.join(str(r.get(k) or '') for k in ('title','heading','name','topic')).lower();title_tokens=_tokens(title);title_match=(len(q&title_tokens)/len(q))*0.35 if title_tokens else 0.0;verification_bonus=0.1 if _verified(r) else 0.0;score=coverage+phrase+citation_match+title_match+verification_bonus;excerpt=re.sub(r'\s+',' ',body).strip()[:900]
    hits.append({'corpus':corpus,'score':round(score,4),'title':r.get('title') or r.get('heading') or r.get('name') or r.get('topic') or r.get('citation') or 'Legal authority','citation':r.get('citation') or r.get('section_number'),'source_url':_source_url(r.get('source_url')),'verification_status':r.get('verification_status') or r.get('status') or 'unverified','excerpt':excerpt,**_metadata(r,corpus),**_legal_status(r)})
 hits.sort(key=lambda x:(x['score'],x['verification_status'].lower() in {'verified','official','validated','confirmed'}),reverse=True)
 notice='Results come from GA.LAW.HELP internal indexed public-law records. Missing/unindexed authority is not invented; currency and precedential status remain unknown unless the corpus stores explicit status-check evidence.'
 if not hits:notice='No matching indexed authority was found. Add specific legal facts, a charge, statute, motion, case name, or rights issue. Missing/unindexed authority is not invented.'
 return {'query':query,'mode':mode,'hits':hits[:max(1,min(int(limit),50))],'coverage_notice':notice}
