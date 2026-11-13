/** One paper-reader / upload batch is at most 10 pages. Extra picks never wipe pages already chosen. */

export const MAX_PAGES_PER_BATCH = 10;

export type CapResult<T> = {
  pages: T[];
  added: number;
  dropped: number;
  message: string;
};

export function remaining(count: number, max = MAX_PAGES_PER_BATCH): number {
  return Math.max(0, max - Math.max(0, count));
}

export function canAddMore(count: number, max = MAX_PAGES_PER_BATCH): boolean {
  return remaining(count, max) > 0;
}

export function counterLabel(count: number, max = MAX_PAGES_PER_BATCH, lang: "en" | "es" = "en"): string {
  return lang === "es" ? `${count} de ${max}` : `${count} of ${max}`;
}

export function overflowMessage(added: number, dropped: number, existing: number, lang: "en" | "es" = "en"): string {
  if (dropped <= 0) return "";
  if (lang === "es") {
    if (added === 0) {
      return "Ya tiene 10 páginas en este lote. Envíelas primero y después puede agregar más páginas a este caso.";
    }
    return `Se pueden agregar 10 páginas a la vez. Guardé las primeras ${added} de esta selección y dejé las páginas que ya tenía.`;
  }
  if (added === 0) {
    return "You already have 10 pages in this batch. Send these first, then add more pages to this case.";
  }
  return `You can add 10 pages at a time. I kept the first ${added} of this selection and left your earlier pages in place.`;
}

/** Append incoming pages up to the remaining slots. Never clears `existing`. */
export function capIncoming<T>(existing: T[], incoming: T[], max = MAX_PAGES_PER_BATCH, lang: "en" | "es" = "en"): CapResult<T> {
  const room = remaining(existing.length, max);
  const keptIncoming = incoming.slice(0, room);
  const dropped = Math.max(0, incoming.length - keptIncoming.length);
  return {
    pages: existing.concat(keptIncoming),
    added: keptIncoming.length,
    dropped,
    message: overflowMessage(keptIncoming.length, dropped, existing.length, lang),
  };
}
