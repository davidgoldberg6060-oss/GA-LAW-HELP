import{useState}from'react';
import data from './funnyGeorgia.json';
import {LoadingPhrase, LOADING} from './LoadingPhrase';
import{lawParagraphs}from'./LawAccordion';
type Law={title:string;summary:string;citation:string;jurisdiction:string;category:string;source_url:string;status:string};
type Case={name:string;court:string;year:number;citation:string;summary:string;source_url:string};
type Loaded={title?:string;text:string;note?:string|null};
const laws=data.laws as Law[];const cases=data.cases as Case[];
const DEFAULT_API='https://api-production-60cc.up.railway.app';
// citation -> stored text, or null when the backend has no stored text (404).
const cache=new Map<string,Loaded|null>();
/** Funny Laws tab. "Open source" expands the FULL stored text in place (accordion: one open at a time). Never navigates away. */
export default function FunnyGeorgia({api=DEFAULT_API}:{api?:string}){
 const[tab,setTab]=useState<'laws'|'cases'>('laws');const[q,setQ]=useState('');
 const[open,setOpen]=useState<string|null>(null);const[state,setState]=useState<'idle'|'loading'|'error'>('idle');
 const m=(...f:string[])=>!q.trim()||f.some(x=>x.toLowerCase().includes(q.trim().toLowerCase()));
 const shownLaws=laws.filter(l=>m(l.title,l.summary,l.citation,l.category,l.jurisdiction));
 const shownCases=cases.filter(c=>m(c.name,c.summary,c.court,c.citation));
 async function load(cite:string){
  setState('loading');
  try{const r=await fetch(api+'/public/georgia-laws/law?citation='+encodeURIComponent(cite));
   if(r.ok)cache.set(cite,await r.json());else if(r.status===404)cache.set(cite,null);else throw new Error(String(r.status));
   setState('idle');}catch{setState('error');}
 }
 function toggle(cite:string){if(open===cite){setOpen(null);return;}setOpen(cite);if(!cache.has(cite))load(cite);else setState('idle');}
 function panel(cite:string){
  if(open!==cite)return null;const law=cache.get(cite);
  return <div className="lawText" role="region" aria-label={'Full text of '+cite}>
   {!cache.has(cite)&&state==='loading'?<LoadingPhrase lines={LOADING.laws} label="Loading full text" />
   :!cache.has(cite)&&state==='error'?<p>Couldn't load the full text. Check your connection and try again. <button type="button" onClick={()=>load(cite)}>Retry</button></p>
   :law?<>{law.title&&<h4>{law.title}</h4>}<div className="lawScroll">{lawParagraphs(law.text||'No text is stored for this item yet.').map((p,i)=><p key={i} style={{marginLeft:p.level*18}}>{p.text}</p>)}</div>{law.note&&<small>Note: {law.note}</small>}</>
   :<p>The full text of {cite} isn't stored in STANDALONE ASSISTANT yet, so there's nothing to show here.</p>}
  </div>;
 }
 const btn=(cite:string)=><button type="button" className="funnyToggle" aria-expanded={open===cite} onClick={()=>toggle(cite)}>{open===cite?'Close source ▴':'Open source ▾'}</button>;
 return <div className="funnyBrowser">
  <div className="tabs" role="tablist"><button role="tab" aria-selected={tab==='laws'} className={tab==='laws'?'active':''} onClick={()=>{setTab('laws');setOpen(null);}}>Funny Laws ({laws.length})</button><button role="tab" aria-selected={tab==='cases'} className={tab==='cases'?'active':''} onClick={()=>{setTab('cases');setOpen(null);}}>Funny Cases ({cases.length})</button></div>
  <input className="funnySearch" aria-label="Search funny laws and cases" placeholder="Search funny laws and cases…" value={q} onChange={e=>setQ(e.target.value)}/>
  <div className="funGrid">{tab==='laws'?shownLaws.map(l=><article key={l.citation+l.title}><small>{l.category}</small><h3>{l.title}</h3><p>{l.summary}</p><p><b>{l.citation}</b> · {l.jurisdiction}</p>{!l.status.startsWith('In the current Georgia Code')&&<p>⚠ Status: {l.status}</p>}{btn(l.citation)}{panel(l.citation)}</article>)
   :shownCases.map(c=><article key={c.name}><small>{c.court} · {c.year}</small><h3>{c.name}</h3><p>{c.summary}</p><p><b>{c.citation}</b></p>{btn(c.citation)}{panel(c.citation)}</article>)}</div>
  {(tab==='laws'?shownLaws:shownCases).length===0&&<p>No matches. Try another word.</p>}
  <p className="funnyNote">{data.note}</p>
 </div>;
}
