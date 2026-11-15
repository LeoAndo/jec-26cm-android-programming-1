// 本文はJavaScriptなしでも読めます。記録はこのブラウザ内だけに保存します。
(() => {
  const defaults = {
    copy: 'コピー', copy_label: '{title}のコードをコピー', copied: 'コピーしました',
    copy_success: 'コードをコピーしました。Android Studioに貼り付けてください。',
    copy_shortcut: '⌘ Cでコピー', copy_selected: 'コードを選択しました。⌘ Cでコピーしてください。',
    progress: '{count} / {total} ステップ確認済み',
    contents: '目次', resources: 'ほかの単元・共通資料',
    file_location: 'ファイルの場所を確認する',
    code_scroll: '長い行は、コードの枠内を横にスクロールできます。',
    table_scroll: '表の右側は、枠内を横にスクロールして確認できます。'
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
    document.querySelectorAll('.sidebar nav a[href^="#"]').forEach(link => {
      const marker = link.querySelector('.nav-check');
      if (marker) marker.textContent = checks.find(input => link.hash === `#${input.dataset.check}`)?.checked ? '✓' : '';
    });
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

  // コードのコピーボタンは付けない（README「授業用教科書の基本方針」9）。
  // 特例は、data-copy-button を付けた <pre> だけ。押しても動かないボタンを見せないよう、HTMLには書かずにここで作る。
  document.querySelectorAll('pre[data-copy-button]').forEach(pre => {
    const heading = pre.previousElementSibling;
    if (!heading?.classList.contains('code-head')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = message('copy');
    button.setAttribute('aria-label', message('copy_label', { title: heading.textContent.trim() }));
    heading.append(button);
    let timer;
    const show = (label, announcement, restore) => {
      const status = document.querySelector('[data-copy-status]');
      button.textContent = message(label);
      if (status) status.textContent = message(announcement);
      clearTimeout(timer);
      if (restore) timer = setTimeout(() => {
        button.textContent = message('copy');
        if (status) status.textContent = '';
      }, 3000);
    };
    button.addEventListener('click', async () => {
      try {
        // クリックの処理の中で、ほかの処理を待たずに呼ぶ（Safariは、操作の直後でなければ書き込みを断る）。
        await navigator.clipboard.writeText(pre.textContent);
        show('copied', 'copy_success', true);
        return;
      } catch { /* navigator.clipboard がないブラウザや、断られたときは、下の方法へ */ }
      // コードを選択して、選択範囲をコピーする命令を試す。それも断られたら、選択を残して ⌘ C を促す。
      const range = document.createRange();
      range.selectNodeContents(pre);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      let copied = false;
      try { copied = document.execCommand('copy'); } catch { /* 命令のないブラウザ */ }
      // ⌘ C を押すのは学生なので、その案内は消さずに残す（次に押したときに切り替わる）。
      show(copied ? 'copied' : 'copy_shortcut', copied ? 'copy_success' : 'copy_selected', copied);
    });
  });

  // 本文・翻訳の原文を変えず、翻訳済みの要素を使って教科書の表示を整える。
  const enhanceTextbook = () => {
    if (!document.body.classList.contains('textbook')) return null;
    const sidebar = document.querySelector('.sidebar');
    const inner = sidebar?.querySelector('.sidebar-inner');
    const main = document.querySelector('main');
    if (!sidebar || !inner || !main) return null;
    const element = (tag, className, text) => {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text !== undefined) node.textContent = text;
      return node;
    };
    const decoration = (className, text) => {
      const node = element('span', className, text);
      node.setAttribute('aria-hidden', 'true');
      return node;
    };

    main.querySelectorAll(':scope > section[id^="step-"]').forEach(section => {
      const heading = section.querySelector(':scope > h2');
      const meta = section.querySelector(':scope > .step-meta');
      const number = section.id.match(/^step-(\d+)$/)?.[1];
      if (!heading || !meta || number === undefined) return;
      const header = element('header', 'step-heading');
      const title = element('div');
      meta.before(header);
      title.append(heading, meta);
      header.append(decoration('big-step', number.padStart(2, '0')), title);
    });
    main.querySelectorAll('h3').forEach(heading => {
      const first = heading.firstChild;
      const match = first?.nodeType === Node.TEXT_NODE && first.textContent.match(/^\s*([①-⑳])\s*/);
      if (!match) return;
      first.textContent = first.textContent.slice(match[0].length);
      heading.classList.add('action-heading');
      heading.prepend(element('span', 'instruction-number', String(match[1].codePointAt(0) - 0x245f)));
    });
    main.querySelectorAll('.file').forEach(file => {
      const match = file.textContent.match(/^([^：:]+)[：:]\s*([\s\S]+)$/);
      if (!match) return;
      const value = match[2].trim();
      const singlePath = /^[\w./$-]+\.[\w]+$/.test(value) && value.includes('/');
      const box = element('div', 'file-box');
      for (const attribute of file.attributes) if (attribute.name !== 'class') box.setAttribute(attribute.name, attribute.value);
      const content = element('div');
      content.append(element('div', 'file-label', match[1].trim()),
        element('div', 'file-name', singlePath ? value.split('/').at(-1) : value));
      if (singlePath) {
        const path = element('details', 'file-path');
        path.append(element('summary', '', message('file_location')), element('p', '', value));
        content.append(path);
      }
      box.append(decoration('file-icon', '{ }'), content);
      file.replaceWith(box);
    });

    // textContent からテキストノードだけを作るので、コードの記号・空白・コピー内容を保つ。
    const scrollHints = [];
    main.querySelectorAll('pre').forEach(pre => {
      const code = pre.querySelector('code');
      if (code) {
        const text = code.textContent;
        const tokens = /<!--[\s\S]*?-->|\/\*[\s\S]*?\*\/|\/\/[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:var|return|public|private|protected|class|extends|void|package|import|new|if|else|for|while|static|final|true|false|null)\b|\b[A-Z][A-Za-z0-9_]*\b/g;
        const fragment = document.createDocumentFragment();
        let offset = 0;
        for (const token of text.matchAll(tokens)) {
          fragment.append(document.createTextNode(text.slice(offset, token.index)));
          const value = token[0];
          const kind = /^(?:\/\/|\/\*|<!--)/.test(value) ? 'comment'
            : /^["']/.test(value) ? 'string' : /^[A-Z]/.test(value) ? 'type' : 'keyword';
          fragment.append(element('span', `syntax-${kind}`, value));
          offset = token.index + value.length;
        }
        fragment.append(document.createTextNode(text.slice(offset)));
        code.replaceChildren(fragment);
      }
      const hint = element('p', 'scroll-hint', message('code_scroll'));
      hint.hidden = true;
      pre.after(hint);
      scrollHints.push([pre, hint]);
    });
    main.querySelectorAll('table').forEach(table => {
      const headers = [...table.querySelectorAll(':scope > thead > tr:first-child > th')];
      const rows = [...table.querySelectorAll(':scope > tbody > tr')];
      const regular = headers.length && rows.every(row => row.children.length === headers.length
        && [...row.children].every(cell => cell.colSpan === 1 && cell.rowSpan === 1));
      if (!regular) return;
      table.dataset.columns = String(headers.length);
      rows.forEach(row => [...row.children].forEach((cell, index) => {
        cell.dataset.label = headers[index].textContent.trim();
      }));
      if (headers.length > 3) {
        const scroll = element('div', 'table-scroll');
        scroll.tabIndex = 0;
        scroll.setAttribute('role', 'region');
        scroll.setAttribute('aria-label', table.closest('section')?.querySelector('h2')?.textContent || headers.map(cell => cell.textContent).join(' / '));
        table.before(scroll);
        scroll.append(table);
        const hint = element('p', 'scroll-hint', message('table_scroll'));
        hint.hidden = true;
        scroll.after(hint);
        scrollHints.push([scroll, hint]);
      }
    });

    const unit = inner.querySelector('[aria-current="page"]')?.textContent.trim() || document.title;
    const nav = inner.querySelector('nav');
    const eyebrow = inner.querySelector('.eyebrow');
    if (eyebrow && nav?.getAttribute('aria-label')) eyebrow.textContent = nav.getAttribute('aria-label');
    const progress = inner.querySelector('.progress');
    if (progress) inner.prepend(progress);
    nav?.querySelectorAll('a[href^="#"]').forEach(link => link.append(decoration('nav-check', '')));
    const resources = inner.querySelector('.resources');
    if (resources) {
      const help = element('div', 'lesson-help-links');
      resources.querySelectorAll('a[href^="#"]').forEach(link => help.append(link));
      const details = element('details', 'lesson-resources');
      resources.before(help, details);
      details.append(element('summary', '', message('resources')), resources);
    }
    const bar = element('div', 'lesson-bar-inner');
    const current = element('div', 'lesson-current');
    const step = element('span', 'current-step');
    const title = element('span', 'current-title');
    current.append(step, title);
    const menu = element('details', 'lesson-menu');
    const summary = element('summary');
    summary.append(element('span', '', message('contents')), decoration('menu-chevron', ''));
    const panel = element('div', 'lesson-menu-content');
    panel.append(inner);
    menu.append(summary, panel);
    bar.append(element('span', 'unit-name', unit.replace('：', ' ')), current, menu);
    sidebar.classList.add('lesson-bar');
    sidebar.append(bar);
    document.body.classList.add('has-lesson-nav');
    const resize = () => {
      document.documentElement.style.setProperty('--lesson-nav-height', `${bar.getBoundingClientRect().height}px`);
      scrollHints.forEach(([container, hint]) => { hint.hidden = container.scrollWidth <= container.clientWidth; });
    };
    resize();
    if ('ResizeObserver' in window) {
      const observer = new ResizeObserver(resize);
      observer.observe(bar);
      scrollHints.forEach(([container]) => observer.observe(container));
    } else {
      window.addEventListener('resize', resize);
      main.addEventListener('toggle', resize, true);
    }
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.open) { menu.open = false; summary.focus(); }
    });
    document.addEventListener('click', event => {
      if (menu.open && !menu.contains(event.target)) menu.open = false;
    });
    update();
    return { menu, step, title };
  };
  const lessonNavigation = enhanceTextbook();
  const links = [...document.querySelectorAll('.sidebar a[href^="#"]')];
  const sections = [...document.querySelectorAll('main > section[id]')];
  const activeSection = () => {
    if (lessonNavigation) {
      const style = getComputedStyle(document.documentElement);
      const languageHeight = parseFloat(style.getPropertyValue('--language-nav-height')) || 0;
      const lessonHeight = parseFloat(style.getPropertyValue('--lesson-nav-height')) || 0;
      return sections.filter(item => item.getBoundingClientRect().top <= languageHeight + lessonHeight + 90).at(-1) || sections[0];
    }
    // 共通資料は固定の教材バーがないので、従来の画面高さによる判定を保つ。
    return [...document.querySelectorAll('main section[id]')]
      .filter(item => item.getBoundingClientRect().top <= window.innerHeight / 3).at(-1);
  };
  const updateLocation = () => {
    const section = activeSection();
    if (!section) return;
    links.forEach(link => {
      if (link.hash === `#${section.id}`) link.setAttribute('aria-current', 'step');
      else link.removeAttribute('aria-current');
    });
    const number = section.id.match(/^step-(\d+)$/)?.[1];
    const heading = section.querySelector('h2')?.textContent || '';
    lessonNavigation.step.textContent = number === undefined ? (links.find(link => link.hash === `#${section.id}`)?.textContent || heading) : `STEP ${number.padStart(2, '0')}`;
    lessonNavigation.title.textContent = number === undefined ? '' : heading;
  };
  if (lessonNavigation) {
    let queued = false;
    window.addEventListener('scroll', () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => { queued = false; updateLocation(); });
    }, { passive: true });
    updateLocation();
  } else if ('IntersectionObserver' in window) {
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

  // 閉じた完成コードへのリンクも、初期URL・クリック・履歴移動で同じ場所を開く。
  const revealTarget = (hash, focus = false) => {
    let target;
    try { target = document.getElementById(decodeURIComponent(hash.slice(1))); } catch { return; }
    if (!target) return;
    for (let parent = target.parentElement; parent; parent = parent.parentElement) {
      if (parent.tagName === 'DETAILS') parent.open = true;
    }
    if (focus) {
      const destination = target.matches('section') ? target.querySelector('h2') || target : target;
      if (!destination.hasAttribute('tabindex')) destination.tabIndex = -1;
      destination.focus({ preventScroll: true });
    }
    requestAnimationFrame(() => {
      target.scrollIntoView({ block: 'start', behavior: 'instant' });
      if (lessonNavigation) updateLocation();
    });
  };
  if (lessonNavigation) {
    document.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', event => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      let target;
      try { target = document.getElementById(decodeURIComponent(link.hash.slice(1))); } catch { return; }
      if (!target) return;
      event.preventDefault();
      lessonNavigation.menu.open = false;
      try { history.pushState(null, '', link.hash); } catch { window.location.hash = link.hash; }
      revealTarget(link.hash, true);
    }));
    window.addEventListener('hashchange', () => revealTarget(window.location.hash));
    window.addEventListener('popstate', () => {
      if (window.location.hash) revealTarget(window.location.hash);
    });
  }

  // from は最初の単元、back は共通資料をたどった順の「ファイル名#節」。
  // URLに持たせることで、file://・新しいタブ・言語切替でも直前へ戻れる。
  const from = parameters.get('from');
  const backTo = from && /^[a-z0-9-]+$/.test(from) ? from : null;
  const backValues = parameters.getAll('back');
  const backPages = backValues.every(value => /^[a-z0-9-]+\.html(?:#[a-z0-9-]+)?$/.test(value)) ? backValues : [];
  const setNavigation = (target, pages) => {
    if (backTo) target.searchParams.set('from', backTo);
    target.searchParams.delete('back');
    pages.forEach(page => target.searchParams.append('back', page));
  };
  document.querySelectorAll('a[data-back]').forEach(link => {
    if (backPages.length) {
      const target = new URL(backPages.at(-1), window.location.href);
      setNavigation(target, backPages.slice(0, -1));
      link.setAttribute('href', target.href);
    } else if (backTo) {
      const target = new URL(`../${backTo}/index.html`, window.location.href);
      const fallback = new URL(link.getAttribute('href'), window.location.href);
      // 同じ単元なら、Auto ImportのSTEP 1など既定の復帰位置も残す。
      if (fallback.pathname === target.pathname) target.hash = fallback.hash;
      link.setAttribute('href', target.href);
    }
    // 戻り先がない直接起動では、HTMLにある既定のリンクを使う。
  });
  document.querySelectorAll('a[data-keep-from]').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    const current = new URL(window.location.href);
    const target = new URL(href, current);
    const directory = new URL('.', current);
    const filename = current.pathname.split('/').at(-1);
    if (!/\/common\/$/.test(directory.pathname) || !/^[a-z0-9-]+\.html$/.test(filename)
        || new URL('.', target).href !== directory.href || !/^[a-z0-9-]+\.html$/.test(target.pathname.split('/').at(-1))) return;
    const section = link.closest('section[id]');
    const previous = `${filename}${section ? `#${section.id}` : current.hash}`;
    // 本文の「setupへ戻る」などで既に読んだページへ戻るときは、履歴を巻き戻す。
    const previousIndex = backPages.findIndex(page => new URL(page, current).pathname === target.pathname);
    setNavigation(target, previousIndex < 0 ? [...backPages, previous] : backPages.slice(0, previousIndex));
    link.setAttribute('href', target.href);
  });

  // 言語名が折り返しても、固定メニューの下に目次とSTEPを表示する。
  const languageNav = document.querySelector('.language-nav');
  if (languageNav) {
    const resizeNav = () => {
      document.documentElement.style.setProperty('--language-nav-height', `${languageNav.getBoundingClientRect().height}px`);
      if (lessonNavigation) updateLocation();
    };
    resizeNav();
    document.documentElement.classList.add('has-language-nav');
    if ('ResizeObserver' in window) new ResizeObserver(resizeNav).observe(languageNav);
    else window.addEventListener('resize', resizeNav);
  }

  if (lessonNavigation && window.location.hash) revealTarget(window.location.hash);

  // 言語を替えても、共通資料の戻り先・いま読んでいるSTEP・確認済みの記録を保つ。
  document.querySelectorAll('a[data-language-link]').forEach(link => {
    const base = link.getAttribute('href');
    const updateTarget = () => {
      const target = new URL(base, window.location.href);
      setNavigation(target, backPages);
      loadSaved();
      if (checks.length && Object.keys(records).length) target.searchParams.set('checks', JSON.stringify(records));
      const section = activeSection();
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
