"""Discovery parser for official Supreme Court of Georgia opinion-year pages.

Year pages are useful for discovering docket IDs, titles and official opinion
links. They are NOT treated as proof of a Georgia Reports citation: the Court
states slip opinions can change and final/official text follows later. Citation
therefore remains unset until source-published citation evidence is obtained.
"""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import re

from .source_acquisition import OfficialDocumentRequest

_DOCKET=re.compile(r"\bS\d{2}[A-Z]\d{4}\b",re.I)
_ALLOWED_HOSTS={"www.gasupreme.us","gasupreme.us"}


@dataclass(frozen=True)
class DiscoveredSupremeOpinion:
    docket_numbers: tuple[str,...]
    title: str
    url: str

    def as_request(self)->OfficialDocumentRequest:
        return OfficialDocumentRequest(
            source_key="georgia_supreme_court",
            url=self.url,
            title=self.title,
            citation=None,
            external_id=",".join(self.docket_numbers),
        )


class _Links(HTMLParser):
    def __init__(self):
        super().__init__();self.href=None;self.text=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            self.href=dict(attrs).get("href");self.text=[]
    def handle_data(self,data):
        if self.href is not None:self.text.append(data)
    def handle_endtag(self,tag):
        if tag.lower()=="a" and self.href is not None:
            self.links.append((self.href," ".join("".join(self.text).split())))
            self.href=None;self.text=[]


def discover_supreme_opinions(page_html:str, *, page_url:str)->list[DiscoveredSupremeOpinion]:
    """Return only official-host linked entries whose visible text contains a docket ID."""
    if urlparse(page_url).hostname not in _ALLOWED_HOSTS:
        raise ValueError("Supreme Court discovery requires an official gasupreme.us page")
    parser=_Links();parser.feed(page_html)
    found=[];seen=set()
    for href,text in parser.links:
        dockets=tuple(dict.fromkeys(x.upper() for x in _DOCKET.findall(text)))
        if not dockets or not text:continue
        url=urljoin(page_url,href)
        parsed=urlparse(url)
        if parsed.scheme!="https" or parsed.hostname not in _ALLOWED_HOSTS:continue
        key=(dockets,url)
        if key in seen:continue
        seen.add(key);found.append(DiscoveredSupremeOpinion(dockets,text,url))
    return found
