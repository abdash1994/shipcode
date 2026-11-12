const {chromium}=require('playwright');const {spawn}=require('child_process');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
const start=(port,env)=>{const p=spawn('python3',['-m','uvicorn','app:app','--port',String(port),'--log-level','error'],{cwd:'capapi',env:{...process.env,...env}});return p;};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const web=spawn('python3',['-m','http.server','8765','-d','site','--bind','127.0.0.1'],{cwd:'.'});const servers=[web,start(8101,{}),start(8102,{NOCORS:'1'}),start(8103,{CREATE_STATUS:'200'}),start(8104,{NOIDEM:'1'})];for(const port of [8101,8102,8103,8104,8765]){for(let i=0;i<60;i++){try{await fetch('http://127.0.0.1:'+port+(port==8765?'/index.html':'/health'));break;}catch(e){await wait(250);}}}
 const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:800}});const p=await c.newPage();
 await p.route('https://**',r=>r.abort());await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://127.0.0.1:8765/index.html#capstone');await p.waitForTimeout(500);
 const run=async url=>{await p.fill('#capUrl',url);await p.click('[data-act=capcheck]');await p.waitForFunction(()=>!capBusy,null,{timeout:30000});await p.waitForTimeout(200);return p.evaluate(()=>({txt:document.querySelector('#contract').innerText,res:capRes&&capRes.res&&capRes.res.map(r=>r[1]),err:capRes&&capRes.error||''}))};
 let r=await run('http://127.0.0.1:8101');ok('correct service passes all 8',r.res&&r.res.length===8&&r.res.every(x=>x),r.txt.slice(0,400));
 ok('summary says 8 of 8',/8 of 8 pass/.test(r.txt));
 ok('result saved to progress (host only)',await p.evaluate(()=>{const c=S.proof.contract;return c&&c.passed===8&&c.total===8&&c.base==='http://127.0.0.1:8101'}));
 r=await run('http://127.0.0.1:8102');ok('no CORS: clear hint, not a crash',/CORS/.test(r.err)&&r.res&&r.res.length===0,r.err);
 r=await run('http://127.0.0.1:8103');ok('wrong create status is named',r.res&&r.res[1]===false&&/got status 200, expected 201/.test(r.txt),r.txt.slice(0,300));
 r=await run('http://127.0.0.1:8104');ok('missing idempotency is caught, rest pass',r.res&&r.res[6]===false&&r.res.filter(x=>!x).length===1,JSON.stringify(r.res));
 r=await run('http://127.0.0.1:9');ok('nothing listening: helpful message',/could not reach/i.test(r.err));
 r=await run('ftp://nope');ok('bad address rejected before any request',/web address/.test(r.err));
 r=await run('http://example.com');ok('plain http to a real host rejected',/web address/.test(r.err));
 r=await run('<script>alert(1)</script>');ok('hostile input escaped',!await p.evaluate(()=>!!document.querySelector('#contract script'))&&/web address/.test(r.err));
 // Dockerfile quality checks with mocked GitHub
 const mock=async(dockerfile)=>{await p.unroute('https://api.github.com/**').catch(()=>{});await p.route('https://api.github.com/**',async route=>{const u=route.request().url();const j=o=>route.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify(o)});
   if(/\/contents\/$/.test(u))return j([{name:'Dockerfile'},{name:'README.md'}]);if(/contents\/Dockerfile/.test(u))return j({content:Buffer.from(dockerfile).toString('base64')});if(/\/readme/.test(u))return j({});if(/contents\/requirements/.test(u))return j({content:Buffer.from('fastapi').toString('base64')});return j({})});};
 const verify=()=>p.evaluate(async()=>{const r=await verifyProof(27,'https://github.com/a/b','https://x.example.com');return r.res.map(x=>x.join(':')).join(',')});
 await mock('FROM python:3.12-slim\nUSER app\nHEALTHCHECK CMD curl -f http://localhost/ || exit 1\n');
 let v=await verify();ok('good Dockerfile passes pin/user/health',/dock-pin:true,dock-user:true,dock-health:true/.test(v),v);
 await mock('FROM python:latest\nCMD x\n');v=await verify();ok('bad Dockerfile fails all three',/dock-pin:false,dock-user:false,dock-health:false/.test(v),v);
 await mock('FROM python:3.12\nUSER root\nHEALTHCHECK CMD true\n');v=await verify();ok('USER root is not non-root',/dock-user:false/.test(v)&&/dock-health:true/.test(v),v);
 await mock('FROM node:20 AS build\nFROM python:3.12-slim\nUSER 1000\nHEALTHCHECK CMD true\n');v=await verify();ok('multi-stage with unpinned? both pinned ok',/dock-pin:true/.test(v)&&/dock-user:true/.test(v),v);
 ok('no page errors',errs.length===0,errs.join('|'));
 servers.forEach(s=>s.kill());await b.close();console.log(fails?'FAILS '+fails:'ALL PASS');process.exit(fails?1:0)})();
