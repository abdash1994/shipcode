const {chromium}=require('playwright');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
(async()=>{const web=require('child_process').spawn('python3',['serve.py']);for(let i=0;i<60;i++){try{await fetch('http://127.0.0.1:8765/index.html');break;}catch(e){await new Promise(r=>setTimeout(r,200));}}
const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:800}});const p=await c.newPage();
await p.route('https://**',r=>r.abort());await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(400);
await p.evaluate(()=>{S.start=todayISO();S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'full',depth:'full'};save();location.hash='';route();});await p.waitForTimeout(300);
// ---- order on Today
const order=await p.evaluate(()=>[...document.querySelectorAll('.view > *')].map(e=>(e.querySelector('.eyebrow')||e).textContent.trim().slice(0,28)));
const idx=t=>order.findIndex(x=>x.toLowerCase().includes(t));
ok('Today shows the steps in order before any extras',idx('1 · learn')>0&&idx('1 · learn')<idx('2 · drills')&&idx('2 · drills')<idx('3 · code labs')&&idx('3 · code labs')<idx('4 · hands-on')&&idx('4 · hands-on')<idx('also today'),JSON.stringify(order));
ok('first thing to do is the lesson, not a lab',await p.evaluate(()=>{const b=document.querySelector('.bento .bm.primary .btn');return b.dataset.part==='concept'&&/Start the lesson/.test(b.textContent)&&/Lesson: /.test(document.querySelector('.bento .bm.primary h2').textContent)}));
ok('drills and labs are locked until the lesson is done',await p.evaluate(()=>document.querySelector('[data-act=drills]').disabled&&[...document.querySelectorAll('[data-act=lab]')].every(x=>x.disabled)&&document.querySelectorAll('.locked-step').length===2));
// ---- lesson player
await p.click('.bento [data-act=next]');await p.waitForSelector('[data-le=next]');
ok('lesson opens on screen 1 of 9 with Continue disabled',await p.evaluate(()=>/1\/9/.test(sheetIn.innerText)&&document.querySelector('[data-le=next]').disabled&&les.n===1));
await p.click('[data-le=run]');await p.waitForFunction(()=>les.out!==null&&!les.busy,null,{timeout:90000});
ok('the example runs and shows its output',await p.evaluate(()=>les.out==='Hello\nI am learning Python'),await p.evaluate(()=>les.out));
await p.fill('#lescode','print("changed " + str(2 + 3))');await p.click('[data-le=run]');await p.waitForFunction(()=>les.out==='changed 5',null,{timeout:30000});ok('edited code runs',true);
await p.fill('#lescode','print(oops)');await p.click('[data-le=run]');await p.waitForFunction(()=>/NameError/.test(les.out||''),null,{timeout:30000});ok('a mistake shows the real error, not a crash',true);
// wrong answers
const wrong=await p.evaluate(()=>les.sc[0].q.o.map((_,i)=>i).filter(i=>i!==les.sc[0].q.a));
await p.click(`[data-le=pick][data-i="${wrong[0]}"]`);
ok('a wrong answer does not let you continue, and does not give the answer away',await p.evaluate(()=>document.querySelector('[data-le=next]').disabled&&/Not quite/.test(sheetIn.innerText)&&!/Each print\(\) writes/.test(sheetIn.innerText)));
ok('typed code survives the re-render',await p.evaluate(()=>document.getElementById('lescode').value==='print(oops)'));
await p.click(`[data-le=pick][data-i="${wrong[1]}"]`);ok('after two misses the reason is shown',await p.evaluate(()=>/Each print\(\) writes/.test(sheetIn.innerText)&&!!document.querySelector('.lopt.hinted')));
await p.click(`[data-le=pick][data-i="${await p.evaluate(()=>les.sc[0].q.a)}"]`);ok('right answer unlocks Continue',await p.evaluate(()=>!document.querySelector('[data-le=next]').disabled&&/Right\./.test(sheetIn.innerText)));
await p.click('[data-le=next]');ok('moves to screen 2',await p.evaluate(()=>les.i===1&&/2\/9/.test(sheetIn.innerText)));
// close and resume
await p.click('[data-le=close]');await p.waitForTimeout(200);
ok('Today now says Continue the lesson',/Continue the lesson/.test(await p.innerText('.bento')));
await p.reload();await p.waitForTimeout(400);await p.click('[data-act=lesson]');
ok('resumes at screen 2 after a reload; Back works and keeps screen 1 passed',await p.evaluate(()=>{if(les.i!==1)return false;lesAct('back');return les.i===0&&les.ok===true}));
// walk every screen of every authored day by answering correctly; write tasks use the reference solution
for(const day of [1,2,3,4,5,6,7]){await p.evaluate(d=>{closeSheet();localStorage.removeItem('shipcode.lesson');openLesson(d);},day);
  const N=await p.evaluate(()=>les.sc.length);let bad='';
  for(let i=0;i<N;i++){const q=await p.evaluate(()=>les.sc[les.i].q);
    if(q.k==='mc'){await p.click(`[data-le=pick][data-i="${q.a}"]`);}
    else{await p.click('[data-le=wrun]');await p.waitForFunction(()=>les.wres&&!les.busy,null,{timeout:60000});if(await p.evaluate(()=>les.ok)){bad='starter passed on day '+day;break;}
      await p.fill('#leswrite',q.sol);await p.click('[data-le=wrun]');await p.waitForFunction(()=>les.ok&&!les.busy,null,{timeout:60000}).catch(()=>{bad='solution failed on day '+day;});if(bad)break;}
    if(!await p.evaluate(()=>les.ok)){bad='stuck at day '+day+' screen '+i;break;}
    await p.click('[data-le=next]');}
  ok('Day '+day+': all '+N+' screens walk through in the browser, write task graded',!bad&&await p.evaluate(d=>les&&les.fin&&S.tasks[d+'-c']===true,day),bad);}
