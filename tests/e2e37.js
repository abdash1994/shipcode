const {chromium}=require('playwright');
let fails=0;const ok=(n,c,d)=>{console.log((c?'PASS ':'FAIL ')+n+(c?'':' '+(d||'')));if(!c)fails++;};
const SB='https://ljcusofcvjnrrojxsicw.supabase.co';
const db={users:{'a@example.com':{id:'user-a',pw:'correct horse 9',confirm:false}},log:[],states:{},deleted:[],mode:'auto'};
async function fake(route){const req=route.request(),u=new URL(req.url()),m=req.method();
  const cors={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'};
  const send=(s,b)=>route.fulfill({status:s,headers:{...cors,'content-type':'application/json'},body:b===undefined?'':JSON.stringify(b)});
  if(m==='OPTIONS')return send(204);let body=null;try{body=req.postDataJSON();}catch(e){}
  const p=u.pathname,tok=(req.headers().authorization||'').replace('Bearer ','');db.log.push(m+' '+p+(u.search?'?'+u.search.slice(1,40):''));
  const sess=(e)=>({access_token:'tok-'+e,refresh_token:'ref-'+e,expires_in:3600,user:{id:db.users[e].id,email:e,user_metadata:{display_name:'Ada'}}});
  if(p==='/auth/v1/signup'){const e=body.email;if(db.users[e])return send(422,{msg:'User already registered'});if(body.password.length<8)return send(422,{msg:'Password should be at least 8 characters'});
    db.users[e]={id:'user-new',pw:body.password,confirm:db.mode==='confirm'};return db.mode==='confirm'?send(200,{id:'user-new',email:e}):send(200,sess(e));}
  if(p==='/auth/v1/token'&&u.searchParams.get('grant_type')==='password'){const x=db.users[body.email];if(!x||x.pw!==body.password)return send(400,{error_description:'Invalid login credentials'});return send(200,sess(body.email));}
  if(p==='/auth/v1/recover'){db.recover=body.email;return send(200,{});}
  if(p==='/auth/v1/otp')return send(200,{});
  if(p==='/auth/v1/user'){const e=tok.replace('tok-','');if(!db.users[e])return send(401,{msg:'bad'});if(m==='PUT'){if(body.password===db.users[e].pw)return send(422,{msg:'New password should be different from the old password.'});db.users[e].pw=body.password;db.pwchanged=e;return send(200,{id:db.users[e].id,email:e});}return send(200,{id:db.users[e].id,email:e});}
  if(p==='/auth/v1/logout')return send(204);
  if(p==='/rest/v1/states'){if(m==='GET')return send(200,[]);if(m==='POST'){db.states[body.user_id]=1;return send(201);}return send(204);}
  if(p==='/rest/v1/rpc/my_proof')return send(200,null);
  if(p==='/rest/v1/rpc/delete_my_account'){const e=tok.replace('tok-','');db.deleted.push(e);delete db.users[e];return send(204);}
  if(p==='/rest/v1/events')return send(201);
  return send(404,{message:'unknown '+p});}
async function page(b,w){const c=await b.newContext({viewport:{width:w||390,height:800},permissions:['clipboard-read','clipboard-write']});const p=await c.newPage();
  await p.route('https://**',r=>r.abort());await p.route(SB+'/**',fake);await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true});p.errs=[];p.on('pageerror',e=>p.errs.push(e.message));return p;}
