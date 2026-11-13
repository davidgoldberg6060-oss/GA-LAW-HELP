/** Unauthenticated guest helpers. Private case tools must keep using authApi. */
export type GuestRightsAnswer = {
  question: string;
  answer: string;
  notice: string;
  /** Criminal-case stage detected in the question; links to the My Case guide. */
  case_stage?: string | null;
};

export type GuestResource = {title: string; url: string; kind: string; official: boolean};

export type GuestResearch = {
  query: string;
  topic: string;
  guidance: string;
  resources: GuestResource[];
  /** Laws the answer relies on; each expands inline to its full text. */
  laws?: {citation: string; title?: string | null; id?: number | null}[];
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

/** Server limit for POST /public/rights-assistant `query` (backend/app/main.py). */
export const GUEST_QUERY_MAX_CHARS = 4000;
/** Server limit for GET /public/encounter `situation` (backend/app/public_rights.py max_length). */
export const ENCOUNTER_SITUATION_MAX_CHARS = 400;
export const GUEST_QUERY_TOO_LONG_MESSAGE =
  'Your question is too long for free research. Please shorten it to 4,000 characters or fewer and focus on the key facts.';

/** The encounter pack only needs a short situation label; trim instead of failing with HTTP 422. */
export function encounterSituation(query: string): string {
  return query.trim().slice(0, ENCOUNTER_SITUATION_MAX_CHARS);
}

export async function guestRightsAndEncounter(
  apiBase: string,
  requestJson: GuestRequestJson,
  query: string,
): Promise<{answer: GuestRightsAnswer; research: GuestResearch}> {
  const q = query.trim();
  if (q.length > GUEST_QUERY_MAX_CHARS) throw new Error(GUEST_QUERY_TOO_LONG_MESSAGE);
  const [assistant, pack] = await Promise.all([
    requestJson<PublicRightsAssistantResponse>('/public/rights-assistant', {method: 'POST', body: JSON.stringify({query: q, mode: 'rights'})}),
    // The encounter pack is supplementary: a failure here must not discard the grounded answer.
    requestJson<PublicEncounterResponse>('/public/encounter?situation=' + encodeURIComponent(encounterSituation(q))).catch(
      (): PublicEncounterResponse => ({}),
    ),
  ]);
  const answerText =
    typeof assistant.analysis === 'string' && assistant.analysis.trim()
      ? assistant.analysis
      : assistant.answer || 'No grounded rights answer was returned.';
  const answer: GuestRightsAnswer = {
    question: q,
    answer: answerText,
    notice: assistant.coverage_notice || pack.disclaimer || '',
    case_stage: (assistant as {case_stage?: string}).case_stage || null,
  };
  const research: GuestResearch = {
    query: q,
    topic: 'Georgia rights and encounter information',
    guidance: pack.prompt || pack.disclaimer || '',
    // Cited laws open inline (full text in the app) instead of linking out to downloads.
    resources: guestOfficialIndexes(pack),
    laws: Array.isArray((assistant as {laws_cited?: unknown}).laws_cited) ? (assistant as {laws_cited: {citation: string; title?: string; id?: number}[]}).laws_cited : [],
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

/** What a screen continues from (server `continuity` block / GET /me/conversation). */
export type Continuity = {
  continued?: boolean;
  turn_id?: number;
  screen_last_topic?: string | null;
  elsewhere_topic?: string | null;
  elsewhere_screen?: string | null;
};

export type AiHelpReply = {
  answer: string;
  notice: string;
  turnId?: number;
  continuity?: Continuity | null;
  /** Laws the answer cites (shown in its "Laws cited" section). */
  laws?: { citation: string; title?: string | null; id?: number | null }[];
  /** Up to 3 short suggested follow-up questions. */
  followUps?: string[];
  /** One-line "why this matters" per follow-up question (Defense Plan hidden issues). */
  followUpWhy?: Record<string, string>;
  /** Automatic Defense Plan: "built" or "needs_details" (asked 1-2 questions). */
  planStatus?: string;
  /** My Case stage whose motion maker fits this answer (e.g. "pretrial"). */
  caseStage?: string;
  publicDefenderProblems?: boolean;
};

/**
 * AI Help chat turn. With a device token the server continues this screen's own thread plus one
 * short note about the latest topic elsewhere in the app; without one it answers as a plain guest.
 */
export async function aiHelpAsk(requestJson: GuestRequestJson, query: string, token?: string | null): Promise<AiHelpReply> {
  const q = query.trim();
  if (q.length > GUEST_QUERY_MAX_CHARS) throw new Error(GUEST_QUERY_TOO_LONG_MESSAGE);
  const data = await requestJson<PublicRightsAssistantResponse & { continuity?: Continuity }>('/public/rights-assistant', {
    method: 'POST',
    headers: token ? { Authorization: 'Bearer ' + token } : {},
    body: JSON.stringify({ query: q, mode: 'general', feature: 'ai_help' }),
  });
  const answer = typeof data.analysis === 'string' && data.analysis.trim() ? data.analysis : data.answer || 'No grounded answer was returned.';
  const continuity = data.continuity && typeof data.continuity === 'object' ? data.continuity : null;
  const raw = data as { laws_cited?: unknown; follow_ups?: unknown; follow_up_details?: unknown };
  const laws = Array.isArray(raw.laws_cited)
    ? (raw.laws_cited as { citation?: unknown; title?: unknown; id?: unknown }[])
        .filter((l) => l && typeof l.citation === 'string' && l.citation.trim())
        .map((l) => ({ citation: String(l.citation), title: typeof l.title === 'string' ? l.title : null, id: typeof l.id === 'number' ? l.id : null }))
    : [];
  const followUps = Array.isArray(raw.follow_ups) ? (raw.follow_ups as unknown[]).filter((q): q is string => typeof q === 'string' && !!q.trim()).slice(0, 3) : [];
  const extra = data as { defense_plan?: { status?: unknown }; case_stage?: unknown; public_defender_problems?: unknown };
  const planStatus = extra.defense_plan && typeof extra.defense_plan.status === 'string' ? extra.defense_plan.status : undefined;
  const caseStage = typeof extra.case_stage === 'string' && extra.case_stage ? extra.case_stage : undefined;
  const publicDefenderProblems = extra.public_defender_problems === true;
  const followUpWhy: Record<string, string> = {};
  if (Array.isArray(raw.follow_up_details)) {
    for (const d of raw.follow_up_details as { question?: unknown; why?: unknown }[]) {
      if (d && typeof d.question === 'string' && typeof d.why === 'string' && followUps.includes(d.question)) followUpWhy[d.question] = d.why.slice(0, 200);
    }
  }
  return { answer, notice: data.coverage_notice || '', turnId: continuity?.turn_id, continuity, laws, followUps,
    followUpWhy: Object.keys(followUpWhy).length ? followUpWhy : undefined, planStatus, caseStage, publicDefenderProblems: publicDefenderProblems || undefined };
}
