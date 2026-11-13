/** English / Spanish UI strings and the language preference (device only). */

export type Lang = "en" | "es";

const LANG_KEY = "ga_language";
const VOICE_KEY = "ga_read_aloud_voice";

const STRINGS: Record<string, { en: string; es: string }> = {
  settings: { en: "Settings", es: "Configuración" },
  language: { en: "Language", es: "Idioma" },
  english: { en: "English", es: "Inglés" },
  spanish: { en: "Spanish", es: "Español" },
  languageHint: {
    en: "This switches the app and AI answers to Spanish. Legal citations stay as written. This is legal information, not legal advice.",
    es: "Esto cambia la aplicación y las respuestas de la IA al español. Las citas legales se quedan como están escritas. Esto es información legal, no asesoramiento jurídico.",
  },
  notice: {
    en: "This is legal information, not legal advice.",
    es: "Esto es información legal, no asesoramiento jurídico.",
  },
  translationNotice: {
    en: "This translation is for understanding only. The original English document is what counts in court.",
    es: "Esta traducción es solo para que usted entienda el documento. En la corte, el documento original en inglés es el que cuenta.",
  },
  courtroomPrep: { en: "Courtroom prep", es: "Preparación para la corte" },
  courtroomHint: {
    en: "A day-before and day-of checklist for Georgia courts.",
    es: "Una lista para el día antes y el día de la corte en Georgia.",
  },
  paperReader: { en: "Paper reader", es: "Lector de papeles" },
  paperHint: {
    en: "Photograph or upload a citation, warrant, summons, eviction notice or court order. We pull out the charge, dates, case number and court in plain language.",
    es: "Fotografía o sube una citación, una orden, un desalojo u otra orden de la corte. Extraemos el cargo, las fechas, el número de caso y el tribunal en palabras sencillas.",
  },
  takePhoto: { en: "Take a photo of a paper", es: "Tomar una foto de un papel" },
  chooseFile: { en: "Choose a photo or PDF", es: "Elegir una foto o un PDF" },
  translateSpanish: { en: "Translate this paper to Spanish", es: "Traducir este papel al español" },
  photoAndTranslate: {
    en: "Photograph and translate to Spanish",
    es: "Fotografiar y traducir al español",
  },
  readPaper: { en: "Read this paper", es: "Leer este papel" },
  buildDefense: { en: "Build my defense", es: "Armar mi defensa" },
  sharePdf: { en: "Share as PDF", es: "Compartir como PDF" },
  downloadPdf: { en: "Download PDF", es: "Descargar PDF" },
  readAloud: { en: "Read aloud", es: "Leer en voz alta" },
  stopReading: { en: "Stop reading", es: "Dejar de leer" },
  voice: { en: "Read aloud voice", es: "Voz para leer en voz alta" },
  voiceOff: { en: "Off", es: "Apagado" },
  butler: { en: "The Butler", es: "The Butler" },
  nanny: { en: "The Nanny", es: "The Nanny" },
  butlerHint: {
    en: "A refined, warm, older British voice. An original voice — not based on any person or character.",
    es: "Una voz británica, culta y cálida. Es una voz original, no está basada en ninguna persona ni personaje.",
  },
  nannyHint: {
    en: "A chatty, warm New York voice. An original voice — not based on any person or character.",
    es: "Una voz de Nueva York, conversadora y cálida. Es una voz original, no está basada en ninguna persona ni personaje.",
  },
  voiceHint: {
    en: "Uses the free voices already on your phone or browser. Legal wording stays the same, and the not-legal-advice notice is always read.",
    es: "Usa las voces gratis que ya están en su teléfono o navegador. El contenido legal no cambia, y siempre se lee el aviso de que no es asesoramiento jurídico.",
  },
};

function store() {
  return typeof window !== "undefined" ? window.localStorage : undefined;
}

export function getLang(): Lang {
  const raw = store()?.getItem(LANG_KEY) || "";
  return raw.toLowerCase().startsWith("es") ? "es" : "en";
}

export function setLang(lang: Lang) {
  store()?.setItem(LANG_KEY, lang);
  if (typeof document !== "undefined") document.documentElement.lang = lang === "es" ? "es" : "en";
}

export function t(key: string, lang: Lang = getLang()): string {
  const row = STRINGS[key];
  if (!row) return key;
  return lang === "es" ? row.es : row.en;
}

export function languageInstruction(lang: Lang = getLang()): string {
  if (lang === "es") {
    return (
      "Respond in Spanish. Write every section heading in English exactly as required " +
      "(for example 'Quick answer' and 'Questions to ask your lawyer'). " +
      "Keep legal citations (O.C.G.A. sections, case names, court rule numbers, " +
      "docket numbers and case numbers) exactly as written in the original. " +
      "End with this disclaimer in Spanish: 'Esto es información legal, no asesoramiento jurídico.'"
    );
  }
  return "Respond in English.";
}

export type VoiceId = "off" | "butler" | "nanny";

export function getVoice(): VoiceId {
  const raw = (store()?.getItem(VOICE_KEY) || "off").toLowerCase();
  return raw === "butler" || raw === "nanny" ? raw : "off";
}

export function setVoice(id: VoiceId) {
  store()?.setItem(VOICE_KEY, id);
}
