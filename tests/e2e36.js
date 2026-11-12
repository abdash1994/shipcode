const {chromium}=require('playwright');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
(async()=>{const web=require('child_process').spawn('python3',['serve.py']);for(let i=0;i<60;i++){try{await fetch('http://127.0.0.1:8765/index.html');break;}catch(e){await new Promise(r=>setTimeout(r,200));}}
const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:800}});const p=await c.newPage();
await p.route('https://**',r=>r.abort());await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(400);
await p.evaluate(()=>{S.start=todayISO();S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'full',depth:'full'};save();location.hash='';route();});await p.waitForTimeout(300);

await p.evaluate(()=>{location.hash='#pro';});await p.waitForTimeout(400);
const keys=await p.evaluate(()=>proKeys());
ok('Pro track page lists every module grouped by track',await p.evaluate(()=>document.querySelectorAll('.prorow').length===proKeys().length&&document.querySelectorAll('.view h2').length>=3),'rows '+await p.evaluate(()=>document.querySelectorAll('.prorow').length));
ok('Pro page tells the learner honestly that tools cannot run here',await p.evaluate(()=>/cannot run inside a browser/.test(document.body.innerText)));
await p.click('.prorow');await p.waitForSelector('[data-le=next]');
ok('clicking a module opens its lesson with the track and title',await p.evaluate(()=>les&&typeof les.n==='string'&&sheetIn.innerText.toLowerCase().includes(PRO[les.n].track.toLowerCase())));
for(const key of keys){await p.evaluate(k=>{closeSheet();localStorage.removeItem('shipcode.lesson');openLesson(k);},key);
  const N=await p.evaluate(()=>les.sc.length);let bad='';
  for(let i=0;i<N;i++){const q=await p.evaluate(()=>les.sc[les.i].q);
    if(q.k==='mc'){await p.click(`[data-le=pick][data-i="${q.a}"]`);}
    else{await p.click('[data-le=wrun]');await p.waitForFunction(()=>(les.wres)&&!les.busy,null,{timeout:150000});if(await p.evaluate(()=>les.ok)){bad='starter passed';break;}
      await p.fill('#leswrite',q.sol);await p.click('[data-le=wrun]');await p.waitForFunction(()=>les.ok&&!les.busy,null,{timeout:150000}).catch(()=>{bad='solution failed: '+JSON.stringify(les.wres).slice(0,300)});if(bad)break;}
    if(!await p.evaluate(()=>les.ok)){bad='stuck at screen '+i;break;}
    await p.click('[data-le=next]');}
  ok('Pro '+key+': all '+N+' screens walk through, write task graded, module recorded',!bad&&await p.evaluate(k=>les&&les.fin&&!!S.pro[k],key),bad);}
ok('completed modules survive a reload',await (async()=>{await p.reload();await p.waitForTimeout(500);return p.evaluate(n=>Object.keys(S.pro||{}).length===n,keys.length);})());
await p.evaluate(()=>{location.hash='#pro'});await p.waitForTimeout(300);
ok('finished modules show a tick',await p.evaluate(n=>[...document.querySelectorAll('.prorow')].filter(b=>/✓/.test(b.innerText)).length===n,keys.length));
ok('no page errors',errs.length===0,errs.join('|'));
console.log(fails?'FAILED '+fails:'ALL PASS');await b.close();web.kill();process.exit(fails?1:0);})();
