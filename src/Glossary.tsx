import { useState } from 'react';
import { glossaryFor } from './glossary';
export function Glossary({ text }: { text: string }) {
  const [open, setOpen] = useState(false);
  const terms = glossaryFor(text);
  if (!terms.length) return null;
  return <div className="glossary"><button type="button" className="mcRun" onClick={() => setOpen(!open)}>Legal terms explained ({terms.length}) {open ? '▲' : '▼'}</button>
    {open && <dl>{terms.map(([t, d]) => <div key={t}><dt><b>{t}</b></dt><dd>{d}</dd></div>)}</dl>}</div>;
}
