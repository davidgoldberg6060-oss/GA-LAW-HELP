import data from "./publicDefenderProblemsData.json" with { type: "json" };
import { getLang, t, type Lang } from "./i18n.ts";

export type GuideSection = { id: string; title: string; items: string[] };
export type GuideTemplate = { id: string; kind: string; motionKey: string | null; title: string; body: string };
export type GuideLink = { id: string; label: string; url: string };
export type Guide = {
  title: string;
  hint: string;
  language: Lang;
  quick: string;
  sections: GuideSection[];
  templates: GuideTemplate[];
  links: GuideLink[];
  motionKey: string;
  disclaimer: string;
  notice: string;
};

const DISTRUST = /work(?:ing|s)? (with|for|against)|working against|with the (state|da|prosecutor)|against me|not (helping|working for) me|won'?t (call|meet|visit|see|talk|review)|never (call|called|meet|met|visit|review)|pressur(?:e|ing|ed).{0,40}plea|conflict of interest|co-?defendant|fire (my|the) (lawyer|attorney|public defender)|get (a |me )?(new|different|another) (lawyer|attorney|public defender)|ineffective|working with the state|defensor p[uú]blico/i;
const COUNSEL = /public defender|court[- ]appointed|appointed (counsel|lawyer|attorney)|defensor p[uú]blico|abogado asignado|(my|mi) (lawyer|attorney|counsel|abogado)/i;
const REQUEST_ONLY = /how do i (get|ask for|request)|qualify for|apply for/i;

export function detectsPdProblem(text: string): boolean {
  const q = (text || "").trim();
  if (!q || (REQUEST_ONLY.test(q) && !DISTRUST.test(q))) return false;
  return COUNSEL.test(q) && (DISTRUST.test(q) || /state|prosecutor|prosecution|\bda\b|against/i.test(q));
}

export function guide(language: Lang = getLang()): Guide {
  const lang: Lang = language === "es" ? "es" : "en";
  const spanish = lang === "es";
  return {
    title: spanish ? data.title_es : data.title_en,
    hint: spanish ? data.hint_es : data.hint_en,
    language: lang,
    quick: spanish ? data.quick_es : data.quick_en,
    sections: data.sections.map((spec) => ({
      id: spec.id,
      title: spanish ? spec.title_es : spec.title_en,
      items: spec.items.map((item) => (spanish ? item.es : item.en)).filter(Boolean),
    })),
    templates: data.templates.map((row) => ({
      id: row.id,
      kind: row.kind,
      motionKey: "motion_key" in row ? (row as {motion_key?: string}).motion_key || null : null,
      title: spanish ? row.title_es : row.title_en,
      body: spanish ? row.body_es : row.body_en,
    })),
    links: data.links.map((row) => ({ id: row.id, label: spanish ? row.label_es : row.label_en, url: row.url })),
    motionKey: "discharge_appointed_counsel",
    disclaimer: spanish ? data.disclaimer_es : data.disclaimer_en,
    notice: t("notice", lang),
  };
}

export function guideText(pack: Guide, includeTemplates = true): string {
  const quickLabel = pack.language === "es" ? "Respuesta rápida" : "Quick answer";
  const lines = [pack.title, "", quickLabel, pack.quick];
  for (const section of pack.sections) {
    if (!section.items.length) continue;
    lines.push("", section.title, ...section.items.map((item) => "• " + item));
  }
  if (includeTemplates) {
    const label = pack.language === "es" ? "Plantillas" : "Templates";
    for (const tmpl of pack.templates) {
      lines.push("", label + ": " + tmpl.title, tmpl.body);
    }
  }
  lines.push("", pack.disclaimer, pack.notice);
  return lines.join("\n").trim() + "\n";
}
