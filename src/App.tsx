import React,{FormEvent,useEffect,useRef,useState}from'react';
import{Scale,Search,FileText,ShieldCheck,MessageSquare,BookOpen,ExternalLink,X,LogOut,UserRound,LoaderCircle,Car,ShieldAlert,Mic,Volume2,LockKeyhole,ChevronRight,Square}from'lucide-react';

const API='https://api-production-60cc.up.railway.app';
type Resource={title:string;url:string;kind:string;official:boolean};
type Research={query:string;topic:string;guidance:string;resources:Resource[];notice:string};
type User={id:number;email:string;role:string};
const funFacts=[
{title:'Why old laws can sound strange',text:'Georgia law has been revised for generations. Some rules that sound funny online may be outdated, local, misquoted, or missing important context.'},
{title:'Myth or real law?',text:'GA.LAW.HELP separates viral “weird law” claims from rules that can be traced to an official source.'},
{title:'Learn before you log in',text:'Public legal-learning features are available without an account. An account is only needed for private work such as saved cases and evidence.'}
];

type ScenarioKey='traffic'|'public'|'home'|'questioning'|'arrest'|'witness';
const scenarios:Record<ScenarioKey,{label:string;title:string;tips:string[];phrases:string[]}>={
 traffic:{label:'Traffic stop',title:'Stay calm and make every movement predictable',tips:[
  'Pull over safely, stop the engine, lower the window, and keep your hands visible.',
  'Tell the officer before reaching for your license, registration, insurance, or another item.',
  'Do not argue on the roadside. Save names, times, badge numbers, and objections for later.'
 ],phrases:[
  'Officer, I want to cooperate. I am keeping my hands visible. Please tell me before you want me to reach for anything.',
  'I do not consent to a search. I will not resist or interfere.',
  'I do not wish to answer questions. Am I free to leave?'
 ]},
 public:{label:'Public encounter',title:'Find out whether you are free to leave',tips:[
  'Keep your hands visible and avoid sudden movements.',
  'Calmly ask whether you are being detained or are free to leave.',
  'Do not physically resist, even if you believe the stop is improper.'
 ],phrases:[
  'Officer, am I being detained, or am I free to leave?',
  'I do not consent to a search. I will not resist.',
  'I choose to remain silent and do not wish to answer questions.'
 ]},
 home:{label:'Police at the door',title:'Slow the encounter down without obstructing',tips:[
  'Ask who is there and why before opening the door.',
  'Ask to see any warrant through a window or where it can be read safely.',
  'Do not physically block officers. State any lack of consent calmly and contact a lawyer.'
 ],phrases:[
  'Officer, do you have a warrant? Please hold it where I can read it.',
  'I do not consent to entry or a search. I will not physically interfere.',
  'I choose to remain silent and want legal counsel before answering questions.'
 ]},
 questioning:{label:'Interview room',title:'Do not try to talk your way out of an interrogation',tips:[
  'Ask clearly whether you are free to leave.',
  'If you do not want to answer, say so clearly and request a lawyer before questioning.',
  'Do not lie, guess, sign what you do not understand, or discuss the facts with other detainees.'
 ],phrases:[
  'Am I free to leave?',
  'I am choosing to remain silent. I want a lawyer before any questioning.',
  'I do not want to sign anything until I have spoken with a lawyer.'
 ]},
 arrest:{label:'Arrest or custody',title:'Protect safety first, then protect the record',tips:[
  'Do not resist, run, pull away, or try to explain the whole situation.',
  'State clearly that you are remaining silent and want a lawyer.',
  'Do not discuss facts in a patrol car, booking area, recorded phone call, or with other detainees.'
 ],phrases:[
  'I will not resist. I am choosing to remain silent and want a lawyer.',
  'Please tell me what you need me to do physically, and I will comply.',
  'I do not consent to a search, but I will not interfere.'
 ]},
 witness:{label:'Witness or victim',title:'Share urgent safety facts without guessing',tips:[
  'Call 911 when anyone faces immediate danger or needs medical help.',
  'Give essential safety information, but do not speculate or fill gaps with guesses.',
  'Ask for an incident number and preserve photos, messages, names, and times.'
 ],phrases:[
  'I can share what I personally saw, but I do not want to guess.',
  'Please give me the incident number and your name or badge number.',
  'I would like a victim advocate or lawyer before a detailed recorded interview.'
 ]}
};
const scenarioKeys=Object.keys(scenarios) as ScenarioKey[];
const rightsStatement='Officer, I want to cooperate and remain calm. I am choosing to remain silent, I do not consent to any searches, and I want a lawyer before questioning. I will not resist or interfere. Please tell me what you need me to do physically.';
function suggestedReply(text:string,scenario:ScenarioKey){
 const t=text.toLowerCase();
 if(/step out|get out|hands|turn around|move over|stand/.test(t))return 'I will comply. Please tell me where you want me to move and what you want me to do with my hands.';
 if(/search|look inside|open the|consent/.test(t))return 'I do not consent to a search. I will not resist or interfere.';
 if(/arrest|under arrest|custody/.test(t))return 'I am choosing to remain silent and want a lawyer. I will not resist.';
 if(/license|registration|insurance/.test(t))return 'My documents are available. Please tell me when and where you want me to reach for them.';
 if(/where were|why did|what happened|tell me|question/.test(t))return 'I do not wish to answer questions. I am choosing to remain silent.';
 if(/free to leave|detained|go now/.test(t))return 'Officer, am I being detained, or am I free to leave?';
 return scenarios[scenario].phrases[0];
}

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
 const[tool,setTool]=useState<'avoid'|'police'|null>(null);const[scenario,setScenario]=useState<ScenarioKey>('traffic');
 const[transcript,setTranscript]=useState('');const[listening,setListening]=useState(false);const recognitionRef=useRef<any>(null);

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
 function stopListening(){recognitionRef.current?.stop();recognitionRef.current=null;setListening(false)}
 function closeTool(){stopListening();window.speechSynthesis?.cancel();setTool(null)}
 function openPolice(){if(!user){setMode('login');setAuthOpen(true);setNotice('Sign in to use the paid police-encounter assistant.');return}setTool('police')}
 function startListening(){
  const SpeechRecognition=(window as any).SpeechRecognition||(window as any).webkitSpeechRecognition;
  if(!SpeechRecognition){setNotice('Live listening is not supported in this browser. You can still tap a prepared response.');return}
  stopListening();const recognition=new SpeechRecognition();recognition.continuous=true;recognition.interimResults=true;recognition.lang='en-US';
  recognition.onresult=(event:any)=>{let words='';for(let i=event.resultIndex;i<event.results.length;i++)words+=event.results[i][0].transcript+' ';setTranscript(previous=>(previous+' '+words).trim())};
  recognition.onerror=()=>{setListening(false);setNotice('Microphone listening stopped. Check browser microphone permission and try again.')};
  recognition.onend=()=>setListening(false);recognitionRef.current=recognition;recognition.start();setListening(true);
 }
 function speak(text:string){
  if(!('speechSynthesis'in window)){setNotice('Read-aloud is not supported in this browser.');return}
  window.speechSynthesis.cancel();const speech=new SpeechSynthesisUtterance(text);speech.rate=.9;speech.pitch=1;window.speechSynthesis.speak(speech);
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
  <section className="cards" aria-label="Choose a tool">
   <button className="toolCard" onClick={()=>document.getElementById('law-library')?.scrollIntoView({behavior:'smooth'})}><FileText/><span><h3>Georgia Law Library</h3><p>Explore statutes, opinions and official legal sources.</p></span><ChevronRight/></button>
   <button className="toolCard" onClick={()=>user?setNotice('Your private case workspace is ready for the next build step.'):setAuthOpen(true)}><MessageSquare/><span><h3>Private Case Assistant</h3><p>Organize private facts, evidence and saved research.</p></span><ChevronRight/></button>
   <button className="toolCard" onClick={()=>setTool('avoid')}><ShieldAlert/><span><h3>Avoid Trouble</h3><p>Pick a situation and see calm, practical safety steps.</p></span><ChevronRight/></button>
   <button className="toolCard premiumCard" onClick={openPolice}><Car/><span><b className="premiumLabel"><LockKeyhole size={13}/> PAID SERVICE</b><h3>Help Me Talk to Police</h3><p>Listen, suggest and read respectful responses aloud.</p></span><ChevronRight/></button>
  </section>
  <section className="learn" id="law-library"><div className="sectionTitle"><BookOpen/><div><h2>Funny, Weird & Surprising Georgia Law</h2><p>Browse as a guest. Claims should be verified against an official source before being presented as current law.</p></div></div>
   <div className="funGrid">{funFacts.map(x=><article key={x.title}><h3>{x.title}</h3><p>{x.text}</p></article>)}</div></section>
  {tool&&<div className="modalBack" onMouseDown={e=>{if(e.target===e.currentTarget)closeTool()}}><section className="toolModal" role="dialog" aria-modal="true" aria-label={tool==='avoid'?'Avoid trouble':'Help me talk to police'}>
   <button className="close" onClick={closeTool} aria-label="Close"><X/></button>
   {tool==='avoid'?<><ShieldAlert className="modalLogo"/><h2>Avoid Trouble</h2><p>Choose the situation closest to what is happening. Safety comes first; this is general information, not a substitute for a lawyer.</p>
    <div className="scenarioButtons">{scenarioKeys.map(key=><button key={key} className={scenario===key?'active':''} onClick={()=>setScenario(key)}>{scenarios[key].label}</button>)}</div>
    <div className="guidance"><h3>{scenarios[scenario].title}</h3><ul>{scenarios[scenario].tips.map(tip=><li key={tip}>{tip}</li>)}</ul></div>
    <div className="dangerNote"><ShieldAlert/>If anyone is in immediate danger or needs medical care, call 911. Never physically resist or make sudden movements to operate the app.</div>
   </>:<><div className="premiumHeading"><Mic className="modalLogo"/><span className="premiumLabel"><LockKeyhole size={13}/> PAID SERVICE PREVIEW</span></div><h2>Help Me Talk to Police</h2>
    <div className="dangerNote"><ShieldAlert/>Only use the phone when it is safe and permitted. Keep your hands visible, follow physical directions, and never let the app argue, resist, or interrupt.</div>
    <div className="scenarioButtons">{scenarioKeys.slice(0,5).map(key=><button key={key} className={scenario===key?'active':''} onClick={()=>{setScenario(key);setTranscript('')}}>{scenarios[key].label}</button>)}</div>
    <div className="listenBox"><div><b>Live listening</b><small>Your browser processes speech for suggestions. GA.LAW.HELP does not save the audio or transcript in this preview.</small></div>
     <button className={listening?'stopButton':'listenButton'} onClick={listening?stopListening:startListening}>{listening?<><Square size={16}/>Stop</>:<><Mic size={17}/>Start listening</>}</button>
    </div>
    <label className="transcriptLabel">What was heard<textarea value={transcript} onChange={e=>setTranscript(e.target.value)} placeholder="The live transcript will appear here. You can also type what the officer said."/></label>
    <div className="replyCard"><small>Suggested calm response</small><p>{suggestedReply(transcript,scenario)}</p><button onClick={()=>speak(suggestedReply(transcript,scenario))}><Volume2 size={17}/>Read this aloud</button></div>
    <button className="rightsButton" onClick={()=>speak(rightsStatement)}><ShieldCheck size={18}/><span><b>Read my rights statement aloud</b><small>States silence, no consent to search, request for counsel, and no resistance.</small></span></button>
    <div className="sourceLinks"><span>General constitutional references:</span><a href="https://constitution.congress.gov/constitution/amendment-4/" target="_blank" rel="noreferrer">Fourth Amendment</a><a href="https://constitution.congress.gov/constitution/amendment-5/" target="_blank" rel="noreferrer">Fifth Amendment</a><a href="https://constitution.congress.gov/constitution/amendment-6/" target="_blank" rel="noreferrer">Sixth Amendment</a></div>
    <small className="previewNote">Preview access is enabled for testing. A secure subscription checkout must be connected before customers can be charged.</small>
   </>}
  </section></div>}
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