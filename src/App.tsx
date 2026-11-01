import React,{FormEvent,useEffect,useRef,useState}from'react';
import{Scale,Search,FileText,ShieldCheck,MessageSquare,BookOpen,ExternalLink,X,LogOut,UserRound,LoaderCircle,Car,ShieldAlert,Mic,Volume2,LockKeyhole,ChevronRight,Square,Circle,Play,Download,Trash2,HardDrive,MapPin,Phone,Save,ClipboardList,UserPlus,Send,CheckCircle2,Fingerprint,Eye,EyeOff,Upload}from'lucide-react';
import{guestEncounterReply,guestRightsAndEncounter}from'./guestPublic';
import ApprovedScreens from './ApprovedScreens';
import FunnyGeorgia from './FunnyGeorgia';
import './approvedScreens.css';

const API='https://api-production-60cc.up.railway.app';
const ACCESS_KEY='ga_access_token',REFRESH_KEY='ga_refresh_token';
class ApiError extends Error{status:number;constructor(status:number,message:string){super(message);this.status=status}}
function accessToken(){return sessionStorage.getItem(ACCESS_KEY)}
function refreshToken(){return sessionStorage.getItem(REFRESH_KEY)}
function saveSession(access:string,refresh:string){sessionStorage.setItem(ACCESS_KEY,access);sessionStorage.setItem(REFRESH_KEY,refresh)}
function clearSession(){sessionStorage.removeItem(ACCESS_KEY);sessionStorage.removeItem(REFRESH_KEY)}
function migrateLegacySession(){
 const access=localStorage.getItem(ACCESS_KEY),refresh=localStorage.getItem(REFRESH_KEY);
 if(access&&!sessionStorage.getItem(ACCESS_KEY))sessionStorage.setItem(ACCESS_KEY,access);
 if(refresh&&!sessionStorage.getItem(REFRESH_KEY))sessionStorage.setItem(REFRESH_KEY,refresh);
 localStorage.removeItem(ACCESS_KEY);localStorage.removeItem(REFRESH_KEY);
}

type Resource={title:string;url:string;kind:string;official:boolean};
type Research={query:string;topic:string;guidance:string;resources:Resource[];notice:string};
type AIAnswer={question:string;answer:string;notice:string};
type User={id:number;email:string;role:string};
type CaseSummary={id:number;title:string;case_number:string|null;county:string|null;case_type:string;stage:string|null};
type CaseForm={title:string;case_number:string;county:string;case_type:string;stage:string;narrative:string};
type Finding={id:number;issue:string;category:string;favors:string;analysis:string;counterargument:string;facts_needed:string;confidence:string};
type SimilarAuthority={id:number;citation:string;title:string|null;status:string;source_url:string|null;match_score:number;verified_versions:Array<{id:number;source_url:string;verification_status:string}>};
type EvidenceItem={id:number;filename:string;media_type:string;bytes:number;sha256:string;uploaded_at:string;verified_at:string|null;original_preserved:boolean};
const emptyCase=():CaseForm=>({title:'',case_number:'',county:'',case_type:'criminal',stage:'investigation',narrative:''});

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


type LocalRecording={id:string;blob:Blob;createdAt:number;expiresAt:number;scenario:ScenarioKey;mimeType:string;caseId?:number;sha256?:string;interrupted?:boolean;cloudCopiedAt?:number};
type TrustedContact={name:string;phone:string};
type IncidentDraft={startedAt:string;location:string;agency:string;officer:string;badge:string;vehicle:string;notes:string};
const AUDIO_DB='ga-law-help-local-audio';
function openAudioDb():Promise<IDBDatabase>{
 return new Promise((resolve,reject)=>{
  const request=indexedDB.open(AUDIO_DB,1);
  request.onupgradeneeded=()=>{const db=request.result;if(!db.objectStoreNames.contains('recordings')){const store=db.createObjectStore('recordings',{keyPath:'id'});store.createIndex('expiresAt','expiresAt')}};
  request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);
 });
}
function idbRequest<T>(request:IDBRequest<T>):Promise<T>{return new Promise((resolve,reject)=>{request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error)})}
function idbDone(transaction:IDBTransaction):Promise<void>{return new Promise((resolve,reject)=>{transaction.oncomplete=()=>resolve();transaction.onerror=()=>reject(transaction.error);transaction.onabort=()=>reject(transaction.error)})}
async function saveLocalRecording(row:LocalRecording){
 const db=await openAudioDb();const transaction=db.transaction('recordings','readwrite');transaction.objectStore('recordings').put(row);await idbDone(transaction);db.close();
}
async function purgeExpiredLocalRecordings():Promise<LocalRecording[]>{
 const db=await openAudioDb();const read=db.transaction('recordings','readonly');const rows=await idbRequest(read.objectStore('recordings').getAll()) as LocalRecording[];await idbDone(read);
 const expired=rows.filter(row=>row.expiresAt<=Date.now());
 if(expired.length){const write=db.transaction('recordings','readwrite');for(const row of expired)write.objectStore('recordings').delete(row.id);await idbDone(write)}
 db.close();return rows.filter(row=>row.expiresAt>Date.now()).sort((a,b)=>b.createdAt-a.createdAt);
}
async function deleteLocalRecording(id:string){
 const db=await openAudioDb();const transaction=db.transaction('recordings','readwrite');transaction.objectStore('recordings').delete(id);await idbDone(transaction);db.close();
}
function formatBytes(bytes:number){if(bytes<1024)return bytes+' B';if(bytes<1048576)return(bytes/1024).toFixed(1)+' KB';return(bytes/1048576).toFixed(1)+' MB'}
async function sha256Blob(blob:Blob){const digest=await crypto.subtle.digest('SHA-256',await blob.arrayBuffer());return Array.from(new Uint8Array(digest)).map(byte=>byte.toString(16).padStart(2,'0')).join('')}
async function uploadEncounterCopy(blob:Blob,scenario:ScenarioKey,recordingCaseId?:number){
 const token=accessToken();const caseId=recordingCaseId?String(recordingCaseId):localStorage.getItem('ga_encounter_case_id');
 if(!token||!caseId)return {uploaded:false,reason:'Sign in and select an encounter case to enable protected cloud/email copies.'};
 const ext=blob.type.includes('ogg')?'ogg':blob.type.includes('mp4')?'m4a':'webm';
 const form=new FormData();form.append('file',blob,'encounter-'+scenario+'-'+new Date().toISOString().replace(/[:.]/g,'-')+'.'+ext);
 const res=await fetch(API+'/cases/'+encodeURIComponent(caseId)+'/evidence',{method:'POST',headers:{Authorization:'Bearer '+token},body:form});
 const data=await res.json().catch(()=>({detail:'Upload failed'}));if(!res.ok)throw new Error(data.detail||'Upload failed');return {uploaded:true,...data};
}

async function api<T=any>(path:string,options:RequestInit={}):Promise<T>{
 const res=await fetch(API+path,{...options,headers:{'Content-Type':'application/json',...(options.headers||{})}});
 const data=await res.json().catch(()=>({detail:'The server returned an unreadable response.'}));
 if(!res.ok)throw new ApiError(res.status,typeof data.detail==='string'?data.detail:'Request failed');
 return data;
}
async function authApi(path:string,options:RequestInit={}){
 const run=(token:string)=>api(path,{...options,headers:{...(options.headers||{}),Authorization:'Bearer '+token}});
 const current=accessToken();if(!current)throw new Error('Sign in to use the private case workspace.');
 try{return await run(current)}
 catch(error){
  if(!(error instanceof ApiError)||error.status!==401)throw error;
  const refresh=refreshToken();if(!refresh){clearSession();throw new Error('Your secure session expired. Sign in again.')}
  try{const rotated=await api('/auth/refresh',{method:'POST',body:JSON.stringify({refresh_token:refresh})});saveSession(rotated.access_token,rotated.refresh_token);return await run(rotated.access_token)}
  catch{clearSession();throw new Error('Your secure session expired. Sign in again.')}
 }
}

