const {chromium,devices}=require('playwright');(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices['iPhone 13']});await c.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort());const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+process.cwd()+'/vercel/index.html');await p.waitForTimeout(500);let f=0;const ok=(n,v)=>{if(!v)f++;console.log((v?'PASS ':'FAIL ')+n)};
const base=`S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'sprint',depth:'core'};S.start=shift(todayISO(),-3);S.done=[1];S.dates=[shift(todayISO(),-2),shift(todayISO(),-1)];S.frozen=[];S.pause=null;S.pledge=null;S.ifthen=null;S.cele={};S.labs={};S.errs={TypeError:3};save();`;
const go=async h=>{await p.evaluate(h=>{location.hash=h;route();},h);await p.waitForTimeout(250);};
await p.evaluate(base);await go('#today');
ok('5 tabs on phone',await p.evaluate(()=>[...document.querySelectorAll('.tabs a')].filter(a=>getComputedStyle(a).display!=='none').length===5));
ok('reference tab hidden on phone',await p.evaluate(()=>getComputedStyle(document.querySelector('.tabs a[data-tab=ref]')).display==='none'));
ok('7 week dots',await p.evaluate(()=>document.querySelectorAll('#wkDots .wd').length===7));
ok('header fits (no horizontal overflow)',await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
ok('header items inside viewport',await p.evaluate(()=>[...document.querySelectorAll('header .col > *')].every(e=>e.getBoundingClientRect().right<=innerWidth)));
ok('bento on Today',await p.evaluate(()=>document.querySelectorAll('.bento .bm').length===3));
ok('bento start lab button opens a lab',await (async()=>{await p.click('.bento [data-act=next]');await p.waitForTimeout(300);if(!await p.evaluate(()=>!!les&&les.n===currentDay()))throw new Error('bento first step should open the lesson');await p.evaluate(()=>{closeSheet();const n=currentDay();S.tasks[n+'-c']=true;DAYS[n-1].drills.forEach(d=>{S.solved[d.id]=todayISO();});save();route();});await p.waitForTimeout(200);await p.click('.bento [data-act=next][data-part=labs]');await p.waitForTimeout(400);return await p.evaluate(()=>!document.getElementById('sheet').hidden&&!!lab)})());
// drawer inside a lab keeps the lab
await p.evaluate(()=>{window.__lab=lab});
await p.click('.sheet-head [data-drawer=open]');await p.waitForTimeout(250);
ok('drawer open in lab, search hidden, cheat sheet shown',await p.evaluate(()=>!document.getElementById('drawer').hidden&&document.getElementById('drQ').hidden&&/Python/.test(document.getElementById('drBody').innerText)));
await p.keyboard.press('Escape');await p.waitForTimeout(150);
ok('Esc closes only the drawer; lab still open and same object',await p.evaluate(()=>document.getElementById('drawer').hidden&&!document.getElementById('sheet').hidden&&lab===window.__lab));
await p.keyboard.press('Escape');await p.waitForTimeout(250);
ok('second Esc closes the lab',await p.evaluate(()=>document.getElementById('sheet').hidden));
// search
await p.click('header [data-drawer=open]');await p.waitForTimeout(200);await p.fill('#drQ','day 12');await p.waitForTimeout(150);
ok('search finds Day 12',await p.evaluate(()=>/day 12/i.test(document.getElementById('drBody').innerText)));
await p.fill('#drQ','keyerror');await p.waitForTimeout(150);ok('search finds KeyError',await p.evaluate(()=>/KeyError/.test(document.getElementById('drBody').innerText)));
await p.keyboard.press('Enter');await p.waitForTimeout(300);ok('Enter jumps to #errors',await p.evaluate(()=>location.hash==='#errors'&&document.getElementById('drawer').hidden));
// Errors page
ok('diagnose card + locked clues',await p.evaluate(()=>document.querySelectorAll('.diag details.rev').length===3&&document.querySelectorAll('.diag details.rev.locked').length===2));
await p.click('.diag details.rev:nth-of-type(2) summary').catch(()=>{});
ok('locked clue does not open',await p.evaluate(()=>!document.querySelectorAll('.diag details.rev')[1].open));
await p.click('.diag details.rev >> nth=0 >> summary');await p.waitForTimeout(100);
ok('opening hint unlocks root cause',await p.evaluate(()=>!document.querySelectorAll('.diag details.rev')[1].classList.contains('locked')));
ok('error accordions',await p.evaluate(()=>document.querySelectorAll('.erracc').length>=15));
ok('drill button on TypeError row',await p.evaluate(()=>[...document.querySelectorAll('.erracc')].find(d=>/TypeError/.test(d.innerText)).querySelector('[data-act=practice]')!==null));
ok('EVERY error row has a drill button that opens a real lab',await p.evaluate(()=>[...document.querySelectorAll('.erracc')].every(d=>{const b=d.querySelector('[data-act=practice]');return b&&labById(b.dataset.lab)})));
ok('copy buttons on code',await p.evaluate(()=>document.querySelectorAll('.cpbtn').length>=1));
await p.click('[data-ui=diagnext]');await p.waitForTimeout(150);ok('another case rotates',await p.evaluate(()=>document.querySelectorAll('.diag').length===1));
// Think
await go('#think');ok('think steps are progressive',await p.evaluate(()=>document.querySelectorAll('details.rev').length===4&&document.querySelectorAll('details.rev.locked').length===3));
// Path
await go('#path');ok('30-day map has 30 days and a current day',await p.evaluate(()=>document.querySelectorAll('.pg').length===30&&document.querySelectorAll('.pg.cur').length===1));
// HUD tip + ticker
await go('#today');await p.click('[data-hud]');await p.waitForTimeout(150);ok('week tip shows rule text',await p.evaluate(()=>/of 7 days this week/.test(document.getElementById('hudTip').innerText)&&!document.getElementById('hudTip').hidden));
await p.evaluate(()=>{hudShown.l=0;});
await p.evaluate(()=>{S.labs={...S.labs,'L1-1':'2026-01-01'};topStats();});await p.waitForTimeout(80);
ok('counter animates up',await p.evaluate(()=>document.getElementById('labsN').parentElement.classList.contains('bump')));
await p.waitForTimeout(1000);ok('counter lands on the right number',await p.evaluate(()=>+document.getElementById('labsN').textContent===labsPassedN()));
// strict mode text
await p.evaluate(()=>{S.habit.mode='strict';});ok('strict tip mentions freezes',await p.evaluate(()=>/freeze/.test(weekTip())));
// desktop sidebar keeps Reference
const n=await b.newContext({...devices['iPhone SE']});await n.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort());const sm=await n.newPage();await sm.goto('file://'+process.cwd()+'/vercel/index.html');await sm.waitForTimeout(400);await sm.evaluate(()=>{S.start=shift(todayISO(),-3);save();location.hash='#today';route();});await sm.waitForTimeout(300);
ok('320px: every header item inside the screen',await sm.evaluate(()=>innerWidth<=320&&[...document.querySelectorAll('header .col > *')].every(e=>e.getBoundingClientRect().right<=innerWidth&&e.getBoundingClientRect().width>0)));
const d=await c.newPage();await d.setViewportSize({width:1280,height:800});await d.goto('file://'+process.cwd()+'/vercel/index.html');await d.waitForTimeout(400);
ok('desktop sidebar shows Reference',await d.evaluate(()=>getComputedStyle(document.querySelector('.tabs a[data-tab=ref]')).display!=='none'));
ok('no page errors '+errs.join('|'),!errs.length);console.log(f?'FAILS '+f:'ALL PASS');await b.close();})();
