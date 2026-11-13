const {chromium}=require('playwright');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
(async()=>{const web=require('child_process').spawn('python3',[require('path').join(__dirname,'serve.py')]);for(let i=0;i<60;i++){try{await fetch('http://127.0.0.1:8765/index.html');break;}catch(e){await new Promise(r=>setTimeout(r,200));}}
const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:800}});const p=await c.newPage();
await p.route('https://**',r=>r.abort());await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(400);
await p.evaluate(()=>{S.start=todayISO();S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'full',depth:'full'};save();location.hash='';route();openLesson(8);});
await p.waitForSelector('[data-le=next]');
await p.click('[data-le=run]');await p.waitForFunction(()=>les.out!==null&&!les.busy,null,{timeout:60000});
ok('SQL example runs and shows a result table',await p.evaluate(()=>/^id \| name \| city \| email\n1 \| Acme/.test(les.out)),await p.evaluate(()=>les.out));
await p.fill('#lescode','SELEC nope');await p.click('[data-le=run]');await p.waitForFunction(()=>/^Error:/.test(les.out||''),null,{timeout:30000});
ok('a SQL typo shows the engine error, not a crash',await p.evaluate(()=>/syntax error/i.test(les.out)),await p.evaluate(()=>les.out));
// walk to the write task of day 8 and try wrong answers
for(const day of [8,9,10,11]){await p.evaluate(d=>{closeSheet();localStorage.removeItem('shipcode.lesson');openLesson(d);},day);
  const N=await p.evaluate(()=>les.sc.length);let bad='';
  for(let i=0;i<N;i++){const q=await p.evaluate(()=>les.sc[les.i].q);
    if(q.k==='mc'){await p.click(`[data-le=pick][data-i="${q.a}"]`);}
    else{
      await p.click('[data-le=wrun]');await p.waitForFunction(()=>les.wres&&!les.busy,null,{timeout:60000});
      if(await p.evaluate(()=>les.ok)){bad='starter passed';break;}
      if(day===8){
        await p.fill('#leswrite',"SELECT name, salary FROM employees WHERE dept = 'Engineering' ORDER BY salary DESC");
        await p.click('[data-le=wrun]');await p.waitForFunction(()=>!les.busy&&les.wres&&!les.ok,null,{timeout:30000});
        ok('wrong rows show expected vs yours',await p.evaluate(()=>/Expected/.test(sheetIn.innerText)&&/Your code gave/.test(sheetIn.innerText)&&!les.ok));
        await p.fill('#leswrite',"SELECT name, salary FROM employees WHERE name IN ('Priya','Karan','Li') ORDER BY salary DESC, name");
        await p.click('[data-le=wrun]');await p.waitForFunction(()=>!les.busy&&les.wres&&!les.ok,null,{timeout:30000});
        ok('hard-coded names pass the visible data but are caught by the hidden data',await p.evaluate(()=>/hidden set of data/.test(sheetIn.innerText)),await p.evaluate(()=>sheetIn.innerText.slice(-400)));
        await p.fill('#leswrite',"SELECT 1 AS x");await p.click('[data-le=wrun]');await p.waitForFunction(()=>!les.busy&&les.wres&&!les.ok,null,{timeout:30000});
        ok('no FROM is rejected with a plain message',await p.evaluate(()=>/FROM/.test(sheetIn.innerText)));
      }
      await p.fill('#leswrite',q.sol);await p.click('[data-le=wrun]');await p.waitForFunction(()=>les.ok&&!les.busy,null,{timeout:60000}).catch(()=>{bad='solution failed'});if(bad)break;}
    if(!await p.evaluate(()=>les.ok)){bad='stuck at screen '+i;break;}
    await p.click('[data-le=next]');}
  ok('Day '+day+': all '+N+' screens walk through, SQL write task graded',!bad&&await p.evaluate(d=>les&&les.fin&&S.tasks[d+'-c']===true,day),bad);}
ok('no page errors',errs.length===0,errs.join('|'));
console.log(fails?'FAILED '+fails:'ALL PASS');await b.close();web.kill();process.exit(fails?1:0);})();
