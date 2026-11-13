import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { CATEGORIES, PROMPT_AFTER_OPENS, PROMPT_GAP_MS, shouldPrompt, validateFeedback } from "../src/usage.ts";

describe("shouldPrompt", () => {
  const now = 1_000_000_000_000;
  it("waits until a few uses", () => {
    assert.equal(shouldPrompt(PROMPT_AFTER_OPENS - 1, null, null, now), false);
    assert.equal(shouldPrompt(PROMPT_AFTER_OPENS, null, null, now), true);
  });
  it("does not repeat within two weeks of a prompt or a sent rating", () => {
    assert.equal(shouldPrompt(10, now - PROMPT_GAP_MS + 1000, null, now), false);
    assert.equal(shouldPrompt(10, null, now - PROMPT_GAP_MS + 1000, now), false);
    assert.equal(shouldPrompt(10, now - PROMPT_GAP_MS - 1000, null, now), true);
  });
});

describe("validateFeedback", () => {
  it("requires a rating or a comment, and a valid optional email", () => {
    assert.equal(validateFeedback({ rating: null, category: "idea", comment: "", contactEmail: "" }) != null, true);
    assert.equal(validateFeedback({ rating: 4, category: "idea", comment: "", contactEmail: "" }), null);
    assert.equal(validateFeedback({ rating: null, category: "bug", comment: "It crashed.", contactEmail: "" }), null);
    assert.equal(validateFeedback({ rating: 5, category: "other", comment: "ok", contactEmail: "bad" }) != null, true);
    assert.equal(validateFeedback({ rating: 5, category: "other", comment: "ok", contactEmail: "a@b.co" }), null);
  });
  it("lists the five app-feedback categories", () => {
    assert.deepEqual(CATEGORIES.map((c) => c.id), ["bug", "design", "idea", "slow", "other"]);
  });
});
