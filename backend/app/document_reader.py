"""Read photos / PDFs of case papers with a vision-capable model and explain them in plain language.

Order: Gemini (inline image/PDF parts) through the configured model chain, then OpenRouter vision
models, then xAI / OpenAI Responses API with input_image. Text PDFs are read locally with pypdf first,
so they also work with text-only fallbacks. File contents and prompts are never logged.
"""
from __future__ import annotations

import base64
import io
import json
import logging
import os
import re
import time

from . import ai_models
from . import ai_assistant as _ai

logger = logging.getLogger(__name__)

MAX_FILES = int(os.getenv("DOC_READ_MAX_FILES", "10"))
MAX_FILE_BYTES = int(os.getenv("DOC_READ_MAX_FILE_BYTES", str(15 * 1024 * 1024)))
MAX_TOTAL_BYTES = int(os.getenv("DOC_READ_MAX_TOTAL_BYTES", str(30 * 1024 * 1024)))
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
PDF_TYPE = "application/pdf"
OPENROUTER_VISION_DEFAULT = "google/gemma-4-31b-it:free,google/gemma-4-26b-a4b-it:free"

PROMPT = """The user photographed or uploaded {count} page(s) of paperwork about a legal matter in Georgia
(for example a court notice, citation, indictment, bond order, probation paper, letter from a lawyer or court).
{question_line}
Read every page carefully, including small print, handwriting, stamps and dates. Then return ONLY JSON with these keys:
"readable": true or false (false only if the pages are too blurry, dark or cut off to read),
"document_type": short name of the paper (e.g. "Notice of arraignment"),
"extracted_text": the important text you read, page by page, as plain text (keep names, case numbers, dates, charges and code sections exactly as written; mark unreadable parts as [unreadable]),
"summary": 2-4 plain-language sentences saying what this paper is and what it means,
"key_dates": list of strings, each a date/time/deadline found on the paper and what it is for,
"charges_or_claims": list of strings exactly as written on the paper (empty if none),
"case_number": the case, citation, warrant or docket number exactly as written, or "",
"court": the court name and county if listed, or "",
"field_explanations": an object with optional keys "charge_or_claim", "dates", "case_number", "court" — each a one-line plain-English explanation of what that item means for the person (what it is, not legal advice),
"next_steps": list of practical steps the person can take, most urgent first,
"questions_for_lawyer": list of questions to ask their lawyer or public defender,
"helpful_flags": list of short points in the paper that could help the person's defense or side, only if they are really on the paper: missing or wrong information (names, dates, case number, code section, court, officer or landlord details), an element of the charge or claim that the paper does not allege, a missing signature or notice, a defect in how or when it was served, inconsistent facts, or a date that may already be past (empty list if none),
"photo_tips": a short tip if some part was hard to read, otherwise "".
Only use facts that are on the paper. Do not invent laws, case numbers or deadlines. This is legal information, not legal advice."""


class DocumentInputError(ValueError):
    pass


def sniff_type(data: bytes, declared: str | None, filename: str | None = "") -> str:
    head = data[:16]
    if head.startswith(b"%PDF"):
        return PDF_TYPE
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG"):
        return "image/png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    if head[4:8] == b"ftyp" and head[8:12] in (b"heic", b"heix", b"mif1", b"msf1", b"heis", b"hevc"):
        return "image/heic"
    declared = (declared or "").split(";")[0].strip().lower()
    if declared in IMAGE_TYPES or declared == PDF_TYPE:
        return declared
    name = (filename or "").lower()
    for ext, mt in ((".pdf", PDF_TYPE), (".jpg", "image/jpeg"), (".jpeg", "image/jpeg"), (".png", "image/png"),
                    (".webp", "image/webp"), (".heic", "image/heic"), (".heif", "image/heif")):
        if name.endswith(ext):
            return mt
    return declared or "application/octet-stream"


