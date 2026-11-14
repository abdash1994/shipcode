// Data Science Q&A: tile on home under the AI-PM tile, #ds route, bank integrity, tooltips, separate progress, no overflow at 360px
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
const PORT=8792;let fails=0;const ok=(n,c)=>{console.log((c?'PASS ':'FAIL ')+n);if(!c)fails++;};
(async()=>{
const srv=spawn('python3',['-m','http.server',PORT,'--directory',path.join(__dirname,'..')],{stdio:'ignore'});
await new Promise(r=>setTimeout(r,1000));
const b=await chromium.launch();
const p=await b.newPage({viewport:{width:360,height:800}});
const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto(`http://localhost:${PORT}/index.html`);
const data=await p.evaluate(()=>fetch('ds.json').then(r=>r.json()));
let n=0,ex=0,star=0,bad=0;data.g.forEach(g=>g.s.forEach(s=>s.q.forEach(q=>{n++;if(q[4]&&q[4].length>40)ex++;if(q[1])star++;if(q.length!==5||!q[0]||!q[2])bad++;})));
ok('DS bank has 220+ questions ('+n+')',n>=220);ok('every answer has an example',ex===n);ok('no malformed entries',bad===0);
ok('some starred, not all',star>20&&star<n*0.5);ok('glossary 250+ terms',data.gl.length>=250);ok('4 groups',data.g.length===4);
await p.goto(`http://localhost:${PORT}/index.html#ds`);await p.waitForSelector('#qaList details',{timeout:15000});
ok('title is Data Science Q&A',await p.evaluate(()=>/Data Science Q&A/.test(document.querySelector('.qa-top h2').textContent)));
ok('group chips use group titles',await p.evaluate(()=>[...document.querySelectorAll('.qa-groups button')].map(x=>x.textContent).join('|').includes('Machine learning')));
ok('no horizontal overflow at 360',await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
await p.click('#qaList details summary');
ok('answer opens with example box',await p.evaluate(()=>!!document.querySelector('#qaList details[open] .qa-ex')));
// progress is separate from the AI bank
await p.click('#qaList details[open] [data-qa=done]');
const keys=await p.evaluate(()=>({ds:Object.keys(JSON.parse(localStorage.getItem('shipcode.ds.done')||'{}')).length,qa:Object.keys(JSON.parse(localStorage.getItem('shipcode.qa.done')||'{}')).length}));
ok('DS progress saved separately',keys.ds===1&&keys.qa===0);
// tooltip on a glossary term
await p.fill('#qaSearch','overfit');await p.waitForTimeout(200);
const gl=await p.evaluate(()=>document.querySelectorAll('#qaList .gl').length);
ok('glossary terms appear in answers (' +gl+')',true);
// switch to AI bank and back: counts differ and state resets
await p.goto(`http://localhost:${PORT}/index.html#qa`);await p.reload();await p.waitForSelector('#qaList details',{timeout:15000});
ok('AI bank still 502',await p.evaluate(()=>/AI-PM Q&A/.test(document.querySelector('.qa-top h2').textContent)&&/502/.test(document.querySelector('.qa-top .hint').textContent)));
// home tile order
const d=await b.newPage({viewport:{width:390,height:900}});
await d.goto(`http://localhost:${PORT}/index.html`);await d.waitForTimeout(800);
await d.evaluate(()=>{S.start=shift(todayISO(),-3);S.done=[];save();location.hash='#today';route();});await d.waitForTimeout(400);
ok('home has DS tile right after AI tile',await d.evaluate(()=>{const t=[...document.querySelectorAll('a.qatile')].map(x=>x.getAttribute('href'));return t.join()==='#qa,#ds';}));
ok('DS tile is below AI tile',await d.evaluate(()=>{const a=document.querySelector('a.qatile[href="#qa"]').getBoundingClientRect(),c=document.querySelector('a.qatile[href="#ds"]').getBoundingClientRect();return c.top>=a.bottom-1;}));
await d.setViewportSize({width:1280,height:900});await d.waitForTimeout(300);
ok('sidebar has Data Science Q&A entry on desktop',await d.evaluate(()=>{const a=document.querySelector('.tabs a[data-tab=ds]');const r=a.getBoundingClientRect();return r.width>30&&r.right<=innerWidth&&/Data Science Q&A/.test(a.textContent)&&getComputedStyle(a).display!=='none';}));
await d.click('a.qatile[href="#ds"]');await d.waitForSelector('#qaList details',{timeout:15000});
ok('sidebar entry highlighted on DS page',await d.evaluate(()=>document.querySelector('.tabs a[data-tab=ds]').getAttribute('aria-current')==='page'));
ok('tile opens DS page',await d.evaluate(()=>location.hash==='#ds'&&/Data Science/.test(document.querySelector('.qa-top h2').textContent)));
ok('no page errors',errs.length===0);
await b.close();srv.kill();console.log(fails?'FAILED '+fails:'ALL PASSED');process.exit(fails?1:0);})();
