// Node.js 22以降とmacOSのChromeで実行。普段のブラウザと別プロファイルを使う。
import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const target = path.resolve(process.argv[2] || path.join(root, 'docs/practice/midterm.html'));
const profile = await fs.mkdtemp(path.join(os.tmpdir(), 'midterm-404-chrome-'));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ['--headless=new', '--no-first-run', '--no-default-browser-check', '--user-data-dir=' + profile, '--remote-debugging-port=0', 'about:blank'], {stdio:'ignore'});
let ws;
try {
  let port;
  for(let i=0; i<100; i++) {
    try { port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0]; break; }
    catch { await new Promise(resolve=>setTimeout(resolve,100)); }
  }
  if(!port) throw Error('Chromeを起動できませんでした。');
  const tab=await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
  ws=new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true});});
  let id=0; const pending=new Map(), exceptions=[], requests=[];
  ws.addEventListener('message',event=>{
    const message=JSON.parse(event.data);
    if(message.id) {const p=pending.get(message.id); pending.delete(message.id); message.error?p.reject(Error(JSON.stringify(message.error))):p.resolve(message.result);}
    if(message.method==='Runtime.exceptionThrown') exceptions.push(message.params);
    if(message.method==='Network.requestWillBeSent') requests.push(message.params.request.url);
  });
  function send(method,params={}) {return new Promise((resolve,reject)=>{const key=++id;pending.set(key,{resolve,reject});ws.send(JSON.stringify({id:key,method,params}));});}
  async function evaluate(expression) {
    const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
    if(r.exceptionDetails) throw Error(JSON.stringify(r.exceptionDetails));
    return r.result.value;
  }
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
  await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:pathToFileURL(target).href});
  await evaluate(`new Promise(resolve=>{const ready=()=>{if(document.querySelector('#start')&&!document.querySelector('#start').disabled)resolve(true);else setTimeout(ready,20)};ready()})`);
  const result=await evaluate(`(() => {
    const $=id=>document.getElementById(id), assert=(v,m)=>{if(!v)throw Error(m)};
    const source=[...$('question-bank').querySelectorAll('article')];
    assert(source.length===120,'120問');
    const answerId=Object.fromEntries(source.map(q=>[q.dataset.id,[...q.querySelectorAll('.options li')].findIndex(c=>c.dataset.correct==='true')]));
    const fill=(mode)=>[...document.querySelectorAll('#questions fieldset')].forEach((q,i)=>{
      if(mode==='partial'&&i>=10)return;
      const inputs=[...q.querySelectorAll('input')];
      const correct=answerId[q.dataset.questionId];
      const selected=inputs.find(x=>mode==='wrong'?Number(x.value)!==correct:Number(x.value)===correct);
      selected.click();
    });
    const submit=()=>$('quiz-form').requestSubmit();
    const sets=new Set(), orders=new Set(), choiceOrders=new Set();
    for(let trial=0;trial<80;trial++) {
      $(trial?'retry':'start').click();
      const q=[...document.querySelectorAll('#questions fieldset')];
      assert(q.length===20,'20問'); assert(new Set(q.map(x=>x.dataset.questionId)).size===20,'重複なし');
      const counts={}; q.forEach(x=>{const unit=x.dataset.questionId.slice(0,3);counts[unit]=(counts[unit]||0)+1});
      assert(Object.keys(counts).length===10&&Object.values(counts).every(n=>n===2),'各単元2問');
      sets.add(q.map(x=>x.dataset.questionId).sort().join(',')); orders.add(q.map(x=>x.dataset.questionId).join(','));
      q.forEach(x=>choiceOrders.add([...x.querySelectorAll('input')].map(i=>i.value).join('')));
      fill('correct'); assert($('answered').textContent==='20','回答済み20'); submit();
      assert($('score').textContent==='100'&&!$('results').hidden,'正答がシャッフル後も100点');
      assert($('review').querySelectorAll('article.correct').length===20,'解説20問');
    }
    assert(sets.size>1&&orders.size>1&&choiceOrders.size>1,'抽選・問題順・選択肢順の変化');
    $('retry').click(); fill('wrong'); submit(); assert($('score').textContent==='0'&&$('blank-count').textContent==='0','全誤答0点');
    $('retry').click(); fill('partial'); submit(); assert(!$('confirm-unanswered').hidden,'未回答確認');
    $('keep-answering').click(); assert($('confirm-unanswered').hidden&&document.activeElement.type==='radio','未回答へ戻る');
    submit(); $('confirm-grade').click(); assert($('score').textContent==='50'&&$('blank-count').textContent==='10','10正答・10未回答');
    $('retry').click(); assert($('answered').textContent==='0'&&!document.querySelector('#questions input:checked'),'再挑戦で回答消去');
    submit(); $('confirm-grade').click(); assert($('score').textContent==='0'&&$('blank-count').textContent==='20','全未回答0点');
    $('choose-mode').click(); document.querySelector('[name="mode"][value="timed"]').click(); $('start').click();
    assert($('timer').textContent==='60:00'&&!$('timer-box').hidden,'60分開始');
    const now=Date.now; Date.now=()=>now()+61*60*1000; document.dispatchEvent(new Event('visibilitychange')); Date.now=now;
    assert(!$('results').hidden&&!$('expired').hidden&&$('blank-count').textContent==='20','別タブ経過時も時間切れ自動採点');
    $('retry').click(); assert($('timer').textContent==='60:00','時間をリセット');
    submit(); $('confirm-grade').click(); $('choose-mode').click();
    assert(!$('setup').hidden,'設定に戻る'); $('catalog').open=true;
    assert($('question-bank').querySelectorAll('.explanation').length===120,'全解説一覧');
    assert(document.documentElement.scrollWidth<=innerWidth,'デスクトップで横はみ出しなし');
    return {pool:120,trials:80,balanced:true,uniqueSets:sets.size,optionOrders:choiceOrders.size,grading:true,unanswered:true,retry:true,timer:true};
  })()`);
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:false});
  const narrow=await evaluate(`({overflow:document.documentElement.scrollWidth>innerWidth,catalog:document.querySelectorAll('#question-bank article').length})`);
  if(narrow.overflow)throw Error('390pxの画面で横にはみ出します。');
  await evaluate(`document.querySelector('#catalog').open=false; scrollTo(0,0); true`);
  if(process.argv[3]) {
    const output=path.resolve(process.argv[3]); await fs.mkdir(output,{recursive:true});
    const shot=await send('Page.captureScreenshot',{format:'png'}); await fs.writeFile(path.join(output,'midterm-mobile.png'),Buffer.from(shot.data,'base64'));
    await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
    const desktop=await send('Page.captureScreenshot',{format:'png'}); await fs.writeFile(path.join(output,'midterm-desktop.png'),Buffer.from(desktop.data,'base64'));
  }
  if(exceptions.length)throw Error(JSON.stringify(exceptions));
  if(requests.some(url=>/^https?:/.test(url)))throw Error('外部通信が発生しました。');
  console.log(JSON.stringify({target,offline:true,...result,narrow,exceptions:exceptions.length,networkRequests:requests.length},null,2));
} finally {
  if(ws)ws.close(); chrome.kill('SIGTERM');
  await new Promise(resolve=>chrome.exitCode!==null?resolve():chrome.once('exit',resolve));
  await fs.rm(profile,{recursive:true,force:true});
}
