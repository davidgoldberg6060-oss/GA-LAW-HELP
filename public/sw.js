const CACHE='ga-law-help-shell-v1';
const CORE=['/manifest.webmanifest','/icons/icon-192.png','/icons/icon-512.png'];
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const cache=await caches.open(CACHE);const shell=await fetch('/',{cache:'reload'});const html=await shell.clone().text();
 const assets=[...html.matchAll(/(?:src|href)="([^"]+\.(?:js|css))"/g)].map(match=>match[1]).filter(path=>path.startsWith('/'));
 await cache.put('/',shell);await cache.addAll([...CORE,...assets]);await self.skipWaiting();
})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 const keys=await caches.keys();await Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key)));await self.clients.claim();
})()));
self.addEventListener('fetch',event=>{
 const request=event.request;if(request.method!=='GET')return;
 const url=new URL(request.url);if(url.origin!==self.location.origin)return;
 if(request.mode==='navigate'){
  event.respondWith((async()=>{try{const fresh=await fetch(request);const cache=await caches.open(CACHE);cache.put('/',fresh.clone());return fresh}catch{return(await caches.match('/'))||Response.error()}})());return;
 }
 event.respondWith((async()=>{const cached=await caches.match(request);if(cached)return cached;const fresh=await fetch(request);if(fresh.ok){const cache=await caches.open(CACHE);cache.put(request,fresh.clone())}return fresh})());
});