/** No-login access: a random device key in localStorage maps to an anonymous server identity. */
const DEVICE_KEY='ga_device_key';
function deviceKey(){let k=localStorage.getItem(DEVICE_KEY);if(!k){const b=new Uint8Array(32);crypto.getRandomValues(b);k=btoa(String.fromCharCode(...b)).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');localStorage.setItem(DEVICE_KEY,k)}return k}
async function anonymousSession(){const data=await api('/auth/anonymous',{method:'POST',body:JSON.stringify({device_key:deviceKey()})});saveSession(data.access_token,data.refresh_token);return authApi('/me')}

const FREE_LAUNCH=true;

export default function App(){
 const[q,setQ]=useState('');const[research,setResearch]=useState<Research|null>(null);const[aiAnswer,setAiAnswer]=useState<AIAnswer|null>(null);const[researching,setResearching]=useState(false);
 const[authOpen,setAuthOpen]=useState(false);const[mode,setMode]=useState<'login'|'register'|'forgot'|'reset'>('login');
 const[email,setEmail]=useState('');const[password,setPassword]=useState('');const[showPassword,setShowPassword]=useState(false);const[authError,setAuthError]=useState('');const[authBusy,setAuthBusy]=useState(false);
 const passwordAccepted=password.length>=15&&password.length<=128;
 const[user,setUser]=useState<User|null>(null);const paid=FREE_LAUNCH||!!user&&(user.role==='paid'||user.role==='admin');const[notice,setNotice]=useState('');
 const[tool,setTool]=useState<'avoid'|'police'|'case'|null>(null);const[scenario,setScenario]=useState<ScenarioKey>('traffic');
 const[transcript,setTranscript]=useState('');const[listening,setListening]=useState(false);const recognitionRef=useRef<any>(null);const[encounterReply,setEncounterReply]=useState('');const[encounterBusy,setEncounterBusy]=useState(false);const encounterTimerRef=useRef<number|null>(null);const[cameraOn,setCameraOn]=useState(false);const cameraVideoRef=useRef<HTMLVideoElement|null>(null);const cameraStreamRef=useRef<MediaStream|null>(null);
 const[recording,setRecording]=useState(false);const[recordings,setRecordings]=useState<LocalRecording[]>([]);
 const[retentionDays,setRetentionDays]=useState<180|365|400>(()=>{const saved=Number(localStorage.getItem('ga_audio_retention_days'));return saved===180||saved===400?saved:365});
 const mediaRecorderRef=useRef<MediaRecorder|null>(null);const mediaStreamRef=useRef<MediaStream|null>(null);const audioChunksRef=useRef<Blob[]>([]);const recoveryIdRef=useRef<string|null>(null);const recordingCaseIdRef=useRef<number|undefined>(undefined);
 const[incident,setIncident]=useState<IncidentDraft>(()=>{try{const saved=localStorage.getItem('ga_incident_draft');if(saved)return JSON.parse(saved)}catch{}return{startedAt:new Date().toISOString().slice(0,16),location:'',agency:'',officer:'',badge:'',vehicle:'',notes:''}});
 const[trusted,setTrusted]=useState<TrustedContact>(()=>{try{const saved=localStorage.getItem('ga_trusted_contact');if(saved)return JSON.parse(saved)}catch{}return{name:'',phone:''}});
 const[cases,setCases]=useState<CaseSummary[]>([]);const[activeCaseId,setActiveCaseId]=useState<number|null>(null);const[caseForm,setCaseForm]=useState<CaseForm>(emptyCase());const[findings,setFindings]=useState<Finding[]>([]);const[caseBusy,setCaseBusy]=useState(false);const[motionFacts,setMotionFacts]=useState('');const[motionResult,setMotionResult]=useState('');const[motionBusy,setMotionBusy]=useState(false);const[caseMotionResult,setCaseMotionResult]=useState('');const[caseDefenseResult,setCaseDefenseResult]=useState('');const[chargeCheck,setChargeCheck]=useState<any>(null);const[similarAuthorities,setSimilarAuthorities]=useState<SimilarAuthority[]>([]);const[evidence,setEvidence]=useState<EvidenceItem[]>([]);const[evidenceBusy,setEvidenceBusy]=useState(false);const[online,setOnline]=useState(()=>navigator.onLine);const[installPrompt,setInstallPrompt]=useState<any>(null);const[paywallOpen,setPaywallOpen]=useState(false);const[billingBusy,setBillingBusy]=useState(false);

 useEffect(()=>{
  const updateOnline=()=>setOnline(navigator.onLine);const captureInstall=(event:any)=>{event.preventDefault();setInstallPrompt(event)};
  window.addEventListener('online',updateOnline);window.addEventListener('offline',updateOnline);window.addEventListener('beforeinstallprompt',captureInstall);
  return()=>{window.removeEventListener('online',updateOnline);window.removeEventListener('offline',updateOnline);window.removeEventListener('beforeinstallprompt',captureInstall)}
 },[]);
 useEffect(()=>{migrateLegacySession();if(!accessToken())return;
  authApi('/me').then(setUser).catch(()=>{clearSession();setUser(null)});
 },[]);
 useEffect(()=>{
  const params=new URLSearchParams(window.location.search);const membership=params.get('membership');
  if(membership==='cancelled'){window.history.replaceState({},'', '/');setNotice('Checkout cancelled. You were not charged.')}
  if(membership==='success'&&accessToken()){
   window.history.replaceState({},'', '/');setNotice('Payment received. Activating membership…');
   let attempts=0;const check=()=>authApi('/me').then(profile=>{setUser(profile);if(profile.role==='paid'||profile.role==='admin'){setPaywallOpen(false);setNotice('Membership active. Paid tools are unlocked.');return}if(++attempts<6)window.setTimeout(check,2000)}).catch(()=>{});
   check();
  }
  const token=params.get('token');
  if(window.location.pathname==='/reset-password'&&token){setMode('reset');setAuthOpen(true);setAuthError('');return}
  if(window.location.pathname==='/verify-email'&&token){
   setAuthOpen(true);setAuthBusy(true);
   api('/auth/verify-email',{method:'POST',body:JSON.stringify({token})}).then(()=>{
    window.history.replaceState({},'', '/');setMode('login');setNotice('Email verified. You can sign in now.');
   }).catch(error=>{setMode('login');setAuthError(error instanceof Error?error.message:'The verification link is invalid or expired.')}).finally(()=>setAuthBusy(false));
  }
 },[]);
 useEffect(()=>{const sync=()=>{syncRecoveredRecordings().catch(()=>{})};window.addEventListener('online',sync);const timer=window.setTimeout(sync,1200);return()=>{window.removeEventListener('online',sync);window.clearTimeout(timer)}},[user]);
 useEffect(()=>{purgeExpiredLocalRecordings().then(async rows=>{
  const recovered=rows.filter(row=>row.id.startsWith('recovery-'));
  if(recovered.length){
   const normalized=await Promise.all(rows.map(async row=>{
    if(!row.id.startsWith('recovery-'))return row;
    const sha256=row.sha256||await sha256Blob(row.blob).catch(()=>undefined);
    const fixed={...row,sha256,interrupted:true};await saveLocalRecording(fixed).catch(()=>{});return fixed;
   }));
   setRecordings(normalized);setNotice('Recovered '+recovered.length+' interrupted encounter recording'+(recovered.length===1?'':'s')+' from this device. The recovered copy has been preserved.');
  }else setRecordings(rows);
 }).catch(()=>setNotice('Local recording storage could not be opened on this device.'))},[]);
 useEffect(()=>{localStorage.setItem('ga_incident_draft',JSON.stringify(incident))},[incident]);
 useEffect(()=>{localStorage.setItem('ga_trusted_contact',JSON.stringify(trusted))},[trusted]);

 async function runResearch(e?:FormEvent){e?.preventDefault();if(!q.trim()){setNotice('Enter a Georgia legal question first.');return}
  setNotice('');setResearching(true);setAiAnswer(null);setResearch(null);
  try{
   const {answer,research}=await guestRightsAndEncounter(API,api,q.trim());
   setAiAnswer(answer);setResearch(research);setTimeout(()=>document.getElementById('research-results')?.scrollIntoView({behavior:'smooth'}),50)
  }catch(err){setNotice(err instanceof Error?err.message:'GA.LAW.HELP is temporarily unavailable.')}finally{setResearching(false)}
 }

 async function startCamera(){
  if(cameraOn)return;
  if(!navigator.mediaDevices?.getUserMedia){setNotice('Camera access is not supported in this browser.');return}
  try{
   const stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false});
   cameraStreamRef.current=stream;setCameraOn(true);
   setTimeout(()=>{if(cameraVideoRef.current){cameraVideoRef.current.srcObject=stream;cameraVideoRef.current.play().catch(()=>{})}},0);
  }catch{setNotice('Camera permission was not granted. Encounter help still works without the camera.')}
 }
 function stopCamera(){
  if(recording){setNotice('Stop the legal-encounter recording before turning the camera off so the evidence file is not unexpectedly interrupted.');return}
  cameraStreamRef.current?.getTracks().forEach(track=>track.stop());cameraStreamRef.current=null;
  if(cameraVideoRef.current)cameraVideoRef.current.srcObject=null;setCameraOn(false);
 }
 async function getEncounterAI(text:string){
  const heard=text.trim();if(!heard||encounterBusy)return;
  setEncounterBusy(true);
  try{
   const prompt='LIVE POLICE ENCOUNTER. Scenario: '+scenarios[scenario].label+'. The officer/person said: "'+heard+'". Give ONE short, calm sentence the user can safely say aloud now. Prioritize physical compliance and safety. Do not argue, threaten, evade, resist, lie, or give a long legal explanation.';
   const data=await guestEncounterReply(api,prompt);
   setEncounterReply(data.answer||suggestedReply(heard,scenario));
  }catch{setEncounterReply(suggestedReply(heard,scenario))}
  finally{setEncounterBusy(false)}
 }
 useEffect(()=>{
  if(!tool||tool!=='police'||!transcript.trim())return;
  if(encounterTimerRef.current)window.clearTimeout(encounterTimerRef.current);
  encounterTimerRef.current=window.setTimeout(()=>getEncounterAI(transcript),450);
  return()=>{if(encounterTimerRef.current)window.clearTimeout(encounterTimerRef.current)}
 },[transcript,scenario,tool]);

 async function submitAuth(e:FormEvent){e.preventDefault();setAuthError('');
  if((mode==='register'||mode==='reset')&&!passwordAccepted){setAuthError('Your password must be between 15 and 128 characters.');return}
  setAuthBusy(true);
  try{
   if(mode==='forgot'){
    await api('/auth/forgot-password',{method:'POST',body:JSON.stringify({email})});
    setMode('login');setNotice('If an account exists for that email, a password-reset link has been sent.');return;
   }
   if(mode==='reset'){
    const token=new URLSearchParams(window.location.search).get('token');if(!token)throw new Error('This password-reset link is missing its secure token.');
    await api('/auth/reset-password',{method:'POST',body:JSON.stringify({token,new_password:password})});
    window.history.replaceState({},'', '/');setMode('login');setPassword('');setNotice('Password reset. Sign in with your new password.');return;
   }
   const data=await api(mode==='login'?'/auth/login':'/auth/register',{method:'POST',body:JSON.stringify({email,password})});
   if(!data.access_token){
    setMode('login');setPassword('');setNotice('Account created. Check your email for the verification link, then sign in.');return;
   }
   saveSession(data.access_token,data.refresh_token);
   const profile=await fetch(API+'/me',{headers:{Authorization:'Bearer '+data.access_token}}).then(r=>r.json());
   setUser(profile);setAuthOpen(false);setPassword('');setNotice(mode==='register'?'Account created. You are signed in.':'Welcome back. You are signed in.');
  }catch(err){setAuthError(err instanceof Error?err.message:'Could not complete account access.')}finally{setAuthBusy(false)}
 }
 async function resendVerification(){
  if(!email.trim()){setAuthError('Enter your email address first.');return}
  setAuthBusy(true);setAuthError('');
  try{await api('/auth/resend-verification',{method:'POST',body:JSON.stringify({email})});setNotice('If that account still needs verification, a new link has been sent.')}
  catch(error){setAuthError(error instanceof Error?error.message:'The verification email could not be requested.')}finally{setAuthBusy(false)}
 }
 async function startRecording(){
  if(recording)return;stopListening();
  if(tool!=='police'){setNotice('Recording is available only inside a law-enforcement or legal-encounter workflow.');return}
  if(!navigator.mediaDevices?.getUserMedia||!('MediaRecorder'in window)){setNotice('Legal-encounter recording is not supported in this browser.');return}
  try{
   const stream=await navigator.mediaDevices.getUserMedia(cameraOn?{audio:true,video:{facingMode:{ideal:'environment'}}}:{audio:true});mediaStreamRef.current=stream;
   if(cameraOn){cameraStreamRef.current?.getTracks().forEach(track=>track.stop());cameraStreamRef.current=stream;if(cameraVideoRef.current){cameraVideoRef.current.srcObject=stream;cameraVideoRef.current.play().catch(()=>{})}}
   navigator.storage?.persist?.().catch(()=>false);
   const preferred=cameraOn?(MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')?'video/webm;codecs=vp8,opus':MediaRecorder.isTypeSupported('video/webm')?'video/webm':''):(MediaRecorder.isTypeSupported('audio/webm;codecs=opus')?'audio/webm;codecs=opus':MediaRecorder.isTypeSupported('audio/webm')?'audio/webm':'');
   const recorder=new MediaRecorder(stream,preferred?{mimeType:preferred}:undefined);mediaRecorderRef.current=recorder;audioChunksRef.current=[];recoveryIdRef.current='recovery-'+(crypto.randomUUID?.()||String(Date.now()));recordingCaseIdRef.current=Number(localStorage.getItem('ga_encounter_case_id'))||undefined;
   recorder.ondataavailable=event=>{if(event.data.size){audioChunksRef.current.push(event.data);const recoveryId=recoveryIdRef.current;if(recoveryId){const recoveryBlob=new Blob(audioChunksRef.current,{type:recorder.mimeType||'audio/webm'});const now=Date.now();saveLocalRecording({id:recoveryId,blob:recoveryBlob,createdAt:now,expiresAt:now+retentionDays*86400000,scenario,mimeType:recorder.mimeType||'audio/webm',caseId:recordingCaseIdRef.current}).catch(()=>{})}}};
   recorder.onerror=()=>{stream.getTracks().forEach(track=>track.stop());setRecording(false);setNotice('Recording stopped because the browser reported an audio error.')};
   recorder.onstop=async()=>{
    try{
     const mimeType=recorder.mimeType||'audio/webm';const blob=new Blob(audioChunksRef.current,{type:mimeType});
     if(blob.size){const now=Date.now();const id=crypto.randomUUID?.()||String(now);const sha256=await sha256Blob(blob);await saveLocalRecording({id,blob,createdAt:now,expiresAt:now+retentionDays*86400000,scenario,mimeType,caseId:recordingCaseIdRef.current,sha256});setRecordings(await purgeExpiredLocalRecordings());try{const copy=await uploadEncounterCopy(blob,scenario,recordingCaseIdRef.current);setNotice(copy.uploaded?'Encounter preserved locally and in GA.LAW.HELP. Email confirmation attempted for your account.':'Encounter preserved locally. '+copy.reason)}catch{setNotice('Encounter preserved locally. Protected cloud/email copy could not be completed; keep this device copy.')}}
    }catch{setNotice('The recording could not be saved. Your browser storage may be full or unavailable.')}
    finally{const recoveryId=recoveryIdRef.current;recoveryIdRef.current=null;if(recoveryId)deleteLocalRecording(recoveryId).catch(()=>{});stream.getTracks().forEach(track=>track.stop());mediaRecorderRef.current=null;mediaStreamRef.current=null;audioChunksRef.current=[];recordingCaseIdRef.current=undefined;if(cameraOn){cameraStreamRef.current=null;if(cameraVideoRef.current)cameraVideoRef.current.srcObject=null;setCameraOn(false)}setRecording(false)}
   };
   recorder.start(1000);setRecording(true);setNotice(cameraOn?'Legal encounter video + audio recording started. Recovery checkpoints stay on this device while recording.':'Legal encounter audio recording started. Recovery checkpoints stay on this device while recording.');
  }catch{setNotice('Microphone permission was not granted. Allow microphone access and try again.')}
 }
 function stopRecording(){const recorder=mediaRecorderRef.current;if(recorder&&recorder.state!=='inactive')recorder.stop()}
 async function syncRecoveredRecordings(){
  if(!navigator.onLine)return;
  const rows=await purgeExpiredLocalRecordings();
  const pending=rows.filter(row=>row.interrupted&&!row.cloudCopiedAt&&row.blob.size>0);
  if(!pending.length)return;
  let copied=0;
  for(const row of pending){
   try{
    const result=await uploadEncounterCopy(row.blob,row.scenario,row.caseId);
    if(result.uploaded){const updated={...row,cloudCopiedAt:Date.now()};await saveLocalRecording(updated);copied++}
   }catch{}
  }
  if(copied){setRecordings(await purgeExpiredLocalRecordings());setNotice(copied+' recovered encounter recording'+(copied===1?' was':'s were')+' copied to protected GA.LAW.HELP storage. Account email confirmation was attempted.')}
 }
 function playRecording(row:LocalRecording){const url=URL.createObjectURL(row.blob);if(row.mimeType.startsWith('video/')){const w=window.open(url,'_blank');if(!w){URL.revokeObjectURL(url);setNotice('Allow pop-ups to preview this legal-encounter video, or use Download.');return}setTimeout(()=>URL.revokeObjectURL(url),60000);return}const audio=new Audio(url);audio.onended=()=>URL.revokeObjectURL(url);audio.onerror=()=>URL.revokeObjectURL(url);audio.play().catch(()=>{URL.revokeObjectURL(url);setNotice('This recording could not be played by the browser.')})}
 function downloadRecording(row:LocalRecording){const url=URL.createObjectURL(row.blob);const link=document.createElement('a');const extension=row.mimeType.includes('ogg')?'ogg':row.mimeType.startsWith('video/mp4')?'mp4':row.mimeType.includes('mp4')?'m4a':'webm';link.href=url;link.download='ga-law-help-'+new Date(row.createdAt).toISOString().replace(/[:.]/g,'-')+'.'+extension;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
 async function removeRecording(row:LocalRecording){const warning=row.cloudCopiedAt?'Permanently delete this DEVICE copy? A protected GA.LAW.HELP copy may still exist for the linked case. This does not delete the server evidence copy.':'Permanently delete the ONLY confirmed local copy of this legal-encounter recording? This cannot be undone.';if(!window.confirm(warning))return;await deleteLocalRecording(row.id);setRecordings(await purgeExpiredLocalRecordings());setNotice(row.cloudCopiedAt?'Device copy deleted. The protected case evidence copy was not deleted.':'Local recording deleted.')}
 function changeRetention(value:string){const days=Number(value) as 180|365|400;setRetentionDays(days);localStorage.setItem('ga_audio_retention_days',String(days))}
 function updateTrusted(field:keyof TrustedContact,value:string){setTrusted(previous=>({...previous,[field]:value}))}
 async function shareSafetyStatus(safe=false){
  if(!trusted.phone.trim()){setNotice('Add a trusted contact phone number first.');return}
  const location=incident.location?' Location: '+incident.location+'.':'';
  const message=safe?'GA.LAW.HELP safety check: I am safe after my law-enforcement encounter. I will contact you when I am able.':'GA.LAW.HELP safety check: I am currently in a '+scenarios[scenario].label.toLowerCase()+' encounter. It began around '+(incident.startedAt||new Date().toLocaleString())+'.'+location+' I will check in when safe.';
  const sms='sms:'+trusted.phone.replace(/[^+\d]/g,'')+'?body='+encodeURIComponent(message);
  try{if(navigator.share){await navigator.share({title:'GA.LAW.HELP safety check',text:message})}else{window.location.href=sms}}catch(error){if((error as Error)?.name!=='AbortError')window.location.href=sms}
 }
 function updateIncident(field:keyof IncidentDraft,value:string){setIncident(previous=>({...previous,[field]:value}))}
 function captureLocation(){
  if(!navigator.geolocation){setNotice('Location is not available in this browser.');return}
  setNotice('Requesting your location…');navigator.geolocation.getCurrentPosition(
   position=>{updateIncident('location',position.coords.latitude.toFixed(6)+', '+position.coords.longitude.toFixed(6)+' (accuracy about '+Math.round(position.coords.accuracy)+' m)');setNotice('Location added to the local incident report.')},
   ()=>setNotice('Location permission was not granted or your position was unavailable.'),
   {enableHighAccuracy:true,timeout:12000,maximumAge:0}
  );
 }
 function exportIncident(){
  const lines=['GA.LAW.HELP — INCIDENT SUMMARY','Created: '+new Date().toLocaleString(),'Encounter type: '+scenarios[scenario].label,'Encounter began: '+(incident.startedAt||'Not entered'),'Location: '+(incident.location||'Not entered'),'Agency: '+(incident.agency||'Not entered'),'Officer: '+(incident.officer||'Not entered'),'Badge number: '+(incident.badge||'Not entered'),'Vehicle / unit: '+(incident.vehicle||'Not entered'),'','User notes:',incident.notes||'None entered','','Local recordings listed in this browser: '+recordings.length,...recordings.map(row=>'- '+new Date(row.createdAt).toLocaleString()+' | '+scenarios[row.scenario].label+(row.interrupted?' | RECOVERED AFTER INTERRUPTION':'')+' | '+formatBytes(row.blob.size)+' | expires '+new Date(row.expiresAt).toLocaleDateString()+(row.sha256?' | SHA-256 '+row.sha256:'')),'','This user-created summary is not legal advice. Preserve original files and provide copies only to people the user authorizes.'];
  const blob=new Blob([lines.join('\n')],{type:'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download='ga-law-help-incident-'+new Date().toISOString().slice(0,10)+'.txt';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 function clearIncident(){if(!window.confirm('Clear the local incident report? Download it first if you need a copy.'))return;setIncident({startedAt:new Date().toISOString().slice(0,16),location:'',agency:'',officer:'',badge:'',vehicle:'',notes:''})}
 function stopListening(){recognitionRef.current?.stop();recognitionRef.current=null;setListening(false)}
 function closeTool(){stopRecording();stopListening();window.speechSynthesis?.cancel();setTool(null)}
 async function openCaseWorkspace(){
  if(!user){try{setUser(await anonymousSession())}catch{setMode('register');setAuthOpen(true);setNotice('Create a free account or sign in to use private case tools.');return}}
  if(!paid){setPaywallOpen(true);return}
  setTool('case');setCaseBusy(true);
  try{const rows=await authApi('/cases');setCases(rows);if(rows.length)await selectCase(rows[0].id);else startNewCase()}
  catch(error){setNotice(error instanceof Error?error.message:'The case workspace could not be loaded.')}finally{setCaseBusy(false)}
 }
 function startNewCase(){setActiveCaseId(null);localStorage.removeItem('ga_encounter_case_id');setCaseForm(emptyCase());setFindings([]);setCaseMotionResult('');setCaseDefenseResult('');setSimilarAuthorities([]);setEvidence([])}
 async function selectCase(id:number){
  setCaseBusy(true);try{const[detail,analysis,caseEvidence]=await Promise.all([authApi('/cases/'+id),authApi('/cases/'+id+'/analysis'),authApi('/cases/'+id+'/evidence')]);setActiveCaseId(id);localStorage.setItem('ga_encounter_case_id',String(id));setCaseForm({title:detail.title||'',case_number:detail.case_number||'',county:detail.county||'',case_type:detail.case_type||'criminal',stage:detail.stage||'',narrative:detail.narrative||''});setFindings(analysis.findings||[]);setEvidence(caseEvidence||[]);setCaseMotionResult('');setCaseDefenseResult('');setSimilarAuthorities([])}
  catch(error){setNotice(error instanceof Error?error.message:'The case could not be opened.')}finally{setCaseBusy(false)}
 }
 function updateCaseForm(field:keyof CaseForm,value:string){setCaseForm(previous=>({...previous,[field]:value}))}
 async function saveCase(event?:FormEvent){
  event?.preventDefault();if(!caseForm.title.trim()){setNotice('Add a short case title first.');return null}setCaseBusy(true);
  try{const payload={...caseForm,title:caseForm.title.trim(),case_number:caseForm.case_number||null,county:caseForm.county||null,stage:caseForm.stage||null,narrative:caseForm.narrative||null};const saved=activeCaseId?await authApi('/cases/'+activeCaseId,{method:'PATCH',body:JSON.stringify(payload)}):await authApi('/cases',{method:'POST',body:JSON.stringify(payload)});const id=activeCaseId||saved.id;const rows=await authApi('/cases');setCases(rows);setActiveCaseId(id);localStorage.setItem('ga_encounter_case_id',String(id));setNotice(activeCaseId?'Private case updated.':'Private case created.');return id}
  catch(error){setNotice(error instanceof Error?error.message:'The case could not be saved.');return null}finally{setCaseBusy(false)}
 }
 async function runCaseScreening(){
  let id=activeCaseId;if(!id)id=await saveCase() as number|null;if(!id)return;setCaseBusy(true);
  try{await authApi('/cases/'+id,{method:'PATCH',body:JSON.stringify({...caseForm,case_number:caseForm.case_number||null,county:caseForm.county||null,stage:caseForm.stage||null,narrative:caseForm.narrative||null})});const result=await authApi('/cases/'+id+'/analysis/run',{method:'POST',body:JSON.stringify({focus:'full_case'})});setFindings(result.findings||[]);setNotice('Issue screening completed. Each finding still needs record and source verification.')}
  catch(error){setNotice(error instanceof Error?error.message:'The screening could not be completed.')}finally{setCaseBusy(false)}
 }
 async function screenMotions(){
  if(!motionFacts.trim()){setNotice('Enter the case facts, dates, charge, and current stage first.');return}
  if(!user){try{setUser(await anonymousSession())}catch{setMode('register');setAuthOpen(true);setNotice('Sign in to use the private case workspace.');return}}
  setMotionBusy(true);setMotionResult('');
  try{
   let id=activeCaseId;
   if(!id){
    const title=motionFacts.trim().split('\n')[0].slice(0,120)||'Private motion screen';
    const created=await authApi('/cases',{method:'POST',body:JSON.stringify({title,case_type:'criminal',stage:'investigation',narrative:motionFacts.trim()})});
    id=created.id;setActiveCaseId(id);localStorage.setItem('ga_encounter_case_id',String(id));
   }
   const data=await authApi('/cases/'+id+'/motion-screen',{method:'POST',body:JSON.stringify({additional_facts:motionFacts.trim()})});
   const coverage=data.authority_coverage?('\n\nVerification mode: '+(data.verification_mode||'VERIFIED_REGISTRY_ONLY')+'\n'+JSON.stringify(data.authority_coverage)):('\n\nVerification mode: '+(data.verification_mode||'VERIFIED_REGISTRY_ONLY'));
   setMotionResult((data.analysis||'No motion screen was returned.')+coverage+(data.notice?'\n\n'+data.notice:''));
   setNotice('Private motion screening completed. Specific citations are limited to the verified registry. Verify current authority, deadlines, and local rules before filing.');
  }catch(error){setNotice(error instanceof Error?error.message:'Motion screening could not be completed.')}finally{setMotionBusy(false)}
 }
 async function checkActiveCaseMotions(){
  let id=activeCaseId;if(!id)id=await saveCase() as number|null;if(!id)return;
  const facts=['Case title: '+caseForm.title,'Case number: '+(caseForm.case_number||'Not entered'),'Georgia county: '+(caseForm.county||'Not entered'),'Case type: '+caseForm.case_type,'Current stage: '+(caseForm.stage||'Not entered'),'User narrative: '+(caseForm.narrative||'Not entered')].join('\n');
  setCaseBusy(true);setCaseMotionResult('');
  try{const data=await authApi('/cases/'+id+'/motion-screen',{method:'POST',body:JSON.stringify({})});setCaseMotionResult(data.analysis);setNotice('Motion and relief screening completed. Verify authorities and deadlines before filing.')}
  catch(error){setNotice(error instanceof Error?error.message:'Motion screening could not be completed.')}finally{setCaseBusy(false)}
 }
 async function runChargeCheck(){
  let id=activeCaseId;if(!id)id=await saveCase() as number|null;if(!id)return;
  setCaseBusy(true);setChargeCheck(null);
  try{const data=await authApi('/cases/'+id+'/charge-check',{method:'POST',body:JSON.stringify({situation:(caseForm.narrative||'').trim()})});setChargeCheck(data);setNotice(data.refused?data.message:'Charge Check completed. These are estimates; talk to a Georgia criminal defense lawyer or public defender.')}
  catch(error){setNotice(error instanceof Error?error.message:'Charge Check could not be completed.')}finally{setCaseBusy(false)}
 }
 async function checkDefenseStrategy(){
  let id=activeCaseId;if(!id)id=await saveCase() as number|null;if(!id)return;
  const facts=['Case title: '+caseForm.title,'Case number: '+(caseForm.case_number||'Not entered'),'Georgia county: '+(caseForm.county||'Not entered'),'Case type: '+caseForm.case_type,'Current stage: '+(caseForm.stage||'Not entered'),'User narrative: '+(caseForm.narrative||'Not entered')].join('\n');
  setCaseBusy(true);setCaseDefenseResult('');
  try{const data=await authApi('/cases/'+id+'/defense-analysis',{method:'POST',body:JSON.stringify({})});setCaseDefenseResult(data.analysis);setNotice('Defense-side analysis completed. Verify the record and cited authority before relying on it.')}
  catch(error){setNotice(error instanceof Error?error.message:'Defense analysis could not be completed.')}finally{setCaseBusy(false)}
 }
 async function findSimilarAuthorities(){
  let id=activeCaseId;if(!id)id=await saveCase() as number|null;if(!id)return;
  setCaseBusy(true);setSimilarAuthorities([]);
  try{const data=await authApi('/cases/'+id+'/similar-authorities');setSimilarAuthorities(data.results||[]);setNotice((data.results||[]).length?'Similar Georgia authority research leads found. Verify each before relying on it.':'No matching indexed authority found yet. This does not mean no relevant precedent exists.')}
  catch(error){setNotice(error instanceof Error?error.message:'Similar-case research could not be completed.')}finally{setCaseBusy(false)}
 }
 async function uploadCaseEvidence(event:React.ChangeEvent<HTMLInputElement>){
  const file=event.target.files?.[0];event.target.value='';if(!file)return;
  if(!activeCaseId){setNotice('Save the private case before adding documents or evidence.');return}
  const token=accessToken();if(!token){setNotice('Sign in again to upload evidence.');return}
  setEvidenceBusy(true);
  try{
   const form=new FormData();form.append('file',file);
   const response=await fetch(API+'/cases/'+activeCaseId+'/evidence',{method:'POST',headers:{Authorization:'Bearer '+token},body:form});
   const data=await response.json().catch(()=>({detail:'Upload failed'}));if(!response.ok)throw new Error(data.detail||'Upload failed');
   setEvidence(await authApi('/cases/'+activeCaseId+'/evidence'));setNotice('Original file preserved with SHA-256 integrity protection.');
  }catch(error){setNotice(error instanceof Error?error.message:'The file could not be uploaded.')}finally{setEvidenceBusy(false)}
 }
 async function verifyCaseEvidence(item:EvidenceItem){
  if(!activeCaseId)return;setEvidenceBusy(true);
  try{const result=await authApi('/cases/'+activeCaseId+'/evidence/'+item.id+'/verify',{method:'POST',body:'{}'});setEvidence(await authApi('/cases/'+activeCaseId+'/evidence'));setNotice(result.verified?'Integrity verified. The stored bytes match the original SHA-256 record.':'Integrity warning: the stored bytes did not match the original record.')}
  catch(error){setNotice(error instanceof Error?error.message:'Evidence integrity could not be verified.')}finally{setEvidenceBusy(false)}
 }
 async function downloadCaseEvidence(item:EvidenceItem){
  if(!activeCaseId)return;const token=accessToken();if(!token){setNotice('Sign in again to download evidence.');return}
  setEvidenceBusy(true);
  try{
   const response=await fetch(API+'/cases/'+activeCaseId+'/evidence/'+item.id+'/download',{headers:{Authorization:'Bearer '+token}});
   if(!response.ok){const data=await response.json().catch(()=>({detail:'Download failed'}));throw new Error(data.detail||'Download failed')}
   const blob=await response.blob();const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=item.filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setNotice('Downloaded your preserved evidence copy.');
  }catch(error){setNotice(error instanceof Error?error.message:'Evidence could not be downloaded.')}finally{setEvidenceBusy(false)}
 }
 function exportCasePlan(){
  const lines=['GA.LAW.HELP — PRIVATE CASE SCREENING','Created: '+new Date().toLocaleString(),'Title: '+caseForm.title,'Case number: '+(caseForm.case_number||'Not entered'),'County: '+(caseForm.county||'Not entered'),'Type: '+caseForm.case_type,'Stage: '+(caseForm.stage||'Not entered'),'','User narrative:',caseForm.narrative||'None entered','','SCREENING LEADS',...findings.flatMap((item,index)=>['',String(index+1)+'. '+item.issue,'Why it may matter: '+item.analysis,'Possible opposing position: '+item.counterargument,'Records and facts needed: '+item.facts_needed,'Status: '+item.confidence]),'','These are issue-screening leads, not legal conclusions or attorney advice. Verify the full record, deadlines, current law, and procedural posture with a licensed lawyer.'];const blob=new Blob([lines.join('\n')],{type:'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download='ga-law-help-case-screening-'+new Date().toISOString().slice(0,10)+'.txt';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)
 }
 function openPolice(){setTool('police')}
 function openRights(next:ScenarioKey=scenario){setScenario(next);setTool('avoid')}
 function startListening(){
  if(recording){setNotice('Stop the local audio recording before starting live transcription.');return}
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
 async function startCheckout(){
  if(!user){setPaywallOpen(false);setMode('register');setAuthOpen(true);return}
  setBillingBusy(true);
  try{const result=await authApi('/billing/checkout',{method:'POST',body:'{}'});if(result.already_paid){setPaywallOpen(false);setUser({...user,role:'paid'});return}if(!result.checkout_url)throw new Error('Secure checkout is unavailable.');window.location.assign(result.checkout_url)}
  catch(error){setNotice(error instanceof Error?error.message:'Secure checkout could not be started.')}finally{setBillingBusy(false)}
 }
 async function installApp(){
  if(!installPrompt)return;await installPrompt.prompt();await installPrompt.userChoice.catch(()=>null);setInstallPrompt(null);
 }
 async function logout(){
  const refresh=refreshToken();clearSession();localStorage.removeItem('ga_encounter_case_id');setUser(null);setNotice('You are signed out.');
  if(refresh)try{await api('/auth/logout',{method:'POST',body:JSON.stringify({refresh_token:refresh})})}catch{}
 }

 const authTitle=mode==='login'?'Welcome back':mode==='register'?'Create your private account':mode==='forgot'?'Reset your password':'Choose a new password';
 const authIntro=mode==='login'?'Sign in to continue to your saved cases and tools.':mode==='register'?'One secure account for your cases, incident notes and evidence.':mode==='forgot'?'Enter your email and we will send a secure reset link if an account exists.':'Use 15–128 characters for your new password.';

 return <main>
  <header><div className="brand"><Scale/><div><b>STANDALONE ASSISTANT</b><span>GA.LAW.HELP</span></div></div>
   <div className="headerActions">{installPrompt&&<button className="installButton" onClick={installApp}>Install app</button>}{user?<div className="account"><span><UserRound size={16}/>{user.email}</span><button onClick={logout} aria-label="Sign out"><LogOut size={17}/> Sign out</button></div>:
   <button onClick={()=>setAuthOpen(true)}>Sign in</button>}</div>
  </header>
  {!online&&<div className="offlineBanner" role="status"><ShieldAlert size={16}/><span><b>Offline safety mode</b> — encounter guidance and saved device recordings remain available. AI, sign-in, syncing and case files need internet.</span></div>}
  {notice&&<div className="notice" role="status">{notice}</div>}
  <section className="hero"><div className="pill"><ShieldCheck size={16}/> Georgia legal research workspace</div><h1>Georgia law.<br/><em>Clearer answers.</em></h1>
   <p>Learn about Georgia law without creating an account. Sign in only when you want private case tools, saved research, evidence uploads, and syncing.</p>
   <form className="ask" onSubmit={runResearch}><Search/><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask about Georgia law…" aria-label="Georgia legal question"/>
    <button disabled={researching}><Search size={15}/>{researching?<><LoaderCircle className="spin" size={17}/>Checking</>:'Free research'}</button></form>
   <small>Legal information and research assistance — not a substitute for advice from a licensed attorney.</small>
  </section>
  <ApprovedScreens signedIn={!!user} onSignIn={()=>setAuthOpen(true)} onCases={openCaseWorkspace} onAnalysis={openCaseWorkspace} onLogout={logout} onRights={openRights} onAsk={(text)=>{if(text.trim())setQ(text);}} askGuest={async(text)=>{const packed=await guestRightsAndEncounter(API,api,text);return{answer:packed.answer.answer,notice:packed.answer.notice};}} />
  {(aiAnswer||research)&&<section className="results" id="research-results">
   {aiAnswer&&<><div className="resultHead"><MessageSquare/><div><span>Ask GA.LAW.HELP</span><h2>AI legal information</h2></div></div><p className="question">“{aiAnswer.question}”</p><div className="aiAnswer" style={{whiteSpace:'pre-wrap'}}>{aiAnswer.answer}</div><small>{aiAnswer.notice}</small></>}
   {research&&<><div className="resultHead" style={{marginTop:'1.5rem'}}><Search/><div><span>Verify and research</span><h2>{research.topic}</h2></div></div><p>{research.guidance}</p><div className="sources">{research.resources.map(r=><a key={r.url} href={r.url} target="_blank" rel="noreferrer"><div><b>{r.title}</b><span>{r.official===false?r.kind+' · not a verified current citation':r.kind+' · Official source'}</span></div><ExternalLink size={18}/></a>)}</div><small>{research.notice}</small></>}
  </section>}
  <section className="homeDashboard" aria-label="Quick legal help">
   <div className="dashboardHeading"><div><span className="eyebrow">What is happening?</span><h2>Get to the right help fast</h2></div><p>Choose the closest situation. During an encounter, keep your hands visible and operate your phone only when safe and permitted.</p></div>
   <div className="encounterGrid">
    <button onClick={()=>{setScenario('traffic');openPolice()}}><Car/><span><b>Traffic Stop</b><small>Calm phrases and safety mode</small></span></button>
    <button onClick={()=>{setScenario('questioning');openPolice()}}><Mic/><span><b>Being Questioned</b><small>Silence and lawyer request</small></span></button>
    <button onClick={()=>{setScenario('arrest');openPolice()}}><ShieldAlert/><span><b>Arrested / Detained</b><small>Protect safety and the record</small></span></button>
    <button onClick={()=>{setScenario('home');openPolice()}}><ShieldCheck/><span><b>Police at My Door</b><small>Warrant and consent guidance</small></span></button>
    <button onClick={()=>openRights('public')}><UserRound/><span><b>Public Encounter</b><small>Ask if you are free to leave</small></span></button>
    <button className="emergencyAction" onClick={()=>openRights('witness')}><Phone/><span><b>Emergency Information</b><small>Danger, medical help, witnesses</small></span></button>
   </div>
  </section>
  <section className="cards" aria-label="Your legal tools">
   <button className="toolCard" onClick={()=>document.getElementById('law-library')?.scrollIntoView({behavior:'smooth'})}><FileText/><span><h3>Funny & Myth Checker</h3><p>Free: explore surprising Georgia-law claims and learn how to separate myths from verified law.</p></span><ChevronRight/></button>
   <button className="toolCard" onClick={openCaseWorkspace}><MessageSquare/><span><h3>My Cases</h3><p>Create private cases, screen issues, test counterarguments and organize the record.</p></span><ChevronRight/></button>
   <button className="toolCard" onClick={openCaseWorkspace}><HardDrive/><span><h3>My Documents</h3><p>Upload, verify and download case documents and preserved evidence.</p></span><ChevronRight/></button>
   <button className="toolCard" onClick={()=>{setScenario('traffic');openPolice()}}><Play/><span><h3>My Recordings</h3><p>Open legal-encounter recordings stored on this device and protected case copies.</p></span><ChevronRight/></button>
   <button className="toolCard" onClick={()=>openRights()}><ShieldAlert/><span><h3>Know My Rights</h3><p>Choose a situation and see calm, practical safety steps in plain language.</p></span><ChevronRight/></button>
   <button className="toolCard premiumCard" onClick={openPolice}><Car/><span><b className="premiumLabel"><ShieldCheck size={13}/> FREE WITH ACCOUNT</b><h3>Help Me Talk to Police</h3><p>Listen, suggest and read respectful responses aloud.</p></span><ChevronRight/></button>
  </section>
  <section className="learn" id="law-library"><div className="sectionTitle"><BookOpen/><div><h2>Funny, Weird & Surprising Georgia Law</h2><p>Browse free as a guest: real Georgia laws and court cases that sound made up, each with its citation and source.</p></div></div>
   <FunnyGeorgia/></section>
  <button className="encounterFab" onClick={()=>{setScenario('traffic');openPolice()}}><ShieldAlert size={20}/><span><b>Encounter Help</b><small>Open safety mode</small></span></button>
  {tool&&<div className="modalBack" onMouseDown={e=>{if(e.target===e.currentTarget)closeTool()}}><section className="toolModal" role="dialog" aria-modal="true" aria-label={tool==='avoid'?'Avoid trouble':tool==='case'?'Private case assistant':'Help me talk to police'}>
   <button className="close" onClick={closeTool} aria-label="Close"><X/></button>
   {tool==='avoid'?<><ShieldAlert className="modalLogo"/><h2>Avoid Trouble</h2><p>Choose the situation closest to what is happening. Safety comes first; this is general information, not a substitute for a lawyer.</p>
    <div className="scenarioButtons">{scenarioKeys.map(key=><button key={key} className={scenario===key?'active':''} onClick={()=>setScenario(key)}>{scenarios[key].label}</button>)}</div>
    <div className="guidance"><h3>{scenarios[scenario].title}</h3><ul>{scenarios[scenario].tips.map(tip=><li key={tip}>{tip}</li>)}</ul></div>
    <div className="dangerNote"><ShieldAlert/>If anyone is in immediate danger or needs medical care, call 911. Never physically resist or make sudden movements to operate the app.</div>
   </>:tool==='case'?<><MessageSquare className="modalLogo"/><h2>Private Case Assistant</h2><p>Organize the facts, identify research leads, test the opposing position, and build a record checklist. Only you can access cases through your signed-in account.</p>
    <div className="caseTabs"><button className={!activeCaseId?'active':''} onClick={startNewCase}>+ New case</button>{cases.map(item=><button key={item.id} className={activeCaseId===item.id?'active':''} onClick={()=>selectCase(item.id)}>{item.title}</button>)}</div>
    <form className="caseForm" onSubmit={saveCase}><div className="caseGrid"><label>Case title<input value={caseForm.title} onChange={e=>updateCaseForm('title',e.target.value)} placeholder="Example: Fulton County criminal case" required/></label><label>Case number<input value={caseForm.case_number} onChange={e=>updateCaseForm('case_number',e.target.value)} placeholder="If known"/></label><label>Georgia county<input value={caseForm.county} onChange={e=>updateCaseForm('county',e.target.value)} placeholder="County"/></label><label>Case type<select value={caseForm.case_type} onChange={e=>updateCaseForm('case_type',e.target.value)}><option value="criminal">Criminal</option><option value="appeal">Appeal</option><option value="habeas">Habeas / post-conviction</option><option value="probation">Probation / parole</option><option value="family">Family</option><option value="housing">Housing</option><option value="civil">Other civil</option></select></label><label>Current stage<select value={caseForm.stage} onChange={e=>updateCaseForm('stage',e.target.value)}><option value="investigation">Investigation</option><option value="charged">Charged / pretrial</option><option value="plea">Plea discussions</option><option value="trial">Trial</option><option value="sentencing">Sentencing</option><option value="appeal">Appeal</option><option value="habeas">Habeas / post-conviction</option><option value="probation">Probation or parole</option></select></label></div><label className="caseNarrative">What happened and what needs review<textarea value={caseForm.narrative} onChange={e=>updateCaseForm('narrative',e.target.value)} placeholder="Include important dates, charges, police actions, plea or trial history, sentence, prior appeals, and what records you have. Separate facts from assumptions."/></label>
     <div className="caseActions"><button type="submit" disabled={caseBusy}>{caseBusy?<LoaderCircle className="spin" size={16}/>:<Save size={16}/>}Save private case</button><button type="button" className="screenButton" disabled={caseBusy} onClick={runChargeCheck}><ShieldCheck size={16}/>Charge Check: what could I be charged with?</button><button type="button" className="screenButton" disabled={caseBusy} onClick={runCaseScreening}><ShieldCheck size={16}/>Run issue screening</button><button type="button" className="screenButton" disabled={caseBusy} onClick={checkActiveCaseMotions}><Scale size={16}/>Check motions & relief</button><button type="button" className="screenButton" disabled={caseBusy} onClick={checkDefenseStrategy}><ShieldCheck size={16}/>Defense-side review</button><button type="button" className="screenButton" disabled={caseBusy} onClick={findSimilarAuthorities}><Search size={16}/>Find similar Georgia cases</button>{findings.length>0&&<button type="button" onClick={exportCasePlan}><Download size={16}/>Export plan</button>}</div>
    </form>
    <div className="screeningNotice">This system identifies issues to investigate. It does not determine guilt, promise an outcome, or replace a licensed attorney.</div>{caseMotionResult&&<div className="replyCard"><small>Case-specific motions & relief review</small><p style={{whiteSpace:'pre-wrap'}}>{caseMotionResult}</p><small>Drafting or filing should happen only after current authority, deadlines, record facts and local court requirements are verified.</small></div>}{chargeCheck&&<div className="replyCard"><small>Charge Check (estimate)</small>{chargeCheck.emergency&&<p><b>{chargeCheck.emergency.message}</b> {chargeCheck.emergency.resources.map((r:any)=>r.label+': '+r.contact).join(' · ')}</p>}{chargeCheck.refused?<p>{chargeCheck.message}</p>:<><p>{chargeCheck.estimate_note}</p>{chargeCheck.message&&<p>{chargeCheck.message}</p>}{chargeCheck.charges.length>0&&<><h3>Likely charges</h3>{chargeCheck.charges.map((c:any,i:number)=><p key={i}><b>{c.charge}</b> ({c.level_label}) — <a href={c.citation.source_url} target="_blank" rel="noreferrer">{c.citation.citation}</a><br/>{c.why}<br/><small>{c.penalty?'Penalty (from the law): “'+c.penalty+'”':c.penalty_note}</small></p>)}</>}{chargeCheck.defenses.length>0&&<><h3>Possible defenses and weak spots</h3>{chargeCheck.defenses.map((x:any,i:number)=><p key={i}><b>{x.title}</b> <small>{x.kind_label}</small><br/>{x.explanation}{(x.citations||[]).map((c:any)=><a key={c.citation} href={c.source_url} target="_blank" rel="noreferrer"> {c.citation}</a>)}</p>)}</>}{chargeCheck.lowest_outcome.length>0&&<><h3>Ways to get the lowest outcome</h3>{chargeCheck.lowest_outcome.map((x:any,i:number)=><p key={i}><b>{x.title}</b><br/>{x.explanation}{(x.citations||[]).map((c:any)=><a key={c.citation} href={c.source_url} target="_blank" rel="noreferrer"> {c.citation}</a>)}</p>)}</>}{chargeCheck.lawyer_take&&<><h3>{chargeCheck.lawyer_take.label}</h3><p>{chargeCheck.lawyer_take.text}</p><small>{chargeCheck.lawyer_take.disclaimer}</small></>}<p><b>{chargeCheck.rights_reminder}</b></p></>}<small>{chargeCheck.disclaimer}</small></div>}{caseDefenseResult&&<div className="replyCard"><small>Potential defense strategy</small><p style={{whiteSpace:'pre-wrap'}}>{caseDefenseResult}</p><small>This reviews lawful arguments counsel could investigate. It does not decide guilt or predict an outcome.</small></div>}{similarAuthorities.length>0&&<div className="findings"><h3>Similar Georgia authority leads</h3>{similarAuthorities.map(item=><article key={item.id}><div className="findingHead"><b>{item.citation}</b><span>Match {item.match_score}</span></div><p>{item.title||'Untitled authority'}</p><small>{item.verified_versions.length?item.verified_versions.length+' verified source version(s)':'No verified source version linked yet'}</small>{item.source_url&&<p><a href={item.source_url} target="_blank" rel="noreferrer">Open source <ExternalLink size={14}/></a></p>}</article>)}</div>}
    <details className="protectionPanel"><summary><HardDrive size={18}/><span><b>Documents & evidence</b><small>Private files linked only to this saved case</small></span></summary>
     <div className="evidenceWorkspace"><label className="evidenceUpload"><Upload size={17}/><span>{evidenceBusy?'Working…':'Add document, photo, audio or video'}</span><input type="file" disabled={evidenceBusy||!activeCaseId} onChange={uploadCaseEvidence}/></label>
     {!activeCaseId&&<p>Save this case before adding evidence.</p>}
     {activeCaseId&&evidence.length===0&&<p>No files have been added to this case.</p>}
     {evidence.map(item=><article key={item.id}><div><b>{item.filename}</b><small>{item.media_type} · {formatBytes(item.bytes)}</small><small><Fingerprint size={11}/> SHA-256 {item.sha256}</small><small>{item.verified_at?'Integrity verified '+new Date(item.verified_at).toLocaleString():'Integrity not checked yet'}</small></div><div><button type="button" disabled={evidenceBusy} onClick={()=>verifyCaseEvidence(item)}><ShieldCheck size={15}/>Verify</button><button type="button" disabled={evidenceBusy} onClick={()=>downloadCaseEvidence(item)}><Download size={15}/>Download</button></div></article>)}</div>
    </details>
    {findings.length>0?<div className="findings"><h3>Screening leads</h3>{findings.map(item=><article key={item.id}><div className="findingHead"><b>{item.issue}</b><span>{item.confidence.replaceAll('_',' ')}</span></div><p>{item.analysis}</p><details><summary>Possible opposing position</summary><p>{item.counterargument}</p></details><details><summary>Records and facts needed</summary><p>{item.facts_needed}</p></details></article>)}</div>:activeCaseId&&<div className="emptyFindings">Save the facts, then run issue screening to create a review plan.</div>}
   </>:<><div className="premiumHeading"><Mic className="modalLogo"/><span className="premiumLabel"><ShieldCheck size={13}/> FREE LAUNCH</span></div><h2>Help Me Talk to Police</h2>
    <div className="dangerNote"><ShieldAlert/>Only use the phone when it is safe and permitted. Keep your hands visible, follow physical directions, and never let the app argue, resist, or interrupt.</div>
    <div className="scenarioButtons">{scenarioKeys.slice(0,5).map(key=><button key={key} className={scenario===key?'active':''} onClick={()=>{setScenario(key);setTranscript('')}}>{scenarios[key].label}</button>)}</div>
    <div className="listenBox"><div><b>Live listening</b><small>Your browser processes speech for suggestions. GA.LAW.HELP does not save the audio or transcript in this preview.</small></div>
     <button className={listening?'stopButton':'listenButton'} onClick={listening?stopListening:startListening}>{listening?<><Square size={16}/>Stop</>:<><Mic size={17}/>Start listening</>}</button>
    </div>
    <section className="cameraBox">
     <div><b>Optional camera</b><small>The camera stays off until you turn it on. Use it only when safe and permitted.</small></div>
     <button className={cameraOn?'stopButton':'listenButton'} onClick={cameraOn?stopCamera:startCamera}>{cameraOn?<><Square size={16}/>Camera off</>:<>Turn camera on</>}</button>
     {cameraOn&&<><div className="recordingActive"><span/>CAMERA ON — live preview only</div><video ref={cameraVideoRef} playsInline muted style={{width:'100%',borderRadius:'14px',marginTop:'10px',background:'#000'}}/></>}
     <small>GA.LAW.HELP does not silently activate the camera. This preview is not uploaded or analyzed by AI yet.</small>
    </section>
    <section className="recordingBox">
     <div className="recordingHead"><div><b><HardDrive size={17}/>Save audio on this device</b><small>Choose how long each new recording stays in this browser.</small></div><select value={retentionDays} onChange={e=>changeRetention(e.target.value)} aria-label="Recording retention period"><option value="180">180 days</option><option value="365">365 days</option><option value="400">400 days</option></select></div>
     <button className={recording?'recordStop':'recordStart'} onClick={recording?stopRecording:startRecording}>{recording?<><Square size={16}/>Stop and save recording</>:<><Circle size={17}/>Start local recording</>}</button>
     {recording&&<div className="recordingActive"><span/>Recording in progress — keep the phone visible and use it only when safe and permitted.</div>}
     <p className="recordingWarning">Record only when lawful. Consent and location rules can vary. Files remain in this browser profile, are removed when the app next opens after expiration, and may disappear earlier if the browser or phone clears site data. Download important recordings.</p>
     {recordings.length>0&&<div className="recordingList"><h3>Legal Encounter Evidence</h3><p className="recordingWarning">Your device copy stays separate from any protected GA.LAW.HELP copy. Download important evidence before clearing browser or phone data.</p>{recordings.map(row=><article key={row.id}><div><b>{scenarios[row.scenario].label}</b><span>{new Date(row.createdAt).toLocaleString()} · {formatBytes(row.blob.size)}</span>{row.interrupted&&<small><b>RECOVERED AFTER INTERRUPTION</b></small>}<small>{row.mimeType.startsWith('video/')?'Video + audio':'Audio'} · Expires {new Date(row.expiresAt).toLocaleDateString()}</small><small>{row.cloudCopiedAt?'Protected GA.LAW.HELP copy saved '+new Date(row.cloudCopiedAt).toLocaleString():'Device copy'}</small>{row.sha256&&<small className="hashLine"><Fingerprint size={11}/>SHA-256 {row.sha256}</small>}</div><div><button onClick={()=>playRecording(row)} aria-label="Play recording"><Play size={16}/></button><button onClick={()=>downloadRecording(row)} aria-label="Download your copy"><Download size={16}/></button><button className="deleteRecording" onClick={()=>removeRecording(row)} aria-label="Delete device copy"><Trash2 size={16}/></button></div></article>)}</div>}
    </section>
    <details className="protectionPanel"><summary><Scale size={18}/><span><b>Check My Case for Motions</b><small>Private case tool. Uses the verified motion registry and requires sign-in.</small></span></summary>
<label className="incidentNotes">Case information<textarea value={motionFacts} onChange={e=>setMotionFacts(e.target.value)} placeholder="Court/county, charges, case stage, arrest/indictment/plea/trial/sentencing dates, sentence, searches/statements, evidence issues, appeal history, and documents available."/></label>
<button className="primary" disabled={motionBusy} onClick={screenMotions}>{motionBusy?<><LoaderCircle className="spin" size={17}/>Checking case…</>:<><Scale size={17}/>Check My Case for Motions</>}</button>
{motionResult&&<div className="replyCard"><small>Motion & relief screening</small><p style={{whiteSpace:'pre-wrap'}}>{motionResult}</p><small>Legal information, not legal advice. Verify current authority, deadlines, local rules and filing requirements before filing.</small></div>}
</details>
<details className="protectionPanel"><summary><ClipboardList size={18}/><span><b>Build an incident report</b><small>Saved locally as you type</small></span></summary>
     <div className="incidentGrid"><label>Encounter began<input type="datetime-local" value={incident.startedAt} onChange={e=>updateIncident('startedAt',e.target.value)}/></label><label>Location<input value={incident.location} onChange={e=>updateIncident('location',e.target.value)} placeholder="Address or coordinates"/></label><label>Agency<input value={incident.agency} onChange={e=>updateIncident('agency',e.target.value)} placeholder="Police or sheriff department"/></label><label>Officer name<input value={incident.officer} onChange={e=>updateIncident('officer',e.target.value)} placeholder="If known"/></label><label>Badge number<input value={incident.badge} onChange={e=>updateIncident('badge',e.target.value)} inputMode="numeric" placeholder="If visible"/></label><label>Vehicle / unit<input value={incident.vehicle} onChange={e=>updateIncident('vehicle',e.target.value)} placeholder="Patrol car or unit number"/></label></div>
     <button className="locationButton" onClick={captureLocation}><MapPin size={16}/>Add my current coordinates</button>
     <label className="incidentNotes">Timeline and notes<textarea value={incident.notes} onChange={e=>updateIncident('notes',e.target.value)} placeholder="Write only what you remember. Separate what you personally saw or heard from what someone else told you."/></label>
     <div className="incidentActions"><button onClick={exportIncident}><Download size={16}/>Export report</button><button className="clearReport" onClick={clearIncident}><Trash2 size={16}/>Clear</button></div>
    </details>
    <details className="protectionPanel"><summary><UserPlus size={18}/><span><b>Trusted contact check-in</b><small>Contact details stay on this device</small></span></summary>
     <div className="trustedFields"><label>Contact name<input value={trusted.name} onChange={e=>updateTrusted('name',e.target.value)} placeholder="Family member or trusted person"/></label><label>Mobile number<input type="tel" value={trusted.phone} onChange={e=>updateTrusted('phone',e.target.value)} placeholder="Phone number"/></label></div>
     <p className="trustedNote">The app prepares a message, but you choose whether and how to send it. Automatic silent messages are not sent.</p>
     <div className="trustedActions"><button onClick={()=>shareSafetyStatus(false)}><Send size={16}/>Share encounter started</button><button className="safeButton" onClick={()=>shareSafetyStatus(true)}><CheckCircle2 size={16}/>Send “I’m safe”</button></div>
    </details>
    <details className="protectionPanel"><summary><Phone size={18}/><span><b>Reach real legal help</b><small>Independent lawyer and legal-aid resources</small></span></summary>
     <div className="legalHelpLinks"><a href="https://www.glsp.org/" target="_blank" rel="noreferrer"><b>Georgia Legal Services Program</b><span>Statewide civil legal aid outside metro Atlanta</span><ExternalLink size={16}/></a><a href="https://atlantalegalaid.org/" target="_blank" rel="noreferrer"><b>Atlanta Legal Aid</b><span>Civil legal aid in the Atlanta area</span><ExternalLink size={16}/></a><a href="https://www.gabar.org/" target="_blank" rel="noreferrer"><b>State Bar of Georgia</b><span>Find public resources and Georgia lawyers</span><ExternalLink size={16}/></a><a href="https://www.lsc.gov/about-lsc/what-legal-aid/i-need-legal-help" target="_blank" rel="noreferrer"><b>Legal Services Corporation</b><span>Search for funded legal aid by location</span><ExternalLink size={16}/></a></div>
     <p className="lawyerBoundary">Opening a resource does not create an attorney-client relationship. A lawyer must accept the matter and confirm representation.</p>
    </details>
        <label className="transcriptLabel">What was heard<textarea value={transcript} onChange={e=>setTranscript(e.target.value)} placeholder="The live transcript will appear here. You can also type what the officer said."/></label>
    <div className="replyCard"><small>{encounterBusy?'AI is preparing a fast response…':'Suggested calm response'}</small><p>{encounterReply||suggestedReply(transcript,scenario)}</p><button onClick={()=>speak(encounterReply||suggestedReply(transcript,scenario))}><Volume2 size={17}/>Read this aloud</button></div>
    <button className="rightsButton" onClick={()=>speak(rightsStatement)}><ShieldCheck size={18}/><span><b>Read my rights statement aloud</b><small>States silence, no consent to search, request for counsel, and no resistance.</small></span></button>
    <div className="sourceLinks"><span>General constitutional references:</span><a href="https://constitution.congress.gov/constitution/amendment-4/" target="_blank" rel="noreferrer">Fourth Amendment</a><a href="https://constitution.congress.gov/constitution/amendment-5/" target="_blank" rel="noreferrer">Fifth Amendment</a><a href="https://constitution.congress.gov/constitution/amendment-6/" target="_blank" rel="noreferrer">Sixth Amendment</a></div>
    <small className="previewNote">Preview access is enabled for testing. A secure subscription checkout must be connected before customers can be charged.</small>
   </>}
  </section></div>}
  {!FREE_LAUNCH&&paywallOpen&&<div className="modalBack" onMouseDown={e=>{if(e.target===e.currentTarget)setPaywallOpen(false)}}><section className="modal paywallModal" role="dialog" aria-modal="true" aria-label="Paid membership required">
   <button className="close" onClick={()=>setPaywallOpen(false)} aria-label="Close"><X/></button><LockKeyhole className="modalLogo"/><span className="eyebrow">GA.LAW.HELP Membership</span><h2>Paid feature</h2>
   <p>Ask GA.LAW.HELP, rights guidance, and police-encounter help stay free and do not require sign-in. Private cases, documents, case recordings, motion screening, and defense analysis stay login-only.</p>
   {!user?<div className="paywallActions"><button className="primary" onClick={()=>{setPaywallOpen(false);setMode('register');setAuthOpen(true)}}>Create account</button><button onClick={()=>{setPaywallOpen(false);setMode('login');setAuthOpen(true)}}>Sign in</button></div>:<><div className="membershipStatus"><ShieldCheck/><span><b>Signed in — membership inactive</b><small>Your free account can still use guest rights research. Private case tools stay signed-in only.</small></span></div><button className="primary membershipCheckout" disabled={billingBusy} onClick={startCheckout}>{billingBusy?<><LoaderCircle className="spin" size={16}/>Opening secure checkout…</>:<>Start paid membership</>}</button></>}
   <small className="previewNote">Checkout opens on Stripe. Access unlocks only after Stripe confirms the subscription.</small>
  </section></div>}
  {authOpen&&<div className="modalBack" onMouseDown={e=>{if(e.target===e.currentTarget&&mode!=='reset')setAuthOpen(false)}}><section className={`modal authModal ${mode==='register'?'registerMode':''}`} role="dialog" aria-modal="true" aria-label="Account access">
   <button className="close" onClick={()=>{if(mode==='reset')window.history.replaceState({},'', '/');setAuthOpen(false)}} aria-label="Close"><X/></button>
   <div className="authHeading"><span className="authIcon"><Scale/></span><div><span className="eyebrow">{mode==='login'?'Private workspace':mode==='register'?'Secure account setup':'Account recovery'}</span><h2>{authTitle}</h2><p>{authIntro}</p></div></div>
   {(mode==='login'||mode==='register')&&<div className="tabs" aria-label="Choose account action"><button type="button" className={mode==='login'?'active':''} onClick={()=>{setMode('login');setAuthError('');setShowPassword(false)}}>Sign in</button><button type="button" className={mode==='register'?'active':''} onClick={()=>{setMode('register');setAuthError('');setShowPassword(false)}}>Create account</button></div>}
   {mode==='register'&&<div className="accountBenefits" aria-label="Account benefits">
    <div><LockKeyhole size={19}/><span><b>Private workspace</b><small>Keep saved case work behind your sign-in.</small></span></div>
    <div><ShieldCheck size={19}/><span><b>Security starts here</b><small>Use a unique password you do not use elsewhere.</small></span></div>
   </div>}
   <form onSubmit={submitAuth}>
    {mode!=='reset'&&<label>Email address<input type="email" value={email} onChange={e=>setEmail(e.target.value)} autoComplete="email" placeholder="you@example.com" required/></label>}
    {mode!=='forgot'&&<label>{mode==='reset'?'New password':'Password'}<div className="passwordInput"><input type={showPassword?'text':'password'} value={password} onChange={e=>setPassword(e.target.value)} autoComplete={mode==='login'?'current-password':'new-password'} minLength={mode==='login'?1:15} maxLength={mode==='login'?undefined:128} aria-describedby={mode==='register'||mode==='reset'?'password-help':undefined} aria-invalid={(mode==='register'||mode==='reset')&&password.length>0&&!passwordAccepted} required/><button type="button" onClick={()=>setShowPassword(value=>!value)} aria-label={showPassword?'Hide password':'Show password'}>{showPassword?<EyeOff size={18}/>:<Eye size={18}/>}</button></div></label>}
    {(mode==='register'||mode==='reset')&&<div className="passwordGuide" id="password-help">
     <div className={`passwordRule ${passwordAccepted?'met':''}`}><CheckCircle2 size={18}/><span><b>15–128 characters required</b><small>{password.length?password.length+' characters entered':'Spaces count and are allowed.'}</small></span></div>
     <div className="passwordTip"><Fingerprint size={18}/><span><b>Make it memorable and unique</b><small>Try four or more unrelated words, or use a password manager. Capital letters, numbers and symbols are allowed, but not required.</small></span></div>
    </div>}
    {authError&&<div className="error" role="alert">{authError}</div>}
    <button className="primary accountSubmit" disabled={authBusy||((mode==='register'||mode==='reset')&&!passwordAccepted)}>{authBusy?<><LoaderCircle className="spin" size={17}/>Please wait</>:mode==='login'?'Sign in securely':mode==='register'?'Create secure account':mode==='forgot'?'Send reset link':'Save new password'}</button>
    {mode==='login'&&<button type="button" className="authLink" onClick={()=>{setMode('forgot');setAuthError('');setPassword('')}}>Forgot your password?</button>}
    {mode==='login'&&authError.toLowerCase().includes('verification')&&<button type="button" className="authLink" onClick={resendVerification}>Send a new verification email</button>}
    {(mode==='forgot'||mode==='reset')&&<button type="button" className="authLink" onClick={()=>{if(mode==='reset')window.history.replaceState({},'', '/');setMode('login');setAuthError('');setPassword('')}}>Back to sign in</button>}
    {mode==='register'&&<small className="accountFinePrint">Public legal learning remains available without an account.</small>}
   </form></section></div>}
 </main>
}