import { HelpLovedOne } from './HelpLovedOne';
import { Glossary } from './Glossary';
import {useEffect, useState} from 'react';
import {LawAccordion} from './LawAccordion';

/** 'My Case' hub (web): case type -> criminal stage -> next steps, deadlines, motions with stored Georgia law. */
export const STAGES: [string, string][] = [
  ['arrested', 'Arrested / bond'], ['pretrial', 'Charged / pretrial'], ['plea', 'Plea offer'], ['trial', 'Trial'],
  ['sentenced', 'Sentenced'], ['appeal', 'Appeal'], ['prison', 'Serving a sentence – get out or reduce time'],
  ['probation', 'Probation / parole'], ['record', 'Clear a record'],
];
const DATE_FIELDS: Record<string, [string, string][]> = {
  arrested: [['arrest_date', 'Arrest date']],
  pretrial: [['arraignment_date', 'Arraignment date']], plea: [['arraignment_date', 'Arraignment date']], trial: [['arraignment_date', 'Arraignment date']],
  sentenced: [['sentence_date', 'Sentence date'], ['final_date', 'Conviction final (optional)']],
  appeal: [['sentence_date', 'Sentence date'], ['final_date', 'Conviction final (optional)']],
  prison: [['sentence_date', 'Sentence date'], ['final_date', 'Conviction final (optional)']],
  probation: [['sentence_date', 'Sentence date']], record: [],
};
type Cite = {citation: string; title?: string; id?: number};
type Guide = {stage_label: string; next_steps: string[]; family_tips: string[]; timeline: {title: string; due: string; label: string; passed: boolean}[];
  options: {key: string; title: string; what: string; deadline?: string | null; where?: string | null; highlight: boolean; deadline_status?: {label: string; passed: boolean} | null; citations: Cite[]}[];
  motions?: {key: string; title: string; goal_label: string; what: string; fits?: string | null; score: number; deadline?: string | null; deadline_status?: {label: string; passed: boolean; due: string} | null; citations: Cite[]; draftable: boolean}[];
  questions?: {id: string; q: string; options: string[]}[];
  laws_cited: Cite[]; resources: {title: string; url: string}[]; find_case?: {title: string; url: string}[]; disclaimer: string};
type Saved = {id: string; name: string; stage: string; details: Record<string, string>; saved_at: string};
const KEY = 'ga_my_cases';
const load = (): Saved[] => { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; } };

export function detectStageLabel(stage?: string | null) { return STAGES.find(([k]) => k === stage)?.[1]; }

