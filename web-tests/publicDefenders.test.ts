import assert from "node:assert/strict";
import test from "node:test";
import { OFFICE_COUNT, searchOffices, barDirectory, outcomeNote } from "../src/publicDefenderOffices.ts";
import { detectsPdProblem, guide, guideText } from "../src/publicDefenderProblems.ts";

test("official directory has every GPDC circuit and does not invent missing names", () => {
  assert.equal(OFFICE_COUNT, 51);
  const fulton = searchOffices("Fulton");
  assert.equal(fulton.length, 1);
  assert.equal(fulton[0].circuit, "Atlanta Circuit");
  const gwinnett = searchOffices("Gwinnett");
  assert.equal(gwinnett[0].opt_out, true);
  assert.equal(gwinnett[0].defender, null);
  const bar = barDirectory("en");
  assert.equal(bar.url, "https://www.gabar.org/member-directory/");
  assert.match(bar.explainer, /does not show win\/loss/i);
  assert.match(outcomeNote("en"), /does not publish an official per-attorney/);
});

test("problem guide detects distrust and keeps verified habeas deadlines", () => {
  assert.equal(detectsPdProblem("my public defender is working with the state"), true);
  assert.equal(detectsPdProblem("how do I get a public defender"), false);
  const pack = guide("en");
  const text = guideText(pack);
  assert.match(text, /O\.C\.G\.A\. § 9-14-42/);
  assert.match(text, /4 years/);
  assert.match(text, /1 year/);
  assert.match(text, /180 days/);
  assert.equal(text.includes("Georgia Public Defender Act"), false);
  assert.ok(pack.templates.some((t) => t.motionKey === "discharge_appointed_counsel"));
  const es = guide("es");
  assert.match(guideText(es), /no asesoramiento jurídico/);
});
