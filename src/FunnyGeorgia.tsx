import{useState}from'react';
import data from './funnyGeorgia.json';
type Law={title:string;summary:string;citation:string;jurisdiction:string;category:string;source_url:string;status:string};
type Case={name:string;court:string;year:number;citation:string;summary:string;source_url:string};
const laws=data.laws as Law[];const cases=data.cases as Case[];
export default function FunnyGeorgia(){
 const[tab,setTab]=useState<'laws'|'cases'>('laws');const[q,setQ]=useState('');
 const m=(...f:string[])=>!q.trim()||f.some(x=>x.toLowerCase().includes(q.trim().toLowerCase()));
 const shownLaws=laws.filter(l=>m(l.title,l.summary,l.citation,l.category,l.jurisdiction));
 const shownCases=cases.filter(c=>m(c.name,c.summary,c.court,c.citation));
 return <div className="funnyBrowser">
  <div className="tabs" role="tablist"><button role="tab" aria-selected={tab==='laws'} className={tab==='laws'?'active':''} onClick={()=>setTab('laws')}>Funny Laws ({laws.length})</button><button role="tab" aria-selected={tab==='cases'} className={tab==='cases'?'active':''} onClick={()=>setTab('cases')}>Funny Cases ({cases.length})</button></div>
  <input className="funnySearch" aria-label="Search funny laws and cases" placeholder="Search funny laws and cases…" value={q} onChange={e=>setQ(e.target.value)}/>
  <div className="funGrid">{tab==='laws'?shownLaws.map(l=><article key={l.citation+l.title}><small>{l.category}</small><h3>{l.title}</h3><p>{l.summary}</p><p><b>{l.citation}</b> · {l.jurisdiction}</p>{!l.status.startsWith('In the current Georgia Code')&&<p>⚠ Status: {l.status}</p>}<a href={l.source_url} target="_blank" rel="noreferrer">Open source ↗</a></article>)
   :shownCases.map(c=><article key={c.name}><small>{c.court} · {c.year}</small><h3>{c.name}</h3><p>{c.summary}</p><p><b>{c.citation}</b></p><a href={c.source_url} target="_blank" rel="noreferrer">Open source ↗</a></article>)}</div>
  {(tab==='laws'?shownLaws:shownCases).length===0&&<p>No matches. Try another word.</p>}
  <p className="funnyNote">{data.note}</p>
 </div>;
}