export default function MyCase({api, onCivil, onAsk, initial}: {api: string; onCivil: () => void; onAsk: () => void; initial?: {stage: string; situation: string} | null}) {
  const [step, setStep] = useState<'hub' | 'stages' | 'form'>('hub');
  const [stage, setStage] = useState('');
  const [details, setDetails] = useState<Record<string, string>>({});
  const [guide, setGuide] = useState<Guide | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  const [saved, setSaved] = useState<Saved[]>(load);
  useEffect(() => { if (initial?.stage) { setStage(initial.stage); setDetails({situation: initial.situation}); setGuide(null); setStep('form'); } }, [initial]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  async function draftMotion(key: string, title: string) {
    const r = await fetch(api + '/public/motion-draft', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({key, details})});
    if (!r.ok) { setErr('Could not create the draft.'); return; }
    const d = await r.json();
    const w = window.open('', '_blank');
    if (w) { w.document.title = title; const pre = w.document.createElement('pre'); pre.style.whiteSpace = 'pre-wrap'; pre.style.font = '13px monospace'; pre.textContent = d.text; w.document.body.appendChild(pre); }
    const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([d.text], {type: 'text/plain'})); a.download = title.replace(/[^A-Za-z0-9]+/g, '_') + '.txt'; a.click();
  }
  async function run(st = stage, d = details, ans = answers) {
    setBusy(true); setErr(''); setGuide(null);
    try {
      const r = await fetch(api + '/public/case-guide', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({stage: st, details: d, answers: ans})});
      if (!r.ok) throw new Error('Could not load the guide. Please try again.');
      setGuide(await r.json());
    } catch (e) { setErr((e as Error).message); }
    setBusy(false);
  }
  function save() {
    const s: Saved = {id: String(Date.now()), name: (details.situation || detectStageLabel(stage) || 'Case').slice(0, 40), stage, details, saved_at: new Date().toLocaleDateString()};
    const next = [s, ...load()].slice(0, 20); localStorage.setItem(KEY, JSON.stringify(next)); setSaved(next);
  }
  function remove(id: string) { const next = load().filter((s) => s.id !== id); localStorage.setItem(KEY, JSON.stringify(next)); setSaved(next); }
  return (
    <section className="myCase" id="my-case">
      <div className="sectionTitle"><div><h2>My Case</h2><p>Step-by-step help through a whole case – yours or someone else's: what to do next, deadlines, and the Georgia laws that apply.</p></div></div>
      {step !== 'hub' && <button type="button" className="mcBack" onClick={() => setStep(step === 'form' ? 'stages' : 'hub')}>‹ Back</button>}
      {step === 'hub' && <>
        <h3>What kind of case?</h3>
        <div className="mcChoices">
          <button type="button" className="mcChoice gold" onClick={() => setStep('stages')}><b>Criminal ›</b><span>Arrest, charges, plea, trial, sentence, prison, probation, record</span></button>
          <button type="button" className="mcChoice" onClick={onCivil}><b>Civil ›</b><span>Landlord, deposit, debt, money owed, family, contracts</span></button>
          <button type="button" className="mcChoice" onClick={onAsk}><b>Not sure – just ask ›</b><span>Describe it in your own words</span></button>
        </div>
        {saved.length > 0 && <><h3>Saved cases</h3><div className="mcChoices">{saved.map((s) => <div key={s.id} className="mcSaved">
          <button type="button" className="mcChoice" onClick={() => { setStage(s.stage); setDetails(s.details); setStep('form'); run(s.stage, s.details); }}><b>{s.name} ›</b><span>{detectStageLabel(s.stage)} · saved {s.saved_at}</span></button>
          <button type="button" className="mcDelete" aria-label={'Delete ' + s.name} onClick={() => remove(s.id)}>Delete</button></div>)}</div>
          <small>Saved in this browser only.</small></>}
      </>}
      {step === 'stages' && <>
        <h3>What stage is the case in?</h3>
        <div className="mcChoices">{STAGES.map(([k, l]) => <button key={k} type="button" className={'mcChoice' + (k === 'prison' ? ' gold' : '')} onClick={() => { setStage(k); setDetails({}); setGuide(null); setStep('form'); }}><b>{l} ›</b></button>)}</div>
      </>}
      {step === 'form' && <>
        <h3>{detectStageLabel(stage)}</h3>
        <textarea rows={4} placeholder="Describe the case: charges, court and county, sentence, plea or trial, time served, any issues (lawyer, evidence, sentence)…" value={details.situation || ''} onChange={(e) => setDetails({...details, situation: e.target.value})}/>
        {(DATE_FIELDS[stage] || []).map(([k, l]) => <label key={k} className="mcDate">{l}<input type="date" value={details[k] || ''} onChange={(e) => setDetails({...details, [k]: e.target.value})}/></label>)}
        <button type="button" className="mcRun" disabled={busy} onClick={() => run()}>{busy ? 'Finding next steps…' : 'Show next steps'}</button>
        {err && <p className="mcErr">{err}</p>}
        {guide && <div className="mcResult">
          <h3>Next steps</h3><ul>{guide.next_steps.map((s) => <li key={s}>{s}</li>)}</ul>
          {guide.family_tips.length > 0 && <><h4>Family and friends can help</h4><ul>{guide.family_tips.map((s) => <li key={s}>{s}</li>)}</ul></>}
          {(guide.questions || []).length > 0 && <div className="mcOption"><h4>A few quick questions</h4>{guide.questions!.map((q) => <p key={q.id}>{q.q} {q.options.map((o) => <button key={o} type="button" className="mcChip" onClick={() => { const a = {...answers, [q.id]: o}; setAnswers(a); run(stage, details, a); }}>{o}</button>)}</p>)}</div>}
          {(guide.motions || []).length > 0 && <><h3>Motions that could help</h3>{guide.motions!.map((m, i) => <article key={m.key} className={'mcOption' + (m.score >= 3 ? ' gold' : '')}>
            <small className="mcMatch">{m.goal_label}{m.score >= 3 ? ' · STRONG FIT' : ''}</small><h4>{i + 1}. {m.title}</h4><p>{m.what}</p>
            {m.fits && <p className="mcWhere">Why it fits: {m.fits}</p>}
            {m.deadline && <p className={'mcDeadline' + (m.deadline_status?.passed ? ' passed' : '')}>⏰ Deadline: {m.deadline}{m.deadline_status ? ` (${m.deadline_status.due}: ${m.deadline_status.label})` : ''}</p>}
            <LawAccordion api={api} items={m.citations}/>
            {m.draftable && <button type="button" className="mcRun" onClick={() => draftMotion(m.key, m.title)}>Draft this motion</button>}
          </article>)}<small>Drafts are fill-in-the-blank templates to review with a lawyer. They never include case law.</small></>}
          {guide.timeline.length > 0 && <div className="mcTimeline"><h3>Deadline timeline</h3>{guide.timeline.map((t) => <p key={t.title}><b>{t.due}</b> · {t.title} <span className={t.passed ? 'passed' : ''}>{t.label}</span></p>)}<small>Estimates from the dates entered. Confirm every deadline with a lawyer.</small></div>}
          <h3>Other filings and options</h3>
          {guide.options.map((o) => <article key={o.key} className={'mcOption' + (o.highlight ? ' gold' : '')}>
            {o.highlight && <small className="mcMatch">MATCHES THE DESCRIPTION</small>}
            <h4>{o.title}</h4><p>{o.what}</p>
            {o.deadline && <p className={'mcDeadline' + (o.deadline_status?.passed ? ' passed' : '')}>⏰ Deadline: {o.deadline}{o.deadline_status ? ` (${o.deadline_status.label})` : ''}</p>}
            {o.where && <p className="mcWhere">Where to file: {o.where}</p>}
            <LawAccordion api={api} items={o.citations}/>
          </article>)}
          <div className="mcActions"><button type="button" onClick={save}>Save this case</button></div>
          <Glossary text={JSON.stringify(guide)} />{guide.find_case?.length ? <><h3>Find their case</h3><p>{guide.find_case.map((r) => <a key={r.url} href={r.url} target="_blank" rel="noreferrer">{r.title} </a>)}</p></> : null}<HelpLovedOne /><h3>Free and low-cost help</h3><p>{guide.resources.map((r) => <a key={r.url} href={r.url} target="_blank" rel="noreferrer">{r.title} </a>)}</p>
          <small>{guide.disclaimer}</small>
        </div>}
      </>}
    </section>
  );
}
