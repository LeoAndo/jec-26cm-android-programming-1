// 本文はJavaScriptなしでも読めます。記録はこのブラウザ内だけに保存します。
(() => {
  const defaults = {
    copy: 'コピー', copy_label: '{title}のコードをコピー', copied: 'コピーしました',
    copy_success: 'コードをコピーしました。Android Studioに貼り付けてください。',
    copy_shortcut: '⌘ Cでコピー', copy_selected: 'コードを選択しました。⌘ Cでコピーしてください。',
    progress: '{count} / {total} ステップ確認済み'
  };
  let messages = defaults;
  try {
    const text = document.querySelector('#textbook-i18n')?.textContent;
    if (text) messages = { ...defaults, ...JSON.parse(text) };
  } catch { /* 古い配布物でも日本語のUIを利用可能 */ }
  const message = (name, values = {}) => messages[name].replace(/\{(\w+)\}/g, (token, key) => values[key] ?? token);
  const checks = [...document.querySelectorAll('[data-check]')];
  const key = document.body.dataset.progressKey || 'jec-android1-helloandroid-v1';
  const timeKey = `${key}:updated-at`;
  const knownIds = new Set(checks.map(item => item.dataset.check));
  const records = {};
  const mergeRecords = incoming => {
    if (!incoming || typeof incoming !== 'object' || Array.isArray(incoming)) return;
    Object.entries(incoming).forEach(([id, record]) => {
      if (!knownIds.has(id) || !record || typeof record.checked !== 'boolean'
          || !Number.isFinite(record.updatedAt) || record.updatedAt < 0) return;
      const previous = records[id];
      // 時刻のない旧形式どうしでは、既存の確認済み記録を優先する。
      if (!previous || record.updatedAt > previous.updatedAt
          || (record.updatedAt === previous.updatedAt && record.checked)) records[id] = record;
    });
  };
  const loadSaved = () => {
    try {
      const saved = JSON.parse(localStorage.getItem(key) || '{}') || {};
      const times = JSON.parse(localStorage.getItem(timeKey) || '{}') || {};
      mergeRecords(Object.fromEntries(Object.entries(saved).filter(([, value]) => typeof value === 'boolean')
        .map(([id, checked]) => [id, { checked, updatedAt: Number.isFinite(times[id]) ? times[id] : 0 }])));
    } catch { /* 保存できない環境でも利用可能 */ }
  };
  const save = () => {
    try {
      // 確認済みの保存形式は旧版でも読めるままにし、更新時刻だけを別に保存する。
      localStorage.setItem(key, JSON.stringify(Object.fromEntries(Object.entries(records).map(([id, value]) => [id, value.checked]))));
      localStorage.setItem(timeKey, JSON.stringify(Object.fromEntries(Object.entries(records).map(([id, value]) => [id, value.updatedAt]))));
    } catch { /* このページ上では引き継ぐ */ }
  };
  loadSaved();
  // file:// のページ別保存にも対応する。未操作のページは既存の記録を上書きしない。
  const parameters = new URLSearchParams(window.location.search);
  if (parameters.has('checks')) {
    try {
      mergeRecords(JSON.parse(parameters.get('checks')));
      save();
    } catch { /* 不正な引き継ぎ値は保存済みの記録に影響させない */ }
    parameters.delete('checks');
    const clean = new URL(window.location.href);
    clean.search = parameters.toString();
    try { history.replaceState(null, '', clean.href); } catch { /* file:// の履歴更新が禁止でも本文は利用可能 */ }
  }
  const update = () => {
    const count = checks.filter(input => input.checked).length;
    const label = document.querySelector('[data-progress-label]');
    const progress = document.querySelector('progress');
    if (label) label.textContent = message('progress', { count, total: checks.length });
    if (progress) { progress.max = checks.length; progress.value = count; }
  };
  checks.forEach(input => {
    input.checked = records[input.dataset.check]?.checked === true;
    input.addEventListener('change', () => {
      loadSaved();
      const id = input.dataset.check;
      records[id] = { checked: input.checked, updatedAt: Math.max(Date.now(), (records[id]?.updatedAt || 0) + 1) };
      update();
      save();
    });
  });
  update();

  document.querySelectorAll('pre').forEach(pre => {
    const heading = pre.previousElementSibling;
    if (!heading?.classList.contains('code-head')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = message('copy');
    button.setAttribute('aria-label', message('copy_label', { title: heading.textContent.trim() }));
    heading.append(button);
    button.addEventListener('click', async () => {
      const status = document.querySelector('[data-copy-status]');
      try {
        await navigator.clipboard.writeText(pre.textContent);
        button.textContent = message('copied');
        if (status) status.textContent = message('copy_success');
      } catch {
        const range = document.createRange();
        range.selectNodeContents(pre);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = message('copy_shortcut');
        if (status) status.textContent = message('copy_selected');
      }
      setTimeout(() => { button.textContent = message('copy'); }, 3000);
    });
  });

  const links = [...document.querySelectorAll('.sidebar a[href^="#"]')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        links.forEach(link => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'step');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '0px 0px -65% 0px', threshold: 0 });
    document.querySelectorAll('main section[id]').forEach(section => observer.observe(section));
  }

  // 共通資料の「もとの教科書へ戻る」は、開く前に見ていた単元へ戻す。
  // 単元側のリンクが ?from=<単元フォルダ名> を付けている。
  // 付いていないとき（共通資料を直接開いたとき）は、hrefのリンク先をそのまま使う。
  const backTo = new URLSearchParams(window.location.search).get('from');
  if (backTo && /^[a-z0-9-]+$/.test(backTo)) {
    document.querySelectorAll('a[data-back]').forEach(link => {
      link.setAttribute('href', `../${backTo}/index.html`);
    });
    // 共通資料どうしのリンクにも ?from= を引き継ぐ。
    // これがないと、別の共通資料へ移った時点で戻り先がA01に戻ってしまう。
    // ?from= は # の前に入れる（setup.html#emulator → setup.html?from=calc-game#emulator）。
    // # のうしろに足すと、# 以降の一部として扱われ、その位置へ移動できず、from も引き継がれない。
    document.querySelectorAll('a[data-keep-from]').forEach(link => {
      const href = link.getAttribute('href');
      if (!href || href.includes('?')) return;
      const hashAt = href.indexOf('#');
      const page = hashAt < 0 ? href : href.slice(0, hashAt);
      const hash = hashAt < 0 ? '' : href.slice(hashAt);
      link.setAttribute('href', `${page}?from=${backTo}${hash}`);
    });
  }

  // 言語名が折り返しても、固定メニューの下に目次とSTEPを表示する。
  const languageNav = document.querySelector('.language-nav');
  if (languageNav) {
    const resizeNav = () => document.documentElement.style.setProperty('--language-nav-height', `${languageNav.getBoundingClientRect().height}px`);
    resizeNav();
    document.documentElement.classList.add('has-language-nav');
    if ('ResizeObserver' in window) new ResizeObserver(resizeNav).observe(languageNav);
    else window.addEventListener('resize', resizeNav);
  }

  // 言語を替えても、共通資料の戻り先・いま読んでいるSTEP・確認済みの記録を保つ。
  document.querySelectorAll('a[data-language-link]').forEach(link => {
    const base = link.getAttribute('href');
    const updateTarget = () => {
      const target = new URL(base, window.location.href);
      const from = new URLSearchParams(window.location.search).get('from');
      if (from && /^[a-z0-9-]+$/.test(from)) target.searchParams.set('from', from);
      loadSaved();
      if (checks.length && Object.keys(records).length) target.searchParams.set('checks', JSON.stringify(records));
      const section = [...document.querySelectorAll('main section[id]')].filter(item => item.getBoundingClientRect().top <= window.innerHeight / 3).at(-1);
      target.hash = section ? section.id : window.location.hash;
      link.href = target.href;
    };
    updateTarget();
    link.addEventListener('click', updateTarget);
    link.addEventListener('contextmenu', updateTarget);
    // キーボード操作・新しいタブで開く操作でも、最新のリンク先を使う。
    link.addEventListener('focus', updateTarget);
    window.addEventListener('hashchange', updateTarget);
  });

  let closedForScreen = [];
  window.addEventListener('beforeprint', () => {
    closedForScreen = [...document.querySelectorAll('details:not([open])')];
    closedForScreen.forEach(detail => { detail.open = true; });
  });
  window.addEventListener('afterprint', () => {
    closedForScreen.forEach(detail => { detail.open = false; });
    closedForScreen = [];
  });
})();
