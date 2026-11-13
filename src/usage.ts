/** First-party anonymous usage counts and app-feedback helpers. No question text is sent. */
export const WEB_VERSION = "0.1.0";
export const SESSION_GAP_MS = 30 * 60 * 1000;
export const PROMPT_AFTER_OPENS = 4;
export const PROMPT_GAP_MS = 14 * 24 * 60 * 60 * 1000;

export const FEATURES = ["chat", "case_check", "motion_maker", "funny_laws", "find_legal_help", "uploads"] as const;
export type Feature = (typeof FEATURES)[number];

export const CATEGORIES: { id: FeedbackCategory; label: string }[] = [
  { id: "bug", label: "Bug or crash" },
  { id: "design", label: "Design or hard to use" },
  { id: "idea", label: "Missing feature or idea" },
  { id: "slow", label: "Slow" },
  { id: "other", label: "Other" },
];
export type FeedbackCategory = "bug" | "design" | "idea" | "slow" | "other";

const FIRST = "ga_usage_first_open";
const LAST_SESSION = "ga_usage_last_session";
const OPEN_COUNT = "ga_usage_open_count";
const LAST_PROMPT = "ga_usage_last_prompt";
const LAST_FEEDBACK = "ga_usage_last_feedback";

export type UsageEvent = { type: "open" | "session" | "first_open" | "install" | "feature"; feature?: Feature };

export function shouldPrompt(opens: number, lastPromptAt: number | null, lastFeedbackAt: number | null, now: number): boolean {
  if (opens < PROMPT_AFTER_OPENS) return false;
  const last = Math.max(lastPromptAt || 0, lastFeedbackAt || 0);
  if (last && now - last < PROMPT_GAP_MS) return false;
  return true;
}

export type UsageClient = { api: string; getToken: () => Promise<string | null> };

let client: UsageClient | null = null;
let currentScreen = "home";

export function setScreen(id: string) { currentScreen = id || "home"; }
export function getScreen() { return currentScreen; }

function store() { return typeof window !== "undefined" ? window.localStorage : undefined; }

export function initUsage(opts: UsageClient, now = Date.now()) {
  client = opts;
  const ls = store();
  if (!ls) return;
  const events: UsageEvent[] = [];
  if (!ls.getItem(FIRST)) {
    ls.setItem(FIRST, "1");
    events.push({ type: "first_open" }, { type: "install" });
  }
  const last = Number(ls.getItem(LAST_SESSION) || 0);
  events.push({ type: "open" });
  if (!last || now - last >= SESSION_GAP_MS) events.push({ type: "session" });
  ls.setItem(LAST_SESSION, String(now));
  ls.setItem(OPEN_COUNT, String(Number(ls.getItem(OPEN_COUNT) || 0) + 1));
  void sendEvents(events);
}

export function trackFeature(feature: Feature) {
  void sendEvents([{ type: "feature", feature }]);
}

export function openCount(): number {
  return Number(store()?.getItem(OPEN_COUNT) || 0);
}

export function promptDue(now = Date.now()): boolean {
  const ls = store();
  if (!ls) return false;
  return shouldPrompt(
    Number(ls.getItem(OPEN_COUNT) || 0),
    Number(ls.getItem(LAST_PROMPT) || 0) || null,
    Number(ls.getItem(LAST_FEEDBACK) || 0) || null,
    now,
  );
}

export function markPromptSeen() { store()?.setItem(LAST_PROMPT, String(Date.now())); }
export function markFeedbackSent() { store()?.setItem(LAST_FEEDBACK, String(Date.now())); }

async function sendEvents(events: UsageEvent[]) {
  if (!client || !events.length) return;
  try {
    const token = await client.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "X-App-Platform": "web",
      "X-App-Version": WEB_VERSION,
    };
    if (token) headers.Authorization = "Bearer " + token;
    await fetch(client.api + "/usage/events", {
      method: "POST",
      headers,
      body: JSON.stringify({ platform: "web", app_version: WEB_VERSION, events }),
    });
  } catch {
    /* usage counts must never block the app */
  }
}

export type FeedbackPayload = {
  rating: number | null;
  category: FeedbackCategory;
  comment: string;
  contactEmail: string;
  screen?: string;
};

export function validateFeedback(input: FeedbackPayload): string | null {
  if (!CATEGORIES.some((c) => c.id === input.category)) return "Choose a category.";
  const comment = input.comment.trim();
  if (input.rating == null && !comment) return "Please add a star rating or a short comment.";
  if (input.rating != null && (input.rating < 1 || input.rating > 5)) return "Rating must be 1 to 5 stars.";
  const email = input.contactEmail.trim();
  if (email && !/^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/.test(email)) return "That contact email does not look valid.";
  return null;
}

export async function sendFeedback(input: FeedbackPayload): Promise<string> {
  const error = validateFeedback(input);
  if (error) throw new Error(error);
  if (!client) throw new Error("Feedback is not ready yet. Please try again.");
  const token = await client.getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-App-Platform": "web",
    "X-App-Version": WEB_VERSION,
  };
  if (token) headers.Authorization = "Bearer " + token;
  const res = await fetch(client.api + "/feedback", {
    method: "POST",
    headers,
    body: JSON.stringify({
      platform: "web",
      app_version: WEB_VERSION,
      screen: input.screen || currentScreen,
      rating: input.rating,
      category: input.category,
      comment: input.comment.trim() || null,
      contact_email: input.contactEmail.trim() || null,
    }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = typeof body.detail === "string" ? body.detail : "Feedback could not be sent. Please try again.";
    throw new Error(detail);
  }
  markFeedbackSent();
  return typeof body.message === "string" ? body.message : "Thank you. Your feedback helps us improve STANDALONE ASSISTANT.";
}
