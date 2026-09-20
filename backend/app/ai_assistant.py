import json
import os
import urllib.error
import urllib.request

OPENAI_URL = "https://api.openai.com/v1/responses"

SYSTEM_INSTRUCTIONS = """You are GA.LAW.HELP, a Georgia-focused legal information and research assistant.
Give clear, calm, plain-language legal information, not legal representation.
Do not claim to be a lawyer and do not promise outcomes.
Distinguish known facts, assumptions, and issues that need verification.
For Georgia-law questions, encourage verification against current official Georgia statutes, court rules, and controlling opinions.
When dates matter, say that the law in effect on the relevant date must be checked.
For police encounters, prioritize physical safety: never encourage resistance, obstruction, evasion, destruction of evidence, or deception.
If a user describes an emergency or immediate danger, prioritize emergency help.
Keep answers concise and useful. End with a short reminder that the response is legal information, not legal advice."""
    
def ask_openai(question: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("AI service is not configured")
    model = os.getenv("OPENAI_MODEL", "gpt-5.6").strip() or "gpt-5.6"
    payload = json.dumps({
        "model": model,
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": question,
        "max_output_tokens": 900,
    }).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_URL,
        data=payload,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError("AI provider request failed: " + detail[:500]) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("AI provider is temporarily unreachable") from exc
    text = (data.get("output_text") or "").strip()
    if not text:
        parts = []
        for item in data.get("output", []):
            for part in item.get("content", []):
                if part.get("type") == "output_text" and part.get("text"):
                    parts.append(part["text"])
        text = "\n".join(parts).strip()
    if not text:
        raise RuntimeError("AI provider returned an empty response")
    return text
