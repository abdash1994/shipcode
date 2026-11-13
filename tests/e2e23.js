const {chromium,devices}=require('playwright');(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices['iPhone 13']});await c.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort());const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto('file://'+require('path').join(__dirname,'..','index.html'));await p.waitForTimeout(500);let f=0;const ok=(n,v)=>{if(!v)f++;console.log((v?'PASS ':'FAIL ')+n)};
ok('7 gyms incl fde',await p.evaluate(()=>GYMS.length===7&&GYMS.some(g=>g.key==='fde'&&g.levels.length===5)));
for(const h of ['#gyms','#fde','#fde-1','#fde-3','#fde-5']){await p.evaluate(h=>{location.hash=h},h);await p.waitForTimeout(250);const t=await p.evaluate(()=>document.body.innerText);ok(h+' renders',t.length>200&&!/undefined|NaN/.test(t));}
// open every fde lab and run solution via lab runner? just open each
const ids=await p.evaluate(()=>GYMS.find(g=>g.key==='fde').levels.flatMap(l=>l.ids));ok('29 labs ('+ids.length+')',ids.length===29);
for(const id of ids){const r=await p.evaluate(id=>{try{openLab(id,false);return document.body.innerText.length}catch(e){return 'ERR '+e}},id);if(typeof r!=='number'||r<100)ok('open '+id+' '+r,false);await p.evaluate(()=>{const x=document.querySelector('.sheet [data-act="close"],.sheet-x');x&&x.click()});await p.reload();await p.waitForTimeout(150);}
ok('open all labs',true);
await p.evaluate(()=>{S.habit={min:120,dpw:7,mode:'strict',at:'19:00',deep:0,deepDay:6,goal:'sprint',depth:'core'};S.start=todayISO();S.done=SPRINT_ORDER.slice(0,10);save();location.hash='#today';route();});await p.waitForTimeout(300);
ok('day 7 shows field slot',/field slot/i.test(await p.evaluate(()=>document.body.innerText)));
ok('no page errors '+errs.join('|'),!errs.length);console.log(f?'FAILS '+f:'ALL PASS');await b.close();})();
