#!/usr/bin/env python3
"""Law-enforcement rights/procedure authority ingestion for GA.LAW.HELP.

Creates source-grounded records for stops, detention, arrest, searches, warrants,
consent, interrogation/Miranda, vehicles, homes, evidence handling, custody, and
use of force. The app should describe conduct as generally permitted, generally
prohibited, fact-dependent, unsettled, or policy-specific only when supported by
current authority.

This importer only accepts explicitly configured PUBLIC sources. It never treats
an agency policy as constitutional law and never fabricates missing authority.
"""
from __future__ import annotations
import argparse, hashlib, json, re, urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

UA="GA.LAW.HELP-public-legal-corpus/1.0"
ALLOWED_CLASSIFICATIONS={"generally_permitted","generally_prohibited","fact_dependent","unsettled","policy_specific","unclassified"}

@dataclass
class AuthorityRecord:
    jurisdiction: str
    topic: str | None
    authority_level: str | None
    authority_name: str | None
    citation: str | None
    classification: str
    rule_text: str
    source_url: str
    retrieved_at: str
    sha256: str
    effective_date: str | None
    end_date: str | None
    verification_status: str


def fetch(url:str)->str:
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8",errors="replace")


def plain(raw:str)->str:
    raw=re.sub(r"(?is)<script.*?>.*?</script>|<style.*?>.*?</style>"," ",raw)
    return re.sub(r"\s+"," ",re.sub(r"(?s)<[^>]+>"," ",raw)).strip()


def normalize(url:str,raw:str,level:str|None=None,topic:str|None=None)->AuthorityRecord:
    text=plain(raw)
    return AuthorityRecord(
        jurisdiction="Georgia / United States", topic=topic, authority_level=level,
        authority_name=None, citation=None, classification="unclassified",
        rule_text=text, source_url=url,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        sha256=hashlib.sha256(text.encode()).hexdigest(), effective_date=None,
        end_date=None, verification_status="verified_source_pending_rule_segmentation")


def configured(path:Path):
    if not path.exists(): return []
    data=json.loads(path.read_text(encoding="utf-8")); out=[]
    for s in data.get("sources",[]):
        cat=(s.get("category") or "").lower()
        if s.get("enabled",True) and s.get("url") and cat in {"law_enforcement","constitutional_law","criminal_procedure","police_procedure","rights"}:
            out.append((s["url"],s.get("authority_level"),s.get("topic")))
    return out


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--source",action="append",default=[],help="URL; repeatable")
    p.add_argument("--sources-file",default="data/legal_sources.json")
    p.add_argument("--output",default="data/corpus/law_enforcement_authorities.jsonl")
    a=p.parse_args()
    entries=[(u,None,None) for u in a.source] or configured(Path(a.sources_file))
    if not entries: raise SystemExit("No verified law-enforcement authority sources configured; refusing to guess.")
    records=[normalize(url,fetch(url),level,topic) for url,level,topic in entries]
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8") as f:
        for r in records: f.write(json.dumps(asdict(r),ensure_ascii=False)+"\n")
    print(f"Wrote {len(records)} law-enforcement authority snapshots to {out}")
    return 0

if __name__=="__main__": raise SystemExit(main())