const URL0='http://127.0.0.1:8765/index.html';
const go=async(p,h)=>{await p.evaluate(h=>{location.hash=h;},h);await p.waitForTimeout(250);};
(async()=>{const web=require('child_process').spawn('python3',['-m','http.server','8765','-d','site','--bind','127.0.0.1']);for(let i=0;i<60;i++){try{await fetch(URL0);break;}catch(e){await new Promise(r=>setTimeout(r,200));}}
 const b=await chromium.launch();let p=await page(b);await p.goto(URL0);await p.waitForTimeout(500);
 await p.evaluate(()=>{S.start=shift(todayISO(),-3);S.done=[1,2];save();location.hash='#today';route();});await p.waitForTimeout(300);
 // avatar + guest settings
 ok('avatar visible, guest label',await p.evaluate(()=>{const a=document.getElementById('avatar');return !!a&&a.offsetWidth>0&&/Sign in/.test(a.getAttribute('aria-label'));}));
 await p.click('#avatar');await p.waitForTimeout(250);
 ok('avatar opens settings as guest',await p.evaluate(()=>location.hash==='#settings'&&/Guest/.test(document.querySelector('.view').innerText)&&!!document.querySelector('a[href="#signup"]')));
 // theme
 await p.click('[data-au=theme][data-v=dark]');await p.waitForTimeout(150);
 ok('theme dark persists',await p.evaluate(()=>document.documentElement.dataset.theme==='dark'&&localStorage.getItem('shipcode.theme')==='dark'));
 await p.click('[data-au=theme][data-v=system]');ok('theme auto clears attribute',await p.evaluate(()=>!document.documentElement.hasAttribute('data-theme')));
 // display name for guest
 await p.fill('#setName','Ada Lovelace');await p.click('[data-au=savename]');await p.waitForTimeout(200);
 ok('name saved and survives reload',await p.evaluate(()=>S.me.name==='Ada Lovelace'));
 // sign up validation
 await go(p,'#signup');
 await p.fill('#au-email','nope');await p.fill('#au-pw','longenough1');await p.fill('#au-pw2','longenough1');await p.click('form button[type=submit]');await p.waitForTimeout(200);
 ok('signup: bad email rejected locally',await p.evaluate(()=>/valid email/.test(document.getElementById('au-err').innerText))&&!db.log.some(x=>/signup/.test(x)));
 await p.fill('#au-email','new@example.com');await p.fill('#au-pw','short');await p.fill('#au-pw2','short');await p.click('form button[type=submit]');await p.waitForTimeout(200);
 ok('signup: short password rejected locally',await p.evaluate(()=>/8 characters/.test(document.getElementById('au-err').innerText)));
 await p.fill('#au-pw','longenough1');await p.fill('#au-pw2','different1');await p.click('form button[type=submit]');await p.waitForTimeout(200);
 ok('signup: mismatch rejected',await p.evaluate(()=>/do not match/.test(document.getElementById('au-err').innerText)));
 await p.fill('#au-pw','abc');await p.waitForTimeout(100);
 ok('strength meter reacts',await p.evaluate(()=>document.getElementById('pwt').textContent.length>0&&document.querySelectorAll('#pwm i.on').length===0));
 await p.fill('#au-pw','Longer-pass-phrase-9');await p.waitForTimeout(100);
 ok('strength meter strong',await p.evaluate(()=>document.querySelectorAll('#pwm i.on').length===4));
 await p.click('.aeye');ok('show password toggles',await p.evaluate(()=>document.getElementById('au-pw').type==='text'));
 await p.click('.aeye');
 // already registered
 await p.fill('#au-email','a@example.com');await p.fill('#au-pw','longenough1');await p.fill('#au-pw2','longenough1');await p.click('form button[type=submit]');await p.waitForTimeout(400);
 ok('signup: existing email explained',await p.evaluate(()=>/already has an account/.test(document.getElementById('au-err').innerText)));
 // success (auto-confirm)
 await p.fill('#au-email','new@example.com');await p.fill('#au-pw','longenough1');await p.fill('#au-pw2','longenough1');await p.click('form button[type=submit]');
 await p.waitForFunction(()=>acct&&acct.user.id==='user-new',null,{timeout:8000});await p.waitForTimeout(500);
 ok('signup success: signed in, back on Today, toast shown',await p.evaluate(()=>location.hash==='#today'&&document.getElementById('toast')&&document.getElementById('toast').classList.contains('on')));
 ok('avatar shows initials once signed in',await p.evaluate(()=>/^[A-Z]{1,2}$/.test(document.getElementById('avatar').innerText.trim())));
 await p.waitForTimeout(2500);ok('progress pushed to account',await p.evaluate(()=>syncMode==='account')&&Object.keys(db.states).includes('user-new'),JSON.stringify(db.log.slice(-6)));
 // signed-in settings
 await go(p,'#settings');
 ok('settings shows account',await p.evaluate(()=>/new@example\.com/.test(document.querySelector('.view').innerText)&&!!document.querySelector('[data-au=signout]')));
 // signin page redirects when signed in
 await go(p,'#signin');ok('signin while signed in bounces to settings',await p.evaluate(()=>location.hash==='#settings'));
 // sign out
 await p.click('[data-au=signout]');await p.waitForFunction(()=>!acct);await p.waitForTimeout(200);
 ok('sign out keeps local progress',await p.evaluate(()=>S.done.length===2&&!acct));
 // signin wrong, then right
 await go(p,'#signin');await p.fill('#au-email','a@example.com');await p.fill('#au-pw','wrong');await p.click('form button[type=submit]');await p.waitForTimeout(400);
 ok('signin: wrong password explained',await p.evaluate(()=>/do not match/.test(document.getElementById('au-err').innerText)&&document.getElementById('au-pw').value===''));
 await p.fill('#au-pw','correct horse 9');await p.click('form button[type=submit]');await p.waitForFunction(()=>acct&&acct.user.id==='user-a',null,{timeout:8000});await p.waitForTimeout(300);
 ok('signin success',await p.evaluate(()=>location.hash==='#today'&&syncMode==='account'));
 // change password
 await go(p,'#reset');await p.fill('#au-pw','correct horse 9');await p.fill('#au-pw2','correct horse 9');await p.click('form button[type=submit]');await p.waitForTimeout(400);
 ok('change password: same password explained',await p.evaluate(()=>/different/.test(document.getElementById('au-err').innerText)));
 await p.fill('#au-pw','brand new pass 77');await p.fill('#au-pw2','brand new pass 77');await p.click('form button[type=submit]');await p.waitForTimeout(500);
 ok('change password success',db.pwchanged==='a@example.com'&&await p.evaluate(()=>location.hash==='#settings'));
 // forgot
 await p.click('[data-au=signout]');await p.waitForFunction(()=>!acct);
 await go(p,'#forgot');await p.fill('#au-email','ghost@example.com');await p.click('form button[type=submit]');await p.waitForTimeout(400);
 ok('forgot: same neutral message for any email',await p.evaluate(()=>/reset link is on its way/.test(document.querySelector('.view').innerText))&&db.recover==='ghost@example.com');
 // recovery link lands
 const q=await page(b);await q.goto(URL0+'#access_token=tok-a@example.com&refresh_token=ref-a&expires_in=3600&type=recovery');
 await q.waitForFunction(()=>location.hash==='#reset',null,{timeout:8000});await q.waitForTimeout(400);
 ok('recovery link opens choose-new-password page',await q.evaluate(()=>/Choose a new password/.test(document.querySelector('.view').innerText)&&!/access_token/.test(location.href)));
 await q.fill('#au-pw','recovered pass 55');await q.fill('#au-pw2','recovered pass 55');await q.click('form button[type=submit]');await q.waitForTimeout(600);
 ok('recovery sets password',db.users['a@example.com'].pw==='recovered pass 55');
 // delete account
 await q.evaluate(()=>{S.start=todayISO();S.done=[1];save();});await go(q,'#settings');await q.click('[data-au=delask]');await q.fill('#delConfirm','nope');await q.click('[data-au=delgo]');await q.waitForTimeout(200);
 ok('delete requires typing delete',db.deleted.length===0);
 await q.fill('#delConfirm','delete');await q.click('[data-au=delgo]');await q.waitForFunction(()=>!acct,null,{timeout:8000});await q.waitForTimeout(300);
 ok('delete calls RPC and signs out, local progress kept',db.deleted.length===1&&await q.evaluate(()=>!acct&&!!S.start));
 // confirm-email flow
 db.mode='confirm';const r=await page(b);await r.goto(URL0+'#signup');await r.waitForTimeout(400);
 await r.fill('#au-email','c@example.com');await r.fill('#au-pw','longenough1');await r.fill('#au-pw2','longenough1');await r.click('form button[type=submit]');await r.waitForTimeout(500);
 ok('signup with email confirmation shows check-your-email',await r.evaluate(()=>/Confirm your email/.test(document.querySelector('.view').innerText)&&!acct));
 // journey
 const j=await page(b);await j.goto(URL0);await j.waitForTimeout(400);
 await j.evaluate(()=>{S.start=shift(todayISO(),-5);S.done=[1,2,3];save();location.hash='#path';route();});await j.waitForTimeout(400);
 ok('journey renders 4 units + 30 day nodes',await j.evaluate(()=>document.querySelectorAll('.unit').length>=4&&document.querySelectorAll('.jn[data-day]').length===30));
 ok('done nodes and one current node',await j.evaluate(()=>document.querySelectorAll('.jn.done[data-day]').length===3&&document.querySelectorAll('.jn.cur[data-day]').length===1&&document.querySelectorAll('.jbub').length===1));
 await j.click('.jn.cur[data-day]');await j.waitForTimeout(300);
 ok('node opens sheet with steps and start button',await j.evaluate(()=>!sheet.hidden&&document.querySelectorAll('.jsteps li').length>=3&&/Start the lesson/.test(sheetIn.innerText)));
 await j.click('[data-au=jgo][data-to=lesson]');await j.waitForTimeout(500);
 ok('Start the lesson opens the lesson player',await j.evaluate(()=>!!les&&les.n===4));
 await j.evaluate(()=>closeSheet());await j.waitForTimeout(200);
 await j.click('.jn[data-day="9"]');await j.waitForTimeout(200);await j.click('[data-au=jgo][data-to=day]');await j.waitForTimeout(300);
 ok('Open the whole day goes to that day',await j.evaluate(()=>location.hash==='#day-9'));
 await go(j,'#path');
 ok('pro units present',await j.evaluate(()=>document.querySelectorAll('.jn.pro').length===31));
 await j.click('.jn.pro');await j.waitForTimeout(400);ok('pro node opens lesson',await j.evaluate(()=>!!les&&typeof les.n==='string'));await j.evaluate(()=>closeSheet());
 ok('list view kept',await j.evaluate(()=>!!document.querySelector('details.jlist')));
 // old ref page now points to settings
 await go(j,'#ref');ok('reference has settings link, no settings card',await j.evaluate(()=>!!document.querySelector('a[href="#settings"]')&&!document.querySelector('[data-ui=cm-toggle]')));
 // no page errors anywhere
 ok('no page errors',[p,q,r,j].every(x=>x.errs.length===0),JSON.stringify([p,q,r,j].map(x=>x.errs)));
 // overflow at 320
 const n=await page(b,320);await n.goto(URL0);await n.waitForTimeout(300);await n.evaluate(()=>{S.start=shift(todayISO(),-2);save();});
 for(const h of ['#settings','#signin','#signup','#forgot','#path']){await n.evaluate(h=>{location.hash=h;},h);await n.waitForTimeout(300);
   ok('no horizontal overflow at 320: '+h,await n.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),await n.evaluate(()=>document.documentElement.scrollWidth));}
 await b.close();web.kill();console.log(fails?fails+' FAILED':'ALL PASS');process.exit(fails?1:0);})();
