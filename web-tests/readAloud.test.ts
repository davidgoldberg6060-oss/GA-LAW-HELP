import assert from "node:assert/strict";
import test from "node:test";
import { spokenText, VOICES } from "../src/readAloud.ts";

test("spoken text keeps legal wording and always adds the notice", () => {
  const body = "Challenge the stop. See O.C.G.A. § 40-6-391.";
  const butler = spokenText(body, "butler", "en");
  assert.ok(butler.startsWith(VOICES.butler.introEn));
  assert.match(butler, /Challenge the stop/);
  assert.match(butler, /O\.C\.G\.A\. § 40-6-391/);
  assert.match(butler, /not legal advice/);
  const nanny = spokenText(body, "nanny", "en");
  assert.ok(nanny.startsWith(VOICES.nanny.introEn));
  assert.notEqual(VOICES.butler.locale, VOICES.nanny.locale);
  assert.ok(VOICES.butler.rate < VOICES.nanny.rate);
  const spanish = spokenText("Impugne la parada.", "nanny", "es");
  assert.ok(spanish.startsWith(VOICES.nanny.introEs));
  assert.match(spanish, /no asesoramiento jurídico/);
  const catalog = (VOICES.butler.description || "") + JSON.stringify(VOICES);
  // descriptions live in i18n, but the module itself must not name real people or trademarks
  for (const banned of ["Alfred", "Batman", "Drescher", "Fran "]) {
    assert.equal(catalog.includes(banned), false);
  }
});
