/* AI-PM Q&A page, home tile, nav entry and the always-on star/follow footer. Run: node tests/e2e39.js (serves this folder on 8766) */
const {chromium}=require('playwright');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
(async()=>{const web=require('child_process').spawn('python3',['-m','http.server','8766','-d',__dirname+'/..','--bind','127.0.0.1']);await new Promise(r=>setTimeout(r,1200));
const b=await chromium.launch();
async function pg(w,h){const c=await b.newContext({viewport:{width:w,height:h||800}});const p=await c.newPage();p.errs=[];p.on('pageerror',e=>p.errs.push(e.message));await p.goto('http://127.0.0.1:8766/index.html');await p.waitForTimeout(800);return p;}
for(const w of [360,390,1280]){
 const p=await pg(w);
 await p.evaluate(()=>{S.start=shift(todayISO(),-3);S.done=[];save();location.hash='#today';route();});await p.waitForTimeout(400);
 ok(w+' home has Q&A tile',await p.evaluate(()=>!!document.querySelector('a.qatile[href="#qa"]')));
 ok(w+' footer shows star + linkedin on home',await p.evaluate(()=>{const f=document.getElementById('mkfoot');return f.offsetHeight>0&&/star it on GitHub/.test(f.innerText)&&!!f.querySelector('a[href*=linkedin]');}));
 ok(w+' nav entry visible',await p.evaluate(()=>{const a=document.querySelector('.tabs a[data-tab=qa]');const r=a.getBoundingClientRect();return r.width>30&&r.right<=innerWidth+1&&/AI-PM Q&A/.test(a.innerText);}));
 await p.click('.tabs a[data-tab=qa]');await p.waitForTimeout(900);
 ok(w+' qa page loads 234 AI questions',await p.evaluate(()=>document.querySelectorAll('#qaList details').length===234&&/234 shown/.test(document.getElementById('qaCount').innerText)));
 ok(w+' no horizontal scroll',await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 ok(w+' tab highlighted',await p.evaluate(()=>document.querySelector('.tabs a[data-tab=qa]').getAttribute('aria-current')==='page'));
 ok(w+' footer on qa page',await p.evaluate(()=>document.getElementById('mkfoot').offsetHeight>0));
 await p.click('#qaList details summary');await p.waitForTimeout(150);
 ok(w+' answer opens, no S/T/A/R labels',await p.evaluate(()=>{const d=document.querySelector('#qaList details');return d.open&&d.querySelector('.qa-ans p').innerText.length>40&&!document.querySelector('.qa-ans .lab');}));
 await p.click('[data-qa=done]');await p.waitForTimeout(100);
 ok(w+' mark answerable persists',await p.evaluate(()=>/1 of 478/.test(document.getElementById('qaCount').innerText)&&Object.keys(JSON.parse(localStorage.getItem('shipcode.qa.done'))).length===1));
 await p.fill('#qaSearch','RAG');await p.waitForTimeout(150);
 ok(w+' search filters',await p.evaluate(()=>{const n=document.querySelectorAll('#qaList details').length;return n>0&&n<234;}));
 await p.fill('#qaSearch','');await p.click('[data-qa=g][data-i="1"]');await p.waitForTimeout(200);
 ok(w+' group switch',await p.evaluate(()=>/94 shown/.test(document.getElementById('qaCount').innerText)));
 await p.click('[data-qa=rand]');await p.waitForTimeout(500);
 ok(w+' random opens one',await p.evaluate(()=>document.querySelectorAll('#qaList details[open]').length>=1));
 if(w===390){await p.screenshot({path:'/tmp/qa390.png'});
  await p.evaluate(()=>{location.hash='#today';});await p.waitForTimeout(300);
  await p.click('#mkfoot a[data-au=star]',{noWaitAfter:true}).catch(()=>{});await p.waitForTimeout(400);
  ok('after star click footer thanks and keeps linkedin',await p.evaluate(()=>/Thanks for the star/.test(document.getElementById('mkfoot').innerText)&&!!document.querySelector('#mkfoot a[href*=linkedin]')));}
 if(w===1280)await p.screenshot({path:'/tmp/qa1280.png'});
 ok(w+' no page errors',p.errs.length===0,p.errs.join('|'));
 await p.context().close();}
await b.close();web.kill();console.log(fails?fails+' FAILED':'ALL PASS');process.exit(fails?1:0);})();
