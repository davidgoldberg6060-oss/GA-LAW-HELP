import { FormEvent, useState } from "react";
import { CATEGORIES, type FeedbackCategory, sendFeedback, validateFeedback } from "./usage";

type Props = { screen?: string; onDone?: () => void };

export default function FeedbackForm({ screen, onDone }: Props) {
  const [rating, setRating] = useState<number | null>(null);
  const [category, setCategory] = useState<FeedbackCategory>("idea");
  const [comment, setComment] = useState("");
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [sent, setSent] = useState(false);

  async function submit(e?: FormEvent) {
    e?.preventDefault();
    const payload = { rating, category, comment, contactEmail: email, screen };
    const error = validateFeedback(payload);
    if (error) { setNotice(error); return; }
    setBusy(true);
    setNotice("");
    try {
      const message = await sendFeedback(payload);
      setSent(true);
      setNotice(message);
      onDone?.();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Feedback could not be sent.");
    } finally {
      setBusy(false);
    }
  }

  if (sent) {
    return (
      <div className="feedbackForm">
        <h2>Help us improve</h2>
        <p>{notice || "Thank you. Your feedback helps us improve STANDALONE ASSISTANT."}</p>
      </div>
    );
  }

  return (
    <form className="feedbackForm" onSubmit={submit}>
      <h2>Help us improve</h2>
      <p>Tell us about the app itself — a bug, the design, something missing, or a slow spot. Legal questions still go to AI Help.</p>
      <fieldset>
        <legend>How is the app overall? (optional)</legend>
        <div className="starRow" role="radiogroup" aria-label="App rating">
          {[1, 2, 3, 4, 5].map((n) => (
            <button type="button" key={n} className={rating != null && rating >= n ? "star on" : "star"} aria-label={n + " star" + (n === 1 ? "" : "s")} aria-pressed={rating === n} onClick={() => setRating(n)}>★</button>
          ))}
          {rating != null && <button type="button" className="starClear" onClick={() => setRating(null)}>Clear</button>}
        </div>
      </fieldset>
      <label>
        What's this about?
        <select value={category} onChange={(e) => setCategory(e.target.value as FeedbackCategory)}>
          {CATEGORIES.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
        </select>
      </label>
      <label>
        Your feedback
        <textarea rows={5} maxLength={2000} value={comment} onChange={(e) => setComment(e.target.value)} placeholder="What could be better?" />
      </label>
      <label>
        Email if you want a reply (optional)
        <input type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
      </label>
      {notice && <p className="chatNotice">{notice}</p>}
      <button type="submit" className="feedbackSend" disabled={busy}>{busy ? "Sending…" : "Send feedback"}</button>
    </form>
  );
}
