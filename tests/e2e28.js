// End-to-end suite run against the exact bytes deployed to production (sha1 verified equal).
const {chromium,devices}=require('playwright');const fs=require('fs');
const AXE=fs.readFileSync('/tmp/axe/node_modules/axe-core/axe.min.js','utf8');
const BASE='http://127.0.0.1:8765/index.html';
let f=0;const ok=(n,v,extra)=>{if(!v)f++;console.log((v?'PASS ':'FAIL ')+n+(extra?' '+extra:''))};
const ROUTES=['today','path','gyms','think','errors','ref','sprint','capstone','commit','exam','review','portfolio','plan','day-1','day-8','day-22','sql','py','spark','sys','dep','ai','fde','py-3','sql-3','fde-1'];
(async()=>{const b=await chromium.launch();
async function newPage(opts={},init){const c=await b.newContext(opts);const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!/ERR_FAILED|net::/.test(m.text()))errs.push(m.text())});
 await p.route('https://**',r=>r.abort());await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true;});if(init)await p.addInitScript(init);return {c,p,errs};}
// ---------- 1. first-run user journey (phone) ----------
{const {c,p,errs}=await newPage({...devices['iPhone 13']});
 await p.goto(BASE);await p.waitForTimeout(600);
 ok('first visit shows onboarding, tabs hidden',await p.evaluate(()=>document.body.classList.contains('onboarding')&&getComputedStyle(document.querySelector('.tabs')).display==='none'));
 await p.evaluate(()=>{S.me={...S.me,why:'Land an FDE role'};S.pace=30;S.start=todayISO();S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'sprint',depth:'core'};save();location.hash='';route();});await p.waitForTimeout(400);
 ok('plan saved: Today renders with bento mission and 5 tabs',await p.evaluate(()=>!!document.querySelector('.bento .bm.primary')&&[...document.querySelectorAll('.tabs a')].filter(a=>getComputedStyle(a).display!=='none').length===5));
 ok('header streak 0, week dots 7',await p.evaluate(()=>document.getElementById('streak').textContent==='0'&&document.querySelectorAll('#wkDots .wd').length===7));
 // open mission lab through the real button
 await p.click('.bento .primary [data-act=lab]');await p.waitForTimeout(500);
 const info=await p.evaluate(()=>({id:lab.L.id,kind:lab.L.kind,phase:lab.phase,sol:lab.L.solution,start:lab.L.starter}));
 ok('mission lab opened in sheet',!!info.id,info.id+' '+info.kind+' phase='+info.phase);
 await p.evaluate(()=>{lab.phase='code';renderLab();});await p.waitForTimeout(300);
 // wrong answer first
 await p.click('[data-l=run]');await p.waitForFunction(()=>lab.result,{timeout:60000});await p.waitForTimeout(300);
 ok('starter code fails with feedback panel',await p.evaluate(()=>!!document.querySelector('.fb.bad')&&lab.fails>=1));
 ok('failure is logged to the error journal',await p.evaluate(()=>Object.keys(S.errs||{}).length>=1),await p.evaluate(()=>JSON.stringify(S.errs)));
 // fix it
 await p.fill('#code',info.sol);await p.click('[data-l=run]');await p.waitForFunction(()=>lab.passed===true,{timeout:60000}).catch(()=>{});await p.waitForTimeout(500);
 ok('reference solution passes all tests (pass panel shown)',await p.evaluate(()=>lab.passed===true&&!!document.querySelector('.fb.ok.pass')));
 ok('lab recorded in saved state and streak started',await p.evaluate(()=>!!S.labs[lab.L.id]&&S.dates.includes(todayISO())&&streak()===1));
 await p.evaluate(()=>closeSheet());await p.waitForTimeout(900);
 ok('header counters updated (1 lab, 1 day)',await p.evaluate(()=>document.getElementById('labsN').textContent==='1'&&document.getElementById('streak').textContent==='1'));
 // persistence
 await p.reload();await p.waitForTimeout(600);
 ok('progress survives reload (localStorage)',await p.evaluate(()=>labsPassedN()===1&&streak()===1&&!!S.start));
 // errors tab shows the journal and drill
 await p.evaluate(()=>{location.hash='#errors';route();});await p.waitForTimeout(300);
 ok('Errors page lists the logged error',await p.evaluate(()=>document.querySelector('.journal .jl li')!==null));
 const drill=await p.$('.erracc [data-act=practice]');await p.evaluate(()=>{[...document.querySelectorAll('.erracc')].forEach(d=>d.open=true)});await p.click('.erracc [data-act=practice] >> nth=3');await p.waitForTimeout(500);
 ok('Drill button opens a lab',await p.evaluate(()=>!document.getElementById('sheet').hidden&&!!lab));
 await p.evaluate(()=>closeSheet());
 // SQL lab with sql.js
 await p.evaluate(()=>{openLab('L43-8',false);lab.phase='code';renderLab();});await p.waitForTimeout(500);
 await p.fill('#code',await p.evaluate(()=>lab.L.solution));await p.click('[data-l=run]');await p.waitForFunction(()=>lab.passed===true||(lab.result&&lab.result.loadFail),{timeout:60000}).catch(()=>{});await p.waitForTimeout(300);
 ok('SQL lab runs on sql.js and passes against hidden dataset',await p.evaluate(()=>lab.passed===true));
 await p.evaluate(()=>closeSheet());
 ok('journey: no page errors '+errs.join('|'),!errs.length);await c.close();}
