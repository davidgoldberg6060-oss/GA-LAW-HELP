/** One AI screen's chat, kept on this device so the screen resumes where it left off. */
export type ChatLine = { id: string; role: "user" | "assistant"; text: string; turn?: number };

export const MAX_LINES = 40;
const key = (feature: string) => `ga_chat_${feature}`;

type Store = Pick<Storage, "getItem" | "setItem" | "removeItem">;

export function loadThread(store: Store | undefined, feature: string): ChatLine[] {
  try {
    const rows = JSON.parse(store?.getItem(key(feature)) || "[]");
    if (!Array.isArray(rows)) return [];
    return rows
      .filter((r) => r && (r.role === "user" || r.role === "assistant") && typeof r.text === "string")
      .map((r, i) => ({ id: String(r.id || `r${i}`), role: r.role, text: r.text, turn: typeof r.turn === "number" ? r.turn : undefined }))
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
