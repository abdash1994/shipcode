const {chromium}=require('playwright');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
const SB='https://ljcusofcvjnrrojxsicw.supabase.co';
// in-memory fake of the Supabase endpoints the app uses
const db={states:{},proofs:{},events:[],otp:[],tokens:{'tok-A':{id:'user-a',email:'a@example.com'},'tok-B':{id:'user-b',email:'b@example.com'}},refreshed:0,down:false};
async function fake(route){const req=route.request(),u=new URL(req.url()),m=req.method(),h=req.headers();
  const cors={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'};
  const send=(status,body)=>route.fulfill({status,headers:{...cors,'content-type':'application/json'},body:body===undefined?'':JSON.stringify(body)});
  if(m==='OPTIONS')return send(204);
  if(db.down)return route.abort();
  const tok=(h.authorization||'').replace('Bearer ',''),user=db.tokens[tok]||null;let body=null;try{body=req.postDataJSON();}catch(e){}
  const p=u.pathname;
  if(p==='/auth/v1/otp'){db.otp.push({email:body.email,redirect:u.searchParams.get('redirect_to')});return send(200,{});}
  if(p==='/auth/v1/user')return user?send(200,user):send(401,{msg:'bad token'});
  if(p==='/auth/v1/token'){db.refreshed++;return body.refresh_token==='ref-A'?send(200,{access_token:'tok-A',refresh_token:'ref-A',expires_in:3600,user:db.tokens['tok-A']}):send(400,{error_description:'invalid refresh token'});}
  if(p==='/auth/v1/logout')return send(204);
  if(p==='/rest/v1/states'){if(!user)return send(401,{message:'no'});
    if(m==='GET')return send(200,db.states[user.id]?[{state:db.states[user.id]}]:[]);
    if(m==='POST'){if(body.user_id!==user.id)return send(403,{message:'rls'});db.states[user.id]=body.state;return send(201);}
    if(m==='DELETE'){delete db.states[user.id];return send(204);}}
  if(p==='/rest/v1/rpc/my_proof')return user?send(200,Object.keys(db.proofs).find(s=>db.proofs[s].uid===user.id)||null):send(401,{message:'no'});
  if(p==='/rest/v1/rpc/publish_proof'){if(!user)return send(401,{message:'sign in first'});let s=Object.keys(db.proofs).find(s=>db.proofs[s].uid===user.id)||('slug'+user.id.slice(-1)+'12345');db.proofs[s]={uid:user.id,display_name:body.p_name,data:body.p_data,updated_at:'2026-11-12T08:00:00Z'};return send(200,s);}
  if(p==='/rest/v1/rpc/unpublish_proof'){for(const s of Object.keys(db.proofs))if(user&&db.proofs[s].uid===user.id)delete db.proofs[s];return send(204);}
  if(p==='/rest/v1/rpc/get_proof'){const r=db.proofs[body.p_slug];return send(200,r?[{display_name:r.display_name,data:r.data,updated_at:r.updated_at}]:[]);}
  if(p==='/rest/v1/events'){db.events.push(body);return send(201);}
  return send(404,{message:'unknown '+p});}
const HABIT="{min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'full',depth:'full'}";
async function page(b){const c=await b.newContext({viewport:{width:390,height:800},permissions:['clipboard-read','clipboard-write']});const p=await c.newPage();
  await p.route('https://**',r=>r.abort());await p.route(SB+'/**',fake);await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true});p.errs=[];p.on('pageerror',e=>p.errs.push(e.message));return p;}
