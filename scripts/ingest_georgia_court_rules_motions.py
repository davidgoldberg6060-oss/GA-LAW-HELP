#!/usr/bin/env python3
"""Georgia court-rules and motion-authority ingestion for GA.LAW.HELP.

Builds an internal, source-grounded corpus used by the AI to identify potentially
relevant motions and procedural rules. It does NOT claim that a motion is proper
for a user's case without checking facts, court, posture, deadlines, and current
authority.

Only explicitly configured PUBLIC sources are imported. Missing material is
marked unavailable rather than invented.
"""
from __future__ import annotations
import argparse, hashlib, json, re, urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

UA="GA.LAW.HELP-public-legal-corpus/1.0"

@dataclass
class ProcedureRecord:
    jurisdiction: str
    record_type: str
    court: str | None
    name: str | None
    citation: str | None
    procedural_stage: str | None
    deadline_text: str | None
    authority_text: str
    source_url: str
    retrieved_at: str
    sha256: str
    verification_status: str


def fetch(url:str)->str:
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8",errors="replace")


def textify(raw:str)->str:
    raw=re.sub(r"(?is)<script.*?>.*?</script>|<style.*?>.*?</style>"," ",raw)
    return re.sub(r"\s+"," ",re.sub(r"(?s)<[^>]+>"," ",raw)).strip()


def normalize(url:str,raw:str,kind:str)->ProcedureRecord:
    text=textify(raw)
    return ProcedureRecord(
        jurisdiction="Georgia",record_type=kind,court=None,name=None,citation=None,
        procedural_stage=None,deadline_text=None,authority_text=text,source_url=url,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        sha256=hashlib.sha256(text.encode()).hexdigest(),
        verification_status="verified_source_pending_rule_or_motion_segmentation")


def sources(path:Path)->list[tuple[str,str]]:
    if not path.exists(): return []
    data=json.loads(path.read_text(encoding="utf-8")); out=[]
    for s in data.get("sources",[]):
        if not s.get("enabled",True) or not s.get("url"): continue
        cat=(s.get("category") or "").lower()
        if cat in {"court_rules","rules","procedure"}: out.append((s["url"],"court_rule"))
        elif cat in {"motions","motion_authority"}: out.append((s["url"],"motion_authority"))
    return out


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--source",action="append",default=[],help="URL; optionally URL|court_rule or URL|motion_authority")
    p.add_argument("--sources-file",default="data/legal_sources.json")
    p.add_argument("--output",default="data/corpus/georgia_rules_motions.jsonl")
    a=p.parse_args()
    configured=[]
    for item in a.source:
        parts=item.rsplit("|",1); configured.append((parts[0],parts[1] if len(parts)==2 else "court_rule"))
    configured=configured or sources(Path(a.sources_file))
    if not configured: raise SystemExit("No verified Georgia rules/motions sources configured; refusing to guess.")
    records=[normalize(url,fetch(url),kind) for url,kind in configured]
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8") as f:
        for r in records: f.write(json.dumps(asdict(r),ensure_ascii=False)+"\n")
    print(f"Wrote {len(records)} rule/motion source snapshots to {out}")
    return 0

if __name__=="__main__": raise SystemExit(main())
