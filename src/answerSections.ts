/**
 * Turns a plain-text AI answer into a short "Quick answer" plus small, collapsible sections
 * (title + item count), so a phone screen shows a few lines instead of a wall of text.
 * Nothing is dropped: long citation lists move to "Laws cited", side notes become small footnotes.
 * Kept in step with android/.../AnswerSections.kt.
 */
export type AnswerItem = { head: string; detail?: string; meta?: string };
export type SectionKind = "info" | "motions" | "questions" | "deadlines" | "laws" | "help";
export type AnswerSection = { id: string; title: string; kind: SectionKind; items: AnswerItem[]; notes: string[] };
export type LawRef = { citation: string; title?: string | null; id?: number | null };
export type StructuredAnswer = { quick: string; sections: AnswerSection[]; note: string; laws: LawRef[] };

/** Items shown before a "Show more" link inside a section. */
export const SECTION_VISIBLE = 4;
const QUICK_SENTENCES = 3;

const BULLET = /^\s*(?:[•●▪*-]|\d{1,2}[.)])\s+/;
const QUICK_HEADINGS = /^(short answer|quick answer|what's happening|your situation|the issue|facts to confirm)$/i;
const TOP_HEADINGS = new Set([
  "short answer", "quick answer", "how it works in georgia", "how it works", "steps you can take", "questions to ask your lawyer",
  "motions that could help", "deadlines and costs", "where to get help", "laws cited",
  "what's happening", "stay safe right now", "your rights", "what police can and can't do", "what to say or do",
  "facts to confirm", "legal issues", "the other side's arguments", "your side's arguments", "possible motions",
  "next steps", "your situation", "rights that may apply", "what police can do", "what police can't do",
  "your options", "the issue", "facts or evidence needed", "questions to check",
]);
const RENAME: Record<string, string> = {
  "how it works in georgia": "How it works",
  "challenging the evidence": "Ways to fight the evidence",
  "rights and court procedure": "Your rights in court",
  "information to gather for your lawyer": "What to gather for your lawyer",
  "possible motions": "Motions that could help",
};
const GROUP_LABEL = /^[A-Z][A-Za-z ,'’/&()-]{2,60}:$/;
// "O.C.G.A. § 17-5-30", "O.C.G.A. §§ 16-13-2", "Unif. Super. Ct. R. 31.1"
const CITE = /O\.C\.G\.A\.\s*§§?\s*\d{1,2}-\d{1,3}-\d+(?:\.\d+)?|Unif\.\s*(?:Super|State|Magis|Juv)\.\s*Ct\.\s*R\.\s*[\d.]+/g;
const CITE_PAREN = /\s*\((?:[^()]*?)(?:O\.C\.G\.A\.|Unif\.\s*\w+\.\s*Ct\.\s*R\.)[^()]*\)/g;
const SIDE_NOTE = /^(tap\s+["“]?open my case|a lawyer should decide|providers decide eligibility|contacting them doesn'?t guarantee)/i;

function kindOf(title: string): SectionKind {
  const t = title.toLowerCase();
  if (t.includes("motion")) return "motions";
  if (t.startsWith("questions")) return "questions";
  if (t.startsWith("deadlines")) return "deadlines";
  if (t === "laws cited") return "laws";
  if (t.startsWith("where to get help")) return "help";
  return "info";
}

function cleanTitle(raw: string): string {
  const t = raw.replace(/[:：]\s*$/, "").trim();
  return RENAME[t.toLowerCase()] || t;
}

export function isTopHeading(line: string): boolean {
  const t = line.trim().replace(/:$/, "");
  if (TOP_HEADINGS.has(t.toLowerCase())) return true;
  // Unknown short title-like line (no sentence ending, not a bullet).
  if (!t || t.length > 50 || BULLET.test(t) || /[.,;!?]$/.test(line.trim())) return false;
  return /^[A-Z]/.test(t) && t.split(/\s+/).length <= 7 && !/:$/.test(line.trim());
}

export function sentences(text: string): string[] {
  // Do not split after abbreviations used in Georgia citations.
  const guarded = text.replace(/\b(O\.C\.G\.A|U\.S\.C|U\.S|Ga|App|Ct|R|Super|Unif|v|No|St|Mr|Ms|Dr)\./g, (m) => m.replace(/\./g, "\u0001"));
  return guarded
    .split(/(?<=[.!?])\s+(?=[A-Z0-9“"(])/)
    .map((s) => s.replace(/\u0001/g, ".").trim())
    .filter(Boolean);
}

export function citationsIn(text: string): string[] {
  return Array.from(new Set((text.match(CITE) || []).map((c) => c.replace(/\s+/g, " ").replace("§§", "§"))));
}

/** Removes "(O.C.G.A. § 17-5-30, O.C.G.A. § 17-5-21)" style lists; inline citations in a sentence stay. */
export function stripCitationLists(text: string): string {
  return text.replace(CITE_PAREN, "").replace(/\s+([,.:;])/g, "$1").replace(/\s{2,}/g, " ").trim();
}

/** One bullet → short headline + optional one-line detail (+ small meta such as filing timing). */
export function toItem(raw: string, kind: SectionKind): AnswerItem {
  const original = raw.replace(BULLET, "").trim();
  const t = stripCitationLists(original);
  if (kind === "motions") {
    // "Title (O.C.G.A. § …): purpose How it can help: … Timing: …" — the citation list marks the end of the title.
    const withCite = original.match(/^(.{3,110}?)\s*\((?:[^()]*?)(?:O\.C\.G\.A\.|Unif\.)[^()]*\):\s+(.*)$/);
    const m = withCite ? [original, withCite[1], stripCitationLists(withCite[2])] : t.match(/^(.{3,90}?):\s+(.*)$/);
    if (m) {
      const rest = m[2];
      const helps = rest.match(/How it can help:\s*(.*?)(?=\s+Timing:|$)/i)?.[1]?.trim();
      const timing = rest.match(/Timing:\s*(.*)$/i)?.[1]?.trim();
      const purpose = rest.split(/\s+How it can help:/i)[0].split(/\s+Timing:/i)[0].trim();
      return { head: m[1].trim(), detail: helps || purpose || undefined, meta: timing ? "When to file: " + timing : undefined };
    }
  }
  if (kind === "help") {
    const m = t.match(/^([^.]{3,110})\s+[—–]\s+(.*)$/);
    if (m) return { head: m[1].trim(), detail: sentences(m[2]).slice(0, 2).join(" ") || undefined };
  }
  if (kind === "questions") return { head: t };
  const lead = t.match(/^([^.!?]{3,70}):\s+(.*)$/);
  if (lead) return { head: lead[1].trim(), detail: lead[2].trim() || undefined };
  const s = sentences(t);
  return s.length > 1 ? { head: s[0], detail: s.slice(1).join(" ") } : { head: t };
}

function keyOf(c: string): string {
  return c.replace(/\s*\(text as of[^)]*\)/i, "").replace(/\s+/g, " ").trim().toLowerCase();
}

export function structureAnswer(raw: string, known: LawRef[] = []): StructuredAnswer {
  const text = (raw || "").replace(/\r\n?/g, "\n");
  const cites = citationsIn(text);
  const sections: AnswerSection[] = [];
  let quickParts: string[] = [];
  let note = "";
  let top = "";            // current top heading (lowercase)
  let cur: AnswerSection | null = null;
  let sawHeading = false;
  const lawLines: LawRef[] = [];

  const open = (title: string) => {
    const t = cleanTitle(title);
    const existing = sections.find((s) => s.title.toLowerCase() === t.toLowerCase());
    cur = existing || { id: "s" + sections.length, title: t, kind: kindOf(t), items: [], notes: [] };
    if (!existing) sections.push(cur);
  };
  const add = (line: string, bullet: boolean) => {
    if (top === "laws cited") {
      const [c, ...rest] = line.replace(BULLET, "").split(/\s+[—–]\s+/);
      if (c.trim()) lawLines.push({ citation: c.trim(), title: rest.join(" — ") || null });
      return;
    }
    if (QUICK_HEADINGS.test(top) || (!sawHeading && !cur)) {
      quickParts.push(line.replace(BULLET, ""));
      return;
    }
    if (!cur) open("More about this");
    const sec = cur as unknown as AnswerSection;
    const body = line.replace(BULLET, "").trim();
    if (SIDE_NOTE.test(body)) { sec.notes.push(body); return; }
    // A long paragraph or a bullet of 3+ sentences reads better as one short item per sentence.
    if ((sec.kind === "info" || sec.kind === "deadlines") && !/^[^.!?]{3,70}:\s/.test(body)) {
      const parts = sentences(body);
      if (parts.length > 2 || (!bullet && body.length > 120)) {
        parts.forEach((s) => sec.items.push(toItem(s, sec.kind)));
        return;
      }
    }
    // A wrapped line continues the previous bullet.
    if (!bullet && /^[a-z(]/.test(body) && sec.items.length) {
      const last = sec.items[sec.items.length - 1];
      last.detail = ((last.detail || "") + " " + body).trim();
      return;
    }
    sec.items.push(toItem(body, sec.kind));
  };

  for (const rawLine of text.split("\n")) {
    const line = rawLine.trim();
    if (!line) continue;
    if (/^note:/i.test(line)) { note = line.replace(/^note:\s*/i, ""); continue; }
    if (!BULLET.test(line) && isTopHeading(line)) {
      sawHeading = true;
      top = line.replace(/:$/, "").trim().toLowerCase();
      cur = null;
      if (!QUICK_HEADINGS.test(top) && top !== "laws cited") open(line);
      continue;
    }
    if (!BULLET.test(line) && GROUP_LABEL.test(line) && sawHeading && !QUICK_HEADINGS.test(top)) {
      open(line);
      continue;
    }
    add(line, BULLET.test(line));
  }

  // Quick answer: 1-3 short sentences; anything longer moves to the top of the first section.
  const quickSentences = sentences(stripCitationLists(quickParts.join(" ")));
  let quick = quickSentences.slice(0, QUICK_SENTENCES).join(" ");
  const overflow = quickSentences.slice(QUICK_SENTENCES);
  if (!quick && sections.length && sections[0].items.length) {
    const first = sections[0].items.shift() as AnswerItem;
    quick = [first.head, first.detail].filter(Boolean).join(" ");
  }
  if (overflow.length) {
    const target = sections.find((s) => s.kind === "info" && s.items.length) || (() => { const s: AnswerSection = { id: "sq", title: "More about this", kind: "info", items: [], notes: [] }; sections.unshift(s); return s; })();
    target.items.unshift(...overflow.map((s) => toItem(s, "info")));
  }

  // Laws cited: what the server listed, plus any citation the text used; one entry each.
  const laws: LawRef[] = [];
  const seen = new Set<string>();
  for (const l of [...known, ...lawLines, ...cites.map((c) => ({ citation: c }))]) {
    const k = keyOf(l.citation || "");
    if (!k || seen.has(k)) continue;
    seen.add(k);
    laws.push({ ...l, citation: l.citation.replace(/\s*\(text as of[^)]*\)/i, "").trim() });
  }
  const kept = sections.filter((s) => s.items.length || s.notes.length);
  if (laws.length) {
    const lawSec: AnswerSection = { id: "laws", title: "Laws cited", kind: "laws", items: laws.map((l) => ({ head: l.citation, detail: l.title || undefined })), notes: [] };
    const helpAt = kept.findIndex((s) => s.kind === "help");
    if (helpAt >= 0) kept.splice(helpAt, 0, lawSec); else kept.push(lawSec);
  }
  return { quick, sections: kept, note, laws };
}

/** "Motion to suppress evidence, Demand for speedy trial…" preview under a closed Motions title. */
export function teaser(section: AnswerSection, n = 2): string {
  if (section.kind !== "motions" || !section.items.length) return "";
  const names = section.items.slice(0, n).map((i) => i.head);
  return names.join(" · ") + (section.items.length > n ? " · …" : "");
}