(async()=>{const web=require('child_process').spawn('python3',['-m','http.server','8765','-d','site','--bind','127.0.0.1']);for(let i=0;i<60;i++){try{await fetch('http://127.0.0.1:8765/index.html');break;}catch(e){await new Promise(r=>setTimeout(r,200));}}
 const b=await chromium.launch();
 // ---------- device 1: sign in, sync up
 const p=await page(b);await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(400);
 await p.evaluate(h=>{S.start=shift(todayISO(),-4);S.done=[1,2];S.labs={'L1-0':todayISO()};S.habit=eval('('+h+')');save();location.hash='#ref';route();},HABIT);await p.waitForTimeout(200);
 ok('settings shows optional sign-in and says what is stored',/ShipCode account \(optional\)/i.test(await p.innerText('.view'))&&/store your email address and your progress/.test(await p.innerText('.view')));
 await p.fill('#acctEmail','not-an-email');await p.click('[data-ui=acct-send]');ok('bad email rejected locally',/valid email/.test(await p.innerText('.view'))&&db.otp.length===0);
 await p.fill('#acctEmail',' A@Example.com ');await p.click('[data-ui=acct-send]');await p.waitForFunction(()=>/Check your email/.test(document.querySelector('.view').innerText));
 ok('sign-in link requested with this site as the return address',db.otp.length===1&&db.otp[0].email==='a@example.com'&&db.otp[0].redirect==='http://127.0.0.1:8765/',JSON.stringify(db.otp));
 // the emailed link lands back with the session in the address
 await p.goto('http://127.0.0.1:8765/index.html#access_token=tok-A&refresh_token=ref-A&expires_in=3600&token_type=bearer&type=magiclink');await p.waitForFunction(()=>acct&&acct.user.id==='user-a'&&syncMode==='account',null,{timeout:8000});
 ok('token removed from the address bar',await p.evaluate(()=>!/access_token/.test(location.href)&&location.hash==='#ref'));
 ok('signed-in state shown',/Signed in as a@example.com/.test(await p.innerText('.view'))&&/Synced to your ShipCode account/.test(await p.innerText('#syncState')));
 await p.waitForFunction(()=>true);await p.waitForTimeout(1600);
 ok('local progress uploaded on first sign-in',db.states['user-a']&&db.states['user-a'].done.length===2,JSON.stringify(Object.keys(db.states)));
 await p.evaluate(()=>{S.done=[1,2,3];save();});await p.waitForTimeout(1600);ok('later saves reach the account',db.states['user-a'].done.length===3);
 // ---------- device 2: fresh browser, sign in, progress arrives
 const q=await page(b);await q.goto('http://127.0.0.1:8765/index.html#access_token=tok-A&refresh_token=ref-A&expires_in=3600&type=magiclink');
 await q.waitForFunction(()=>S.done.length===3,null,{timeout:8000});
 ok('fresh device receives the synced progress and skips onboarding',await q.evaluate(()=>S.done.length===3&&!!S.start&&!!S.habit&&!document.body.classList.contains('onboarding')));
 await q.reload();await q.waitForFunction(()=>syncMode==='account',null,{timeout:8000});ok('session survives reload',await q.evaluate(()=>acct.user.email==='a@example.com'));
 // newer change on device 2 wins on device 1 at next open
 await q.evaluate(()=>{S.done=[1,2,3,4];save();});await q.waitForTimeout(1600);
 await p.reload();await p.waitForFunction(()=>S.done.length===4,null,{timeout:8000});ok('newer progress from the other device arrives on reload',true);
 // expired token refreshes
 await p.evaluate(()=>{acct.expires_at=1;});await p.evaluate(()=>{S.xp=77;save();});await p.waitForTimeout(1800);ok('expired session refreshes itself and still saves',db.refreshed>=1&&db.states['user-a'].xp===77);
 // other account cannot be read
 const r=await page(b);await r.goto('http://127.0.0.1:8765/index.html#access_token=tok-B&refresh_token=ref-B&expires_in=3600');await r.waitForFunction(()=>acct&&acct.user.id==='user-b'&&syncMode==='account',null,{timeout:8000});
 ok('a different account starts empty',await r.evaluate(()=>S.done.length===0));
 // offline at boot: stays usable
 db.down=true;await p.reload();await p.waitForTimeout(1200);ok('server unreachable: app still works from this browser',await p.evaluate(()=>S.done.length===4&&!!acct));db.down=false;
 // bad link
 const e=await page(b);await e.goto('http://127.0.0.1:8765/index.html#error=access_denied&error_code=otp_expired&error_description=Email+link+is+invalid+or+has+expired');await e.waitForTimeout(500);
 ok('expired link explained, no crash',await e.evaluate(()=>/did not work/.test(acctMsg)&&!acct&&location.hash==='#ref'));
 // ---------- proof page
 await p.reload();await p.waitForFunction(()=>syncMode==='account');await p.evaluate(()=>{location.hash='#proof';route();});await p.waitForTimeout(200);
 ok('proof page shows a preview before publishing',/Preview of what others will see/i.test(await p.innerText('.view'))&&/Not published/i.test(await p.innerText('.view')));
 await p.click('[data-ui=proof-pub]');await p.waitForTimeout(200);ok('name is required',/Type the name/.test(await p.innerText('.view'))&&Object.keys(db.proofs).length===0);
 await p.fill('#proofName','Aditya <b>D</b>');await p.click('[data-ui=proof-pub]');await p.waitForFunction(()=>!!proofSlug);
 const slug=await p.evaluate(()=>proofSlug);const sent=db.proofs[slug];
 ok('published snapshot has counts only: no email, code or drafts',sent&&sent.data.days===4&&!/example\.com|print\(|def /.test(JSON.stringify(sent.data)),JSON.stringify(sent&&sent.data).slice(0,300));
 await p.click('[data-ui=proof-copy]');ok('link copied',(await p.evaluate(()=>navigator.clipboard.readText()))==='http://127.0.0.1:8765/#p-'+slug);
 const v=await page(b);v.on('console',m=>console.log('VCON',m.text().slice(0,200)));await v.goto('http://127.0.0.1:8765/index.html#p-'+slug);await v.waitForTimeout(1500);console.log('VDBG',slug,JSON.stringify(await v.evaluate(()=>({h:location.hash,pv:proofView,t:document.querySelector('.view').innerText.slice(0,120)}))).slice(0,600));await v.waitForFunction(()=>/Lessons completed/i.test(document.querySelector('.view').innerText),null,{timeout:8000});
 const vt=await v.innerText('.view');
 ok('visitor with no account sees the page, escaped, with the honesty note',/Aditya <b>D<\/b>/.test(vt)&&/4 of 30/i.test(vt)&&/not a certificate/i.test(vt)&&!await v.evaluate(()=>!!document.querySelector('.view h1 b')),vt.slice(0,200));
 ok('visitor is not pushed into onboarding and gets a way in',await v.evaluate(()=>!!document.querySelector('a[href="#today"]')));
 // hostile stored data renders safely
 db.proofs['evil00000001']={uid:'x',display_name:'<img src=x onerror=alert(1)>',data:{days:'<script>1</script>',repos:['javascript:alert(1)','https://github.com/a/b"><img src=x>'],tracks:['<i>x</i>'],loops:[{loop:'<b>',best:'x'}],exam:{total:'9<',of:12}},updated_at:'<svg>'};
 await v.goto('http://127.0.0.1:8765/index.html#p-evil00000001');await v.reload();await v.waitForFunction(()=>/Lessons completed/i.test(document.querySelector('.view').innerText),null,{timeout:8000});
 ok('hostile proof data cannot inject markup or script links',await v.evaluate(()=>!document.querySelector('.view img,.view script,.view i,.view svg')&&![...document.querySelectorAll('.view a')].some(a=>/^javascript:/i.test(a.getAttribute('href')||''))));
 await v.goto('http://127.0.0.1:8765/index.html#p-doesnotexist1');await v.reload();await v.waitForFunction(()=>/Page not found/i.test(document.querySelector('.view').innerText),null,{timeout:8000});ok('unknown link says not found',true);
 await p.click('[data-ui=proof-unpub]');await p.waitForFunction(()=>!proofSlug);ok('unpublish removes it',!db.proofs[slug]);
 // ---------- delete cloud copy, sign out
 await p.evaluate(()=>{location.hash='#ref';route();});await p.click('[data-ui=acct-wipe-ask]');await p.click('[data-ui=acct-wipe]');await p.waitForFunction(()=>!acct);
 ok('delete cloud copy removes the server row, keeps this browser',!db.states['user-a']&&await p.evaluate(()=>S.done.length===4&&syncMode==='local'));
 // ---------- opt-in usage counts
 const u=await page(b);await u.goto('http://127.0.0.1:8765/index.html');await u.waitForTimeout(300);
 await u.evaluate(h=>{S.start=shift(todayISO(),-2);S.habit=eval('('+h+')');save();location.hash='';route();},HABIT);await u.waitForTimeout(300);
 ok('asked once on Today, with the approved wording',/Help improve ShipCode\? Share anonymous progress counts and error messages\. No name, email or code is sent\. You can turn this off in Settings\./.test(await u.innerText('#usageAsk')));
 await u.evaluate(()=>{logErr('error','before consent')});await u.waitForTimeout(300);ok('nothing is sent before consent',db.events.length===0);
 await u.click('[data-ui=usage-no]');await u.waitForTimeout(200);ok('"No thanks" hides the question',await u.evaluate(()=>!document.getElementById('usageAsk')&&usageGet().on===false));
 await u.evaluate(()=>{logErr('error','first error after no');route();});await u.waitForTimeout(300);
 ok('asked once more at the first error, still nothing sent',await u.evaluate(()=>!!document.getElementById('usageAsk'))&&db.events.length===0);
 await u.click('[data-ui=usage-no]');await u.evaluate(()=>{logErr('error','again');route();});await u.waitForTimeout(200);ok('a second "no" is final',await u.evaluate(()=>!document.getElementById('usageAsk'))&&db.events.length===0);
 await u.evaluate(()=>{location.hash='#ref';route();});await u.check('[data-ui=usage-toggle]');await u.waitForTimeout(400);
 ok('turning it on in Settings sends one daily snapshot',db.events.length===1&&db.events[0].kind==='snapshot'&&/^[0-9a-f-]{36}$/.test(db.events[0].device),JSON.stringify(db.events).slice(0,300));
 ok('snapshot has no email, name or code',!/@|example|print\(/.test(JSON.stringify(db.events[0])));
 await u.evaluate(()=>{usageSnapshot();for(let i=0;i<9;i++)logErr('error','boom '+i);});await u.waitForTimeout(400);
 ok('one snapshot a day, errors capped at 5',db.events.filter(x=>x.kind==='snapshot').length===1&&db.events.filter(x=>x.kind==='error').length===5);
 await u.uncheck('[data-ui=usage-toggle]');await u.evaluate(()=>{logErr('error','after off')});await u.waitForTimeout(300);ok('turning it off stops sending',db.events.length===6);
 for(const pg of [p,q,r,e,v,u])if(pg.errs.length){ok('no page errors',false,pg.errs.join('|'));}
 ok('no page errors anywhere',[p,q,r,e,v,u].every(x=>x.errs.length===0));
 console.log(fails?'FAILS '+fails:'ALL PASS');web.kill();await b.close();process.exit(fails?1:0)})();
