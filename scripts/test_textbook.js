const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const source = readFileSync(path.join(__dirname, '../docs/assets/textbook.js'), 'utf8');
const key = 'jec-test';

function page(storage = {}, href = 'file:///docs/unit/index.html?from=setup#step-1', options = {}) {
  const inputs = ['step-1', 'step-2'].map(id => ({ dataset: { check: id }, checked: false,
    addEventListener(type, action) { this[type] = action; } }));
  const links = [{ href: '../en/unit/index.html', getAttribute() { return this.href; },
    addEventListener(type, action) { this[type] = action; } }];
  const progress = { value: 0 };
  const label = { textContent: '' };
  let location = new URL(href), resize, height = 42;
  const styles = {}, classes = new Set();
  const nav = { getBoundingClientRect: () => ({ height }) };
  const document = {
    body: { dataset: { progressKey: key } },
    documentElement: { style: { setProperty(name, value) { styles[name] = value; } },
      classList: { add(name) { classes.add(name); } } },
    querySelector(selector) {
      return ({ '[data-progress-label]': label, progress, '.language-nav': nav })[selector] || null;
    },
    querySelectorAll(selector) {
      return ({ '[data-check]': inputs, 'a[data-language-link]': links,
        'main section[id]': [{ id: 'step-1', getBoundingClientRect: () => ({ top: 80 }) }] })[selector] || [];
    }
  };
  class ResizeObserver { constructor(callback) { resize = callback; } observe() {} }
  const window = { get location() { return location; }, innerHeight: 720, ResizeObserver,
    addEventListener() {} };
  const localStorage = { getItem(name) { if (options.blockStorage) throw Error('blocked'); return storage[name] || null; },
    setItem(name, value) { if (options.blockStorage) throw Error('blocked'); storage[name] = value; } };
  vm.runInNewContext(source, { document, window, localStorage, URL, URLSearchParams, ResizeObserver,
    Date, history: { replaceState(_state, _title, value) { location = new URL(value); } } });
  return {
    checked: () => inputs.map(input => input.checked),
    change(index, value) { inputs[index].checked = value; inputs[index].change(); },
    switch() { links[0].click(); return links[0].href; },
    url: () => location,
    resize(value) { height = value; resize(); }, styles, classes, label, progress
  };
}

test('新しい別言語ページから戻っても、保存済みの進捗を消さない', () => {
  const japanese = { [key]: JSON.stringify({ 'step-1': true }) };
  const english = page({});
  const target = page(japanese, english.switch());
  assert.deepEqual(target.checked(), [true, false]);
  assert.equal(target.url().searchParams.get('from'), 'setup');
  assert.equal(target.url().hash, '#step-1');
  assert.equal(target.url().searchParams.has('checks'), false);
});

test('ページ別保存でもチェックと解除を双方向に引き継ぐ', () => {
  const jaStore = {}, enStore = {};
  const ja = page(jaStore);
  ja.change(0, true);
  const en = page(enStore, ja.switch());
  assert.deepEqual(en.checked(), [true, false]);
  en.change(0, false);
  en.change(1, true);
  assert.deepEqual(page(jaStore, en.switch()).checked(), [false, true]);
});

test('古い言語ページの記録で、新しい解除やチェックを巻き戻さない', () => {
  const jaStore = {}, enStore = {};
  const ja = page(jaStore);
  ja.change(0, true);
  const en = page(enStore, ja.switch());
  const stale = en.switch();
  ja.change(0, false);
  ja.change(1, true);
  assert.deepEqual(page(jaStore, stale).checked(), [false, true]);
});

test('保存領域を共有する別ページの更新を、操作の前に取り込む', () => {
  const storage = {};
  const first = page(storage), second = page(storage);
  first.change(0, true);
  second.change(1, true);
  assert.deepEqual(page(storage).checked(), [true, true]);
  assert.deepEqual(JSON.parse(storage[key]), { 'step-1': true, 'step-2': true });
});

test('保存できないブラウザでも、URLでチェックと解除を引き継ぐ', () => {
  const first = page({}, undefined, { blockStorage: true });
  first.change(0, true);
  const second = page({}, first.switch(), { blockStorage: true });
  assert.deepEqual(second.checked(), [true, false]);
  second.change(0, false);
  assert.deepEqual(page({}, second.switch(), { blockStorage: true }).checked(), [false, false]);
});

test('不正なクエリが既存の確認済み記録を消さない', () => {
  for (const bad of ['[]', 'null', '{bad', '{"step-1":{"checked":false,"updatedAt":"bad"}}']) {
    const storage = { [key]: JSON.stringify({ 'step-1': true }) };
    assert.deepEqual(page(storage, `file:///docs/en/unit/index.html?checks=${encodeURIComponent(bad)}`).checked(), [true, false]);
  }
});

test('言語バーの高さが変わると、目次用の余白も更新する', () => {
  const current = page();
  assert.equal(current.styles['--language-nav-height'], '42px');
  assert.equal(current.classes.has('has-language-nav'), true);
  current.resize(110);
  assert.equal(current.styles['--language-nav-height'], '110px');
});
