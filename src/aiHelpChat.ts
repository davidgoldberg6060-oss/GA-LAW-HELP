import { SAFETY_NOTICE } from "./approvedScreenCatalog";

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
};

const PRIVATE_CASE = /my case|case file|upload evidence|docket number/i;
const UNSAFE = /resist|run from|lie to|destroy evidence|hide the/i;

/** Local chat copy only. Real answers must come from /public/rights-assistant. */
export function guestChatReply(question: string): string {
  const q = question.trim();
  if (!q) return `Enter a question. Guest chat stays on /public/rights-assistant. ${SAFETY_NOTICE}`;
  if (UNSAFE.test(q)) return `Do not resist, run, lie, or destroy evidence. ${SAFETY_NOTICE}`;
  if (PRIVATE_CASE.test(q)) {
    return `Private cases, uploads, and case analysis stay login-only. This chat will not open them. ${SAFETY_NOTICE}`;
  }
  return `Sent to guest research on /public/rights-assistant. No code text is invented here, and Lexis notes are not used. ${SAFETY_NOTICE}`;
}

export function appendChat(messages: ChatMessage[], question: string, now = Date.now()): ChatMessage[] {
  const q = question.trim();
  if (!q) return messages;
  return [
    ...messages,
    { id: `u-${now}`, role: "user", text: q },
    { id: `a-${now}`, role: "assistant", text: guestChatReply(q) },
  ];
}
