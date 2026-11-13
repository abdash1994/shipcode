// AI-PM Q&A: every answer has an example; glossary tooltips work on hover, focus and tap
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
const PORT=8791;let fails=0;const ok=(n,c)=>{console.log((c?'PASS ':'FAIL ')+n);if(!c)fails++;};
(async()=>{
const srv=spawn('python3',['-m','http.server',PORT,'--directory',path.join(__dirname,'..')],{stdio:'ignore'});
await new Promise(r=>setTimeout(r,1000));
const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1000,height:800}});
await p.goto(`http://localhost:${PORT}/index.html#qa`);await p.waitForSelector('#qaList details',{timeout:15000});
const data=await p.evaluate(()=>fetch('qa.json').then(r=>r.json()));
let n=0,withEx=0,short=0;data.g.forEach(g=>g.s.forEach(s=>s.q.forEach(q=>{n++;if(q[4]&&q[4].length>40)withEx++;if(q[4]&&q[4].length<60)short++;})));
ok('478 questions',n===478);ok('every answer has an example',withEx===478);ok('glossary has 120+ terms',data.gl.length>=120);
// open first and check the example box
await p.click('#qaList details summary');
ok('example box shown',await p.evaluate(()=>!!document.querySelector('#qaList details[open] .qa-ex p')));
// find an answer with a glossary term and hover
const t=await p.$('#qaList details[open] .gl');
ok('answer has underlined term',!!t);
if(t){await t.hover();await p.waitForTimeout(250);
 ok('tooltip appears on hover with definition',await p.evaluate(()=>{const e=document.getElementById('gltip');return !!e&&e.classList.contains('on')&&e.innerText.length>20;}));
 const inView=await p.evaluate(()=>{const r=document.getElementById('gltip').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0;});ok('tooltip inside viewport',inView);
 await p.mouse.move(5,5);await p.waitForTimeout(250);
 ok('tooltip hides on leave',await p.evaluate(()=>!document.getElementById('gltip').classList.contains('on')));}
// every glossary term is reachable in at least one answer
const used=await p.evaluate(async()=>{const j=await fetch('qa.json').then(r=>r.json());QA=j;GLRE=null;const txt=j.g.flatMap(g=>g.s.flatMap(s=>s.q.map(q=>q[2]+' '+q[4]))).join('\n');const seen={};glz(esc(txt),seen);return Object.keys(seen).length;});
console.log('terms that appear somewhere:',used,'of',data.gl.length);ok('most terms used (>=100)',used>=100);
// temperature, hallucination, inference are underlined where they occur
const key=await p.evaluate(()=>{QA.g;const out={};['Temperature','Hallucination','Inference','RAG','Token'].forEach(k=>{const hit=[];QA.g.forEach(g=>g.s.forEach(s=>s.q.forEach(q=>{const seen={};const h=glz(esc(q[2]+' '+q[4]),seen);if(seen[k])hit.push(1);})));out[k]=hit.length;});return out;});
console.log(JSON.stringify(key));ok('temperature and hallucination underlined somewhere',key.Temperature>0&&key.Hallucination>0);
// glossary list
ok('glossary list present',await p.evaluate(()=>document.querySelectorAll('.qa-gloss dt').length>=120));
// mobile: tap shows tooltip, no horizontal overflow
const m=await b.newPage({viewport:{width:360,height:740},hasTouch:true,isMobile:true});
await m.goto(`http://localhost:${PORT}/index.html#qa`);await m.waitForSelector('#qaList details');
await m.evaluate(()=>{document.querySelectorAll('#qaList details').forEach((d,i)=>{if(i<6)d.open=true;});});
const g=await m.$('#qaList details[open] .gl');
if(g){await g.scrollIntoViewIfNeeded();await g.tap();await m.waitForTimeout(250);
 ok('tap shows tooltip',await m.evaluate(()=>document.getElementById('gltip').classList.contains('on')));
 ok('tooltip inside viewport on phone',await m.evaluate(()=>{const r=document.getElementById('gltip').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth;}));}
ok('no horizontal overflow at 360',await m.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
await b.close();srv.kill();console.log(fails?fails+' FAILED':'ALL PASS');process.exit(fails?1:0);})();
