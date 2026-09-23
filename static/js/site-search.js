(() => {
  const form = document.querySelector('[data-site-search]');
  const input = document.querySelector('[data-search-input]');
  const results = document.querySelector('[data-search-results]');
  if (!form || !input || !results) return;

  const searchUrl = form.dataset.searchUrl || form.getAttribute('action') || '/search/';
  const minLength = 2;
  const debounceMs = 280;
  let activeType = new URLSearchParams(window.location.search).get('type') || 'all';
  let timer = null;
  let requestId = 0;
  let controller = null;

  const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  function highlightMatches(query) {
    const q = (query || '').trim();
    if (q.length < minLength) return;
    const pattern = new RegExp(`(${escapeRegExp(q)})`, 'gi');
    results.querySelectorAll('.site-search__match').forEach((node) => {
      const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
      const textNodes = [];
      while (walker.nextNode()) textNodes.push(walker.currentNode);
      textNodes.forEach((textNode) => {
        pattern.lastIndex = 0;
        if (!pattern.test(textNode.nodeValue || '')) return;
        pattern.lastIndex = 0;
        const fragment = document.createDocumentFragment();
        (textNode.nodeValue || '').split(pattern).forEach((part) => {
          if (!part) return;
          if (part.toLowerCase() === q.toLowerCase()) {
            const mark = document.createElement('mark');
            mark.className = 'site-search__highlight';
            mark.textContent = part;
            fragment.appendChild(mark);
          } else {
            fragment.appendChild(document.createTextNode(part));
          }
        });
        textNode.parentNode.replaceChild(fragment, textNode);
      });
    });
  }

  function applyLanguage() {
    const lang = localStorage.getItem('mopd-lang') || 'en';
    if (typeof window.applyMopdLanguage === 'function') {
      window.applyMopdLanguage(lang);
    }
  }

  function syncUrl(query, type) {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (type && type !== 'all') params.set('type', type);
    const next = params.toString() ? `${searchUrl}?${params}` : searchUrl;
    if (`${window.location.pathname}${window.location.search}` !== next) {
      window.history.replaceState({ q: query, type }, '', next);
    }
  }

  function setBusy(isBusy) {
    results.classList.toggle('is-loading', isBusy);
    results.setAttribute('aria-busy', isBusy ? 'true' : 'false');
  }

  async function fetchResults(query, type) {
    const q = (query || '').trim();
    activeType = type || 'all';

    if (q.length < minLength) {
      if (controller) controller.abort();
      results.innerHTML =
        '<p class="site-search__hint" data-i18n="page.search.hint">Start typing to see matching news, documents, and pages.</p>';
      setBusy(false);
      syncUrl('', 'all');
      applyLanguage();
      return;
    }

    if (controller) controller.abort();
    controller = new AbortController();
    const id = ++requestId;
    setBusy(true);

    const params = new URLSearchParams({ q, type: activeType, partial: '1' });
    try {
      const res = await fetch(`${searchUrl}?${params}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          Accept: 'text/html',
        },
        signal: controller.signal,
        credentials: 'same-origin',
      });
      if (!res.ok) throw new Error(`Search failed (${res.status})`);
      const html = await res.text();
      if (id !== requestId) return;
      results.innerHTML = html;
      highlightMatches(q);
      applyLanguage();
      syncUrl(q, activeType);
    } catch (err) {
      if (err && err.name === 'AbortError') return;
      if (id !== requestId) return;
      results.innerHTML =
        '<p class="site-search__empty">Search could not be completed. Please try again.</p>';
    } finally {
      if (id === requestId) setBusy(false);
    }
  }

  function scheduleSearch() {
    clearTimeout(timer);
    timer = setTimeout(() => {
      fetchResults(input.value, activeType);
    }, debounceMs);
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    clearTimeout(timer);
    fetchResults(input.value, activeType);
  });

  input.addEventListener('input', () => {
    scheduleSearch();
  });

  results.addEventListener('click', (event) => {
    const btn = event.target.closest('[data-search-type]');
    if (!btn || !results.contains(btn)) return;
    event.preventDefault();
    const nextType = btn.dataset.searchType || 'all';
    if (nextType === activeType) return;
    activeType = nextType;
    clearTimeout(timer);
    fetchResults(input.value, activeType);
  });

  // Highlight server-rendered results on first paint.
  if ((input.value || '').trim().length >= minLength) {
    highlightMatches(input.value);
  }
})();