def validate(files: list[tuple[str, bytes]]) -> None:
    if not files:
        raise DocumentInputError("Add at least one photo or PDF of the paper.")
    if len(files) > MAX_FILES:
        raise DocumentInputError(f"Please send {MAX_FILES} pages or fewer at a time.")
    total = 0
    for mt, data in files:
        if not data:
            raise DocumentInputError("One of the files was empty. Please retake the photo.")
        if mt not in IMAGE_TYPES and mt != PDF_TYPE:
            raise DocumentInputError("Only photos (JPG, PNG, WEBP, HEIC) and PDFs can be read.")
        if len(data) > MAX_FILE_BYTES:
            raise DocumentInputError("That file is too large. Please send a smaller photo or a PDF under 15 MB.")
        total += len(data)
    if total > MAX_TOTAL_BYTES:
        raise DocumentInputError("Those pages are too large together. Please send fewer pages at a time.")


def pdf_text(data: bytes, max_chars: int = 60000) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        out = []
        for i, page in enumerate(reader.pages[:40]):
            out.append(f"--- Page {i + 1} ---\n" + (page.extract_text() or "").strip())
        text = "\n".join(out).strip()
        return text[:max_chars]
    except Exception:  # scanned or damaged PDF: the vision model reads it instead
        return ""


def _prompt(count: int, question: str, pdf_texts: list[str], prior_context: str = "") -> str:
    q = (question or "").strip()[:1500]
    line = f'Their question: "{q}"' if q else "They want to understand what it says and what to do next."
    text = PROMPT.format(count=count, question_line=line)
    if prior_context:
        text += "\n\n" + prior_context.strip()
    if pdf_texts:
        text += "\n\nText already extracted from the PDF file(s):\n" + "\n\n".join(pdf_texts)
    return text


def _gemini_parts(files, prompt):
    parts = [{"text": prompt}]
    for mt, data in files:
        parts.append({"inline_data": {"mime_type": mt, "data": base64.b64encode(data).decode("ascii")}})
    return parts


def _ask_gemini_vision(provider, model, files, prompt, timeout):
    config = {"maxOutputTokens": 6000, "responseMimeType": "application/json"}
    if not model.startswith("gemini-2."):
        config["thinkingConfig"] = {"thinkingLevel": "low"}
    payload = {"systemInstruction": {"parts": [{"text": _ai.SYSTEM_INSTRUCTIONS}]},
               "contents": [{"role": "user", "parts": _gemini_parts(files, prompt)}],
               "generationConfig": config}
    headers = {"x-goog-api-key": provider["api_key"], "Content-Type": "application/json"}
    url = f"{provider['url']}/{model}:generateContent"
    try:
        data = _ai._http_post_json(provider, model, url, payload, headers, timeout)
    except _ai.ProviderHTTPError as exc:
        if exc.status != 400 or "thinking" not in str(getattr(exc, "detail", "")).lower():
            raise
        payload["generationConfig"].pop("thinkingConfig", None)
        data = _ai._http_post_json(provider, model, url, payload, headers, timeout)
    texts = []
    for cand in (data.get("candidates") or [])[:1]:
        for part in (cand.get("content") or {}).get("parts") or []:
            if part.get("text") and not part.get("thought"):
                texts.append(part["text"])
    text = "".join(texts).strip()
    if not text:
        raise RuntimeError("AI provider returned an empty response")
    return text


def _ask_compat_vision(provider, model, images, prompt, timeout):
    content = [{"type": "text", "text": prompt}]
    for mt, data in images:
        content.append({"type": "image_url", "image_url": {"url": f"data:{mt};base64," + base64.b64encode(data).decode("ascii")}})
    data = _ai._http_post_json(provider, model, provider["url"],
                               {"model": model, "max_tokens": 4096,
                                "messages": [{"role": "system", "content": _ai.SYSTEM_INSTRUCTIONS},
                                             {"role": "user", "content": content}]},
                               {"Authorization": "Bearer " + provider["api_key"], "Content-Type": "application/json",
                                **(provider.get("headers") or {})}, timeout)
    text = (((data.get("choices") or [{}])[0] or {}).get("message") or {}).get("content") or ""
    if not text.strip():
        raise RuntimeError("AI provider returned an empty response")
    return text.strip()


