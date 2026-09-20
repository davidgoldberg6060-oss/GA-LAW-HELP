import React,{FormEvent,useEffect,useState}from'react';
import{Scale,Search,FileText,ShieldCheck,MessageSquare,BookOpen,ExternalLink,X,LogOut,UserRound,LoaderCircle}from'lucide-react';

const API='https://api-production-60cc.up.railway.app';
type Resource={title:string;url:string;kind:string;official:boolean};
type Research={query:string;topic:string;guidance:string;resources:Resource[];notice:string};
type User={id:number;email:string;role:string};
const funFacts=[
{title:'Why old laws can sound strange',text:'Georgia law has been revised for generations. Some rules that sound funny online may be outdated, local, misquoted, or missing important context.'},
{title:'Myth or real law?',text:'GA.LAW.HELP separates viral “weird law” claims from rules that can be traced to an official source.'},
{title:'Learn before you log in',text:'Public legal-learning features are available without an account. An account is only needed for private work such as saved cases and evidence.'}
];

async function api(path:string,options:RequestInit={}){
 const res=await fetch(API+path,{...options,headers:{'Content-Type':'application/json',...(options.headers||{})}});
 const data=await res.json().catch(()=>({detail:'The server returned an unreadable response.'}));
 if(!res.ok)throw new Error(typeof data.detail==='string'?data.detail:'Request failed');
 return data;
}

