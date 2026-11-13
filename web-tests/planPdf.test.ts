import assert from "node:assert/strict";
import test from "node:test";
import { buildPdf, planText, wrapLines } from "../src/planPdf.ts";

test("wraps long lines without dropping text", () => {
  const lines = wrapLines("Questions to ask your lawyer\n• " + "word ".repeat(40));
  assert.ok(lines.length >= 2);
  assert.equal(lines[0], "Questions to ask your lawyer");
});

test("PDF starts with a header and includes citations and the notice", () => {
  const body = "Your Defense Plan: DUI\n\nQuick answer\nChallenge the stop.\n\nQuestions to ask your lawyer\n• Can the blood test be challenged?\n\nO.C.G.A. § 40-6-391";
  const notice = "This is legal information, not legal advice.";
  const bytes = buildPdf("Your Defense Plan: DUI", body, notice);
  assert.equal(String.fromCharCode(...bytes.slice(0, 8)), "%PDF-1.4");
  const text = new TextDecoder("latin1").decode(bytes);
  assert.match(text, /STANDALONE ASSISTANT/);
  assert.match(text, /Questions to ask your lawyer/);
  assert.match(text, /O\.C\.G\.A\./);
  assert.match(text, /not legal advice/);
  assert.match(text, /%%EOF/);
  assert.match(planText("Plan", "Hello", notice), /not legal advice/);
});
