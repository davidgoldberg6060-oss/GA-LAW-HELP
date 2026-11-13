import data from "./courtroomPrepData.json" with { type: "json" };
import { getLang, type Lang } from "./i18n.ts";

export type PrepSection = { id: string; title: string; items: string[] };
export type Prep = {
  title: string;
  caseType: string | null;
  label: string;
  family: string;
  language: Lang;
  quick: string;
  sections: PrepSection[];
  disclaimer: string;
  notice: string;
};

type Item = { en: string; es: string };
type TypeInfo = {
  label_en: string;
  label_es: string;
  family: string;
  quick_en: string;
  quick_es: string;
} & Record<string, unknown>;

const TYPES = data.types as Record<string, TypeInfo>;

export const CASE_TYPES = [
  { id: "", label: "Any Georgia court date", label_es: "Cualquier fecha de corte en Georgia" },
  ...Object.entries(TYPES).map(([id, info]) => ({
    id,
    label: info.label_en,
    label_es: info.label_es,
  })),
];

function pick(item: Item, lang: Lang): string {
  return ((lang === "es" ? item.es : item.en) || item.en || "").trim();
}

function itemsOf(block: Record<string, unknown> | undefined, section: string, lang: Lang): string[] {
  const rows = (block?.[section] as Item[] | undefined) || [];
  const out: string[] = [];
  const seen = new Set<string>();
  for (const item of rows) {
    const text = pick(item, lang);
    if (text && !seen.has(text)) {
      seen.add(text);
      out.push(text);
    }
  }
  return out;
}

export function prepFor(caseType?: string | null, language: Lang = getLang()): Prep {
  const lang: Lang = language === "es" ? "es" : "en";
  const kind = (caseType || "").trim();
  const info = (kind && TYPES[kind]) || undefined;
  const spanish = lang === "es";
  const label = info ? (spanish ? info.label_es : info.label_en) : spanish ? "Cualquier fecha de corte en Georgia" : "Any Georgia court date";
  const quick = info ? (spanish ? info.quick_es : info.quick_en) : spanish ? data.quick_es : data.quick_en;
  const title = info
    ? (spanish ? `Preparación para la corte: ${label}` : `Courtroom prep: ${label}`)
    : spanish
      ? "Preparación para la corte"
      : "Courtroom prep";
  const general = data.general as Record<string, Item[]>;
  const sections: PrepSection[] = data.sections.map((spec) => {
    const raw = [...itemsOf(info as Record<string, unknown> | undefined, spec.id, lang), ...itemsOf(general, spec.id, lang)];
    const items: string[] = [];
    const seen = new Set<string>();
    for (const item of raw) {
      if (!seen.has(item)) {
        seen.add(item);
        items.push(item);
      }
    }
    return { id: spec.id, title: spanish ? spec.title_es : spec.title_en, items };
  });
  return {
    title,
    caseType: info ? kind : null,
    label,
    family: info?.family || "general",
    language: lang,
    quick,
    sections,
    disclaimer: spanish ? data.disclaimer_es : data.disclaimer_en,
    notice: spanish ? "Esto es información legal, no asesoramiento jurídico." : "This is legal information, not legal advice.",
  };
}

export function prepText(pack: Prep): string {
  const quickLabel = pack.language === "es" ? "Respuesta rápida" : "Quick answer";
  const lines = [pack.title, "", quickLabel, pack.quick];
  for (const section of pack.sections) {
    if (!section.items.length) continue;
    lines.push("", section.title, ...section.items.map((item) => "• " + item));
  }
  lines.push("", pack.disclaimer, pack.notice);
  return lines.join("\n").trim() + "\n";
}
