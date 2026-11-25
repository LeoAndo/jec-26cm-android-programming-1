// NODE_PATH=/path/to/jsdom/node_modules node scripts/check-exam-practice.cjs /private/practice.html [...]
// ローカルで生成した復習HTMLを実行する。ネットワーク・Classroom・クリップボードは使わない。
const fs = require('node:fs');
const assert = require('node:assert/strict');
const {JSDOM, VirtualConsole} = require('jsdom');
assert(process.argv.length > 2, '検査するHTMLを指定してください。');
for (const file of process.argv.slice(2)) {
  let clock = 1800000000000, random = 451;
  const errors = [], virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => errors.push(error.message));
  virtualConsole.on('error', error => errors.push(String(error)));
  const dom = new JSDOM(fs.readFileSync(file, 'utf8'), {
    runScripts:'dangerously', virtualConsole,
    beforeParse(window) {
      window.Date.now = () => clock;
      window.Math.random = () => ((random = (random * 16807) % 2147483647) - 1) / 2147483646;
      window.scrollTo = () => {};
      window.setInterval = () => 1;
      window.clearInterval = () => {};
    }
  });
  const {document, Event} = dom.window, $ = id => document.getElementById(id);
  const data = JSON.parse($('midterm-data').textContent), settings = data.settings;
  assert(settings, '今回用の設定がありません。');
  const size = settings.drawCount, points = settings.pointsPerQuestion ?? 1;
  const score = count => String(Number((count * points).toPrecision(15)));
  const fields = () => [...document.querySelectorAll('#questions fieldset')];
  const snapshot = () => fields().map(q => [q.dataset.questionId, [...q.querySelectorAll('input')].map(x=>x.value)]);
  const language = code => { $('language').value = code; $('language').dispatchEvent(new Event('change', {bubbles:true})); };
  const submit = () => $('quiz-form').dispatchEvent(new Event('submit', {bubbles:true,cancelable:true}));
  function answer(count, right=true) {
    for (const q of fields().slice(0,count)) {
      const correct = data.banks.ja[q.dataset.questionId].answer;
      [...q.querySelectorAll('input')].find(input => (Number(input.value) === correct) === right).click();
    }
  }
  function checkQuestions() {
    assert.equal(fields().length, size);
    assert.equal(new Set(fields().map(q=>q.dataset.questionId)).size,size);
    assert.equal($('draw-total').textContent,String(size));
    for(const q of fields()) {
      const expected = document.createElement('code');
      expected.innerHTML = data.banks.ja[q.dataset.questionId].code;
      assert.equal(q.querySelector('pre code').textContent, expected.textContent);
      assert.equal(q.querySelectorAll('input').length,4);
      assert.deepEqual([...q.querySelectorAll('.letter')].map(el=>el.textContent), ['ア','イ','ウ','エ']);
    }
  }
  assert.equal($('load-error').hidden,true);
  assert.equal(document.querySelectorAll('#language option').length,data.languages.length);
  for(const lang of data.languages) {
    language(lang.code); $('start-practice').click(); checkQuestions();
    const before = snapshot(); answer(1);
    language(data.languages.find(other=>other.code!==lang.code)?.code || lang.code);
    assert.deepEqual(snapshot(),before);
    assert.equal($('answered').textContent,'1');
    assert.equal(document.querySelectorAll('#questions input:checked').length,1);
    $('bilingual').click(); assert.deepEqual(snapshot(),before);
    answer(size); submit();
    assert.equal($('score').textContent,score(size));
    assert.equal($('review').querySelectorAll('article.correct').length,size);
    language(lang.code); assert.equal($('score').textContent,score(size));
    $('choose-mode').click();
  }
  $('start-practice').click(); answer(size,false); submit();
  assert.equal($('score').textContent,'0'); assert.equal($('blank-count').textContent,'0');
  $('retry').click(); assert.equal($('answered').textContent,'0');
  const partial = Math.floor(size/2); answer(partial); submit();
  assert.equal($('confirm-unanswered').hidden,false);
  $('keep-answering').click(); assert.equal(document.activeElement.type,'radio');
  submit(); $('confirm-grade').click();
  assert.equal($('score').textContent,score(partial));
  assert.equal($('blank-count').textContent,String(size-partial));
  $('choose-mode').click();
  document.querySelector('[name=timing][value=timed]').click(); $('start-practice').click();
  const before = snapshot(); clock += settings.durationMinutes*60000-1;
  language(data.languages[0].code); assert.deepEqual(snapshot(),before);
  assert.equal($('timer').textContent,'00:01');
  clock += 1; answer(1);
  assert.equal($('expired').hidden,false); assert.equal($('score').textContent,'0');
  assert.equal($('blank-count').textContent,String(size));
  const orders = new Set();
  for(let trial=0;trial<12;trial++) {
    $('retry').click(); checkQuestions(); orders.add(JSON.stringify(snapshot()));
    submit(); $('confirm-grade').click();
  }
  assert(orders.size>1,'再挑戦で問題・選択肢の順番が変わりません。');
  $('choose-mode').click(); $('catalog').open=true; $('catalog').dispatchEvent(new Event('toggle'));
  assert.equal($('question-bank').querySelectorAll('article').length,Object.keys(data.banks.ja).length);
  assert.equal(document.querySelectorAll('script[src],link[rel=stylesheet],iframe').length,0);
  assert.deepEqual(errors,[]);
  dom.window.close();
  console.log(JSON.stringify({file, pool:Object.keys(data.banks.ja).length, draw:size,
                             languages:data.languages.length, points:settings.pointsPerQuestion,
                             languageState:true, grading:true, deadline:true, retry:true}));
}
