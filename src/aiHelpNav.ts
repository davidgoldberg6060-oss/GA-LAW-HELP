/**
 * What opening the AI Help panel does to the two question fields. Navigation never invents a question,
 * never submits, and never writes into the page's main "Georgia legal question" field. A draft the user
 * typed in the main field is carried into AI Help only when AI Help's own box is still empty.
 */
export function aiHelpQuestionOnOpen(aiHelpQuestion: string, heroDraft?: string): string {
  if (aiHelpQuestion.trim()) return aiHelpQuestion;
  const draft = (heroDraft || "").trim();
  return draft ? draft : aiHelpQuestion;
}
