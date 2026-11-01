import {useState} from 'react';

/** One law, rule, regulation or case that can be expanded inline to its full stored text. */
export type LawItem = {citation: string; title?: string | null; id?: number | null; source_url?: string | null};
type Loaded = {citation: string; title?: string; text: string; note?: string | null; source_url?: string | null};

const cache = new Map<string, Loaded | null>();
const clean = (c: string) => c.replace(/\s*\(text as of[^)]*\)/, '').trim();

/** Paragraph breaks before (a)/(1)/(A) markers with indents by level. */
export function lawParagraphs(text: string): {level: number; text: string}[] {
  const t = text.replace(/\r/g, '').replace(/[ \t]+/g, ' ')
    .replace(/([.;:])\s+(?=\((?:[a-z]{1,2}|\d{1,3}|[A-Z]{1,2})\)\s)/g, '$1\n');
  return t.split(/\n+/).map((p) => p.trim()).filter(Boolean).map((p) => ({
    level: /^\(\d{1,3}\)\s/.test(p) ? 1 : /^\([A-Z]{1,2}\)\s/.test(p) ? 2 : 0,
    text: p,
  }));
}

export function LawAccordion({api, items}: {api: string; items: LawItem[]}) {
  const [open, setOpen] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [, force] = useState(0);
  if (!items.length) return null;
  async function toggle(item: LawItem) {
    const key = clean(item.citation);
    if (open === key) { setOpen(null); return; }
    setOpen(key);
    if (cache.has(key)) return;
    setLoading(true);
    try {
      const q = '?citation=' + encodeURIComponent(key) + (item.id ? '&id=' + item.id : '');
      const r = await fetch(api + '/public/georgia-laws/law' + q);
      cache.set(key, r.ok ? await r.json() : null);
    } catch { cache.set(key, null); }
    setLoading(false); force((n) => n + 1);
  }
  return (
    <ul className="lawAccordion">
      {items.map((item) => {
        const key = clean(item.citation); const isOpen = open === key; const law = cache.get(key);
        const src = (law?.source_url || item.source_url || '').startsWith('https://') ? (law?.source_url || item.source_url) : null;
        return (
          <li key={key} className={isOpen ? 'open' : ''}>
            <button type="button" aria-expanded={isOpen} onClick={() => toggle(item)}>
              <b>{key}</b>{item.title ? <span> — {item.title}</span> : null}<i aria-hidden>{isOpen ? '▴' : '▾'}</i>
            </button>
            {isOpen && (
              <div className="lawText" role="region" aria-label={'Full text of ' + key}>
                {loading && !cache.has(key) ? <p className="lawLoading"><span className="lawSpinner" />Loading full text…</p>
                  : law ? <>
                      {law.title && <h4>{law.title}</h4>}
                      <div className="lawScroll">{lawParagraphs(law.text || 'No text is stored for this item yet.').map((p, i) => <p key={i} style={{marginLeft: p.level * 18}}>{p.text}</p>)}</div>
                      {law.note && <small>Note: {law.note}</small>}
                    </>
                  : <p>The full text of {key} isn't in GA.LAW.HELP yet.</p>}
                {src && <a className="lawSource" href={src} target="_blank" rel="noreferrer">View official source</a>}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
