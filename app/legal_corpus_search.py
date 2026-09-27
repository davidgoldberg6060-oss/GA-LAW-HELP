"""Unified internal legal-corpus retrieval for GA.LAW.HELP.

Searches the app's locally ingested public legal corpus: Georgia appellate cases,
statutes, rules/motion authorities, and law-enforcement authorities. No browser
redirects are required by this module. AI layers should ground answers in the
returned records and expose citations/source metadata to the user.
"""
from __future__ import annotations
import json, math, re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

CORPUS_DIR=Path("data/corpus")
FILES={
 "cases":["georgia_supreme_opinions.jsonl","georgia_court_of_appeals.jsonl"],
 "statutes":["georgia_statutes.jsonl"],
 "motions_rules":["georgia_rules_motions.jsonl"],
 "law_enforcement":["law_enforcement_authorities.jsonl"],
}
TOKEN=re.compile(r"[A-Za-z0-9§.-]+")

@dataclass
class SearchHit:
    corpus:str
    score:float
    title:str
    citation:str|None
    source_url:str|None
    verification_status:str|None
    excerpt:str
    record:dict


def tokens(s:str)->set[str]: return {x.lower() for x in TOKEN.findall(s) if len(x)>1}

def records(path:Path)->Iterable[dict]:
    if not path.exists(): return
    with path.open(encoding="utf-8") as f:
        for line in f:
            try: yield json.loads(line)
            except json.JSONDecodeError: continue

def searchable(r:dict)->str:
    keys=("title","citation","docket_number","heading","text","authority_text","rule_text","name","topic","court","section_number")
    return " ".join(str(r.get(k) or "") for k in keys)

def score(query:str,r:dict)->float:
    q=tokens(query); body=searchable(r); b=tokens(body)
    if not q: return 0.0
    overlap=len(q & b)/len(q)
    phrase=1.0 if query.lower() in body.lower() else 0.0
    cite=0.4 if r.get("citation") and str(r["citation"]).lower() in query.lower() else 0.0
    return overlap + phrase + cite

def excerpt(text:str,query:str,limit:int=650)->str:
    clean=re.sub(r"\s+"," ",text).strip()
    if len(clean)<=limit:return clean
    terms=list(tokens(query)); low=clean.lower(); positions=[low.find(t) for t in terms if low.find(t)>=0]
    pos=min(positions) if positions else 0; start=max(0,pos-limit//3); end=min(len(clean),start+limit)
    return ("…" if start else "")+clean[start:end]+("…" if end<len(clean) else "")

def search(query:str,corpora:list[str]|None=None,limit:int=12)->list[dict]:
    selected=corpora or list(FILES); hits=[]
    for corpus in selected:
        for filename in FILES.get(corpus,[]):
            for r in records(CORPUS_DIR/filename):
                s=score(query,r)
                if s<=0: continue
                body=searchable(r)
                title=str(r.get("title") or r.get("heading") or r.get("name") or r.get("topic") or r.get("citation") or "Legal authority")
                hit=SearchHit(corpus,s,title,r.get("citation"),r.get("source_url"),r.get("verification_status") or r.get("status"),excerpt(body,query),r)
                hits.append(hit)
    hits.sort(key=lambda h:h.score,reverse=True)
    return [asdict(h) for h in hits[:max(1,min(limit,50))]]

def build_grounding_packet(query:str,mode:str="case_analysis",limit:int=12)->dict:
    routing={
      "case_lookup":["cases","statutes"],
      "case_analysis":["cases","statutes","motions_rules","law_enforcement"],
      "rights":["law_enforcement","cases","statutes"],
      "motions":["motions_rules","cases","statutes"],
      "talk_to_me":["law_enforcement","cases","statutes"],
    }
    hits=search(query,routing.get(mode),limit)
    return {
      "query":query,"mode":mode,"hits":hits,
      "instruction":"Answer from these internal records. Distinguish binding authority, persuasive material, agency policy, and unresolved/fact-dependent issues. Never invent citations, cases, deadlines, or outcomes. If the corpus is insufficient, say so."
    }

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("query"); p.add_argument("--mode",default="case_analysis"); p.add_argument("--limit",type=int,default=12)
    a=p.parse_args(); print(json.dumps(build_grounding_packet(a.query,a.mode,a.limit),indent=2,ensure_ascii=False))
