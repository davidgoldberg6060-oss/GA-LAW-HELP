"""Language instructions and not-legal-advice notices (English and Spanish).

Legal citations, case names, rule numbers, and docket or case numbers stay in their
original form. The Spanish notice is the not-legal-advice disclaimer for Spanish answers.
"""
from __future__ import annotations

NOTICE_EN = "This is legal information, not legal advice."
NOTICE_ES = "Esto es información legal, no asesoramiento jurídico."
TRANSLATION_NOTICE_EN = (
    "This translation is for understanding only. The original English document is what counts in court."
)
TRANSLATION_NOTICE_ES = (
    "Esta traducción es solo para que usted entienda el documento. "
    "En la corte, el documento original en inglés es el que cuenta."
)

# Keep section headings in English so the app's tap-to-open parser still works.
_HEADINGS = (
    "Write every section heading in English exactly as required "
    "(for example 'Quick answer' and 'Questions to ask your lawyer'). "
    "Write the body in the requested language. "
    "Keep legal citations (O.C.G.A. sections, case names, court rule numbers, "
    "docket numbers and case numbers) exactly as written in the original."
)


def normalize_language(value: str | None) -> str:
    raw = (value or "en").strip().lower().replace("_", "-")
    if raw.startswith("es") or raw.startswith("espa"):
        return "es"
    return "en"


def is_spanish(value: str | None) -> bool:
    return normalize_language(value) == "es"


def notice(language: str | None = "en") -> str:
    return NOTICE_ES if is_spanish(language) else NOTICE_EN


def translation_notice(language: str | None = "es") -> str:
    """Shown with a Spanish translation of court papers."""
    return TRANSLATION_NOTICE_ES if is_spanish(language) else TRANSLATION_NOTICE_EN


def instruction(language: str | None = "en") -> str:
    """Prompt suffix that clients may prepend to a question, or the server may apply."""
    if is_spanish(language):
        return (
            "Respond in Spanish. " + _HEADINGS + " "
            "End with this disclaimer in Spanish: '" + NOTICE_ES + "'"
        )
    return "Respond in English. " + _HEADINGS + " End with: '" + NOTICE_EN + "'"
