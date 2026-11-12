const {chromium}=require('playwright');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:800},permissions:['clipboard-read','clipboard-write']});const p=await c.newPage();
await p.route('https://**',r=>r.abort());await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(500);
// 1. promise copy
const hero=await p.innerText('.view');
ok('onboarding shows the narrower promise',/SQL strong enough for interviews in about 3 weeks/.test(hero)&&/not yet measured with learners/.test(hero),hero.slice(0,300));
const html=await p.content();
ok('no "forward-deployed-ready" or "Interview-ready" outcome labels left',!/forward-deployed-ready/i.test(html)&&!/"Interview-ready"/.test(html)&&!/interview-ready"/.test(html));
await p.evaluate(()=>{S.start=shift(todayISO(),-3);S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'full',depth:'full'};save();});await p.reload();await p.waitForTimeout(500);
ok('goal label renamed',await p.evaluate(()=>GOALS.find(g=>g.id==='full').name==='Everything: all 30 days'));
// 2. interview page
await p.evaluate(()=>{location.hash='#interview';route();});await p.waitForTimeout(300);
ok('interview page lists 3 loops and the peer card',await p.evaluate(()=>document.querySelectorAll('[data-act=ivstart]').length===3&&!!document.querySelector('#peer')));
ok('path page links to it',await p.evaluate(()=>{location.hash='#path';route();const r=!!document.querySelector('a[href="#interview"]');location.hash='#interview';route();return r}));
await p.click('[data-act=ivstart][data-loop=A]');await p.waitForSelector('#ivclock');
ok('loop A started with 4 rounds and a clock',await p.evaluate(()=>document.querySelectorAll('[data-act=ivopen]').length===4&&/^(59|60):\d\d$/.test(document.getElementById('ivclock').textContent)));
ok('other loops cannot start while one is live',await p.evaluate(()=>{ivStart('B');return ivAtts().length===1}));
// round 2: debug
await p.click('[data-act=ivopen][data-id=I1]');await p.waitForSelector('#code');
ok('debug round opens on the buggy code, not a blank file',await p.evaluate(()=>/items\[0\]/.test(document.getElementById('code').value)&&lab.checkpoint==='iv'&&lab.phase==='code'));
await p.click('[data-l=run]');await p.waitForFunction(()=>lab.result&&!lab.running,{timeout:90000});
ok('buggy code fails',await p.evaluate(()=>!lab.passed));
await p.fill('#code',await p.evaluate(()=>lab.L.solution));await p.click('[data-l=run]');await p.waitForFunction(()=>lab.passed===true,{timeout:90000});
await p.evaluate(()=>closeSheet());await p.waitForTimeout(200);
ok('debug round recorded as solved without help',await p.evaluate(()=>{const r=ivLast().res.I1;return r&&r.ok===true&&r.helped===false}));
// round 3: sql, wrong then closed => not solved
await p.evaluate(()=>{location.hash='#interview';route();});await p.click('[data-act=ivopen][data-id=I2]');await p.waitForSelector('#code');
await p.fill('#code','SELECT c.name, o.order_date, o.amount FROM customers c JOIN orders o ON o.customer_id = c.id');await p.click('[data-l=run]');await p.waitForFunction(()=>lab.result&&!lab.running,{timeout:60000});
ok('wrong SQL (inner join) does not pass',await p.evaluate(()=>!lab.passed));
await p.evaluate(()=>closeSheet());
ok('closing a round counts it as not solved, once',await p.evaluate(()=>{const r=ivLast().res.I2;ivOpen('I2');return r&&r.ok===false&&!lab}));
// round 1: design, full walk
await p.evaluate(()=>{location.hash='#interview';route();});await p.click('[data-act=ivopen][data-id=I0]');await p.waitForSelector('[data-l=qtog]');
for(const i of await p.evaluate(()=>lab.L.questions.map((q,i)=>q[1]?i:-1).filter(i=>i>=0)))await p.click(`[data-l=qtog][data-i="${i}"]`);
await p.click('[data-l=qcheck]');await p.click('[data-l=next]');
for(let i=0;i<await p.evaluate(()=>lab.L.steps.length);i++)await p.click(`.pool [data-l=pick][data-i="${i}"]`);
await p.click('[data-l=ocheck]');await p.click('[data-l=next]');
for(let t=0;t<3;t++){await p.click(`[data-l=tpick][data-i="${await p.evaluate(()=>lab.L.trade[lab.ti||0].a)}"]`);await p.click('[data-l=tnext]');}
await p.fill('#dsum','I would first find out the top reasons customers contact support and the ticket volume for each, and agree a measure of success such as the share of tracking tickets resolved. Then start narrow with one reason, connected to the tracking system data, and hand off to a human agent whenever the bot is unsure. Run a pilot with one team and review transcripts.');
await p.click('[data-l=dsum]');await p.waitForFunction(()=>lab.passed===true,{timeout:5000});
await p.evaluate(()=>closeSheet());
ok('scope round passes when walked correctly',await p.evaluate(()=>ivLast().res.I0&&ivLast().res.I0.ok===true),JSON.stringify(await p.evaluate(()=>ivLast().res)));
// end loop, history
await p.evaluate(()=>{location.hash='#interview';route();});await p.click('[data-act=ivend]');await p.waitForTimeout(200);
ok('ended loop shows 2/4 in history and best on the loop row',/2\/4/.test(await p.innerText('.view'))&&await p.evaluate(()=>/best 2\/4/.test(document.querySelector('[data-loop=A]').innerText)));
await p.reload();await p.waitForTimeout(500);
ok('attempt survives reload',await p.evaluate(()=>ivAtts().length===1&&ivAtts()[0].fin===true&&ivScore(ivAtts()[0])===2));
// timeout behaviour
ok('an expired loop is no longer live',await p.evaluate(()=>{S.iv={at:[...ivAtts(),{loop:'B',t0:Date.now()-61*60000,d:todayISO(),res:{}}]};return !ivLive(ivLast())&&ivDone(ivLast())}));
// 3. peer mock
await p.evaluate(()=>{location.hash='#interview';route();});await p.selectOption('#peerLoop','C');await p.waitForTimeout(200);
ok('script follows the chosen loop and hides nothing the interviewer needs',await p.evaluate(()=>{const t=document.querySelector('#peer').innerHTML;return /Interviewer script for loop C/.test(t)&&/nightly pipeline is too slow/i.test(t)&&/SELECT c\.city/.test(t)&&document.querySelectorAll('#peer details.rev').length===4}));
await p.click('[data-ui=peer-invite]');ok('invite message has the link',/#interview/.test(await p.evaluate(()=>navigator.clipboard.readText())));
await p.selectOption('#pr0','4');await p.selectOption('#pr2','2');await p.fill('#peerNote','Good questions <b>x</b>');await p.click('[data-ui=peer-copy]');
const fb=await p.evaluate(()=>navigator.clipboard.readText());ok('feedback text totals the rubric (4+3+2+3+3=15)',/Total: 15\/20/.test(fb)&&/loop C/.test(fb),fb);
await p.click('[data-ui=peer-log][data-role=candidate]');ok('candidate log needs a score',/from 0 to 20/.test(await p.innerText('#peer'))&&await p.evaluate(()=>S.peer.length===0));
await p.fill('#peerGot','17');await p.click('[data-ui=peer-log][data-role=candidate]');
ok('candidate mock logged',await p.evaluate(()=>S.peer.length===1&&S.peer[0].score===17&&S.peer[0].role==='candidate')&&/17\/20/.test(await p.innerText('#peer')));
await p.fill('#peerNote','<img src=x onerror=alert(1)>');await p.click('[data-ui=peer-log][data-role=interviewer]');
ok('interviewer note is escaped',await p.evaluate(()=>!document.querySelector('#peer img')&&S.peer.length===2));
await p.reload();await p.waitForTimeout(400);ok('peer log survives reload and cleaning',await p.evaluate(()=>S.peer.length===2));
// layout
for(const w of [320,390]){await p.setViewportSize({width:w,height:800});await p.evaluate(()=>{location.hash='#interview';route();});await p.waitForTimeout(200);
 ok('no sideways overflow at '+w,await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth)<=1);}
ok('no page errors',errs.length===0,errs.join('|'));
console.log(fails?'FAILS '+fails:'ALL PASS');await b.close();process.exit(fails?1:0)})();
