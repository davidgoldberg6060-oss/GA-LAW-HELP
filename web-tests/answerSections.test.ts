// Run: node --test --experimental-strip-types web-tests/
import { test } from "node:test";
import assert from "node:assert/strict";
import { structureAnswer, stripCitationLists, teaser, toItem, sentences } from "../src/answerSections.ts";

const ANSWER = `Short answer
• The search of your car can be challenged. A motion to suppress may keep the drugs out. This depends on why police searched. Extra sentence here.

How it works in Georgia
Ways to fight the evidence:
• Police usually need a warrant to search a car.
• Without probable cause or consent, the search may be illegal.
Ways to lessen the outcome:
• First Offender (O.C.G.A. § 42-8-60) may apply if you have no prior felony.

Motions that could help
• Motion to suppress evidence (O.C.G.A. § 17-5-30, O.C.G.A. § 17-5-21): Asks the judge to throw out evidence. How it can help: Without the key evidence, charges are often dropped. Timing: Usually within ten days after arraignment.
• Discovery: get the prosecution's evidence (O.C.G.A. § 17-16-4): Opts into discovery. How it can help: Shows weaknesses early.
• A lawyer should decide whether and when to file any motion; deadlines can be short.

Questions to ask your lawyer
• Was the search of my car legal?
• Should we file a motion to suppress?

Where to get help
• Public defender (Georgia Public Defender Council) — Free if the court finds you qualify. Lawyers for people charged with a crime.
• Providers decide eligibility; contacting them doesn't guarantee they can take your case.

Note: Georgia Code text is from the 2022 edition.`;

test("quick answer is at most 3 sentences; the rest is kept in a section", () => {
  const a = structureAnswer(ANSWER);
  assert.equal(sentences(a.quick).length, 3);
  assert.ok(a.sections.some((s) => s.items.some((i) => i.head === "Extra sentence here.")));
});

test("group labels become their own short sections with counts", () => {
  const a = structureAnswer(ANSWER);
  const titles = a.sections.map((s) => s.title);
  assert.deepEqual(titles, ["Ways to fight the evidence", "Ways to lessen the outcome", "Motions that could help", "Questions to ask your lawyer", "Laws cited", "Where to get help"]);
  assert.equal(a.sections[0].items.length, 3); // 2 bullets + the quick-answer overflow sentence first
  assert.equal(a.sections[0].items[0].head, "Extra sentence here.");
});

test("motions: title headline, how it helps as detail, timing as meta; side notes kept as footnotes", () => {
  const m = structureAnswer(ANSWER).sections.find((s) => s.kind === "motions")!;
  assert.deepEqual(m.items[0], { head: "Motion to suppress evidence", detail: "Without the key evidence, charges are often dropped.", meta: "When to file: Usually within ten days after arraignment." });
  assert.equal(m.items[1].head, "Discovery: get the prosecution's evidence");
  assert.equal(m.items.length, 2);
  assert.match(m.notes[0], /^A lawyer should decide/);
  assert.equal(teaser(m), "Motion to suppress evidence · Discovery: get the prosecution's evidence");
});

test("citation lists move to Laws cited (no citation is lost) and merge with server titles", () => {
  const a = structureAnswer(ANSWER, [{ citation: "O.C.G.A. § 17-5-30 (text as of 2022 edition)", title: "Motion to suppress evidence illegally seized" }]);
  const laws = a.sections.find((s) => s.kind === "laws")!;
  assert.deepEqual(laws.items.map((i) => i.head), ["O.C.G.A. § 17-5-30", "O.C.G.A. § 42-8-60", "O.C.G.A. § 17-5-21", "O.C.G.A. § 17-16-4"]);
  assert.equal(laws.items[0].detail, "Motion to suppress evidence illegally seized");
  const lessen = a.sections.find((s) => s.title === "Ways to lessen the outcome")!;
  assert.equal(lessen.items[0].head, "First Offender may apply if you have no prior felony.");
});