export default function App(){
 const[q,setQ]=useState('');const[research,setResearch]=useState<Research|null>(null);const[researching,setResearching]=useState(false);
 const[authOpen,setAuthOpen]=useState(false);const[mode,setMode]=useState<'login'|'register'>('login');
 const[email,setEmail]=useState('');const[password,setPassword]=useState('');const[authError,setAuthError]=useState('');const[authBusy,setAuthBusy]=useState(false);
 const[user,setUser]=useState<User|null>(null);const[notice,setNotice]=useState('');

 useEffect(()=>{const token=localStorage.getItem('ga_access_token');if(!token)return;
  fetch(API+'/me',{headers:{Authorization:'Bearer '+token}}).then(r=>r.ok?r.json():Promise.reject()).then(setUser).catch(()=>{localStorage.removeItem('ga_access_token');localStorage.removeItem('ga_refresh_token')});
 },[]);

 async function runResearch(e?:FormEvent){e?.preventDefault();if(!q.trim()){setNotice('Enter a Georgia legal question first.');return}
  setNotice('');setResearching(true);try{setResearch(await api('/public/research?q='+encodeURIComponent(q.trim())));setTimeout(()=>document.getElementById('research-results')?.scrollIntoView({behavior:'smooth'}),50)}
  catch(err){setNotice(err instanceof Error?err.message:'Research is temporarily unavailable.')}finally{setResearching(false)}
 }

 async function submitAuth(e:FormEvent){e.preventDefault();setAuthError('');setAuthBusy(true);
  try{const data=await api(mode==='login'?'/auth/login':'/auth/register',{method:'POST',body:JSON.stringify({email,password})});
   if(!data.access_token)throw new Error('Your account was created, but sign-in is waiting for email verification.');
   localStorage.setItem('ga_access_token',data.access_token);localStorage.setItem('ga_refresh_token',data.refresh_token);
   const profile=await fetch(API+'/me',{headers:{Authorization:'Bearer '+data.access_token}}).then(r=>r.json());
   setUser(profile);setAuthOpen(false);setPassword('');setNotice(mode==='register'?'Account created. You are signed in.':'Welcome back. You are signed in.');
  }catch(err){setAuthError(err instanceof Error?err.message:'Could not sign in.')}finally{setAuthBusy(false)}
 }
 function logout(){localStorage.removeItem('ga_access_token');localStorage.removeItem('ga_refresh_token');setUser(null);setNotice('You are signed out.');}

 return <main>
  <header><div className="brand"><Scale/><div><b>STANDALONE ASSISTANT</b><span>GA.LAW.HELP</span></div></div>
   {user?<div className="account"><span><UserRound size={16}/>{user.email}</span><button onClick={logout} aria-label="Sign out"><LogOut size={17}/> Sign out</button></div>:
   <button onClick={()=>setAuthOpen(true)}>Sign in</button>}
  </header>
  {notice&&<div className="notice" role="status">{notice}</div>}
  <section className="hero"><div className="pill"><ShieldCheck size={16}/> Georgia legal research workspace</div><h1>Georgia law.<br/><em>Clearer answers.</em></h1>
   <p>Learn about Georgia law without creating an account. Sign in only when you want private case tools, saved research, evidence uploads, and syncing.</p>
   <form className="ask" onSubmit={runResearch}><Search/><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask about Georgia law…" aria-label="Georgia legal question"/>
    <button disabled={researching}>{researching?<><LoaderCircle className="spin" size={17}/>Checking</>:'Research'}</button></form>
   <small>Legal information and research assistance — not a substitute for advice from a licensed attorney.</small>
  </section>
  {research&&<section className="results" id="research-results"><div className="resultHead"><Search/><div><span>Research starting point</span><h2>{research.topic}</h2></div></div>
   <p className="question">“{research.query}”</p><p>{research.guidance}</p><div className="sources">{research.resources.map(r=><a key={r.url} href={r.url} target="_blank" rel="noreferrer"><div><b>{r.title}</b><span>{r.kind} · Official source</span></div><ExternalLink size={18}/></a>)}</div><small>{research.notice}</small></section>}
  <section className="cards"><article><FileText/><h3>Georgia Law Library</h3><p>Explore statutes, rules, opinions and public legal sources. No account required for public learning.</p></article>
   <article className="clickable" onClick={()=>setAuthOpen(true)}><MessageSquare/><h3>Private Case Assistant</h3><p>{user?'You are signed in. Your private workspace is ready for the next build step.':'Sign in to organize private facts, documents, evidence and research around your matter.'}</p></article>
   <article><ShieldCheck/><h3>Source-first Answers</h3><p>Designed to show authority, dates and citations so legal claims can be checked.</p></article></section>
  <section className="learn"><div className="sectionTitle"><BookOpen/><div><h2>Funny, Weird & Surprising Georgia Law</h2><p>Browse as a guest. Claims should be verified against an official source before being presented as current law.</p></div></div>
   <div className="funGrid">{funFacts.map(x=><article key={x.title}><h3>{x.title}</h3><p>{x.text}</p></article>)}</div></section>
  {authOpen&&<div className="modalBack" onMouseDown={e=>{if(e.target===e.currentTarget)setAuthOpen(false)}}><section className="modal" role="dialog" aria-modal="true" aria-label="Account access">
   <button className="close" onClick={()=>setAuthOpen(false)} aria-label="Close"><X/></button><Scale className="modalLogo"/><h2>{mode==='login'?'Sign in to your private workspace':'Create your private account'}</h2>
   <p>Public learning stays open to everyone. Your account protects private cases, documents and evidence.</p>
   <div className="tabs"><button className={mode==='login'?'active':''} onClick={()=>{setMode('login');setAuthError('')}}>Sign in</button><button className={mode==='register'?'active':''} onClick={()=>{setMode('register');setAuthError('')}}>Create account</button></div>
   <form onSubmit={submitAuth}><label>Email<input type="email" value={email} onChange={e=>setEmail(e.target.value)} autoComplete="email" required/></label>
    <label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} autoComplete={mode==='login'?'current-password':'new-password'} minLength={mode==='register'?10:1} required/></label>
    {mode==='register'&&<small>Use at least 10 characters.</small>}{authError&&<div className="error">{authError}</div>}
    <button className="primary" disabled={authBusy}>{authBusy?<><LoaderCircle className="spin" size={17}/>Please wait</>:mode==='login'?'Sign in':'Create account'}</button>
   </form></section></div>}
 </main>
}