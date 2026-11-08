// Run: node --test --experimental-strip-types web-tests/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { aiHelpQuestionOnOpen } from "../src/aiHelpNav.ts";

const screens = readFileSync(new URL("../src/ApprovedScreens.tsx", import.meta.url), "utf8");
const app = readFileSync(new URL("../src/App.tsx", import.meta.url), "utf8");
const aiBranch = screens.slice(screens.indexOf('if (id === "ai")'), screens.indexOf('if (id === "rights")'));

test("blank fields: opening AI Help invents nothing", () => {
  assert.equal(aiHelpQuestionOnOpen("", ""), "");
  assert.equal(aiHelpQuestionOnOpen("", undefined), "");
  assert.equal(aiHelpQuestionOnOpen("   ", "  "), "   ");
});

test("a typed main-field draft is carried into an empty AI Help box", () => {
  assert.equal(aiHelpQuestionOnOpen("", "  Can my landlord keep my deposit? "), "Can my landlord keep my deposit?");
});

test("an AI Help draft already typed is preserved", () => {
  assert.equal(aiHelpQuestionOnOpen("my own draft", "other text"), "my own draft");
});

test("AI Help navigation does not write to the main field, submit, or use a canned question", () => {
  assert.ok(aiBranch.length > 0);
  assert.doesNotMatch(aiBranch, /onAsk\(/);
  assert.doesNotMatch(aiBranch, /sendGuestChat|askGuest/);
  assert.doesNotMatch(aiBranch, /\.ask input/);
  assert.doesNotMatch(screens, /What should I know before a Georgia police encounter\?/);
});

test("focus moves to AI Help's own question box", () => {
  assert.match(screens, /ref=\{aiQuestionRef\}/);
  assert.match(screens, /if \(panel === "ai"\) aiQuestionRef\.current\?\.focus\(\)/);
});

test("deliberate actions still route questions", () => {
  assert.match(screens, /onClick=\{\(\) => props\.onAsk\(`Title \$\{title\.number\}/); // "Ask on guest research"
  assert.match(screens, /onClick=\{sendGuestChat\}/); // "Send guest question"
  assert.match(app, /heroDraft=\{q\}/);
});
