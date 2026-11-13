import data from "./publicDefenderOfficesData.json" with { type: "json" };
import { getLang, type Lang } from "./i18n.ts";

export type AdditionalOffice = { location: string | null; address: string | null; phone: string | null; fax: string | null };
export type Office = {
  id: string;
  circuit: string;
  opt_out: boolean;
  opt_out_note: string | null;
  counties: string[];
  defender: string | null;
  address: string | null;
  phone: string | null;
  fax: string | null;
  email: string | null;
  website: string | null;
  hours: string | null;
  additional_offices: AdditionalOffice[];
  page_url: string;
  region: string | null;
  juvenile?: { name: string | null; phone: string | null; address: string | null };
};

export const CHECKED_ON = data.checked_on;
export const SOURCE_URL = data.source_url;
export const FIND_TOOL_URL = data.find_tool_url;
export const OFFICE_COUNT = data.offices.length;
export const OFFICES = data.offices as Office[];

export function outcomeNote(lang: Lang = getLang()): string {
  return lang === "es" ? data.outcome_note_es : data.outcome_note_en;
}

export function barDirectory(lang: Lang = getLang()) {
  const bar = data.bar_directory;
  return {
    label: lang === "es" ? bar.label_es : bar.label_en,
    url: bar.url,
    disciplineUrl: bar.discipline_url,
    termsUrl: bar.terms_url,
    explainer: lang === "es" ? bar.explainer_es : bar.explainer_en,
  };
}

function hay(office: Office): string {
  const extra = (office.additional_offices || []).flatMap((o) => [o.location, o.address, o.phone]);
  const juv = office.juvenile ? [office.juvenile.name, office.juvenile.phone] : [];
  return [office.circuit, office.defender, office.address, office.phone, office.email, ...(office.counties || []), office.opt_out_note, office.region, ...extra, ...juv]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

export function searchOffices(query: string): Office[] {
  const q = query.trim().toLowerCase();
  if (!q) return OFFICES;
  const tokens = q.split(/[^a-z0-9]+/).filter(Boolean);
  return OFFICES.filter((office) => {
    const blob = hay(office);
    if (blob.includes(q)) return true;
    return tokens.length > 0 && tokens.every((tok) => blob.includes(tok));
  });
}
