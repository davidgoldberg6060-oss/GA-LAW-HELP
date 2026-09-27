"""GA.LAW.HELP official Georgia Supreme Court opinion ingestion.

Fetches official year index pages, extracts opinion metadata/links, and emits
normalized JSONL for loading into the internal legal corpus. Source documents
remain attributable and versioned; AI-generated text is never stored as law.
"""
from __future__ import annotations
import argparse, hashlib, json, re, urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin

BASE = "https://www.gasupreme.us/"
UA = "GA.LAW.HELP legal-corpus-indexer/1.0"

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self._href=None; self._text=[]
    def handle_starttag(self, tag, attrs):
        if tag == "a": self._href=dict(attrs).get("href"); self._text=[]
    def handle_data(self, data):
        if self._href is not None: self._text.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            text=" ".join("".join(self._text).split())
            self.links.append((text,self._href)); self._href=None; self._text=[]

def fetch(url:str)->bytes:
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=30) as r: return r.read()

def sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()

def parse_year(year:int):
    index=f"{BASE}{year}-opinions/"
    raw=fetch(index); parser=Links(); parser.feed(raw.decode("utf-8","replace"))
    seen=set()
    docket=re.compile(r"\bS\d{2}[A-Z]\d{4}\b",re.I)
    for text,href in parser.links:
        ds=docket.findall(text)
        if not ds: continue
        url=urljoin(index,href)
        key=(tuple(ds),url)
        if key in seen: continue
        seen.add(key)
        yield {
          "court":"Supreme Court of Georgia","jurisdiction":"GA",
          "docket_numbers":ds,"title":text,"source_url":url,
          "index_url":index,"source_kind":"official_court",
          "retrieved_at":datetime.now(timezone.utc).isoformat(),
          "index_sha256":sha256(raw),"verification_status":"official_source_indexed",
          "publication_status":"slip_or_final_verify_from_source"
        }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--year",type=int,action="append")
    ap.add_argument("--out",default="data/georgia_supreme_opinions.jsonl")
    args=ap.parse_args(); years=args.year or [datetime.now().year]
    rows=[]
    for year in years: rows.extend(parse_year(year))
    import os; os.makedirs(os.path.dirname(args.out) or ".",exist_ok=True)
    with open(args.out,"w",encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    print(f"indexed {len(rows)} official opinion records -> {args.out}")
if __name__=="__main__": main()