// finish → drills
ok('finishing offers the drills next',await p.evaluate(()=>!!document.querySelector('[data-le=drills]')));
await p.evaluate(()=>{closeSheet();openLesson(1);for(let i=0;i<8;i++){les.ok=true;lesAct('next');}});
await p.evaluate(()=>{les.ok=true;lesAct('next');});await p.click('[data-le=drills]');
ok('the drills session opens straight from the lesson',await p.evaluate(()=>!!sess&&/Day 1/.test(sess.label)&&les===null));
await p.evaluate(()=>closeSheet());await p.evaluate(()=>{location.hash='';route();});await p.waitForTimeout(200);
ok('after the lesson: drills unlocked and next, labs still locked',await p.evaluate(()=>!document.querySelector('[data-act=drills]').disabled&&document.querySelector('.bento [data-act=next]').dataset.part==='drills'&&[...document.querySelectorAll('[data-act=lab]')].every(x=>x.disabled)));
await p.click('[data-act=unlock]');await p.waitForTimeout(200);
ok('"I already know this" unlocks the labs for the day',await p.evaluate(()=>[...document.querySelectorAll('[data-act=lab]')].every(x=>!x.disabled)&&!document.querySelector('.locked-step')));
await p.evaluate(()=>{DAYS[0].drills.forEach(d=>{S.solved[d.id]=todayISO();});save();route();});await p.waitForTimeout(200);
ok('after drills the next step is the lab',await p.evaluate(()=>document.querySelector('.bento [data-act=next]').dataset.part==='labs'));
// a day without an authored lesson still gets the guided lesson
await p.evaluate(()=>{closeSheet();delete LESSONS[12];openLesson(12);});
ok('Day 12 (no authored lesson) builds screens from its notes and can be finished',await p.evaluate(()=>{const n=les.sc.length;if(n<3)return false;for(let i=0;i<n;i++){if(!les.ok)return false;lesAct('next');}return les.fin&&S.tasks['12-c']===true}));
await p.evaluate(()=>closeSheet());
// layout + keyboardless basics
for(const w of [320,390]){await p.setViewportSize({width:w,height:700});await p.evaluate(()=>{location.hash='';route();openLesson(3);});await p.waitForTimeout(200);
  ok('lesson fits at '+w+'px',await p.evaluate(()=>sheetIn.scrollWidth<=sheetIn.clientWidth+1&&document.documentElement.scrollWidth<=document.documentElement.clientWidth+1));await p.evaluate(()=>closeSheet());}
ok('no page errors',errs.length===0,errs.join('|'));
console.log(fails?'FAILS '+fails:'ALL PASS');web.kill();await b.close();process.exit(fails?1:0)})();
