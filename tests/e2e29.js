const {chromium}=require('playwright');const fs=require('fs');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:800},acceptDownloads:true,permissions:['clipboard-read','clipboard-write']});const p=await c.newPage();
await p.route('https://**',r=>r.abort());await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(400);
await p.evaluate(()=>{S.start=shift(todayISO(),-6);S.done=[1,2,3];S.labs={'L1-0':todayISO(),'L1-1':todayISO()};S.xp=120;S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'full',depth:'full'};drafts['L1-0']='print("hi")';localStorage.setItem(DKEY,JSON.stringify(drafts));save();location.hash='#ref';route();});
await p.waitForTimeout(300);
// export
const [dl]=await Promise.all([p.waitForEvent('download'),p.click('[data-ui=backup]')]);
const path=await dl.path();const bk=JSON.parse(fs.readFileSync(path,'utf8'));
ok('backup file name has date',/^shipcode-backup-\d{4}-\d\d-\d\d\.json$/.test(dl.suggestedFilename()),dl.suggestedFilename());
ok('backup holds progress and drafts',bk.app==='shipcode'&&bk.state.done.length===3&&Object.keys(bk.state.labs).length===2&&bk.drafts['L1-0']==='print("hi")');
// wipe, restore
await p.evaluate(()=>{localStorage.clear();});await p.reload();await p.waitForTimeout(500);
ok('wiped device is blank',await p.evaluate(()=>S.done.length===0&&!S.start));
await p.evaluate(()=>{location.hash='#ref';route();});
await p.setInputFiles('[data-ui=restore]',path);await p.waitForSelector('[data-ui=restore-go]');
ok('confirm shows backup summary',/3 days done and 2 labs/.test(await p.innerText('.confirm')));
await p.click('[data-ui=restore-no]');ok('cancel keeps device blank',await p.evaluate(()=>S.done.length===0));
await p.setInputFiles('[data-ui=restore]',path);await p.click('[data-ui=restore-go]');
ok('restore applies progress',await p.evaluate(()=>S.done.length===3&&Object.keys(S.labs).length===2&&S.xp===120&&drafts['L1-0']==='print("hi")'));
await p.reload();await p.waitForTimeout(500);
ok('restored progress survives reload',await p.evaluate(()=>S.done.length===3&&S.start!==null));
// bad files
fs.writeFileSync('/tmp/bad1.json','{"hello":1}');fs.writeFileSync('/tmp/bad2.json','not json at all');
for(const f of ['/tmp/bad1.json','/tmp/bad2.json']){await p.evaluate(()=>{location.hash='#ref';route();});await p.setInputFiles('[data-ui=restore]',f);await p.waitForTimeout(200);
 ok('rejects '+f,/not a ShipCode backup/.test(await p.innerText('.view'))&&await p.evaluate(()=>S.done.length===3));}
// hostile backup: wrong types sanitised
fs.writeFileSync('/tmp/bad3.json',JSON.stringify({app:'shipcode',state:{done:['x',99,2],labs:'oops',start:5,xp:'1e9'},drafts:[1]}));
await p.evaluate(()=>{location.hash='#ref';route();});await p.setInputFiles('[data-ui=restore]','/tmp/bad3.json');await p.click('[data-ui=restore-go]');
ok('hostile backup is sanitised, app still works',await p.evaluate(()=>S.done.length===1&&S.done[0]===2&&typeof S.labs==='object'&&S.start===null&&S.xp===0));
// error log + report
await p.evaluate(()=>{setTimeout(()=>{throw new Error('boom-test')},0);Promise.reject(new Error('rej-test'));});await p.waitForTimeout(300);
await p.evaluate(()=>{location.hash='#ref';route();});await p.click('[data-ui=report]');
const txt=await p.evaluate(()=>navigator.clipboard.readText());
ok('report lists errors and environment',/boom-test/.test(txt)&&/rej-test/.test(txt)&&/browser: /.test(txt)&&/viewport 390x800/.test(txt),txt.slice(0,300));
ok('report contains no progress or code',!/print\("hi"\)/.test(txt)&&!/xp/.test(txt));
ok('error log capped at 20',await p.evaluate(()=>{for(let i=0;i<40;i++)logErr('t','m'+i);return JSON.parse(localStorage.getItem(ELKEY)).length===20}));
ok('only the deliberate errors reached pageerror',errs.every(m=>/boom-test|rej-test/.test(m)),errs.join('|'));
console.log(fails?'FAILS '+fails:'ALL PASS');await b.close();process.exit(fails?1:0)})();
