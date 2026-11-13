/** Photograph or upload a paper and (optionally) translate it to Spanish. */

export type PaperResult = {
  readable?: boolean;
  document_type?: string;
  extracted_text?: string;
  summary?: string;
  key_dates?: string[];
  charges_or_claims?: string[];
  case_number?: string;
  court?: string;
  field_explanations?: Record<string, string>;
  next_steps?: string[];
  questions_for_lawyer?: string[];
  helpful_flags?: string[];
  answer?: string;
  answer_es?: string;
  translation_notice?: string;
  translation?: unknown;
  defense_plan?: { answer?: string; status?: string; case_stage?: string; label?: string; case_type?: string };
  photo_tips?: string;
};

export type ReadPaper = (files: File[], opts?: { question?: string; translate?: boolean }) => Promise<PaperResult>;
export type TranslatePaper = (result: PaperResult) => Promise<PaperResult>;

export async function readPaperAt(
  apiBase: string,
  token: string | null,
  files: File[],
  opts?: { question?: string; translate?: boolean },
): Promise<PaperResult> {
  if (!files.length) throw new Error("Add a photo or PDF of the paper first.");
  const form = new FormData();
  files.forEach((file, i) => form.append("files", file, file.name || `page-${i + 1}`));
  form.append("question", opts?.question || "");
  form.append("translate", opts?.translate ? "true" : "false");
  form.append("language", opts?.translate ? "es" : "en");
  form.append("defense_plan", "true");
  const res = await fetch(apiBase + "/documents/read", {
    method: "POST",
    headers: token ? { Authorization: "Bearer " + token } : {},
    body: form,
  });
  const data = await res.json().catch(() => ({ detail: "The server returned an unreadable response." }));
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "The paper could not be read.");
  return data as PaperResult;
}

export async function translatePaperAt(apiBase: string, token: string | null, result: PaperResult): Promise<PaperResult> {
  const res = await fetch(apiBase + "/documents/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: "Bearer " + token } : {}) },
    body: JSON.stringify(result),
  });
  const data = await res.json().catch(() => ({ detail: "The server returned an unreadable response." }));
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "The paper could not be translated.");
  return data as PaperResult;
}
