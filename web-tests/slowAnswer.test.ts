import { test } from "node:test";
import assert from "node:assert/strict";
import { AI_TIMEOUT_MS, SLOW_MESSAGE, OFFLINE_MESSAGE, BUSY_MESSAGE, fetchWithTimeout, friendlyFetchError, isRetryable } from "../src/slowAnswer.ts";

test("a slow answer becomes a friendly retryable message, not a raw failure", async () => {
  const hang: typeof fetch = (_u, init) => new Promise((_r, reject) => {
    init?.signal?.addEventListener("abort", () => reject(Object.assign(new Error("aborted"), { name: "AbortError" })));
  });
  await assert.rejects(fetchWithTimeout("https://x/test", {}, 20, hang), (e: unknown) => isRetryable(e) && (e as Error).message === SLOW_MESSAGE);
});

test("offline and gateway errors map to retryable messages", () => {
  assert.equal(friendlyFetchError(new TypeError("Failed to fetch"))?.message, OFFLINE_MESSAGE);
  assert.equal(friendlyFetchError(null, 504)?.message, SLOW_MESSAGE);
  assert.equal(friendlyFetchError(null, 503)?.message, BUSY_MESSAGE);
  assert.equal(friendlyFetchError(null, 400), null);
  assert.equal(friendlyFetchError(new Error("other")), null);
});

test("the browser waits longer than the server's answer budget", async () => {
  assert.ok(AI_TIMEOUT_MS >= 60_000);
  const ok: typeof fetch = async () => new Response("{}");
  assert.equal((await fetchWithTimeout("https://x", {}, 1000, ok)).status, 200);
});