def _ask_responses_vision(provider, model, images, prompt, timeout):
    content = [{"type": "input_text", "text": prompt}]
    for mt, data in images:
        content.append({"type": "input_image", "image_url": f"data:{mt};base64," + base64.b64encode(data).decode("ascii")})
    data = _ai._http_post_json(provider, model, provider["url"],
                               {"model": model, "instructions": _ai.SYSTEM_INSTRUCTIONS, "max_output_tokens": 4096,
                                "input": [{"role": "user", "content": content}]},
                               {"Authorization": "Bearer " + provider["api_key"], "Content-Type": "application/json"}, timeout)
    text = (data.get("output_text") or "").strip()
    if not text:
        text = "\n".join(p.get("text", "") for item in data.get("output", []) for p in item.get("content", [])
                         if p.get("type") == "output_text").strip()
    if not text:
        raise RuntimeError("AI provider returned an empty response")
    return text


def _vision_chain(kind="check"):
    explicit = os.getenv("GEMINI_VISION_MODEL_CHAIN", "")
    if explicit:
        return ai_models._split(explicit)
    # Quality-first: reading small print benefits from the stronger flash models.
    return ai_models.gemini_chain(kind)


def _attempt(key, call):
    try:
        return _ai._try_model(key, call)
    except RuntimeError:  # one model rejecting the request must not stop the rest of the chain
        logger.warning("Vision model rejected the request: model=%s", key)
        return None


def ask_vision(files: list[tuple[str, bytes]], prompt: str) -> tuple[str, str]:
    """Return (raw model text, model key). Raises RuntimeError when every model fails."""
    started = time.monotonic()
    budget = float(os.getenv("DOC_READ_BUDGET_SECONDS", "100"))
    images = [(mt, d) for mt, d in files if mt in IMAGE_TYPES and mt not in ("image/heic", "image/heif")]
    gemini = _ai._gemini_provider()
    if gemini["api_key"]:
        for model in _vision_chain():
            left = budget * 0.7 - (time.monotonic() - started)
            if left < 8:
                break
            key = "gemini:" + model
            text = _attempt(key, lambda m=model, t=min(left, 60.0): _ask_gemini_vision(gemini, m, files, prompt, t))
            if text:
                return text, key
    # Fallbacks only see JPEG/PNG/WEBP images (PDF text is already in the prompt).
    for provider in (ai_models.compat_providers() if images else []):
        if provider["name"] != "openrouter":
            continue
        for model in ai_models._split(os.getenv("OPENROUTER_VISION_MODELS", OPENROUTER_VISION_DEFAULT)):
            left = budget - (time.monotonic() - started)
            if left < 8:
                break
            key = "openrouter:" + model
            text = _attempt(key, lambda p=provider, m=model, t=min(left, 50.0): _ask_compat_vision(p, m, images, prompt, t))
            if text:
                return text, key
    for provider in ((_ai._xai_provider(), _ai._openai_provider()) if images else ()):
        if not provider["api_key"]:
            continue
        model = os.getenv(provider["name"].upper() + "_VISION_MODEL", provider["default_model"]).strip() or provider["default_model"]
        left = budget - (time.monotonic() - started)
        if left < 8:
            break
        key = provider["name"] + ":" + model
        text = _attempt(key, lambda p=provider, m=model, t=min(left, 50.0): _ask_responses_vision(p, m, images, prompt, t))
        if text:
            return text, key
    if "--- Page" in prompt:  # text PDF: any text model can still answer
        return _ai.ask_openai(prompt, "quality"), getattr(_ai.last_model_used, "value", None) or "text"
    raise RuntimeError("AI provider is temporarily unavailable")


def _as_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()][:15]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []



