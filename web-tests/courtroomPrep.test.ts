import assert from "node:assert/strict";
import test from "node:test";
import { prepFor, prepText } from "../src/courtroomPrep.ts";

test("general courtroom prep has day-before and day-of lists", () => {
  const pack = prepFor("", "en");
  assert.equal(pack.sections[0].id, "day_before");
  assert.equal(pack.sections[1].id, "day_of");
  const text = prepText(pack);
  assert.match(text, /Your Honor/);
  assert.match(text, /30 to 45 minutes/);
  assert.match(text, /not legal advice/);
});

test("DUI prep is tailored", () => {
  const pack = prepFor("dui", "en");
  assert.equal(pack.caseType, "dui");
  assert.match(prepText(pack), /implied-consent|ALS|license/i);
});

test("Spanish prep keeps Your Honor and the Spanish disclaimer", () => {
  const pack = prepFor("traffic", "es");
  assert.equal(pack.language, "es");
  assert.match(pack.notice, /no asesoramiento jurídico/);
  assert.ok(pack.sections.some((s) => s.title.includes("El día antes")));
  assert.match(prepText(pack), /Your Honor/);
});
