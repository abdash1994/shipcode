// Share feature: Web Share API when present, otherwise a share sheet (copy, WhatsApp, Telegram, email, SMS, LinkedIn, X); question deep links
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
const PORT=8795;let fails=0;const ok=(n,c)=>{console.log((c?'PASS ':'FAIL ')+n);if(!c)fails++;};
(async()=>{
const srv=spawn('python3',['-m','http.server',PORT,'--directory',path.join(__dirname,'..')],{stdio:'ignore'});
await new Promise(r=>setTimeout(r,1000));
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:390,height:844},permissions:['clipboard-read','clipboard-write']});
const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto(`http://localhost:${PORT}/index.html`);await p.waitForTimeout(800);
await p.evaluate(()=>{S.start=shift(todayISO(),-3);S.done=[];save();location.hash='#today';route();});await p.waitForTimeout(500);
ok('footer has a share link',await p.evaluate(()=>!!document.querySelector('#mkfoot [data-share=app]')));
// 1. no Web Share: sheet appears
await p.evaluate(()=>{delete navigator.share;try{Object.defineProperty(navigator,'share',{value:undefined,configurable:true});}catch(e){}});
await p.click('#mkfoot [data-share=app]');await p.waitForSelector('#shareSheet');
ok('sheet opens with link input',await p.evaluate(()=>/^http/.test(document.querySelector('.share-url').value)));
const hrefs=await p.evaluate(()=>[...document.querySelectorAll('#shareSheet a')].map(a=>a.href));
ok('WhatsApp, Telegram, email, SMS, LinkedIn, X links',['wa.me','t.me','mailto:','sms:','linkedin.com','twitter.com'].every(k=>hrefs.some(h=>h.includes(k))));
ok('links carry the app URL',hrefs.every(h=>decodeURIComponent(h).includes('localhost:'+PORT)));
await p.click('[data-sh=copy]');await p.waitForTimeout(300);
ok('copy puts the link on the clipboard',await p.evaluate(()=>navigator.clipboard.readText()).then(t=>t.includes('localhost:'+PORT)));
ok('sheet fits phone width',await p.evaluate(()=>{const r=document.querySelector('.share-box').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth;}));
await p.keyboard.press('Escape');ok('Escape closes sheet',await p.evaluate(()=>!document.getElementById('shareSheet')));
// 2. Web Share present: called with url, no sheet
await p.evaluate(()=>{window.__s=null;Object.defineProperty(navigator,'share',{value:o=>{window.__s=o;return Promise.resolve();},configurable:true});});
await p.click('#mkfoot [data-share=app]');await p.waitForTimeout(200);
ok('navigator.share called with title, text, url',await p.evaluate(()=>window.__s&&window.__s.title==='ShipCode'&&window.__s.text.length>20&&/^http/.test(window.__s.url)));
ok('no sheet when native share works',await p.evaluate(()=>!document.getElementById('shareSheet')));
// 3. share rejected (not cancel) -> falls back to sheet; cancel -> nothing
await p.evaluate(()=>{Object.defineProperty(navigator,'share',{value:()=>Promise.reject(new DOMException('x','AbortError')),configurable:true});});
await p.click('#mkfoot [data-share=app]');await p.waitForTimeout(200);
ok('user cancel does not open sheet',await p.evaluate(()=>!document.getElementById('shareSheet')));
await p.evaluate(()=>{Object.defineProperty(navigator,'share',{value:()=>Promise.reject(new DOMException('x','NotAllowedError')),configurable:true});});
await p.click('#mkfoot [data-share=app]');await p.waitForTimeout(200);
ok('failure falls back to sheet',await p.evaluate(()=>!!document.getElementById('shareSheet')));
await p.click('[data-sh=close]');
// 4. per-question share deep link
await p.goto(`http://localhost:${PORT}/index.html#sd`);await p.waitForSelector('#qaList details',{timeout:15000});
await p.evaluate(()=>{Object.defineProperty(navigator,'share',{value:undefined,configurable:true});});
await p.click('#qaList details summary');await p.click('#qaList details[open] [data-share]');await p.waitForSelector('#shareSheet');
const u=await p.evaluate(()=>document.querySelector('.share-url').value);
ok('question link is #sd/<id> ('+u+')',/#sd\/[a-z0-9]+$/.test(u));
await p.goto(u.replace(/^https?:\/\/[^/]+/,'http://localhost:'+PORT));await p.waitForSelector('.qa-focus',{timeout:15000});
ok('shared question link opens that single question',await p.evaluate(()=>document.querySelectorAll('#qaList details').length===1));
ok('no page errors',errs.length===0);
await b.close();srv.kill();console.log(fails?'FAILED '+fails:'ALL PASSED');process.exit(fails?1:0);})();
