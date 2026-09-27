"""Internal legal-corpus retrieval used by GA.LAW.HELP API routes."""
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CORPUS=ROOT/'data'/'corpus'
FILES={
 'cases':['georgia_supreme_opinions.jsonl','georgia_court_of_appeals.jsonl'],
 'statutes':['georgia_statutes.jsonl'],
 'motions_rules':['georgia_rules_motions.jsonl'],
 'law_enforcement':['law_enforcement_authorities.jsonl'],
}
ROUTES={
 'case_lookup':['cases','statutes'],
 'case_analysis':['cases','statutes','motions_rules','law_enforcement'],
 'rights':['law_enforcement','cases','statutes'],
 'motions':['motions_rules','cases','statutes'],
 'talk_to_me':['law_enforcement','cases','statutes'],
}
TOK=re.compile(r'[A-Za-z0-9§.-]+')
def _tokens(s): return {x.lower() for x in TOK.findall(s or '') if len(x)>1}
def _rows(path):
 if not path.exists(): return
 with path.open(encoding='utf-8') as f:
  for line in f:
   try: yield json.loads(line)
   except (json.JSONDecodeError,UnicodeDecodeError): continue
def _body(r):
 return ' '.join(str(r.get(k) or '') for k in ('title','citation','docket_number','heading','text','authority_text','rule_text','name','topic','court','section_number'))
def search_internal(query,mode='case_analysis',limit=12):
 query=(query or '').strip()
 if not query: return {'query':'','mode':mode,'hits':[],'coverage_notice':'Enter facts, a charge, statute, motion, case, or rights question.'}
 q=_tokens(query); hits=[]
 for corpus in ROUTES.get(mode,ROUTES['case_analysis']):
  for fn in FILES[corpus]:
   for r in _rows(CORPUS/fn):
    body=_body(r); b=_tokens(body); overlap=len(q&b)/max(1,len(q)); phrase=1 if query.lower() in body.lower() else 0
    score=overlap+phrase
    if score<=0: continue
    excerpt=re.sub(r'\s+',' ',body).strip()[:900]
    hits.append({'corpus':corpus,'score':round(score,4),'title':r.get('title') or r.get('heading') or r.get('name') or r.get('topic') or r.get('citation') or 'Legal authority','citation':r.get('citation'),'source_url':r.get('source_url'),'verification_status':r.get('verification_status') or r.get('status'),'excerpt':excerpt})
 hits.sort(key=lambda x:x['score'],reverse=True)
 return {'query':query,'mode':mode,'hits':hits[:max(1,min(int(limit),50))],'coverage_notice':'Results come from GA.LAW.HELP internal indexed public-law records. Missing/unindexed authority is not invented.'}
