import {useEffect, useState} from 'react';
import {LawAccordion} from './LawAccordion';

/** 'My Case' hub (web): case type -> criminal stage -> next steps, deadlines, motions with stored Georgia law. */
export const STAGES: [string, string][] = [
  ['arrested', 'Arrested / bond'], ['pretrial', 'Charged / pretrial'], ['plea', 'Plea offer'], ['trial', 'Trial'],
  ['sentenced', 'Sentenced'], ['appeal', 'Appeal'], ['prison', 'In prison – get out or reduce time'],
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
  laws_cited: Cite[]; resources: {title: string; url: string}[]; disclaimer: string};
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
  async function run(st = stage, d = details) {
    setBusy(true); setErr(''); setGuide(null);
    try {
      const r = await fetch(api + '/public/case-guide', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({stage: st, details: d})});
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
          {guide.timeline.length > 0 && <div className="mcTimeline"><h3>Deadline timeline</h3>{guide.timeline.map((t) => <p key={t.title}><b>{t.due}</b> · {t.title} <span className={t.passed ? 'passed' : ''}>{t.label}</span></p>)}<small>Estimates from the dates entered. Confirm every deadline with a lawyer.</small></div>}
          <h3>Motions &amp; filings that may apply</h3>
          {guide.options.map((o) => <article key={o.key} className={'mcOption' + (o.highlight ? ' gold' : '')}>
            {o.highlight && <small className="mcMatch">MATCHES WHAT WAS DESCRIBED</small>}
            <h4>{o.title}</h4><p>{o.what}</p>
            {o.deadline && <p className={'mcDeadline' + (o.deadline_status?.passed ? ' passed' : '')}>⏰ Deadline: {o.deadline}{o.deadline_status ? ` (${o.deadline_status.label})` : ''}</p>}
            {o.where && <p className="mcWhere">Where to file: {o.where}</p>}
            <LawAccordion api={api} items={o.citations}/>
          </article>)}
          <div className="mcActions"><button type="button" onClick={save}>Save this case</button></div>
          <h3>Free and low-cost help</h3><p>{guide.resources.map((r) => <a key={r.url} href={r.url} target="_blank" rel="noreferrer">{r.title} </a>)}</p>
          <small>{guide.disclaimer}</small>
        </div>}
      </>}
    </section>
  );
}
