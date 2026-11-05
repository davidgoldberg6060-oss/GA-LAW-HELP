import { useMemo, useState, useRef, useCallback, TouchEvent } from 'react';
import data from './funnyGeorgia.json';
import { LoadingPhrase, LOADING } from './LoadingPhrase';
import { lawParagraphs } from './LawAccordion';

type Law = {
  title: string; summary: string; citation: string; jurisdiction: string;
  category: string; source_url: string; status: string; full_text?: string;
};
type Case = {
  name: string; court: string; year: number; citation: string;
  summary: string; source_url: string; full_text?: string;
};
type Loaded = { title?: string; text: string; note?: string | null };

const laws = data.laws as Law[];
const cases = data.cases as Case[];
const CATEGORIES = (data as { categories?: string[] }).categories
  ?? ['State symbols', 'Animals', 'Food & drink', 'Cars & roads', 'Weird local rules', 'Funny court cases'];
const DEFAULT_API = 'https://api-production-60cc.up.railway.app';
const cache = new Map<string, Loaded | null>();

/** Funny Laws — swipeable card deck (default) + list; Open source / flip uses stored full_text. */
export default function FunnyGeorgia({ api = DEFAULT_API }: { api?: string }) {
  const [tab, setTab] = useState<'laws' | 'cases'>('laws');
  const [q, setQ] = useState('');
  const [category, setCategory] = useState('All');
  const [mode, setMode] = useState<'cards' | 'list'>('cards');
  const [open, setOpen] = useState<string | null>(null);
  const [state, setState] = useState<'idle' | 'loading' | 'error'>('idle');
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [order, setOrder] = useState<number[] | null>(null);
  const startX = useRef(0);
  const dragging = useRef(false);

  const m = (...f: string[]) => !q.trim() || f.some((x) => x.toLowerCase().includes(q.trim().toLowerCase()));
  const shownLaws = useMemo(() => {
    const base = laws.filter((l) => m(l.title, l.summary, l.citation, l.category, l.jurisdiction));
    if (category === 'All') return base;
    if (category === 'Funny court cases') return [];
    return base.filter((l) => l.category === category);
  }, [q, category]);
  const shownCases = useMemo(() => {
    const base = cases.filter((c) => m(c.name, c.summary, c.court, c.citation));
    return category === 'All' || category === 'Funny court cases' ? base : [];
  }, [q, category]);

  const deck = tab === 'cases' || category === 'Funny court cases' ? shownCases : shownLaws;
  const deckOrder = order && order.length === deck.length ? order : deck.map((_, i) => i);
  const cur = deck.length ? deck[deckOrder[Math.min(index, deckOrder.length - 1)]] : null;

  function resetDeck() { setOrder(null); setIndex(0); setFlipped(false); setOpen(null); }

  async function load(cite: string) {
    setState('loading');
    try {
      const r = await fetch(api + '/public/georgia-laws/law?citation=' + encodeURIComponent(cite));
      if (r.ok) cache.set(cite, await r.json());
      else if (r.status === 404) cache.set(cite, null);
      else throw new Error(String(r.status));
      setState('idle');
    } catch { setState('error'); }
  }

  function storedText(cite: string, fallback?: string): Loaded | null | undefined {
    if (cache.has(cite)) return cache.get(cite);
    const law = laws.find((l) => l.citation === cite);
    if (law?.full_text) {
      const loaded = { title: law.title, text: law.full_text, note: law.status };
      cache.set(cite, loaded); return loaded;
    }
    const c = cases.find((x) => x.citation === cite);
    if (c?.full_text) {
      const loaded = { title: c.name, text: c.full_text };
      cache.set(cite, loaded); return loaded;
    }
    if (fallback) return { text: fallback };
    return undefined;
  }

  function toggle(cite: string) {
    if (open === cite) { setOpen(null); return; }
    setOpen(cite);
    if (storedText(cite) === undefined) load(cite); else setState('idle');
  }

  function panel(cite: string, fallback?: string) {
    if (open !== cite) return null;
    const law = storedText(cite, fallback);
    return (
      <div className="lawText" role="region" aria-label={'Full text of ' + cite}>
        {law === undefined && state === 'loading' ? <LoadingPhrase lines={LOADING.laws} label="Loading full text" />
          : law === undefined && state === 'error' ? <p>Couldn't load the full text. <button type="button" onClick={() => load(cite)}>Retry</button></p>
          : law ? <>{law.title && <h4>{law.title}</h4>}<div className="lawScroll">{lawParagraphs(law.text || 'No text is stored for this item yet.').map((p, i) => <p key={i} style={{ marginLeft: p.level * 18 }}>{p.text}</p>)}</div>{law.note && <small>Note: {law.note}</small>}</>
          : <p>The full text of {cite} isn't stored in STANDALONE ASSISTANT yet, so there's nothing to show here.</p>}
      </div>
    );
  }

  const btn = (cite: string) => (
    <button type="button" className="funnyToggle" aria-expanded={open === cite} onClick={() => toggle(cite)}>
      {open === cite ? 'Close source ▴' : 'Open source ▾'}
    </button>
  );

  const onTouchStart = (e: TouchEvent) => { startX.current = e.touches[0].clientX; dragging.current = false; };
  const onTouchEnd = (e: TouchEvent) => {
    const dx = e.changedTouches[0].clientX - startX.current;
    if (Math.abs(dx) > 60 && deck.length) {
      const dir = dx < 0 ? 1 : -1;
      setIndex((i) => (i + dir + deck.length) % deck.length);
      setFlipped(false);
    }
  };

  const share = useCallback(() => {
    if (!cur) return;
    const text = 'citation' in cur && 'title' in cur && 'jurisdiction' in cur
      ? `${(cur as Law).title}\n\n${(cur as Law).summary}\n\n${(cur as Law).citation} • ${(cur as Law).jurisdiction}\n\nFrom STANDALONE ASSISTANT`
      : `${(cur as Case).name} (${(cur as Case).year})\n\n${(cur as Case).summary}\n\n${(cur as Case).citation}\n\nFrom STANDALONE ASSISTANT`;
    if (navigator.share) navigator.share({ text }).catch(() => {});
    else { navigator.clipboard?.writeText(text); }
  }, [cur]);

  return (
    <div className="funnyBrowser">
      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === 'laws'} className={tab === 'laws' ? 'active' : ''} onClick={() => { setTab('laws'); if (category === 'Funny court cases') setCategory('All'); resetDeck(); }}>Funny Laws ({laws.length})</button>
        <button role="tab" aria-selected={tab === 'cases'} className={tab === 'cases' ? 'active' : ''} onClick={() => { setTab('cases'); setCategory('Funny court cases'); resetDeck(); }}>Funny Cases ({cases.length})</button>
      </div>
      <div className="funnyChips" role="toolbar" aria-label="Categories">
        {['All', ...CATEGORIES].filter((v, i, a) => a.indexOf(v) === i).map((cat) => (
          <button key={cat} type="button" className={category === cat ? 'on' : ''} onClick={() => {
            setCategory(cat); setTab(cat === 'Funny court cases' ? 'cases' : 'laws'); resetDeck();
          }}>{cat}</button>
        ))}
      </div>
      <div className="funnyMode">
        <button type="button" className={mode === 'cards' ? 'on' : ''} onClick={() => setMode('cards')}>Cards</button>
        <button type="button" className={mode === 'list' ? 'on' : ''} onClick={() => setMode('list')}>List</button>
      </div>
      <input className="funnySearch" aria-label="Search funny laws and cases" placeholder="Search funny laws and cases…" value={q} onChange={(e) => { setQ(e.target.value); resetDeck(); }} />

      {mode === 'cards' ? (
        <div className="funnyDeck">
          <p className="funnyProgress">{deck.length ? `${Math.min(index, deck.length - 1) + 1} / ${deck.length}` : '0 / 0'}</p>
          {cur ? (
            <article className="funnyCard" onTouchStart={onTouchStart} onTouchEnd={onTouchEnd} onClick={() => setFlipped((f) => !f)}>
              {'title' in cur ? (
                <>
                  <small>{(cur as Law).category}</small>
                  <h3>{(cur as Law).title}</h3>
                  {!flipped ? (
                    <>
                      <p>{(cur as Law).summary}</p>
                      <p><b>{(cur as Law).citation}</b> · {(cur as Law).jurisdiction}</p>
                      <p className="hint">Tap to read the full law · swipe for next</p>
                    </>
                  ) : (
                    <div className="lawScroll">{lawParagraphs((cur as Law).full_text || 'No text stored.').map((p, i) => <p key={i} style={{ marginLeft: p.level * 18 }}>{p.text}</p>)}</div>
                  )}
                </>
              ) : (
                <>
                  <small>{(cur as Case).court} · {(cur as Case).year}</small>
                  <h3>{(cur as Case).name}</h3>
                  {!flipped ? (
                    <>
                      <p>{(cur as Case).summary}</p>
                      <p><b>{(cur as Case).citation}</b></p>
                      <p className="hint">Tap to expand · swipe for next</p>
                    </>
                  ) : (
                    <div className="lawScroll">{lawParagraphs((cur as Case).full_text || (cur as Case).summary).map((p, i) => <p key={i} style={{ marginLeft: p.level * 18 }}>{p.text}</p>)}</div>
                  )}
                </>
              )}
            </article>
          ) : <p>No matches. Try another category or word.</p>}
          <div className="funnyDeckActions">
            <button type="button" onClick={() => { if (deck.length) { setIndex((i) => (i - 1 + deck.length) % deck.length); setFlipped(false); } }}>⟵ Prev</button>
            <button type="button" onClick={() => { const o = deck.map((_, i) => i); for (let i = o.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [o[i], o[j]] = [o[j], o[i]]; } setOrder(o); setIndex(0); setFlipped(false); }}>Shuffle</button>
            <button type="button" onClick={share}>Share</button>
            <button type="button" onClick={() => { if (deck.length) { setIndex((i) => (i + 1) % deck.length); setFlipped(false); } }}>Next ⟶</button>
          </div>
        </div>
      ) : (
        <div className="funGrid">
          {tab === 'laws' || category !== 'Funny court cases'
            ? shownLaws.map((l) => (
              <article key={l.citation + l.title}>
                <small>{l.category}</small>
                <h3>{l.title}</h3>
                <p>{l.summary}</p>
                <p><b>{l.citation}</b> · {l.jurisdiction}</p>
                {!l.status.startsWith('In the current Georgia Code') && <p>⚠ Status: {l.status}</p>}
                {btn(l.citation)}{panel(l.citation, l.full_text)}
              </article>
            ))
            : shownCases.map((c) => (
              <article key={c.name}>
                <small>{c.court} · {c.year}</small>
                <h3>{c.name}</h3>
                <p>{c.summary}</p>
                <p><b>{c.citation}</b></p>
                {btn(c.citation)}{panel(c.citation, c.full_text || c.summary)}
              </article>
            ))}
          {(tab === 'laws' ? shownLaws : shownCases).length === 0 && <p>No matches. Try another word.</p>}
        </div>
      )}
      <p className="funnyNote">{data.note}</p>
    </div>
  );
}
