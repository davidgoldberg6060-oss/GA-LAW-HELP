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
    resources: [],
    notice: pack.disclaimer || assistant.coverage_notice || '',
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
