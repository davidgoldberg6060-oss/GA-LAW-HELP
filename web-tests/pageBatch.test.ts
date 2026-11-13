import assert from "node:assert/strict";
import { test } from "node:test";
import { MAX_PAGES_PER_BATCH, canAddMore, capIncoming, counterLabel, remaining } from "../src/pageBatch.ts";

test("counter starts at 0 of 10 and fills up", () => {
  assert.equal(MAX_PAGES_PER_BATCH, 10);
  assert.equal(counterLabel(0), "0 of 10");
  assert.equal(counterLabel(3, 10, "es"), "3 de 10");
  assert.equal(remaining(0), 10);
  assert.equal(remaining(7), 3);
  assert.equal(remaining(10), 0);
  assert.equal(canAddMore(10), false);
});

test("a later pick is capped to remaining slots and never wipes earlier pages", () => {
  const first = capIncoming(["a", "b", "c"], ["d", "e"]);
  assert.deepEqual(first.pages, ["a", "b", "c", "d", "e"]);
  assert.equal(first.dropped, 0);

  const overflow = capIncoming(["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"], ["n1", "n2", "n3", "n4"]);
  assert.deepEqual(overflow.pages, ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "n1", "n2"]);
  assert.equal(overflow.added, 2);
  assert.equal(overflow.dropped, 2);
  assert.match(overflow.message, /kept the first 2/i);
  assert.ok(overflow.pages.slice(0, 8).every((p, i) => p === `p${i + 1}`));
});

test("selecting more than 10 at once keeps the first 10 and does not discard the batch", () => {
  const incoming = Array.from({ length: 15 }, (_, i) => `f${i + 1}`);
  const result = capIncoming([], incoming);
  assert.equal(result.pages.length, 10);
  assert.deepEqual(result.pages, incoming.slice(0, 10));
  assert.equal(result.dropped, 5);
  assert.match(result.message, /10 pages at a time/i);
});

test("a full batch rejects new files without clearing the 10 already chosen", () => {
  const existing = Array.from({ length: 10 }, (_, i) => `e${i + 1}`);
  const result = capIncoming(existing, ["extra1", "extra2"]);
  assert.deepEqual(result.pages, existing);
  assert.equal(result.added, 0);
  assert.equal(result.dropped, 2);
  assert.match(result.message, /already have 10/i);
});
