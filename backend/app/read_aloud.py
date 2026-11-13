"""Spoken text for the free Read aloud feature.

Two original voice characters (not based on any real actor or trademarked character):

- The Butler: a refined, warm, older British-sounding voice (en-GB, slightly slower, slightly lower).
- The Nanny: a chatty, warm New York-sounding voice (en-US, slightly livelier).

Legal content is never rewritten. A short original intro may be prepended, and the
not-legal-advice notice is always spoken at the end.
"""
from __future__ import annotations

from . import language as lang

OFF = "off"
BUTLER = "butler"
NANNY = "nanny"

VOICES = {
    BUTLER: {
        "id": BUTLER,
        "label": "The Butler",
        "description": "A refined, warm, older British voice. An original voice, not based on any person or character.",
        "locale": "en-GB",
        "locale_es": "es-ES",
        "pitch": 0.85,
        "rate": 0.88,
        "intro_en": "Allow me to read this for you.",
        "intro_es": "Permítame leérselo.",
    },
    NANNY: {
        "id": NANNY,
        "label": "The Nanny",
        "description": "A chatty, warm New York voice. An original voice, not based on any person or character.",
        "locale": "en-US",
        "locale_es": "es-US",
        "pitch": 1.12,
        "rate": 1.06,
        "intro_en": "All right, dear, here is what this says.",
        "intro_es": "Está bien, querida, esto es lo que dice.",
    },
}


def normalize(value: str | None) -> str:
    raw = (value or OFF).strip().lower()
    if raw in (BUTLER, "the butler", "butler"):
        return BUTLER
    if raw in (NANNY, "the nanny", "nanny"):
        return NANNY
    return OFF


def voice(value: str | None) -> dict | None:
    key = normalize(value)
    return dict(VOICES[key]) if key in VOICES else None


def catalog() -> list[dict]:
    rows = [{"id": OFF, "label": "Off", "description": "Do not read answers aloud."}]
    rows.extend(dict(v) for v in VOICES.values())
    return rows


def spoken_text(body: str, voice_id: str | None = OFF, language: str = "en") -> str:
    """Text actually sent to the device speech engine: optional intro, the legal text, then the notice."""
    text = (body or "").strip()
    if not text:
        return ""
    info = voice(voice_id)
    spanish = lang.is_spanish(language)
    notice = lang.notice(language)
    # If the body is a Spanish translation of a paper, also keep the translation notice.
    notes = [notice]
    if lang.TRANSLATION_NOTICE_EN in text or lang.TRANSLATION_NOTICE_ES in text:
        trans = lang.translation_notice(language)
        if trans not in text and trans not in notes:
            notes.append(trans)
    spoken = text
    if info:
        intro = info["intro_es"] if spanish else info["intro_en"]
        if not spoken.startswith(intro):
            spoken = intro + "\n\n" + spoken
    for note in notes:
        if note not in spoken:
            spoken = spoken.rstrip() + "\n\n" + note
    return spoken.strip()
