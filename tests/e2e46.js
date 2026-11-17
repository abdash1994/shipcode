// Directional paths: system design, AI/FDE, data science, interview Q&A are selectable goals with banks to read; plan, Today card and persistence work
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
const PORT=8796;let fails=0;const ok=(n,c)=>{console.log((c?'PASS ':'FAIL ')+n);if(!c)fails++;};
(async()=>{
const srv=spawn('python3',['-m','http.server',PORT,'--directory',path.join(__dirname,'..')],{stdio:'ignore'});
await new Promise(r=>setTimeout(r,1000));
const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844}});
const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto(`http://localhost:${PORT}/index.html`);await p.waitForTimeout(800);
await p.evaluate(()=>{location.hash='#setup';});
const ids=await p.evaluate(()=>GOALS.map(g=>g.id).join());
ok('goals include sys, ai, ds, iv and full stays last ('+ids+')',/sys/.test(ids)&&/ai/.test(ids)&&/ds/.test(ids)&&/iv/.test(ids)&&ids.endsWith('full'));
ok('every goal has valid days',await p.evaluate(()=>GOALS.every(g=>g.days.length>0&&g.days.every(d=>d>=1&&d<=30))));
ok('every banks entry names a real bank',await p.evaluate(()=>GOALS.every(g=>!g.banks||g.banks.every(b=>BANKNAME[b]))));
ok('cleanHabit keeps new goal ids',await p.evaluate(()=>['sys','ai','ds','iv'].every(id=>cleanHabit({min:30,dpw:5,goal:id}).goal===id)));
ok('time math works for every goal',await p.evaluate(()=>GOALS.every(g=>Number.isFinite(totalMin(g.id,'full',true)))));
// drive the real wizard
await p.evaluate(()=>{localStorage.clear();});await p.goto(`http://localhost:${PORT}/index.html`);await p.waitForTimeout(800);
await p.click('[data-act=obgo][data-step="2"]');await p.waitForSelector('.choices .choice');
ok('picker lists the new directions',await p.evaluate(()=>['System design','AI and forward','Data science','Interview prep'].every(t=>[...document.querySelectorAll('.choice b')].some(b=>b.textContent.includes(t)))));
ok('choice shows its reading banks',await p.evaluate(()=>/Reading: /.test(document.querySelector('.choice[data-goal=sys]').textContent)));
await p.click('.choice[data-goal=sys]');await p.click('[data-act=obgo][data-step="4"]');await p.waitForSelector('.tile');
await p.click('[data-act=obgo][data-step="5"]');await p.click('[data-act=obstart]');await p.waitForTimeout(800);
ok('goal saved',await p.evaluate(()=>S.habit&&S.habit.goal==='sys'));
await p.evaluate(()=>{location.hash='#today';route();});await p.waitForTimeout(500);
ok('Today shows the path card linking System Design bank',await p.evaluate(()=>[...document.querySelectorAll('.card.note a')].some(a=>a.getAttribute('href')==='#sd')));
ok('no page errors',errs.length===0);
await b.close();srv.kill();console.log(fails?'FAILED '+fails:'ALL PASSED');process.exit(fails?1:0);})();
