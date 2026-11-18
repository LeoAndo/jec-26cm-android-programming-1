// npm install --prefix /tmp/midterm-check jsdom@26
// NODE_PATH=/tmp/midterm-check/node_modules node scripts/check-midterm-distribution.cjs [HTML]
// 実際の配布HTMLをDOM上で動かし、時計だけを制御する。普段のブラウザは操作しない。
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {JSDOM, VirtualConsole} = require('jsdom');
const file = path.resolve(process.argv[2] || 'dist/midterm/midterm-practice.html');
let clock = 1800000000000;
const errors = [];
const virtualConsole = new VirtualConsole();
virtualConsole.on('jsdomError', error => errors.push(error.message));
virtualConsole.on('error', error => errors.push(String(error)));
const dom = new JSDOM(fs.readFileSync(file, 'utf8'), {
  runScripts: 'dangerously', virtualConsole,
  beforeParse(window) {
    window.Date.now = () => clock;
    window.scrollTo = () => {};
    window.setInterval = () => 1;
    window.clearInterval = () => {};
  }
});
const {document, Event} = dom.window;
const $ = id => document.getElementById(id);
const data = JSON.parse($('midterm-data').textContent);
const changeLanguage = code => { $('language').value = code; $('language').dispatchEvent(new Event('change', {bubbles:true})); };
const fields = () => [...document.querySelectorAll('#questions fieldset')];
const snapshot = () => fields().map(q => [q.dataset.questionId, [...q.querySelectorAll('input')].map(x=>x.value).join('')]);
function checkSet(mock=false) {
  const qs=fields(), counts={};
  assert.equal(qs.length,20); assert.equal(new Set(qs.map(q=>q.dataset.questionId)).size,20);
  for(const q of qs) {
    const id=q.dataset.questionId, item=data.banks.ja[id], group=item.group+':'+item.kind;
    counts[group]=(counts[group]||0)+1;
    if(mock)assert(data.mockIds.includes(id));
    const expectedCode=document.createElement('code'); expectedCode.innerHTML=item.code;
    assert.equal(q.querySelector('pre.question-code code').textContent,expectedCode.textContent);
  }
  assert.equal(Object.keys(counts).length,20); assert(Object.values(counts).every(n=>n===1));
  assert.equal(qs.filter(q=>data.banks.ja[q.dataset.questionId].kind==='blank').length,10);
}
function answer(count=20, correct=true) {
  for(const q of fields().slice(0,count)) {
    const id=q.dataset.questionId, index=data.banks.ja[id].answer;
    const input=[...q.querySelectorAll('input')].find(x=>correct?Number(x.value)===index:Number(x.value)!==index);
    input.click();
  }
}
function submit() { $('quiz-form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})); }
function finishBlank() { submit(); $('confirm-grade').click(); }
function setup() { $('choose-mode').click(); }
assert.equal($('load-error').hidden,true);
assert.equal(data.languages.length,7);
const sets=new Set();
for(const lang of data.languages) {
  changeLanguage(lang.code); $('start-practice').click(); checkSet();
  assert.equal(document.documentElement.lang,lang.code);
  const order=snapshot(); sets.add(order.map(q=>q[0]).sort().join(','));
  answer(1); changeLanguage(lang.code==='ja'?'en':'ja');
  assert.deepEqual(snapshot(),order); assert.equal($('answered').textContent,'1');
  assert.equal(document.querySelectorAll('#questions input:checked').length,1);
  $('bilingual').click(); assert.deepEqual(snapshot(),order);
  answer(); submit(); assert.equal($('score').textContent,'100');
  changeLanguage(lang.code); assert.equal($('score').textContent,'100');
  assert.equal($('review').querySelectorAll('article.correct').length,20);
  setup();
}
assert(sets.size>1);
$('start-practice').click(); answer(20,false); submit(); assert.equal($('score').textContent,'0'); assert.equal($('blank-count').textContent,'0');
$('retry').click(); assert.equal($('answered').textContent,'0'); answer(10); submit(); assert.equal($('confirm-unanswered').hidden,false);
$('keep-answering').click(); assert.equal($('confirm-unanswered').hidden,true); assert.equal(document.activeElement.type,'radio');
submit(); $('confirm-grade').click(); assert.equal($('score').textContent,'50'); assert.equal($('blank-count').textContent,'10'); setup();
// 参照可の60分復習：言語切替で締切を延ばさず、期限後のクリックを採点に含めない。
document.querySelector('[name=timing][value=timed]').click(); $('start-practice').click(); assert.equal($('timer').textContent,'60:00');
answer(1); const before=snapshot(); clock+=60000; changeLanguage('fr'); assert.deepEqual(snapshot(),before); assert.equal($('timer').textContent,'59:00');
clock+=59*60000; answer(2); assert.equal($('results').hidden,false); assert.equal($('expired').hidden,false); assert.equal($('score').textContent,'5'); assert.equal($('blank-count').textContent,'19'); setup();
// 日本語限定、再抽選、時間切れ、採点後の多言語解説。
changeLanguage('my'); $('start-mock').click(); checkSet(true); const mockBefore=snapshot(); assert.equal(document.documentElement.lang,'ja');
assert.equal($('language').disabled,true); assert.equal($('bilingual').disabled,true); assert.equal($('catalog').hidden,true); assert.equal($('question-bank').children.length,0); assert.equal($('review').children.length,0);
assert.equal($('timer').textContent,'60:00'); answer(10); clock+=60*60000; document.dispatchEvent(new Event('visibilitychange'));
assert.equal($('score').textContent,'50'); assert.equal($('blank-count').textContent,'10'); assert.equal($('expired').hidden,false);
changeLanguage('mn'); assert.equal($('score').textContent,'50'); assert.equal(document.documentElement.lang,'mn');
$('retry').click(); checkSet(true); assert.equal(document.documentElement.lang,'ja'); assert.equal($('timer').textContent,'60:00'); assert.equal($('answered').textContent,'0'); assert.notDeepEqual(snapshot(),mockBefore); finishBlank(); setup();
$('catalog').open=true; $('catalog').dispatchEvent(new Event('toggle')); assert.equal($('question-bank').querySelectorAll('article').length,40);
assert.deepEqual(errors,[]);
assert.equal(document.querySelectorAll('script[src], link[rel=stylesheet], iframe').length,0);
dom.window.close();
// 教材ZIP内のページも同じ40問・配分と期限判定で動くことを確かめる。
const practiceDom = new JSDOM(fs.readFileSync(path.join(__dirname,'../docs/practice/midterm.html'),'utf8'), {
  runScripts:'dangerously', virtualConsole,
  beforeParse(window) { window.Date.now=()=>clock; window.setInterval=()=>1; window.clearInterval=()=>{}; }
});
const practiceDoc = practiceDom.window.document, PracticeEvent = practiceDom.window.Event;
const p = id => practiceDoc.getElementById(id);
const practiceFields = () => [...p('questions').querySelectorAll('fieldset')];
const practiceSnapshot = () => practiceFields().map(q=>[q.dataset.questionId,[...q.querySelectorAll('input')].map(x=>x.value).join('')]);
const practiceAnswer = count => { for(const q of practiceFields().slice(0,count)) q.querySelector(`input[value="${data.banks.ja[q.dataset.questionId].answer}"]`).click(); };
const practiceSubmit = () => p('quiz-form').dispatchEvent(new PracticeEvent('submit',{bubbles:true,cancelable:true}));
assert.equal(p('question-bank').querySelectorAll('article').length,40);
practiceDoc.querySelector('[name=mode][value=timed]').click(); p('start').click();
const practiceOrder = practiceSnapshot(), practiceCounts = {};
for(const q of practiceFields()) { const item=data.banks.ja[q.dataset.questionId], key=item.group+':'+item.kind; practiceCounts[key]=(practiceCounts[key]||0)+1; }
assert.equal(Object.keys(practiceCounts).length,20); assert(Object.values(practiceCounts).every(n=>n===1));
practiceAnswer(1); clock+=60*60000; practiceAnswer(2);
assert.equal(p('results').hidden,false); assert.equal(p('expired').hidden,false); assert.equal(p('score').textContent,'5'); assert.equal(p('blank-count').textContent,'19');
p('retry').click(); assert.equal(p('timer').textContent,'60:00'); assert.equal(p('answered').textContent,'0'); assert.notDeepEqual(practiceSnapshot(),practiceOrder);
practiceAnswer(20); practiceSubmit(); assert.equal(p('score').textContent,'100');
p('retry').click(); practiceSubmit(); assert.equal(p('confirm-unanswered').hidden,false); p('keep-answering').click(); assert.equal(p('confirm-unanswered').hidden,true);
practiceSubmit(); p('confirm-grade').click(); assert.equal(p('blank-count').textContent,'20'); assert.equal(p('score').textContent,'0');
assert.deepEqual(errors,[]); practiceDom.window.close();
console.log(JSON.stringify({languages:7,practicePool:40,mockPool:40,questions:20,balanced:true,textbookPage:true,languageState:true,grading:true,unanswered:true,deadline:true,lateAnswerRejected:true,retry:true,externalDependencies:0}));
