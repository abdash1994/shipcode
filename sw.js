/* ShipCode service worker: app shell works offline; the Python and SQL engines are cached after first use. */
const V="shipcode-3a9a58a7fe",SHELL=["/","/manifest.webmanifest","/icon-192.png","/icon-512.png","/fonts/inter-latin-wght-normal.woff2","/fonts/jetbrains-mono-latin-wght-normal.woff2"];
const CDN=/^https:\/\/(cdn\.jsdelivr\.net|fonts\.googleapis\.com|fonts\.gstatic\.com)\//;
self.addEventListener("install",e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener("fetch",e=>{
  const r=e.request;if(r.method!=="GET")return;const u=new URL(r.url);
  if(r.mode==="navigate"){e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(V).then(c=>c.put("/",cp));return res;}).catch(()=>caches.match("/")));return;}
  if(u.origin===location.origin||CDN.test(r.url)){
    e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{if(res&&(res.ok||res.type==="opaque")&&!r.headers.has("range")){const cp=res.clone();caches.open(V).then(c=>c.put(r,cp));}return res;})));}
});
