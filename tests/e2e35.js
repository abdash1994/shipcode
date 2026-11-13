const {chromium}=require('playwright');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
(async()=>{const web=require('child_process').spawn('python3',[require('path').join(__dirname,'serve.py')]);for(let i=0;i<60;i++){try{await fetch('http://127.0.0.1:8765/index.html');break;}catch(e){await new Promise(r=>setTimeout(r,200));}}
const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:800}});const p=await c.newPage();
await p.route('https://**',r=>r.abort());await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(400);
await p.evaluate(()=>{S.start=todayISO();S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'full',depth:'full'};save();location.hash='';route();});await p.waitForTimeout(300);
// walk every screen of every authored day by answering correctly; write tasks use the reference solution
for(const day of [12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]){await p.evaluate(d=>{closeSheet();localStorage.removeItem('shipcode.lesson');openLesson(d);},day);
  const N=await p.evaluate(()=>les.sc.length);let bad='';
  for(let i=0;i<N;i++){const q=await p.evaluate(()=>les.sc[les.i].q);
    if(q.k==='mc'){await p.click(`[data-le=pick][data-i="${q.a}"]`);}
    else{await p.click('[data-le=wrun]');await p.waitForFunction(()=>les.wres&&!les.busy,null,{timeout:120000});if(await p.evaluate(()=>les.ok)){bad='starter passed on day '+day;break;}
      await p.fill('#leswrite',q.sol);await p.click('[data-le=wrun]');await p.waitForFunction(()=>les.ok&&!les.busy,null,{timeout:120000}).catch(()=>{bad='solution failed on day '+day;});if(bad)break;}
    if(!await p.evaluate(()=>les.ok)){bad='stuck at day '+day+' screen '+i;break;}
    await p.click('[data-le=next]');}
  ok('Day '+day+': all '+N+' screens walk through in the browser, write task graded',!bad&&await p.evaluate(d=>les&&les.fin&&S.tasks[d+'-c']===true,day),bad);}
ok('no page errors',errs.length===0,errs.join('|'));
console.log(fails?'FAILED '+fails:'ALL PASS');await b.close();web.kill();process.exit(fails?1:0);})();
