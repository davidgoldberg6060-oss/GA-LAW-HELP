/** Slow AI answers: give up after a fixed wait and show a friendly, retryable message instead of a raw failure. */

/** The server finishes AI answers within ~50 s; the browser waits a little longer for slow networks. */
export const AI_TIMEOUT_MS = 75_000;
/** After this long, the typing bubble says the answer is still coming. */
export const STILL_WORKING_MS = 15_000;

export const SLOW_MESSAGE = "STANDALONE ASSISTANT is taking longer than usual to answer. Your question wasn’t lost — tap Retry to try again.";
export const OFFLINE_MESSAGE = "Couldn’t reach STANDALONE ASSISTANT. Check your internet connection, then tap Retry.";
export const BUSY_MESSAGE = "STANDALONE ASSISTANT is busy right now. Please tap Retry in a moment.";

export class SlowAnswerError extends Error {
  readonly retryable = true;
  constructor(message: string) {
    super(message);
    this.name = "SlowAnswerError";
  }
}

/** Gateway timeouts and overloads are worth retrying; the user did nothing wrong. */
export function isRetryableStatus(status: number): boolean {
  return status === 408 || status === 429 || status === 502 || status === 503 || status === 504;
}

/** Turn a fetch failure (timeout, offline, gateway error) into a friendly retryable error, or null when it's something else. */
export function friendlyFetchError(error: unknown, status?: number): SlowAnswerError | null {
  if (status !== undefined) {
    if (status === 504 || status === 408) return new SlowAnswerError(SLOW_MESSAGE);
    if (isRetryableStatus(status)) return new SlowAnswerError(BUSY_MESSAGE);
    return null;
  }
  const name = (error as { name?: string } | null)?.name;
  if (name === "AbortError" || name === "TimeoutError") return new SlowAnswerError(SLOW_MESSAGE);
  if (error instanceof TypeError) return new SlowAnswerError(OFFLINE_MESSAGE);
  return null;
}

export function isRetryable(error: unknown): boolean {
  return error instanceof SlowAnswerError || (error as { retryable?: boolean } | null)?.retryable === true;
}

/** fetch() that aborts after `ms` (keeping any caller signal) and maps failures to friendly errors. */
export async function fetchWithTimeout(url: string, options: RequestInit = {}, ms = AI_TIMEOUT_MS, fetchImpl: typeof fetch = fetch): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  const outer = options.signal;
  if (outer) {
    if (outer.aborted) controller.abort();
    else outer.addEventListener("abort", () => controller.abort(), { once: true });
  }
  try {
    return await fetchImpl(url, { ...options, signal: controller.signal });
  } catch (error) {
    if (outer?.aborted) throw error; // the caller cancelled on purpose
    throw friendlyFetchError(error) ?? error;
  } finally {
    clearTimeout(timer);
  }
}
