"""Grounded Case Analysis / Talk to Me response construction.

AI analysis is deliberately separated from retrieved authority. Only traceable
records marked verified/official/validated/confirmed are supplied as governing-
authority context; the full retrieval result is still returned for transparency.
"""
from __future__ import annotations

from .internal_legal_search import search_internal

VERIFIED = {"verified", "official", "validated", "confirmed"}
SUPPORTED_MODES = {"case_analysis", "talk_to_me", "rights", "motions"}


def _is_traceable(hit: dict) -> bool:
    """A verification label alone is insufficient for AI legal reliance."""
    status = str(hit.get("verification_status") or "").strip().lower()
    citation = str(hit.get("citation") or "").strip()
    source_url = str(hit.get("source_url") or "").strip()
    return status in VERIFIED and bool(citation) and source_url.startswith("https://")


def _verified_hits(result: dict) -> list[dict]:
    return [hit for hit in result.get("hits", []) if _is_traceable(hit)]


def _authority_context(hits: list[dict]) -> str:
    blocks = []
    for index, hit in enumerate(hits, 1):
        blocks.append(
            f"[{index}] {hit.get('title') or 'Legal authority'}\n"
            f"Citation: {hit.get('citation')}\n"
            f"Corpus: {hit.get('corpus') or 'unknown'}\n"
            f"Verification: {hit.get('verification_status')}\n"
            f"Stored official/source URL: {hit.get('source_url')}\n"
            f"Stored excerpt: {hit.get('excerpt') or ''}"
        )
    return "\n\n".join(blocks)


def grounded_legal_response(query: str, mode: str, ask_ai) -> dict:
    """Retrieve first, then let AI reason only from traceable verified authority."""
    if mode not in SUPPORTED_MODES:
        raise ValueError("Unsupported grounded legal-assistant mode.")

    retrieval = search_internal(query, mode, 12)
    verified = _verified_hits(retrieval)
    if not verified:
        return {
            "mode": mode,
            "analysis": None,
            "authorities": retrieval.get("hits", []),
            "grounded_authority_count": 0,
            "coverage_notice": (
                "No traceable verified indexed authority matched these facts strongly enough for AI legal analysis. "
                "A verification label without both a stored citation and HTTPS source is not enough. "
                "GA.LAW.HELP will not invent authority or present an ungrounded legal conclusion."
            ),
        }

    prompt = f"""GA.LAW.HELP grounded legal analysis request.
Mode: {mode}

USER-SUPPLIED FACTS OR QUESTION (not independently verified):
{query}

TRACEABLE VERIFIED INDEXED AUTHORITIES AVAILABLE FOR THIS RESPONSE:
{_authority_context(verified)}

Rules for this response:
- Treat the user's narrative as allegations/facts to be verified, not established facts.
- Base every material legal conclusion only on the authorities supplied above.
- Cite supplied authorities by [number] and stored citation; never create a citation, case, statute, rule, deadline, sentence, or procedural requirement that is not supplied.
- A stored verification label is not permission to claim an authority is current, binding, or precedential unless the supplied record itself establishes that proposition.
- Never claim that an authority is still good law merely because it appears in the corpus. If currency or precedential status is not supplied, explicitly say that status still requires verification.
- Clearly separate: user facts, legal issues, authority-backed analysis, counterarguments/limitations, and practical next steps.
- If the supplied authority does not establish a proposition, say it requires verification instead of filling the gap from memory.
- Do not predict or guarantee an outcome.
- For a live police encounter, prioritize physical safety and do not encourage resistance, evasion, obstruction, evidence destruction, or deception.
"""
    analysis = ask_ai(prompt)
    return {
        "mode": mode,
        "analysis": analysis,
        "authorities": retrieval.get("hits", []),
        "grounded_authority_count": len(verified),
        "coverage_notice": retrieval.get("coverage_notice"),
    }
