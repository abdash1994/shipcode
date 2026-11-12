const {chromium,devices}=require('playwright');(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices['iPhone 13']});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
process.on('exit',()=>{});await p.route('https://**',r=>r.abort());await p.addInitScript(()=>{window.__SHIPCODE_SELF_RT=true;});
let f=0;const ok=(n,v)=>{if(!v)f++;console.log((v?'PASS ':'FAIL ')+n)};
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(500);
await p.evaluate(()=>{S.start=shift(todayISO(),-3);S.habit={min:120,dpw:7,mode:'flex',at:'19:00',deep:0,deepDay:6,goal:'sprint',depth:'core'};save();});
const openCode=async id=>{await p.evaluate(id=>{openLab(id,false);lab.phase="code";renderLab();},id);await p.waitForTimeout(500);};
// default is the plain editor
await openCode('L53-4');ok('plain textarea by default',await p.evaluate(()=>!document.querySelector('.cm-editor')&&!!document.getElementById('code')));
// settings toggle
await p.evaluate(()=>{closeSheet();location.hash='#settings';route();});await p.waitForTimeout(300);await p.check('[data-ui=cm-toggle]');ok('toggle stored',await p.evaluate(()=>localStorage.getItem('shipcode.cm')==='1'));
await openCode('L53-4');await p.waitForSelector('.cm-editor',{timeout:5000});
ok('CodeMirror mounted, textarea hidden',await p.evaluate(()=>!!document.querySelector('.ed.cm .cm-editor')&&getComputedStyle(document.getElementById('code')).display==='none'));
ok('proxy returns starter code',await p.evaluate(()=>/def count_evens/.test(document.getElementById('code').value)));
ok('syntax highlighting classes present',await p.evaluate(()=>document.querySelectorAll('.cm-editor .tok-keyword').length>0));
ok('mobile keyboard attributes off',await p.evaluate(()=>{const e=document.querySelector('.cm-content');return e.getAttribute('autocorrect')==='off'&&e.getAttribute('autocapitalize')==='off'&&e.getAttribute('spellcheck')==='false'}));
// type the fix: select all, type solution with real keyboard (auto-indent must not double indentation)
await p.click('.cm-content');await p.keyboard.press('Control+A');await p.keyboard.press('Delete');
const lines=['def count_evens(nums):','total = 0','for x in nums:','if x % 2 == 0:','total += 1','DEDENT2','return total'];
for(const l of lines){if(l==='DEDENT2'){await p.keyboard.press('Shift+Tab');await p.keyboard.press('Shift+Tab');continue;}await p.keyboard.type(l);await p.keyboard.press('Enter');}
const v=await p.evaluate(()=>document.getElementById('code').value);console.log(JSON.stringify(v));
ok('auto-indent after colon works',/def count_evens\(nums\):\n    total = 0\n    for x in nums:\n        if x % 2 == 0:\n            total \+= 1\n    return total/.test(v));
// draft survives
await p.evaluate(()=>flushDraft());ok('draft saved from CodeMirror content',await p.evaluate(()=>drafts[draftKey()]&&drafts[draftKey()].includes('total += 1')));
// run with Ctrl+Enter
await p.keyboard.press('Control+Enter');await p.waitForFunction(()=>lab&&lab.result||lab&&lab.passed,{timeout:60000}).catch(()=>{});await p.waitForTimeout(1500);
ok('Ctrl+Enter runs the CodeMirror code and the lab passes',await p.evaluate(()=>lab&&lab.passed===true));
// symbol bar
const symN=await p.$$('[data-l=sym]');console.log('symbol buttons:',symN.length);if(symN.length){const before=await p.evaluate(()=>document.getElementById('code').value.length);await p.click('[data-l=sym][data-c=":"]');ok('symbol bar inserts into CodeMirror',await p.evaluate(b=>document.getElementById('code').value.length>b,before));}
// reset restores starter via proxy
await p.evaluate(()=>{const ed=document.getElementById('code');ed.value='x = 1';});ok('setting value updates the editor',await p.evaluate(()=>document.querySelector('.cm-content').innerText.includes('x = 1')));
// SQL lab
await p.evaluate(()=>closeSheet());await openCode('L43-8');await p.waitForSelector('.cm-editor',{timeout:5000});
ok('SQL lab gets CodeMirror with SQL text',await p.evaluate(()=>/SELECT dept/.test(document.getElementById('code').value)));
await p.keyboard.press('Escape');
// script blocked: stays usable
p.on('console',m=>{if(/DEL/.test(m.text()))console.log(m.text())});
await p.evaluate(()=>{closeSheet();console.log('DEL',delete window.ShipEditor,typeof window.ShipEditor);cmP=null;document.querySelectorAll('script[src="cm/editor.js"]').forEach(s=>s.remove());});
p.on('requestfailed',q=>console.log('REQFAIL',q.url().slice(-30)));
{const cdp=await p.context().newCDPSession(p);await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});}
await p.route('**/cm/editor.js',r=>r.abort());await openCode('L53-5');await p.waitForTimeout(800);
console.log('DBG',await p.evaluate(()=>({cm:!!document.querySelector('.cm-editor'),disp:getComputedStyle(document.getElementById('code')).display,id:document.querySelector('.sheet-head')&&document.querySelector('.sheet-head').innerText.slice(0,40)})));
ok('if the editor fails to load the textarea still works',await p.evaluate(()=>!document.querySelector('.cm-editor')&&getComputedStyle(document.getElementById('code')).display!=='none'));
ok('no page errors '+errs.join('|'),!errs.length);console.log(f?'FAILS '+f:'ALL PASS');await b.close();})();
