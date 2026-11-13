/** Turns a plain-text AI answer into tidy blocks (section headings, bullet lists, paragraphs) for the chat. */
export type ChatBlock =
  | { kind: "heading"; text: string }
  | { kind: "para"; text: string }
  | { kind: "list"; items: { lead: string; text: string }[] };

const BULLET = /^\s*(?:[•●▪*-]|\d{1,2}[.)])\s+/;

/** A line is a section heading when it is short, has no sentence ending, and is not a bullet. */
export function isHeading(line: string): boolean {
  const t = line.trim();
  if (!t || t.length > 60 || BULLET.test(t)) return false;
  if (/[.,;!?]$/.test(t)) return false;
  return /^[A-Z]/.test(t) && t.split(/\s+/).length <= 8;
}

/** "Motion to suppress (O.C.G.A. § 17-5-30): Asks the judge…" → bold lead + text. */
export function splitLead(item: string): { lead: string; text: string } {
  const i = item.indexOf(": ");
  if (i > 0 && i <= 110 && !/[.!?]/.test(item.slice(0, i).replace(/\b(?:O\.C\.G\.A|U\.S\.C|v|Ga|App)\./g, ""))) {
    return { lead: item.slice(0, i), text: item.slice(i + 2) };
  }
  return { lead: "", text: item };
}

export function formatAnswer(raw: string): ChatBlock[] {
  const blocks: ChatBlock[] = [];
  const lines = (raw || "").replace(/\r\n?/g, "\n").split("\n");
  let para: string[] = [];
  const flush = () => {
    // Several lines that are each a question ("Questions to ask your lawyer") read best as a list.
    if (para.length > 1 && para.every((line) => /\?["”')]?$/.test(line))) {
      blocks.push({ kind: "list", items: para.map((text) => ({ lead: "", text })) });
    } else if (para.length) {
      blocks.push({ kind: "para", text: para.join(" ") });
    }
    para = [];
  };
  for (const line of lines) {
    const t = line.trim();
    if (!t) { flush(); continue; }
    if (BULLET.test(t)) {
      flush();
      const item = splitLead(t.replace(BULLET, ""));
      const last = blocks[blocks.length - 1];
      if (last && last.kind === "list") last.items.push(item);
      else blocks.push({ kind: "list", items: [item] });
      continue;
    }
    if (!para.length && isHeading(t)) {
      blocks.push({ kind: "heading", text: t.replace(/:$/, "") });
      continue;
    }
    // A wrapped bullet continues the previous item.
    const last = blocks[blocks.length - 1];
    if (!para.length && last && last.kind === "list" && /^[a-z(]/.test(t)) {
      last.items[last.items.length - 1].text += " " + t;
      continue;
    }
    para.push(t);
  }
  flush();
  return blocks;
}
