"""Turn model output into clean, friendly plain text for every screen (no markdown, no internal
grounding language, one short amendment note), plus a compact 'Laws cited' list."""
from __future__ import annotations
import re

SHORT_AMENDMENT_NOTE = "Georgia Code text is from the 2022 edition; some sections may have changed since. Check with a lawyer before relying on it."

# Internal / meta phrases users must never see. A sentence containing one is dropped.
_META = re.compile(
    r"(?i)\b(supplied|provided|retrieved|indexed|traceable)\s+(verified\s+)?(georgia\s+)?(authorit|statute|law|source|record|excerpt)"
    r"|\bverified (indexed )?(georgia )?authorit"
    r"|\bthis system\b|\bthe system\b|\bgrounding\b|\bdatabase\b|\bcorpus\b|\bingestion\b"
    r"|\bin-app encounter pack\b|\bstatus metadata\b|\bprecedential status\b|\bcurrency (status )?(is )?unknown"
    r"|\bnot (in|among) the (authorities|sources)\b|\bauthorities (list|provided|supplied)\b")
_NOTE_RE = re.compile(r"(?is)\n*\s*(note:\s*)?georgia code text (shown )?is from the (official )?2022 edition.*?(relying on it\.|$)")


def friendly_heading(text: str) -> str:
    t = re.sub(r"[#*_:`]+", "", text).strip()
    t = t.replace(" / ", " or ")
    if t.isupper() or t == t.title():
        t = t.lower().capitalize()
        t = re.sub(r"\bgeorgia\b", "Georgia", t)
    return t


_HEADING_LINE = re.compile(r"^\s*(?:#{1,6}\s*|\*\*|__)?\s*([A-Za-z][A-Za-z ,/&'\-()]{2,60}?)\s*(?:\*\*|__)?\s*:?\s*$")


def _split_sentences(text: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'])", text)


def _drop_meta(line: str) -> str:
    if not _META.search(line):
        return line
    kept = [s for s in _split_sentences(line) if not _META.search(s)]
    return " ".join(kept).strip()


def clean_answer(text: str, *, add_note: bool = False, max_words: int = 420) -> str:
    """Plain text: friendly headings, '•' bullets, no markdown, no meta language, note once."""
    raw = _NOTE_RE.sub("", str(text or ""))
    out: list[str] = []
    skip_section = False
    headings: set[str] = set()
    for line in raw.splitlines():
        s = line.rstrip()
        if not s.strip():
            if out and out[-1] != "":
                out.append("")
            continue
        m = _HEADING_LINE.match(s)
        is_heading = bool(m) and (s.lstrip().startswith(("#", "**", "__")) or m.group(1).isupper())
        if is_heading:
            h = friendly_heading(m.group(1))
            # The sources list is shown separately as 'Laws cited'.
            skip_section = bool(re.search(r"(?i)authorit|laws? cited|sources", h))
            if skip_section:
                continue
            if out and out[-1] != "":
                out.append("")
            out.append(h); headings.add(h)
            continue
        if skip_section:
            continue
        s = re.sub(r"^\s*(?:[*\-+•]|\d+[.)])\s+", "• ", s)          # bullets
        s = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda mm: mm.group(1) or mm.group(2), s)  # bold
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"\1", s)  # italics
        s = re.sub(r"`([^`]*)`", r"\1", s).replace("#", "")
        s = _drop_meta(s)
        if s.strip() and s.strip() != "•":
            out.append(s)
    # drop headings left with no body
    cleaned: list[str] = []
    for i, line in enumerate(out):
        if line in headings:
            nxt = next((x for x in out[i + 1:] if x != ""), None)
            if nxt is None or nxt in headings:
                continue
        cleaned.append(line)
    body = "\n".join(cleaned).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    words = body.split(" ")
    if len(words) > max_words:
        cut = " ".join(words[:max_words])
        end = max(cut.rfind(". "), cut.rfind(".\n"))
        body = cut[: end + 1] if end > len(cut) * 0.5 else cut + "…"
    if add_note and body:
        body += "\n\nNote: " + SHORT_AMENDMENT_NOTE
    return body


def short_title(title: str, citation: str) -> str:
    t = str(title or "").strip()
    c = str(citation or "").strip()
    if c and t.lower().startswith(c.lower()):
        t = t[len(c):].lstrip(" .:-—")
    t = re.split(r";|\.\s", t)[0].strip().rstrip(".")
    return (t[:90] + "…") if len(t) > 90 else t


def laws_cited(authorities: list[dict]) -> list[dict]:
    """Compact user view: citation + short title + id for opening the law in the app."""
    out, seen = [], set()
    for h in authorities or []:
        cite = str(h.get("citation_raw") or h.get("citation") or "").strip()
        cite = re.sub(r"\s*\(text as of[^)]*\)", "", cite)
        if not cite or cite.lower() in seen:
            continue
        seen.add(cite.lower())
        out.append({"citation": cite, "title": short_title(h.get("title"), cite), "id": h.get("id") or h.get("authority_id")})
    return out


_TEXT_KEYS = {"why", "explanation", "text", "analysis", "answer", "message", "summary", "lawyer_take_text", "note"}


def plain_text(value: str) -> str:
    """Markdown-free, meta-free text for short fields (no headings logic, no note)."""
    s = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), str(value or ""))
    s = re.sub(r"(?m)^\s*#{1,6}\s*", "", s)
    s = re.sub(r"(?m)^\s*[*+\-]\s+", "• ", s).replace("`", "")
    return "\n".join(x for x in (_drop_meta(line) for line in s.splitlines()) if x.strip() or x == "").strip()


def sanitize_result(obj, key: str | None = None):
    """Recursively clean user-facing text fields of an AI response (charge/civil checks, loopholes, case tools)."""
    if isinstance(obj, dict):
        return {k: sanitize_result(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_result(v, key) for v in obj]
    if isinstance(obj, str) and key in _TEXT_KEYS:
        return clean_answer(obj) if key in ("analysis", "answer") else plain_text(obj)
    return obj
