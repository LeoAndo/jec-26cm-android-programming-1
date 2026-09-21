const assert = require('node:assert/strict');
const { readFileSync, readdirSync } = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const source = readFileSync(path.join(__dirname, '../docs/assets/textbook.js'), 'utf8');
const key = 'jec-test';

function page(storage = {}, href = 'file:///docs/unit/index.html?from=setup#step-1', options = {}) {
  let location = new URL(href), resize, height = 42;
  const anchor = value => {
    const spec = typeof value === 'string' ? { href: value } : value;
    const attributes = { href: spec.href };
    return {
      get href() { return new URL(attributes.href, location).href; },
      set href(value) { attributes.href = value; },
      getAttribute(name) { return attributes[name] ?? null; },
      setAttribute(name, value) { attributes[name] = value; },
      closest(selector) { return selector === 'section[id]' && spec.section ? { id: spec.section } : null; },
      addEventListener(type, action) { this[type] = action; }
    };
  };
  const inputs = (options.checkIds ?? ['step-1', 'step-2']).map(id => ({ dataset: { check: id }, checked: false,
    addEventListener(type, action) { this[type] = action; } }));
  const links = (options.languageLinks ?? ['../en/unit/index.html']).map(anchor);
  const backLinks = (options.backLinks ?? []).map(anchor);
  const commonLinks = (options.commonLinks ?? []).map(anchor);
  const progress = { value: 0 };
  const label = { textContent: '' };
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
        'a[data-back]': backLinks, 'a[data-keep-from]': commonLinks,
        'main section[id]': options.sections ?? [{ id: 'step-1', getBoundingClientRect: () => ({ top: 80 }) }] })[selector] || [];
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
    common(index = 0) { commonLinks[index].click?.(); return new URL(commonLinks[index].href); },
    back(index = 0) { backLinks[index].click?.(); return new URL(backLinks[index].href); },
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

function commonPage(href, options = {}) {
  // ページを開くたびに別の保存領域・実行環境を作り、新しいタブや再読込でも使えることを確かめる。
  return page({}, href, { checkIds: [], sections: [],
    backLinks: ['../hello-android/index.html', '../hello-android/index.html'],
    languageLinks: [], ...options });
}

for (const base of ['file:///Users/student/Documents/android1-student-materials-2026-09-20/docs/common/',
  'https://example.test/android1/docs/common/']) {
  test(`${new URL(base).protocol} で直接開いた準備からエミュレータへ進み、同じ手順へ戻る`, () => {
    const setup = commonPage(`${base}setup.html`, {
      commonLinks: [{ href: 'emulator.html', section: 'emulator' }]
    });
    const destination = setup.common();
    assert.deepEqual(destination.searchParams.getAll('back'), ['setup.html#emulator']);
    const emulator = commonPage(destination.href);
    for (const index of [0, 1]) {
      const back = emulator.back(index);
      assert.equal(back.href, `${base}setup.html#emulator`);
      assert.equal(commonPage(back.href).back().href, new URL('../hello-android/index.html', base).href);
    }
  });
}

test('単元から共通資料を複数進んでも、1つずつ戻ったあと元の単元へ戻る', () => {
  const base = 'file:///docs/common/';
  const setup = commonPage(`${base}setup.html?from=calc-game`, {
    commonLinks: [{ href: 'other-versions.html', section: 'studio' }]
  });
  const versions = commonPage(setup.common().href, {
    commonLinks: [{ href: 'emulator.html', section: 'baseline' }]
  });
  const emulator = commonPage(versions.common().href);
  const first = emulator.back();
  assert.equal(first.pathname, '/docs/common/other-versions.html');
  assert.equal(first.hash, '#baseline');
  assert.equal(first.searchParams.get('from'), 'calc-game');
  assert.deepEqual(first.searchParams.getAll('back'), ['setup.html#studio']);
  const second = commonPage(first.href).back();
  assert.equal(second.pathname, '/docs/common/setup.html');
  assert.equal(second.hash, '#studio');
  assert.equal(second.searchParams.get('from'), 'calc-game');
  assert.deepEqual(second.searchParams.getAll('back'), []);
  assert.equal(commonPage(second.href).back().href, 'file:///docs/calc-game/index.html');
});

test('本文のリンクで前の資料へ戻ると、その先の履歴を除いて循環を防ぐ', () => {
  const target = new URL('file:///docs/common/emulator.html?from=memo-app');
  target.searchParams.append('back', 'setup.html#studio');
  target.searchParams.append('back', 'other-versions.html#baseline');
  const emulator = commonPage(target.href, {
    commonLinks: ['setup.html#emulator', 'other-versions.html#reading']
  });
  const setup = emulator.common(0);
  assert.equal(setup.hash, '#emulator');
  assert.equal(setup.searchParams.get('from'), 'memo-app');
  assert.deepEqual(setup.searchParams.getAll('back'), []);
  assert.equal(commonPage(setup.href).back().href, 'file:///docs/memo-app/index.html');
  const versions = emulator.common(1);
  assert.equal(versions.hash, '#reading');
  assert.deepEqual(versions.searchParams.getAll('back'), ['setup.html#studio']);
  assert.equal(commonPage(versions.href).back().pathname, '/docs/common/setup.html');
});

