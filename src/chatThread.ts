/** One AI screen's chat, kept on this device so the screen resumes where it left off. */
export type ChatLine = {
  id: string;
  role: "user" | "assistant";
  text: string;
  turn?: number;
  /** Laws cited with an answer (citation + short title). */
  laws?: { citation: string; title?: string | null; id?: number | null }[];
  /** Suggested follow-ups (max 3) for an answer. */
  followUps?: string[];
  /** One-line "why this matters" per follow-up. */
  followUpWhy?: Record<string, string>;
  /** Defense Plan answers: My Case stage for the motion maker, and the user's situation to pre-fill it. */
  caseStage?: string;
  situation?: string;
};

export const MAX_LINES = 40;
const key = (feature: string) => `ga_chat_${feature}`;

type Store = Pick<Storage, "getItem" | "setItem" | "removeItem">;

export function loadThread(store: Store | undefined, feature: string): ChatLine[] {
  try {
    const rows = JSON.parse(store?.getItem(key(feature)) || "[]");
    if (!Array.isArray(rows)) return [];
    return rows
      .filter((r) => r && (r.role === "user" || r.role === "assistant") && typeof r.text === "string")
      .map((r, i) => ({
        id: String(r.id || `r${i}`),
        role: r.role,
        text: r.text,
        turn: typeof r.turn === "number" ? r.turn : undefined,
        laws: Array.isArray(r.laws) ? r.laws.filter((l: { citation?: unknown }) => l && typeof l.citation === "string") : undefined,
        followUps: Array.isArray(r.followUps) ? r.followUps.filter((q: unknown) => typeof q === "string").slice(0, 3) : undefined,
        followUpWhy: r.followUpWhy && typeof r.followUpWhy === "object" && !Array.isArray(r.followUpWhy)
          ? Object.fromEntries(Object.entries(r.followUpWhy as Record<string, unknown>).filter(([, v]) => typeof v === "string")) as Record<string, string>
          : undefined,
        caseStage: typeof r.caseStage === "string" ? r.caseStage : undefined,
        situation: typeof r.situation === "string" ? r.situation.slice(0, 2000) : undefined,
      }))
      .slice(-MAX_LINES);
  } catch {
    return [];
  }
}

export function saveThread(store: Store | undefined, feature: string, rows: ChatLine[]): void {
  try {
    if (!rows.length) store?.removeItem(key(feature));
    else store?.setItem(key(feature), JSON.stringify(rows.slice(-MAX_LINES)));
  } catch {
    /* storage full or blocked: the chat still works for this visit */
  }
}

let seq = 0;
export function lineId(): string {
  seq += 1;
  return `${Date.now().toString(36)}-${seq}`;
}

/** The one quiet line under the chat title; never a transcript. */
export function continuityLine(c: { elsewhere_screen?: string | null; elsewhere_topic?: string | null } | null | undefined, screenLabel: string): string {
  if (!c || !c.elsewhere_topic || !c.elsewhere_screen || c.elsewhere_screen === screenLabel) return "";
  const topic = c.elsewhere_topic.length > 90 ? c.elsewhere_topic.slice(0, 89).trimEnd() + "…" : c.elsewhere_topic;
  return `Continuing from ${c.elsewhere_screen}: “${topic}”`;
}
