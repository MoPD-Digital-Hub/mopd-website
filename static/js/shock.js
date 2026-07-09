/* MoPD Shock — interactions + all page features */

document.addEventListener('DOMContentLoaded', () => {
  if (typeof initMopdI18n === 'function') initMopdI18n();
  initSxLang();
  initSxMenu();
  initSxHeader();
  initSxHeroVideo();
  initSxProgress();
  initSxHeroFeed();
  initSxCounters();
  initSxBackTop();
  initSxReveal();
  initSxAboutTabs();
  initSxClimateDocTabs();
  initSxNewsPage();
  initSxGallery();
  initMpStagger();
});

function initMpStagger() {
  document.querySelectorAll('.mp-stagger').forEach((group) => {
    const parent = group.closest('.mp-reveal');
    if (!parent) return;
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          group.classList.add('is-in');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
    obs.observe(parent);
  });
}

function initSxLang() {
  const onLangClick = (btn) => {
    if (typeof applyMopdLanguage === 'function') {
      applyMopdLanguage(btn.dataset.lang);
    }
    mopdSyncLangButtons(btn.dataset.lang);
  };

  document.querySelectorAll('.sx-lang__btn, .mp-lang__btn, .lang-switch__btn').forEach((btn) => {
    btn.addEventListener('click', () => onLangClick(btn));
  });
}

function initSxMenu() {
  const btn = document.getElementById('sxMenuBtn');
  const panel = document.getElementById('sxMenuPanel');
  const close = document.getElementById('sxMenuClose');
  const backdrop = document.getElementById('sxMenuBackdrop');
  if (!btn || !panel) return;

  const open = () => {
    panel.classList.add('is-open');
    panel.setAttribute('aria-hidden', 'false');
    btn.setAttribute('aria-expanded', 'true');
    btn.setAttribute('aria-label', 'Close menu');
    document.body.classList.add('mp-menu-open');
    document.body.style.overflow = 'hidden';
  };
  const shut = () => {
    panel.classList.remove('is-open');
    panel.setAttribute('aria-hidden', 'true');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-label', 'Open menu');
    document.body.classList.remove('mp-menu-open');
    document.body.style.overflow = '';
  };

  btn.addEventListener('click', () => {
    if (panel.classList.contains('is-open')) shut();
    else open();
  });
  close?.addEventListener('click', shut);
  backdrop?.addEventListener('click', shut);
  panel.querySelectorAll('a').forEach((a) => a.addEventListener('click', shut));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') shut(); });

  panel.querySelectorAll('.sx-menu__group-toggle').forEach((toggle) => {
    toggle.addEventListener('click', () => {
      const group = toggle.closest('.sx-menu__group');
      if (!group) return;
      const isOpen = group.classList.contains('is-open');
      panel.querySelectorAll('.sx-menu__group').forEach((g) => {
        g.classList.remove('is-open');
        g.querySelector('.sx-menu__group-toggle')?.setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        group.classList.add('is-open');
        toggle.setAttribute('aria-expanded', 'true');
      }
    });
  });
}

function initSxHeader() {
  const header = document.getElementById('sxHeader');
  if (!header) return;
  let ticking = false;
  const update = () => {
    header.classList.toggle('is-solid', window.scrollY > 48);
    ticking = false;
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { requestAnimationFrame(update); ticking = true; }
  }, { passive: true });
  update();
}

function initSxProgress() {
  const bar = document.getElementById('scrollProgress');
  if (!bar) return;
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        const h = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.width = h > 0 ? `${(window.scrollY / h) * 100}%` : '0%';
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

function initSxHeroVideo() {
  const mount = document.getElementById('heroVideoMount');
  const poster = document.querySelector('.sx-hero__video-poster');
  const video = mount?.querySelector('.sx-hero__video');
  if (!mount || !video) return;

  const segmentEnd = Math.max(1, parseInt(mount.dataset.videoEnd || '30', 10));
  const posterDelayMs = Math.max(0, parseInt(mount.dataset.videoDelay || '2000', 10));
  let playbackStarted = false;

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return;
  }

  const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  if (conn && (conn.saveData || /(^2g$|^slow-2g$)/.test(conn.effectiveType || ''))) {
    return;
  }

  const showVideo = () => {
    mount.classList.add('is-playing');
    poster?.classList.add('is-hidden');
  };

  const playFromStart = () => {
    video.currentTime = 0;
    video.play().catch(() => {});
  };

  const kickPlay = () => {
    startPlayback(true);
  };

  const startPlayback = (skipDelay = false) => {
    if (playbackStarted) return;
    playbackStarted = true;

    const play = () => {
      video.play().then(showVideo).catch(() => {});
    };

    if (skipDelay || posterDelayMs === 0) {
      play();
    } else {
      setTimeout(play, posterDelayMs);
    }
  };

  video.addEventListener('playing', showVideo);
  video.addEventListener('timeupdate', () => {
    if (video.currentTime >= segmentEnd - 0.15) {
      playFromStart();
    }
  });
  video.addEventListener('ended', playFromStart);

  const shield = mount.querySelector('.sx-hero__video-shield');
  const heroMedia = mount.closest('.sx-hero__media');
  shield?.addEventListener('click', kickPlay);
  heroMedia?.addEventListener('click', kickPlay);

  requestAnimationFrame(() => startPlayback());
}