test('行先のクエリとハッシュを残し、囲むsectionがなければ現在のハッシュへ戻る', () => {
  const setup = commonPage('file:///docs/common/setup.html?from=calc-game#keyboard', {
    commonLinks: ['emulator.html?mode=prepare#run']
  });
  const target = setup.common();
  assert.equal(target.searchParams.get('mode'), 'prepare');
  assert.equal(target.searchParams.get('from'), 'calc-game');
  assert.equal(target.hash, '#run');
  assert.deepEqual(target.searchParams.getAll('back'), ['setup.html#keyboard']);
  assert.equal(commonPage(target.href).back().hash, '#keyboard');
});

test('言語を替えても共通資料を1つずつ戻れ、選んだ言語の単元まで戻れる', () => {
  const target = new URL('file:///docs/common/emulator.html?from=room-sample#run');
  target.searchParams.append('back', 'setup.html#studio');
  target.searchParams.append('back', 'other-versions.html#baseline');
  const japanese = commonPage(target.href, { languageLinks: ['../en/common/emulator.html'] });
  const englishUrl = new URL(japanese.switch());
  assert.equal(englishUrl.pathname, '/docs/en/common/emulator.html');
  assert.equal(englishUrl.hash, '#run');
  assert.equal(englishUrl.searchParams.get('from'), 'room-sample');
  assert.deepEqual(englishUrl.searchParams.getAll('back'), ['setup.html#studio', 'other-versions.html#baseline']);
  const versions = commonPage(englishUrl.href).back();
  assert.equal(versions.pathname, '/docs/en/common/other-versions.html');
  const setup = commonPage(versions.href).back();
  assert.equal(setup.pathname, '/docs/en/common/setup.html');
  assert.equal(commonPage(setup.href).back().href, 'file:///docs/en/room-sample/index.html');
});

test('不正な戻り先を含む履歴は全体を無視し、次の遷移では安全な履歴を作り直す', () => {
  for (const bad of ['../setup.html', 'https://example.test/setup.html', '//example.test/setup.html',
    'setup.html?from=other', 'setup.html#bad/fragment', '', 'setup.html%23emulator']) {
    const target = new URL('file:///docs/common/emulator.html?from=calc-game');
    target.searchParams.append('back', 'setup.html#emulator');
    target.searchParams.append('back', bad);
    const current = commonPage(target.href, {
      commonLinks: ['other-versions.html'], languageLinks: ['../en/common/emulator.html']
    });
    assert.equal(current.back().href, 'file:///docs/calc-game/index.html', bad);
    assert.deepEqual(new URL(current.switch()).searchParams.getAll('back'), [], bad);
    assert.deepEqual(current.common().searchParams.getAll('back'), ['emulator.html'], bad);
  }
});

test('直接開いた資料の既定リンクを残し、不正な単元名で上書きしない', () => {
  for (const from of ['', '../calc-game', 'https://example.test/', 'calc-game/index.html']) {
    const target = new URL('file:///docs/common/auto-import.html');
    if (from) target.searchParams.set('from', from);
    const current = commonPage(target.href, { backLinks: ['../hello-android/index.html#step-1'] });
    assert.equal(current.back().href, 'file:///docs/hello-android/index.html#step-1');
  }
});

test('実際のHTMLで、単元と共通資料のリンクに戻り先の指定漏れがない', () => {
  const root = path.join(__dirname, '..');
  const projects = JSON.parse(readFileSync(path.join(root, 'config/teaching-materials.json'), 'utf8')).projects;
  const textbooks = projects.flatMap(project => project.docs.filter(file => file.startsWith('docs/')));
  const common = readdirSync(path.join(root, 'docs/common')).filter(file => file.endsWith('.html'))
    .map(file => `docs/common/${file}`);
  for (const file of [...textbooks, ...common]) {
    const source = readFileSync(path.join(root, file), 'utf8');
    const current = new URL(`file:///${file}`);
    for (const [tag] of source.matchAll(/<a\b[^>]*>/g)) {
      const href = /\bhref="([^"]+)"/.exec(tag)?.[1];
      if (!href) continue;
      const target = new URL(href.replaceAll('&amp;', '&'), current);
      if (target.protocol !== 'file:' || !target.pathname.startsWith('/docs/common/')
          || !target.pathname.endsWith('.html') || target.pathname === current.pathname) continue;
      if (file.startsWith('docs/common/')) {
        assert.match(tag, /\bdata-keep-from(?:\s|=|>)/, `${file}: ${href}`);
      } else {
        assert.equal(target.searchParams.get('from'), path.basename(path.dirname(file)), `${file}: ${href}`);
      }
    }
  }
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