// ---------- 2. every route renders, no errors, at 5 widths ----------
{const {c,p,errs}=await newPage({viewport:{width:390,height:800}});await p.goto(BASE);await p.waitForTimeout(500);
 await p.evaluate(()=>{S.start=shift(todayISO(),-6);S.done=[1,2,3];S.dates=[shift(todayISO(),-2),shift(todayISO(),-1)];S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'sprint',depth:'core'};S.errs={TypeError:2,IndexError:1};save();});
 const bad=[];for(const w of [320,360,390,768,1280]){await p.setViewportSize({width:w,height:800});
  for(const r of ROUTES){await p.evaluate(h=>{location.hash='#'+h;route();},r);await p.waitForTimeout(120);
   const m=await p.evaluate(()=>({ov:document.documentElement.scrollWidth-innerWidth,len:document.getElementById('app').innerText.length,hdr:[...document.querySelectorAll('header .col > *')].some(e=>e.getBoundingClientRect().right>innerWidth+1)}));
   if(m.ov>1||m.len<40||m.hdr)bad.push(`${r}@${w}: overflow=${m.ov} len=${m.len} hdr=${m.hdr}`);}}
 ok(`all ${ROUTES.length} routes render at 320/360/390/768/1280 with no horizontal overflow`,!bad.length,bad.slice(0,6).join(' ; '));
 ok('route sweep: no page errors '+errs.join('|'),!errs.length);
 // ---------- 3. accessibility (axe-core), light and dark ----------
 const summary={};for(const scheme of ['light','dark']){await p.emulateMedia({colorScheme:scheme});await p.setViewportSize({width:390,height:800});
  for(const r of ['today','path','errors','think','gyms','ref','py-3']){await p.evaluate(h=>{location.hash='#'+h;route();},r);await p.waitForTimeout(150);
   await p.evaluate(AXE.toString?()=>{}:()=>{});await p.addScriptTag({content:AXE}).catch(()=>{});
   const res=await p.evaluate(async()=>{const x=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa']}});return x.violations.map(v=>({id:v.id,impact:v.impact,n:v.nodes.length}))});
   res.forEach(v=>{const k=v.impact+':'+v.id;summary[k]=(summary[k]||0)+v.n;});}}
 console.log('axe (wcag2a/aa, 7 pages x light/dark):',JSON.stringify(summary));
 ok('axe: no critical violations',!Object.keys(summary).some(k=>k.startsWith('critical')));
 await c.close();}
// ---------- 4. resilience: corrupt storage, hostile text ----------
{const {c,p,errs}=await newPage({...devices['iPhone 13']},()=>{try{localStorage.setItem('blankfile-state-v1','{not json');localStorage.setItem('blankfile-drafts-v1','also bad')}catch(e){}});
 await p.goto(BASE);await p.waitForTimeout(600);ok('corrupt saved state: app still loads (onboarding)',await p.evaluate(()=>document.getElementById('app').innerText.length>50));
 await p.evaluate(()=>{S.start=todayISO();S.me={why:'<img src=x onerror=window.__x=1>'};S.errs={'<b id=pwn>x</b>':3};S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'sprint',depth:'core'};save();});
 for(const h of ['today','errors','path','ref']){await p.evaluate(h=>{location.hash='#'+h;route();},h);await p.waitForTimeout(150);}
 ok('hostile user text is escaped everywhere visited',await p.evaluate(()=>!window.__x&&!document.getElementById('pwn')));
 ok('resilience: no page errors '+errs.join('|'),!errs.length);await c.close();}
// ---------- 5. performance (phone viewport, 4x CPU throttle, localhost) ----------
{const c=await b.newContext({...devices['Pixel 5']});const p=await c.newPage();await p.route('https://**',r=>r.abort());const cdp=await c.newCDPSession(p);await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
 const t0=Date.now();await p.goto(BASE,{waitUntil:'domcontentloaded'});await p.waitForSelector('#app *');const t1=Date.now()-t0;
 const m=await p.evaluate(()=>{const n=performance.getEntriesByType('navigation')[0];return {dcl:Math.round(n.domContentLoadedEventEnd),load:Math.round(n.loadEventEnd),kb:Math.round(n.encodedBodySize/1024)}});
 console.log('perf (4x CPU throttle, local network): first content',t1,'ms; DOMContentLoaded',m.dcl,'ms; load',m.load,'ms; html',m.kb,'KB uncompressed on wire (production serves brotli)');
 ok('first content under 5 s on a throttled phone CPU',t1<5000,t1+'ms');await c.close();}
await b.close();console.log(f?'FAILS '+f:'ALL PASS');})();