test("questions stay whole; help items split name and detail; note kept", () => {
  const a = structureAnswer(ANSWER);
  assert.deepEqual(a.sections.find((s) => s.kind === "questions")!.items.map((i) => i.head), ["Was the search of my car legal?", "Should we file a motion to suppress?"]);
  const help = a.sections.find((s) => s.kind === "help")!;
  assert.equal(help.items[0].head, "Public defender (Georgia Public Defender Council)");
  assert.equal(help.notes.length, 1);
  assert.equal(a.note, "Georgia Code text is from the 2022 edition.");
});

test("long multi-sentence bullets become one short item per sentence", () => {
  const a = structureAnswer("Short answer\nYes.\n\nHow it works in Georgia\n• One thing. Two thing. Three thing. Four thing.");
  assert.equal(a.sections[0].items.length, 4);
});

test("plain answers with no headings still render as a quick answer", () => {
  const a = structureAnswer("You can ask for a bond hearing. A judge decides.");
  assert.equal(a.quick, "You can ask for a bond hearing. A judge decides.");
  assert.equal(a.sections.length, 0);
});

test("helpers", () => {
  assert.equal(stripCitationLists("Bond (O.C.G.A. § 17-6-1) may help."), "Bond may help.");
  assert.equal(sentences("Under O.C.G.A. § 17-5-30, you can ask. Then wait.").length, 2);
  assert.equal(toItem("• Get a lawyer: call the public defender.", "info").head, "Get a lawyer");
});

const PLAN = `Your Defense Plan: DUI

Quick answer
Your strongest angle is the blood test. Ask for the license hearing right away.

How they'd build the case against you
• Likely charge: DUI (O.C.G.A. § 40-6-391).
• Impairment: They'd point to the blood test. They'd still need a reliable lab result.
• Weak spots: who drew the blood is unknown.

How to fight back
• Impairment: The State cannot establish impairment because the sample's handling is unproven. Challenge: chain of custody. Motion: Motion to suppress evidence.

Key deadlines
• Check your paperwork for the license deadline.

Questions to ask your lawyer
• Can the blood test be challenged?`;

test("Defense Plan: title line becomes a badge, new sections are tap-to-open with their own kinds", () => {
  const a = structureAnswer(PLAN);
  assert.equal(a.plan, "Your Defense Plan · DUI");
  assert.match(a.quick, /^Your strongest angle is the blood test\./);
  const titles = a.sections.map((s) => s.title);
  assert.deepEqual(titles.slice(0, 4), ["How they'd build the case against you", "How to fight back", "Key deadlines", "Questions to ask your lawyer"]);
  const caseSec = a.sections[0];
  assert.equal(caseSec.kind, "case");
  assert.deepEqual(caseSec.items[1], { head: "Impairment", detail: "They'd point to the blood test. They'd still need a reliable lab result." });
  const fight = a.sections[1];
  assert.equal(fight.kind, "fight");
  assert.deepEqual(fight.items[0], {
    head: "Impairment",
    detail: "The State cannot establish impairment because the sample's handling is unproven.",
    meta: "Challenge: chain of custody · Motion: Motion to suppress evidence",
  });
  assert.equal(a.sections[2].kind, "deadlines");
  assert.ok(a.laws.some((l) => l.citation === "O.C.G.A. § 40-6-391"));
});

test("A normal answer has no plan badge", () => {
  assert.equal(structureAnswer(ANSWER).plan, undefined);
});

test("hidden-issue questions become tappable items with a why line", () => {
  const a = structureAnswer(
    "Your Defense Plan: DUI\n\nQuick answer\nFight the stop.\n\nThings you may not know to ask\n" +
      "• Do I have to appeal my license suspension within 30 days? Why it matters: The ALS appeal is separate from the criminal case.\n\n" +
      "Questions to ask your lawyer\n• Can the stop be challenged?",
  );
  const s = a.sections.find((x) => x.kind === "ask");
  assert.ok(s);
  assert.equal(s!.title, "Things you may not know to ask");
  assert.equal(s!.items[0].head, "Do I have to appeal my license suspension within 30 days?");
  assert.equal(s!.items[0].detail, "Why it matters: The ALS appeal is separate from the criminal case.");
});