def _explanations(value) -> dict:
    if not isinstance(value, dict):
        return {}
    out = {}
    for key in ("charge_or_claim", "dates", "case_number", "court"):
        item = str(value.get(key) or "").strip()
        if item:
            out[key] = item[:400]
    return out


def guess_case_fields(text: str) -> dict:
    """Best-effort case number and court from text already read off the paper."""
    found = {"case_number": "", "court": ""}
    if not text:
        return found
    m = re.search(
        r"(?im)\b(?:case|citation|warrant|docket|ticket|civil action|crim(?:inal)?(?: action)?)\s*(?:no\.?|number|#)\s*[:.]?\s*([A-Z0-9][A-Z0-9\- /]{2,40})",
        text,
    )
    if m:
        found["case_number"] = m.group(1).strip(" .;,/")
    m = re.search(
        r"(?i)\b((?:superior|state|magistrate|juvenile|probate|municipal|recorder'?s?|city|county|supreme|appeals)\s+court(?:\s+of\s+[A-Z][A-Za-z .'-]{2,40})?|[A-Z][A-Za-z .'-]{2,40}\s+(?:superior|state|magistrate|juvenile|probate|municipal)\s+court)",
        text,
    )
    if m:
        found["court"] = re.sub(r"\s+", " ", m.group(1)).strip(" .;,/")
    return found


def _explain(r: dict, key: str, fallback: str) -> str:
    return ((r.get("field_explanations") or {}).get(key) or fallback).strip()


def _quick(r: dict) -> str:
    bits = []
    if r.get("document_type"):
        bits.append("This is a " + r["document_type"] + ((" from " + r["court"]) if r.get("court") else "") + ".")
    elif r.get("summary"):
        bits.append(r["summary"])
    if r.get("charges_or_claims"):
        bits.append("The charge or claim on the paper is " + r["charges_or_claims"][0] + ".")
    dates = r.get("key_dates") or []
    if dates:
        bits.append("A date on the paper is " + dates[0] + ".")
    if r.get("case_number") and "case number" not in " ".join(bits).lower():
        bits.append("The case number is " + r["case_number"] + ".")
    if not bits and r.get("summary"):
        bits.append(r["summary"])
    return " ".join(bits[:4]).strip()


def parse_result(raw: str) -> dict:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    elif not text.startswith("{") and "{" in text:
        text = text[text.index("{"): text.rindex("}") + 1]
    try:
        data = json.loads(text)
    except ValueError:
        data = {"readable": True, "summary": raw.strip()[:4000], "extracted_text": ""}
    if not isinstance(data, dict):
        data = {"summary": str(data)}
    out = {
        "readable": data.get("readable") is not False,
        "document_type": str(data.get("document_type") or "").strip()[:160],
        "extracted_text": str(data.get("extracted_text") or "").strip()[:20000],
        "summary": str(data.get("summary") or "").strip()[:4000],
        "key_dates": _as_list(data.get("key_dates")),
        "charges_or_claims": _as_list(data.get("charges_or_claims")),
        "case_number": str(data.get("case_number") or data.get("docket_number") or "").strip()[:120],
        "court": str(data.get("court") or data.get("court_name") or "").strip()[:200],
        "field_explanations": _explanations(data.get("field_explanations")),
        "next_steps": _as_list(data.get("next_steps")),
        "questions_for_lawyer": _as_list(data.get("questions_for_lawyer")),
        "helpful_flags": _as_list(data.get("helpful_flags")),
        "photo_tips": str(data.get("photo_tips") or "").strip()[:400],
    }
    # If the model left case number or court out of the structured fields, try the extracted text.
    if not out["case_number"] or not out["court"]:
        guessed = guess_case_fields(out.get("extracted_text") or "")
        out["case_number"] = out["case_number"] or guessed.get("case_number", "")
        out["court"] = out["court"] or guessed.get("court", "")
    out["answer"] = format_answer(out)
    return out


