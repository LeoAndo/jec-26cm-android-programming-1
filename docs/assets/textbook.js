// 本文はJavaScriptなしでも読めます。記録はこのブラウザ内だけに保存します。
(() => {
  const checks = [...document.querySelectorAll('[data-check]')];
  const key = 'jec-android1-helloandroid-v1';
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || '{}') || {}; } catch { /* 保存できない環境でも利用可能 */ }
  const update = () => {
    const count = checks.filter(input => input.checked).length;
    const label = document.querySelector('[data-progress-label]');
    const progress = document.querySelector('progress');
    if (label) label.textContent = `${count} / ${checks.length} ステップ確認済み`;
    if (progress) { progress.max = checks.length; progress.value = count; }
  };
  checks.forEach(input => {
    input.checked = saved[input.dataset.check] === true;
    input.addEventListener('change', () => {
      update();
      const state = Object.fromEntries(checks.map(item => [item.dataset.check, item.checked]));
      try { localStorage.setItem(key, JSON.stringify(state)); } catch { /* チェック操作は継続 */ }
    });
  });
  update();

  document.querySelectorAll('pre').forEach(pre => {
    const heading = pre.previousElementSibling;
    if (!heading?.classList.contains('code-head')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'コピー';
    button.setAttribute('aria-label', `${heading.textContent.trim()}のコードをコピー`);
    heading.append(button);
    button.addEventListener('click', async () => {
      const status = document.querySelector('[data-copy-status]');
      try {
        await navigator.clipboard.writeText(pre.textContent);
        button.textContent = 'コピーしました';
        if (status) status.textContent = 'コードをコピーしました。Android Studioに貼り付けてください。';
      } catch {
        const range = document.createRange();
        range.selectNodeContents(pre);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = '⌘ Cでコピー';
        if (status) status.textContent = 'コードを選択しました。⌘ Cでコピーしてください。';
      }
      setTimeout(() => { button.textContent = 'コピー'; }, 3000);
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