function initSxHeroFeed() {
  const cards = document.querySelectorAll('.sx-hero__feed-card');
  const prev = document.getElementById('heroFeedPrev');
  const next = document.getElementById('heroFeedNext');
  if (!cards.length) return;

  let current = 0;
  let timer;

  const go = (i) => {
    current = (i + cards.length) % cards.length;
    cards.forEach((c, idx) => c.classList.toggle('is-active', idx === current));
  };

  prev?.addEventListener('click', () => go(current - 1));
  next?.addEventListener('click', () => go(current + 1));

  const start = () => { timer = setInterval(() => go(current + 1), 7000); };
  const stop = () => clearInterval(timer);
  start();
  document.getElementById('hero')?.addEventListener('mouseenter', stop);
  document.getElementById('hero')?.addEventListener('mouseleave', start);
}

function initSxCounters() {
  const els = document.querySelectorAll('[data-count]');
  if (!els.length) return;

  const run = (el) => {
    const target = parseInt(el.dataset.count, 10);
    const start = performance.now();
    const tick = (now) => {
      const p = Math.min((now - start) / 2000, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.floor(eased * target);
      if (p < 1) requestAnimationFrame(tick);
      else el.textContent = target;
    };
    requestAnimationFrame(tick);
  };

  const obs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        run(e.target);
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.4 });

  els.forEach((el) => obs.observe(el));
}

function initSxBackTop() {
  const btn = document.getElementById('backToTop');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    btn.classList.toggle('is-visible', window.scrollY > 500);
  }, { passive: true });
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

function initSxReveal() {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const els = document.querySelectorAll('.sx-reveal, .mp-reveal, .reveal');
  if (!els.length) return;

  if (reduced) {
    els.forEach((el) => {
      el.classList.add('is-in');
      el.classList.add('visible');
    });
    return;
  }

  const obs = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('is-in');
          entry.target.classList.add('visible');
        }, Math.min(i * 50, 200));
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });

  els.forEach((el) => {
    if (!el.closest('[data-reveal-group]')) obs.observe(el);
  });
}

function initSxAboutTabs() {
  const tabs = document.querySelectorAll('.about__tab');
  const panels = document.querySelectorAll('.about__panel');
  if (!tabs.length) return;

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      tabs.forEach((t) => t.classList.remove('active'));
      panels.forEach((p) => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = document.getElementById(`panel-${target}`);
      if (panel) panel.classList.add('active');
    });
  });
}

function initSxClimateDocTabs() {
  const root = document.querySelector('.doc-tabs');
  if (!root) return;

  const radios = root.querySelectorAll('.doc-tabs__radio');
  const panels = root.querySelectorAll('.doc-tabs__panel');
  const labels = root.querySelectorAll('.doc-tabs__btn');

  const sync = () => {
    const checked = root.querySelector('.doc-tabs__radio:checked');
    if (!checked) return;
    const code = checked.id.replace('doc-cat-', '');
    panels.forEach((panel) => {
      const active = panel.dataset.panel === code;
      panel.classList.toggle('is-active', active);
      panel.hidden = !active;
    });
    labels.forEach((label) => {
      label.classList.toggle('is-active', label.htmlFor === checked.id);
    });
  };

  radios.forEach((radio) => radio.addEventListener('change', sync));
  sync();
}