def format_answer(r: dict) -> str:
    """Plain-English paper reader: a short quick answer, then one-line explanations, then next steps."""
    if not r.get("readable") and not r.get("extracted_text"):
        return ("I couldn't read this paper clearly. " + (r.get("photo_tips") or
                "Try again in good light, hold the phone flat over the page, and make sure all four corners are in the photo."))
    lines = ["Quick answer", _quick(r) or (r.get("summary") or "I read this paper. Open the sections below for the charge, dates, case number and court.")]
    charges = r.get("charges_or_claims") or []
    if charges:
        expl = _explain(r, "charge_or_claim", "This is the charge or claim written on the paper — what the other side says happened.")
        rows = ["• " + charges[0] + " — " + expl]
        rows.extend("• " + c for c in charges[1:])
        lines.append("Charge or claim\n" + "\n".join(rows))
    dates = r.get("key_dates") or []
    if dates:
        expl = _explain(r, "dates", "Check this date with the court clerk or your lawyer. Missing a court date can lead to a warrant or a default.")
        rows = ["• " + dates[0] + ("" if " — " in dates[0] or " - " in dates[0] else " — " + expl)]
        if " — " in dates[0] or " - " in dates[0]:
            rows[0] = "• " + dates[0] + " — " + expl
        rows.extend("• " + d for d in dates[1:])
        lines.append("Important dates\n" + "\n".join(rows))
    if r.get("case_number"):
        expl = _explain(r, "case_number", "This is how the court files and looks up your case. Bring this number when you call the clerk.")
        lines.append("Case number\n• " + r["case_number"] + " — " + expl)
    if r.get("court"):
        expl = _explain(r, "court", "This is the court named on the paper, and usually the courthouse you go to for your date.")
        lines.append("Court\n• " + r["court"] + " — " + expl)
    for title, key in (("What could help in this paper", "helpful_flags"), ("What you can do next", "next_steps"),
                       ("Questions to ask your lawyer", "questions_for_lawyer")):
        if r.get(key):
            lines.append(title + "\n" + "\n".join("• " + x for x in r[key]))
    if r.get("photo_tips"):
        lines.append("Photo tip: " + r["photo_tips"])
    if r.get("answer_es"):
        lines.append(r["answer_es"])
    elif r.get("translation_notice"):
        lines.append(r["translation_notice"])
    lines.append("This is legal information, not legal advice. Check every date with the court clerk or your lawyer.")
    return "\n\n".join(lines)


def attach_spanish(result: dict, translation: dict) -> dict:
    """Add a Spanish translation block to an already-read paper (original English still included)."""
    from . import language as lang
    result = dict(result)
    result["translation"] = translation
    result["answer_es"] = translation.get("answer_es") or ""
    result["translation_notice"] = lang.TRANSLATION_NOTICE_ES
    # Rebuild the English reader, then append the Spanish block (format_answer includes answer_es).
    result["answer"] = format_answer({k: v for k, v in result.items() if k != "answer_es"})
    if result.get("answer_es") and result["answer_es"] not in result["answer"]:
        result["answer"] = result["answer"].rstrip() + "\n\n" + result["answer_es"]
    return result


def read_documents(files: list[tuple[str, bytes]], question: str = "", *, translate_spanish: bool = False, prior_context: str = "") -> dict:
    validate(files)
    pdf_texts = []
    for mt, data in files:
        if mt == PDF_TYPE:
            t = pdf_text(data)
            if len(t) > 200:
                pdf_texts.append(t)
    prompt = _prompt(len(files), question, pdf_texts, prior_context=prior_context)
    raw, model = ask_vision(files, prompt)
    result = parse_result(raw)
    result["model_used"] = model
    result["pages"] = len(files)
    if translate_spanish and result.get("readable"):
        try:
            from . import document_translate as _tr
            result = attach_spanish(result, _tr.translate_result(result))
        except Exception:
            # A failed translation must not hide the English reading.
            from . import language as lang
            result["translation_error"] = "The Spanish translation could not be completed right now. The English reading is below."
            result["translation_notice"] = lang.TRANSLATION_NOTICE_ES
            result["answer"] = format_answer(result)
    return result
