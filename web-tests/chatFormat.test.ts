// Run: node --test --experimental-strip-types web-tests/
import { test } from "node:test";
import assert from "node:assert/strict";
import { formatAnswer, isHeading, splitLead } from "../src/chatFormat.ts";
import { continuityLine, loadThread, saveThread, MAX_LINES } from "../src/chatThread.ts";

const ANSWER = `Short answer
You were searched without a warrant.

Motions that could help
• Motion to suppress evidence (O.C.G.A. § 17-5-30): Asks the judge to throw out evidence.
• Discovery: get the State's evidence.

Questions to ask your lawyer
1. Is a motion to suppress appropriate?
2. What are the deadlines?
Note: Georgia Code text is from the 2022 edition.`;

test("answers become headings, lists and paragraphs", () => {
  const b = formatAnswer(ANSWER);
  assert.deepEqual(b.map((x) => x.kind), ["heading", "para", "heading", "list", "heading", "list", "para"]);
  assert.equal(b[2].kind === "heading" && b[2].text, "Motions that could help");
  const motions = b[3].kind === "list" ? b[3].items : [];
  assert.equal(motions[0].lead, "Motion to suppress evidence (O.C.G.A. § 17-5-30)");
  assert.equal(motions[0].text, "Asks the judge to throw out evidence.");
  assert.equal(b[5].kind === "list" && b[5].items.length, 2);
});

test("sentences are never headings; plain text stays one paragraph", () => {
  assert.equal(isHeading("You were searched without a warrant."), false);
  assert.equal(isHeading("How it works in Georgia"), true);
  assert.deepEqual(formatAnswer("just one line of text."), [{ kind: "para", text: "just one line of text." }]);
  assert.equal(splitLead("Timing matters. See: the rule").lead, "");
});

test("each screen keeps its own thread on the device, bounded", () => {
  const mem = new Map<string, string>();
  const store = { getItem: (k: string) => mem.get(k) ?? null, setItem: (k: string, v: string) => void mem.set(k, v), removeItem: (k: string) => void mem.delete(k) };
  saveThread(store, "ai_help", [{ id: "1", role: "user", text: "car search" }]);
  assert.equal(loadThread(store, "ai_help")[0].text, "car search");
  assert.deepEqual(loadThread(store, "charge_check"), []);
  saveThread(store, "ai_help", Array.from({ length: 60 }, (_, i) => ({ id: String(i), role: "user" as const, text: "q" + i })));
  assert.equal(loadThread(store, "ai_help").length, MAX_LINES);
  saveThread(store, "ai_help", []);
  assert.equal(mem.has("ga_chat_ai_help"), false);
  mem.set("ga_chat_x", "not json");
  assert.deepEqual(loadThread(store, "x"), []);
});

test("continuity is one short line, only for another screen", () => {
  assert.equal(continuityLine({ elsewhere_screen: "AI Help", elsewhere_topic: "car" }, "AI Help"), "");
  assert.equal(continuityLine({ elsewhere_screen: "Charge Check", elsewhere_topic: "car search" }, "AI Help"), "Continuing from Charge Check: “car search”");
  assert.ok(continuityLine({ elsewhere_screen: "Motions", elsewhere_topic: "x".repeat(300) }, "AI Help").length < 130);
  assert.equal(continuityLine(null, "AI Help"), "");
});

test("a stack of questions without bullets becomes a list", () => {
  const b = formatAnswer("Questions to ask your lawyer\nIs a motion to suppress right?\nWhat are the deadlines?\n\nWhere to get help\nCall a public defender.");
  assert.deepEqual(b.map((x) => x.kind), ["heading", "list", "heading", "para"]);
});
