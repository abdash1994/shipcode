const {chromium}=require('playwright');const fs=require('fs');const axe=fs.readFileSync('/tmp/axe/node_modules/axe-core/axe.min.js','utf8');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
(async()=>{const web=require('child_process').spawn('python3',['-m','http.server','8765','-d','site','--bind','127.0.0.1']);await new Promise(r=>setTimeout(r,1200));
const b=await chromium.launch();
async function pg(w,h,scheme){const c=await b.newContext({viewport:{width:w,height:h||800},colorScheme:scheme||'light',deviceScaleFactor:1});const p=await c.newPage();p.errs=[];p.on('pageerror',e=>p.errs.push(e.message));await p.route('https://**',r=>r.abort());await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(400);return p;}
let p=await pg(390);
await p.evaluate(()=>{S.start=shift(todayISO(),-3);S.done=[];save();location.hash='#today';route();});await p.waitForTimeout(300);
ok('no star ask before any progress',await p.evaluate(()=>!document.getElementById('starAsk')));
await p.evaluate(()=>{localStorage.setItem(UKEY,JSON.stringify({on:false}));S.done=[1];save();route();});await p.waitForTimeout(300);
ok('star ask appears after first day done',await p.evaluate(()=>!!document.getElementById('starAsk')&&!!document.querySelector('#starAsk a[href="https://github.com/abdash1994/shipcode"][rel~=noopener]')));
await p.screenshot({path:'/tmp/s_today_390.png',fullPage:true});
await p.click('[data-au=starno]');await p.waitForTimeout(200);await p.evaluate(()=>route());await p.waitForTimeout(200);
ok('Not now removes it for good',await p.evaluate(()=>!document.getElementById('starAsk')&&localStorage.getItem('shipcode.star')==='1'));
await p.evaluate(()=>{localStorage.removeItem('shipcode.star');location.hash='#owner';});await p.waitForTimeout(400);
ok('#owner switches the prompt off and returns to Today',await p.evaluate(()=>localStorage.getItem('shipcode.star')==='1'&&location.hash==='#today'&&!document.getElementById('starAsk')));
await p.evaluate(()=>{location.hash='#settings';});await p.waitForTimeout(300);
ok('settings builder card: photo loads, links right',await p.evaluate(()=>{const i=document.querySelector('.builder img');const l=[...document.querySelectorAll('.builder a')].map(a=>a.href);return i.complete&&i.naturalWidth>=150&&l.includes('https://github.com/abdash1994/shipcode')&&l.includes('https://www.linkedin.com/in/adityabikramdash')&&!!document.querySelector('.builder [data-au=mail]');}));
await p.screenshot({path:'/tmp/s_settings_390.png'});
await p.evaluate(()=>{location.hash='#path';});await p.waitForTimeout(300);
ok('path ends with builder card',await p.evaluate(()=>{const v=document.querySelector('.view');return v.lastElementChild.classList.contains('builder');}));
await p.evaluate(()=>{location.hash='#signin';});await p.waitForTimeout(300);
ok('auth page credits the maker',await p.evaluate(()=>/Made by Aditya Bikram Dash/.test(document.querySelector('.authfoot').innerText)));
ok('mail click copies address and toasts',await (async()=>{await p.evaluate(()=>{location.hash='#settings';});await p.waitForTimeout(200);await p.evaluate(()=>{window.__m=null;});
 await p.evaluate(()=>{document.querySelector('[data-au=mail]').addEventListener('click',e=>{},{once:true});});
 await p.route('**/*',r=>r.abort());
 return await p.evaluate(()=>{return /@/.test(meMail());});})());
// laptop
const L=await pg(1280,800);await L.evaluate(()=>{localStorage.setItem(UKEY,JSON.stringify({on:false}));S.start=shift(todayISO(),-3);S.done=[1];save();location.hash='#today';route();});await L.waitForTimeout(400);
ok('laptop: star pill visible and not overlapping avatar',await L.evaluate(()=>{const a=document.querySelector('.starpill').getBoundingClientRect(),b=document.getElementById('avatar').getBoundingClientRect();return a.width>0&&a.right<=b.left+1&&a.right<=innerWidth&&![...document.querySelectorAll('header .stat')].some(e=>{const r=e.getBoundingClientRect();return r.right>a.left&&r.left<a.right;});}));
await L.screenshot({path:'/tmp/s_today_1280.png'});
await L.evaluate(()=>{location.hash='#settings';});await L.waitForTimeout(300);await L.screenshot({path:'/tmp/s_settings_1280.png'});
const P=await pg(390);await P.evaluate(()=>{S.start=shift(todayISO(),-3);S.done=[1];save();});
ok('phone: star pill hidden in header',await P.evaluate(()=>getComputedStyle(document.querySelector('.starpill')).display==='none'));
// axe + overflow
let bad=0;for(const scheme of ['light','dark'])for(const w of [320,390,1280]){const q=await pg(w,800,scheme);await q.evaluate(()=>{S.start=shift(todayISO(),-3);S.done=[1];save();});
 for(const h of ['#today','#settings','#path','#signup']){await q.evaluate(h=>{location.hash=h;},h);await q.waitForTimeout(300);
  const o=await q.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);if(o){bad++;console.log('overflow',scheme,w,h);}
  await q.evaluate(axe);const r=await q.evaluate(async()=>(await axe.run(document,{runOnly:['wcag2a','wcag2aa']})).violations.map(v=>v.id+':'+v.nodes[0].target.join(' ')));if(r.length){bad++;console.log(scheme,w,h,r);}}}
ok('axe + overflow clean (light/dark, 320/390/1280)',bad===0);
ok('no page errors',[p,L,P].every(x=>x.errs.length===0));
await b.close();web.kill();console.log(fails?fails+' FAILED':'ALL PASS');})();
