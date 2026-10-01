/** Unauthenticated guest helpers. Private case tools must keep using authApi. */
export type GuestRightsAnswer = {
  question: string;
  answer: string;
  notice: string;
};

export type GuestResearch = {
  query: string;
  topic: string;
  guidance: string;
  resources: Array<{title: string; url: string; kind: string; official: boolean}>;
  notice: string;
};

export async function guestRightsAndEncounter(apiBase: string, requestJson: typeof fetch, query: string) {
  const q = query.trim();
  const [assistant, pack] = await Promise.all([
    requestJson('/public/rights-assistant', {method: 'POST', body: JSON.stringify({query: q, mode: 'rights'})}),
    requestJson('/public/encounter?situation=' + encodeURIComponent(q)),
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
    resources: guestOfficialIndexes(pack),
    notice: [pack.disclaimer, pack.coverage_limit, assistant.coverage_notice, 'Index links are official court pages, not a complete code and not a claim that any citation is current.']
      .filter((part) => typeof part === 'string' && part.trim())
      .join(' '),
  };
  return {answer, research};
}

export async function guestEncounterReply(requestJson: typeof fetch, prompt: string) {
  const data = await requestJson('/public/rights-assistant', {
    method: 'POST',
    body: JSON.stringify({query: prompt, mode: 'talk_to_me'}),
  });
  if (!data.answer && data.analysis) data.answer = data.analysis;
  return data;
}

const FALLBACK_INDEXES = [
  {title: 'Supreme Court of Georgia opinion index', url: 'https://www.gasupreme.us/2026-opinions/', kind: 'court index', official: true},
  {title: 'Court of Appeals of Georgia', url: 'https://www.gaappeals.us/', kind: 'court index', official: true},
];

export function guestOfficialIndexes(pack: {official_indexes?: Array<{title?: string; url?: string; kind?: string; official?: boolean}>}) {
  const rows = Array.isArray(pack.official_indexes) && pack.official_indexes.length ? pack.official_indexes : FALLBACK_INDEXES;
  return rows
    .filter((row) => row && typeof row.url === 'string' && row.url.startsWith('https://'))
    .map((row) => ({
      title: row.title || row.url,
      url: row.url as string,
      kind: row.kind || 'court index',
      official: row.official !== false,
    }));
}
