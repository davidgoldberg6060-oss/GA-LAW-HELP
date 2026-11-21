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


# --------------------------------------------------------------- language of a typed question
import re as _re

_ES_WORDS = frozenset("""que qué el la los las del por para con una unos unas tengo tiene tienen estoy está están soy es son
como cómo dónde donde cuando cuándo cuánto porque pero mi mis su sus yo usted ustedes nosotros hago puedo debo quiero necesito
ayuda abogado abogada policía policia arrestaron arresto arrestado detuvieron cárcel carcel multa corte juez casero dueño
desalojar desalojo derechos accidente choque trabajo divorcio esposo esposa hijos anoche ayer hoy también tambien muy sí
qué hacer""".split())
_EN_WORDS = frozenset("""the and was were what how my is are to of for with have has had i i'm i've you your they their this that
it can do does did will would should could from got at on in an be been being""".split())
_WORD = _re.compile(r"[a-záéíóúñü']+", _re.I)


def detect(text: str | None) -> str:
    """'es' when the user's own words are clearly Spanish, else 'en'. Short or mixed text stays English."""
    t = str(text or "")
    words = _WORD.findall(t.lower())
    if not words:
        return "en"
    es = sum(w in _ES_WORDS for w in words) + (2 if _re.search(r"[ñ¿¡]", t) else 0) + len(_re.findall(r"[áéíóú]", t.lower()))
    en = sum(w in _EN_WORDS for w in words)
    return "es" if es >= 2 and es > en * 1.5 else "en"


# Spanish legal words -> English, so topic detection and the Georgia law search (both English) still find the right law.
_ES_HINTS = (
    (r"desaloj\w*|lanzamiento", "eviction"), (r"caser[oa]|arrendador\w*|due[ñn]o de (la )?(casa|apartamento)", "landlord"),
    (r"alquiler|renta\b", "rent"), (r"dep[oó]sito", "security deposit"),
    (r"arrest\w*|detuvieron|detenid[oa]", "arrested"), (r"c[aá]rcel|prisi[oó]n", "jail"), (r"fianza", "bond"),
    (r"choque|accidente de (carro|auto|coche|tr[aá]fico)", "car wreck"), (r"me lastim[eé]|lesi[oó]n|herid[oa]", "injury"),
    (r"en el trabajo|mi jefe|patr[oó]n", "at work"), (r"compensaci[oó]n (laboral|de trabajadores)", "workers comp"),
    (r"despid\w*", "fired"), (r"salario|sueldo|no me pag\w*", "unpaid wages"),
    (r"divorcio|divorciar\w*", "divorce"), (r"custodia", "custody"), (r"manutenci[oó]n", "child support"),
    (r"orden de protecci[oó]n|orden de alejamiento", "protective order"), (r"violencia dom[eé]stica", "family violence"),
    (r"robo|hurto|rob[eé]", "theft shoplifting"), (r"multa|infracci[oó]n", "traffic ticket"),
    (r"licencia (de manejar|de conducir)?|suspendid[oa]", "driver's license suspended"), (r"manejar borracho|ebrio", "DUI"),
    (r"drogas?|marihuana", "drug possession"), (r"arma", "gun"), (r"seguro|aseguradora", "insurance claim denied"),
    (r"incendio|fuego|se quem[oó]", "house fire"), (r"deuda|cobrador\w*|embargo", "debt collection garnishment"),
    (r"demand\w*", "sued lawsuit"), (r"defensor p[uú]blico", "public defender"), (r"abogad[oa]", "lawyer"),
    (r"testamento|herencia", "will probate"), (r"ejecuci[oó]n hipotecaria", "foreclosure"),
    (r"corte|tribunal|audiencia", "court hearing"), (r"polic[ií]a", "police"), (r"registr\w* (mi )?(carro|auto|coche)", "search my car"),
    (r"me ca[ií]|resbal[eé]", "slip and fall"), (r"mordi[oó]|mordida", "dog bite"),
)


def english_hints(text: str | None) -> str:
    """English key words for a Spanish question ('' when none match)."""
    t = str(text or "").lower()
    out: list[str] = []
    for pattern, words in _ES_HINTS:
        if _re.search(pattern, t) and words not in out:
            out.append(words)
    return ", ".join(out)


def with_language(query: str, language: str | None = None) -> str:
    """Spanish answers when the client asked for Spanish (``language``) or the question itself is in Spanish.

    Unchanged when the client already added a 'Respond in ...' instruction (the apps do when their language is set)
    or explicitly asked for English. The instruction goes before a 'User:' line so topic detection only reads the
    user's words, and English key words are added so the (English) law search still finds the right Georgia law."""
    q = str(query or "")
    if _re.search(r"(?m)^\s*Respond in (Spanish|English)\b", q):
        return q
    if (language and str(language).strip()) and not is_spanish(language):
        return q
    from .civil_topics import current_question
    asked = current_question(q)
    if not (is_spanish(language) or detect(asked) == "es"):
        return q
    hints = english_hints(asked)
    asked_out = asked + (f" (English key words: {hints})" if hints else "")
    if _re.search(r"(?:^|\n)User:[ \t]*", q):  # app history wrapper: keep it, annotate the latest message
        head = q[: q.rstrip().rfind(asked)] if asked and asked in q else q + "\n"
        return instruction("es") + "\n\n" + head + asked_out
    return instruction("es") + "\n\nUser: " + asked_out


# --------------------------------------------------------------- server-added footnote in the answer's language
NOTE_ES = "Esta es información legal, no asesoramiento legal."
AMENDMENT_NOTE_ES = ("El texto del Código de Georgia es de la edición de 2022; algunas secciones pueden haber cambiado. "
                     "Consulte con un abogado antes de confiar en él.")
_EN_AMENDMENT = ("Georgia Code text is from the 2022 edition; some sections may have changed since. "
                 "Check with a lawyer before relying on it.")
# The model's own Spanish disclaimer line (the instruction asks it to end with NOTICE_ES); the footnote replaces it.
_ES_DISCLAIMER_LINE = _re.compile(r"(?im)^[ \t•*\-\"'“”]*(?:nota:[ \t]*)?(?:esto|esta) es informaci[oó]n legal,? (?:y )?no (?:es )?asesoramiento (?:jur[ií]dico|legal)\.?[ \t\"'“”]*$\n?")
_NOTE_LINE = _re.compile(r"(?m)^Note:[ \t]*(.*)$")


def localize_note(text: str | None, language: str | None = "es") -> str:
    """Spanish answers: the server's 'Note: ...' footnote becomes 'Nota: Esta es información legal, no asesoramiento
    legal.' (with the Code-edition note in Spanish), and a duplicate disclaimer line from the model is dropped."""
    t = str(text or "")
    if not is_spanish(language):
        return t
    t = _ES_DISCLAIMER_LINE.sub("", t).rstrip()
    notes = list(_NOTE_LINE.finditer(t))
    if notes:
        m = notes[-1]
        body = m.group(1).replace(NOTICE_EN, NOTE_ES).replace(_EN_AMENDMENT, AMENDMENT_NOTE_ES).strip()
        if NOTE_ES not in body:
            body = (NOTE_ES + " " + body).strip()
        t = t[:m.start()] + "Nota: " + body + t[m.end():]
    elif NOTE_ES not in t:
        t += "\n\nNota: " + NOTE_ES
    return _re.sub(r"\n{3,}", "\n\n", t)
