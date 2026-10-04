/** Unauthenticated guest helpers. Private case tools must keep using authApi. */
export type GuestRightsAnswer = {
  question: string;
  answer: string;
  notice: string;
};

export type GuestResource = {title: string; url: string; kind: string; official: boolean};

export type GuestResearch = {
  query: string;
  topic: string;
  guidance: string;
  resources: GuestResource[];
  notice: string;
};

/** JSON request helper (the App's `api`): resolves to the parsed body, throws on non-2xx. */
export type GuestRequestJson = <T>(path: string, init?: RequestInit) => Promise<T>;

export type OfficialIndexRow = {title?: string; url?: string; kind?: string; official?: boolean};

export type IndexedAuthorityRow = {title?: string; citation?: string; source_url?: string | null; url?: string | null};

/** Response of POST /public/rights-assistant (grounded answer or corpus-unavailable fallback). */
export type PublicRightsAssistantResponse = {
  guest?: boolean;
  mode?: string;
  analysis?: string;
  answer?: string;
  authorities?: IndexedAuthorityRow[];
  grounded_authority_count?: number;
  coverage_notice?: string | null;
  official_indexes?: OfficialIndexRow[];
  login_required?: boolean;
};

/** Response of GET /public/encounter?situation=... */
export type PublicEncounterResponse = {
  guest?: boolean;
  disclaimer?: string;
  coverage_limit?: string | null;
  prompt?: string;
  official_indexes?: OfficialIndexRow[];
};

/** GET /public/encounter rejects situation values over 400 characters. */
export const ENCOUNTER_SITUATION_MAX = 400;

export function encounterSituation(query: string): string {
  const trimmed = query.trim();
  return trimmed.length > ENCOUNTER_SITUATION_MAX ? trimmed.slice(0, ENCOUNTER_SITUATION_MAX) : trimmed;
}

export async function guestRightsAndEncounter(
  apiBase: string,
  requestJson: GuestRequestJson,
  query: string,
): Promise<{answer: GuestRightsAnswer; research: GuestResearch}> {
  const q = query.trim();
  const [assistant, pack] = await Promise.all([
    requestJson<PublicRightsAssistantResponse>('/public/rights-assistant', {method: 'POST', body: JSON.stringify({query: q, mode: 'rights'})}),
    requestJson<PublicEncounterResponse>('/public/encounter?situation=' + encodeURIComponent(encounterSituation(q))),
  ]);
  const answerText =
    typeof assistant.analysis === 'string' && assistant.analysis.trim()
      ? assistant.analysis
      : assistant.answer || 'No grounded rights answer was returned.';
  const answer: GuestRightsAnswer = {
    question: q,
    answer: answerText,
    notice: assistant.coverage_notice || pack.disclaimer || '',
  };
  const research: GuestResearch = {
    query: q,
    topic: 'Georgia rights and encounter information',
    guidance: pack.prompt || pack.disclaimer || '',
    resources: [...guestOfficialIndexes(pack), ...indexedAuthorityLinks(assistant)],
    notice: [pack.disclaimer, pack.coverage_limit, assistant.coverage_notice, 'Index links are official court pages, not a complete code and not a claim that any citation is current.']
      .filter((part) => typeof part === 'string' && part.trim())
      .join(' '),
  };
  return {answer, research};
}

export async function guestEncounterReply(requestJson: GuestRequestJson, prompt: string): Promise<PublicRightsAssistantResponse> {
  const data = await requestJson<PublicRightsAssistantResponse>('/public/rights-assistant', {
    method: 'POST',
    body: JSON.stringify({query: prompt, mode: 'talk_to_me'}),
  });
  if (!data.answer && data.analysis) data.answer = data.analysis;
  return data;
}

const FALLBACK_INDEXES: OfficialIndexRow[] = [
  {title: 'Supreme Court of Georgia opinion index', url: 'https://www.gasupreme.us/2026-opinions/', kind: 'court index', official: true},
  {title: 'Court of Appeals of Georgia', url: 'https://www.gaappeals.us/', kind: 'court index', official: true},
];

export function guestOfficialIndexes(pack: {official_indexes?: OfficialIndexRow[]}): GuestResource[] {
  const rows = Array.isArray(pack.official_indexes) && pack.official_indexes.length ? pack.official_indexes : FALLBACK_INDEXES;
  return rows
    .filter((row): row is OfficialIndexRow & {url: string} => Boolean(row) && typeof row.url === 'string' && row.url.startsWith('https://'))
    .map((row) => ({
      title: row.title || row.url,
      url: row.url,
      kind: row.kind || 'court index',
      official: row.official !== false,
    }));
}

export function indexedAuthorityLinks(assistant: {authorities?: IndexedAuthorityRow[]}): GuestResource[] {
  const rows = Array.isArray(assistant.authorities) ? assistant.authorities : [];
  return rows
    .map((row) => {
      const url = typeof row.source_url === 'string' ? row.source_url : row.url;
      if (!url || !url.startsWith('https://')) return null;
      const title = (row.citation || row.title || url).trim();
      if (!title) return null;
      return {
        title,
        url,
        kind: 'indexed authority · not verified as current Georgia law',
        official: false,
      };
    })
    .filter((row): row is GuestResource => row !== null);
}
