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
  document.querySelectorAll('.sx-lang__btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (typeof applyMopdLanguage === 'function') applyMopdLanguage(btn.dataset.lang);
      document.querySelectorAll('.sx-lang__btn').forEach((b) => {
        b.classList.toggle('is-active', b === btn);
      });
    });
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
    document.body.style.overflow = 'hidden';
  };
  const shut = () => {
    panel.classList.remove('is-open');
    panel.setAttribute('aria-hidden', 'true');
    btn.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  };

  btn.addEventListener('click', open);
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
  if (!mount) return;

  const videoId = mount.dataset.videoId || 'd7YfFd1gYAE';
  const segmentEnd = Math.max(1, parseInt(mount.dataset.videoEnd || '30', 10));

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

  const ytCmd = (iframe, func, args = []) => {
    iframe.contentWindow?.postMessage(
      JSON.stringify({ event: 'command', func, args }),
      '*'
    );
  };

  const loadIframe = () => {
    if (mount.dataset.loaded) return;
    mount.dataset.loaded = '1';

    const iframe = document.createElement('iframe');
    iframe.setAttribute('title', 'MoPD hero background video');
    iframe.setAttribute('tabindex', '-1');
    iframe.setAttribute('loading', 'eager');
    iframe.setAttribute('width', '1920');
    iframe.setAttribute('height', '1080');
    iframe.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture');
    iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
    const origin = encodeURIComponent(window.location.origin);
    iframe.src = [
      `https://www.youtube-nocookie.com/embed/${videoId}`,
      '?autoplay=1&mute=1&controls=0&rel=0',
      '&playsinline=1&modestbranding=1&iv_load_policy=3',
      '&disablekb=1&fs=0&cc_load_policy=0&autohide=1',
      '&showinfo=0&enablejsapi=1',
      `&start=0&end=${segmentEnd}`,
      `&origin=${origin}`,
    ].join('');

    let segmentTimer;
    let bootTimer;
    let revealed = false;

    const reveal = () => {
      if (revealed) return;
      revealed = true;
      showVideo();
    };

    const playFromStart = () => {
      ytCmd(iframe, 'seekTo', [0, true]);
      ytCmd(iframe, 'playVideo', []);
    };

    const bootPlayer = () => {
      iframe.contentWindow?.postMessage(
        JSON.stringify({ event: 'listening', id: 1, channel: 'widget' }),
        '*'
      );
      ytCmd(iframe, 'mute', []);
      ytCmd(iframe, 'playVideo', []);
      // Prefer highest available stream (YouTube may cap embed quality)
      ['highres', 'hd1080', 'hd720', 'large'].forEach((q) => {
        ytCmd(iframe, 'setPlaybackQuality', [q]);
      });
    };

    const kickPlay = () => {
      bootPlayer();
      setTimeout(reveal, 350);
    };

    const onYoutubeMessage = (event) => {
      if (!event.origin.includes('youtube')) return;
      let data;
      try {
        data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
      } catch {
        return;
      }

      if (data.event === 'onStateChange') {
        if (data.info === 1) {
          reveal();
        } else if (data.info === 2) {
          ytCmd(iframe, 'playVideo', []);
        } else if (data.info === 0) {
          playFromStart();
        }
      }

      if (data.event === 'infoDelivery' && typeof data.info?.currentTime === 'number') {
        if (data.info.currentTime >= segmentEnd - 0.3) {
          playFromStart();
        }
      }
    };

    window.addEventListener('message', onYoutubeMessage);

    iframe.addEventListener('load', () => {
      [200, 600, 1200, 2000, 3500].forEach((ms) => setTimeout(bootPlayer, ms));
      bootTimer = setInterval(bootPlayer, 4000);
      setTimeout(reveal, 2200);

      segmentTimer = setInterval(() => {
        ytCmd(iframe, 'getCurrentTime', []);
      }, 600);
    });

    const cover = mount.querySelector('.sx-hero__video-cover');
    const mask = mount.querySelector('.sx-hero__video-mask');
    const shield = mount.querySelector('.sx-hero__video-shield');
    const heroMedia = mount.closest('.sx-hero__media');

    if (cover) {
      mount.insertBefore(iframe, cover);
    } else if (shield) {
      mount.insertBefore(iframe, mask || shield);
    } else {
      mount.appendChild(iframe);
    }

    // Programmatic play — shield/cover block the YouTube button from view & clicks
    shield?.addEventListener('click', kickPlay);
    heroMedia?.addEventListener('click', kickPlay);

    mount._ytCleanup = () => {
      window.removeEventListener('message', onYoutubeMessage);
      clearInterval(segmentTimer);
      clearInterval(bootTimer);
    };
  };

  requestAnimationFrame(loadIframe);
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
