import assert from "node:assert/strict";
import test from "node:test";
import { languageInstruction, t } from "../src/i18n.ts";

test("Spanish instruction keeps headings and citations in their original form", () => {
  const inst = languageInstruction("es");
  assert.match(inst, /Respond in Spanish/);
  assert.match(inst, /Quick answer/);
  assert.match(inst, /O\.C\.G\.A\./);
  assert.match(inst, /no asesoramiento jurídico/);
  assert.equal(t("notice", "es"), "Esto es información legal, no asesoramiento jurídico.");
  assert.match(t("translationNotice", "es"), /documento original en inglés es el que cuenta/);
  assert.equal(t("butler", "en"), "The Butler");
  assert.equal(t("nanny", "en"), "The Nanny");
});