function initSxGallery() {
  const items = document.querySelectorAll('.gallery__item');
  if (!items.length) return;

  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.innerHTML = '<button type="button" class="lightbox__close" aria-label="Close">&times;</button><img class="lightbox__img" alt="">';
  document.body.appendChild(lightbox);

  const img = lightbox.querySelector('.lightbox__img');
  const close = () => lightbox.classList.remove('open');

  items.forEach((item) => {
    item.addEventListener('click', () => {
      img.src = item.dataset.full || item.querySelector('img')?.src || '';
      img.alt = item.querySelector('img')?.alt || '';
      lightbox.classList.add('open');
    });
  });

  lightbox.addEventListener('click', (e) => { if (e.target === lightbox) close(); });
  lightbox.querySelector('.lightbox__close').addEventListener('click', close);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
}

function initSxNewsPage() {
  const page = document.querySelector('.news-page');
  if (!page) return;

  const grid = document.getElementById('newsGrid');
  const searchInput = document.getElementById('newsSearchInput');
  const searchForm = document.getElementById('newsSearchForm');
  const dateFilterInput = document.getElementById('newsDateFilter');
  const clearBtn = document.getElementById('newsClearFilters');
  const emptyEl = document.getElementById('newsEmpty');
  const resultsEl = document.getElementById('newsResults');
  const categoryBtns = page.querySelectorAll('[data-news-category]');
  if (!grid || !searchInput) return;

  const cards = [...grid.querySelectorAll('.news-card')];
  let activeCategory = 'all';

  const getCardSearchText = (card) => {
    const parts = [card.dataset.search || '', card.dataset.date || ''];
    card.querySelectorAll('.bilingual').forEach((el) => {
      parts.push(el.dataset.en || '', el.dataset.am || '');
    });
    parts.push(
      card.querySelector('h3')?.textContent || '',
      card.querySelector('.news-card__excerpt')?.textContent || '',
      card.querySelector('.news-card__tag')?.textContent || '',
    );
    return parts.join(' ').toLowerCase();
  };

  const matchesSearch = (query, text) => {
    if (!query) return true;
    return query.split(/\s+/).filter(Boolean).every((term) => text.includes(term));
  };

  const matchesDate = (card) => {
    const filterDate = dateFilterInput?.value;
    return !filterDate || card.dataset.date === filterDate;
  };

  const hasActiveFilters = () => (
    Boolean(searchInput.value.trim() || dateFilterInput?.value) || activeCategory !== 'all'
  );

  const syncResultsTemplate = () => {
    if (!resultsEl) return;
    const amTemplate = window.MOPD_I18N?.am?.['page.news.results'];
    resultsEl.dataset.template = document.documentElement.lang === 'am' && amTemplate
      ? amTemplate
      : 'Showing {count} of {total} articles';
  };

  const updateResultsCount = (visible) => {
    if (!resultsEl) return;
    if (!hasActiveFilters()) {
      resultsEl.hidden = true;
      resultsEl.textContent = '';
      return;
    }
    resultsEl.hidden = false;
    const template = resultsEl.dataset.template || 'Showing {count} of {total} articles';
    resultsEl.textContent = template.replace('{count}', String(visible)).replace('{total}', String(cards.length));
  };

  const filterNews = () => {
    const query = searchInput.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach((card) => {
      const category = card.dataset.category || '';
      const show = (activeCategory === 'all' || category === activeCategory)
        && matchesSearch(query, getCardSearchText(card))
        && matchesDate(card);
      card.hidden = !show;
      card.classList.toggle('is-filtered-out', !show);
      if (show) visible += 1;
    });
    if (emptyEl) emptyEl.hidden = visible > 0;
    updateResultsCount(visible);
    if (clearBtn) clearBtn.hidden = !(searchInput.value.trim() || dateFilterInput?.value);
  };

  searchInput.addEventListener('input', filterNews);
  searchForm?.addEventListener('submit', (e) => { e.preventDefault(); filterNews(); });
  dateFilterInput?.addEventListener('change', filterNews);
  clearBtn?.addEventListener('click', () => {
    searchInput.value = '';
    if (dateFilterInput) dateFilterInput.value = '';
    filterNews();
  });

  categoryBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      categoryBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = btn.dataset.newsCategory || 'all';
      filterNews();
    });
  });

  syncResultsTemplate();
  filterNews();
  window.addEventListener('mopd:language', () => { syncResultsTemplate(); filterNews(); });
}
