"""Spanish translation of a paper already read by the document reader.

Keeps names, case numbers, dates, O.C.G.A. citations, and court names as written.
The translation is for understanding only; the original English document is what counts in court.
"""
from __future__ import annotations

import json
import re

from . import ai_assistant as _ai
from . import document_reader as dr
from . import language as lang

PROMPT = """Translate the following Georgia court paperwork into Spanish for a person who needs to understand it.
Return ONLY JSON with these keys:
"translated_text": a complete, faithful Spanish translation of the document text (keep names, case numbers, dates, O.C.G.A. citations, docket numbers and court names exactly as written in the original),
"plain_language": an object with:
  "document_type": short Spanish name of the paper,
  "summary": 2-4 plain Spanish sentences saying what this paper is and what it means,
  "charges_or_claims": list of objects {{"text": the charge or claim as written, "explanation": one Spanish sentence explaining it}},
  "key_dates": list of objects {{"text": the date line as written, "explanation": one Spanish sentence explaining what that date is}},
  "case_number": the case number exactly as written or "",
  "case_number_explanation": one Spanish sentence, or "",
  "court": the court name exactly as written or "",
  "court_explanation": one Spanish sentence, or "",
  "next_steps": list of practical next steps in Spanish,
  "questions_for_lawyer": list of questions in Spanish for their lawyer,
  "helpful_flags": list of short Spanish points that could help, only if they were in the source.
Do not add facts that are not in the source. Do not give legal advice. This is a translation for understanding only; the original English document is what counts in court.

SOURCE (JSON):
{source}
"""


def _source(result: dict) -> dict:
    return {
        "document_type": result.get("document_type") or "",
        "extracted_text": (result.get("extracted_text") or "")[:12000],
        "summary": result.get("summary") or "",
        "key_dates": result.get("key_dates") or [],
        "charges_or_claims": result.get("charges_or_claims") or [],
        "case_number": result.get("case_number") or "",
        "court": result.get("court") or "",
        "field_explanations": result.get("field_explanations") or {},
        "next_steps": result.get("next_steps") or [],
        "questions_for_lawyer": result.get("questions_for_lawyer") or [],
        "helpful_flags": result.get("helpful_flags") or [],
    }


def parse_translation(raw: str) -> dict:
    text = (raw or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    elif not text.startswith("{") and "{" in text:
        text = text[text.index("{"): text.rindex("}") + 1]
    try:
        data = json.loads(text)
    except ValueError:
        data = {"translated_text": text[:20000], "plain_language": {}}
    if not isinstance(data, dict):
        data = {"translated_text": str(data), "plain_language": {}}
    plain = data.get("plain_language") if isinstance(data.get("plain_language"), dict) else {}
    def pairs(value, default_key="text"):
        out = []
        for item in value or []:
            if isinstance(item, dict):
                t = str(item.get("text") or item.get(default_key) or item.get("date") or "").strip()
                e = str(item.get("explanation") or "").strip()
                if t:
                    out.append({"text": t[:400], "explanation": e[:400]})
            elif str(item).strip():
                out.append({"text": str(item).strip()[:400], "explanation": ""})
        return out[:15]
    return {
        "translated_text": str(data.get("translated_text") or "").strip()[:20000],
        "document_type": str(plain.get("document_type") or "").strip()[:160],
        "summary": str(plain.get("summary") or "").strip()[:4000],
        "charges_or_claims": pairs(plain.get("charges_or_claims")),
        "key_dates": pairs(plain.get("key_dates")),
        "case_number": str(plain.get("case_number") or "").strip()[:120],
        "case_number_explanation": str(plain.get("case_number_explanation") or "").strip()[:400],
        "court": str(plain.get("court") or "").strip()[:200],
        "court_explanation": str(plain.get("court_explanation") or "").strip()[:400],
        "next_steps": dr._as_list(plain.get("next_steps")),
        "questions_for_lawyer": dr._as_list(plain.get("questions_for_lawyer")),
        "helpful_flags": dr._as_list(plain.get("helpful_flags")),
        "notice": lang.TRANSLATION_NOTICE_ES,
        "legal_notice": lang.NOTICE_ES,
    }


def format_spanish(tr: dict, original: dict | None = None) -> str:
    """Spanish translation + plain-language breakdown, then the court-original notice."""
    if not tr.get("translated_text") and not tr.get("summary"):
        return "No se pudo traducir este documento ahora. Inténtelo de nuevo en un minuto.\n\n" + lang.TRANSLATION_NOTICE_ES
    lines = ["Traducción al español"]
    if tr.get("translated_text"):
        lines.append(tr["translated_text"].strip())
    lines.append("Explicación en palabras sencillas")
    bits = []
    if tr.get("document_type"):
        bits.append("Este papel es: " + tr["document_type"] + ".")
    if tr.get("summary"):
        bits.append(tr["summary"])
    if tr.get("court"):
        bits.append("Tribunal: " + tr["court"] + ((". " + tr["court_explanation"]) if tr.get("court_explanation") else "."))
    if tr.get("case_number"):
        bits.append("Número de caso: " + tr["case_number"] + ((". " + tr["case_number_explanation"]) if tr.get("case_number_explanation") else "."))
    lines.append(" ".join(bits) if bits else (tr.get("summary") or ""))
    def block(title, rows, extra=None):
        if not rows:
            return
        lines.append(title)
        for row in rows:
            if isinstance(row, dict):
                line = "• " + row.get("text", "")
                if row.get("explanation"):
                    line += " — " + row["explanation"]
                lines.append(line)
            else:
                lines.append("• " + str(row))
        if extra:
            lines.append(extra)
    block("Cargo o demanda", tr.get("charges_or_claims") or [])
    block("Fechas importantes", tr.get("key_dates") or [])
    if tr.get("case_number"):
        expl = tr.get("case_number_explanation") or "Así es como el tribunal identifica su caso. Tenga este número a la mano cuando llame al secretario."
        lines.append("Número de caso\n• " + tr["case_number"] + " — " + expl)
    if tr.get("court"):
        expl = tr.get("court_explanation") or "Este es el tribunal que aparece en el papel y, por lo general, adonde debe ir."
        lines.append("Tribunal\n• " + tr["court"] + " — " + expl)
    block("Lo que podría ayudar en este papel", tr.get("helpful_flags") or [])
    block("Qué puede hacer ahora", tr.get("next_steps") or [])
    block("Preguntas para su abogado", tr.get("questions_for_lawyer") or [])
    if original and (original.get("extracted_text") or original.get("answer")):
        lines.append("Original en inglés (el que cuenta en la corte)")
        lines.append((original.get("extracted_text") or original.get("answer") or "")[:4000])
    lines.append(lang.TRANSLATION_NOTICE_ES)
    lines.append(lang.NOTICE_ES)
    return "\n\n".join(p for p in lines if p).strip()


def translate_result(result: dict) -> dict:
    """Call a text model to translate an already-read paper. Raises RuntimeError if every model fails."""
    prompt = PROMPT.format(source=json.dumps(_source(result), ensure_ascii=False))
    raw, model = _ai.ask_openai(prompt, "quality"), getattr(_ai.last_model_used, "value", None) or "text"
    # ask_openai returns text only; if it fails it raises.
    tr = parse_translation(raw)
    tr["model_used"] = model
    tr["answer_es"] = format_spanish(tr, result)
    return tr
