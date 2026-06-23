/* MoPD Redesign — Main JavaScript */

function initMopdApp() {
  initMopdI18n();
  initLanguageSwitch();
  initHeader();
  initMobileMenu();
  initCarousel();
  initAboutTabs();
  initDocTabs();
  initScrollReveal();
  initCounters();
  initBackToTop();
  initNewsletter();
  initContactForm();
  initGalleryLightbox();
  initSmoothNav();
  initNewsPage();
}

document.addEventListener('DOMContentLoaded', () => {
  initMopdApp();
});

/* Sticky header on scroll */
function initHeader() {
  const header = document.getElementById('header');
  if (!header) return;

  window.addEventListener('scroll', () => {
    const currentScroll = window.scrollY;
    header.classList.toggle('scrolled', currentScroll > 50);
  });
}

/* Mobile menu toggle */
function initMobileMenu() {
  const toggle = document.getElementById('menuToggle');
  const nav = document.getElementById('nav');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => {
    toggle.classList.toggle('active');
    nav.classList.toggle('open');
    document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
  });

  nav.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', (e) => {
      if (window.innerWidth <= 992 && link.parentElement.classList.contains('nav__dropdown')) {
        const submenu = link.nextElementSibling;
        if (submenu && submenu.classList.contains('nav__submenu')) {
          e.preventDefault();
          link.parentElement.classList.toggle('open');
          return;
        }
      }
      toggle.classList.remove('active');
      nav.classList.remove('open');
      document.body.style.overflow = '';
    });
  });

  nav.querySelectorAll('.nav__submenu a').forEach(link => {
    link.addEventListener('click', () => {
      toggle.classList.remove('active');
      nav.classList.remove('open');
      document.body.style.overflow = '';
    });
  });
}

/* Hero carousel */
function initCarousel() {
  const slides = document.querySelectorAll('.carousel__slide');
  const dotsContainer = document.getElementById('carouselDots');
  const prevBtn = document.getElementById('carouselPrev');
  const nextBtn = document.getElementById('carouselNext');
  if (!slides.length || !dotsContainer || !prevBtn || !nextBtn) return;
  let current = 0;
  let autoplay;

  slides.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.classList.add('carousel__dot');
    if (i === 0) dot.classList.add('active');
    dot.setAttribute('aria-label', `Slide ${i + 1}`);
    dot.addEventListener('click', () => goTo(i));
    dotsContainer.appendChild(dot);
  });

  const dots = dotsContainer.querySelectorAll('.carousel__dot');

  function goTo(index) {
    slides[current].classList.remove('active');
    dots[current].classList.remove('active');
    current = (index + slides.length) % slides.length;
    slides[current].classList.add('active');
    dots[current].classList.add('active');

    const bgImages = document.querySelectorAll('.hero__bg-image');
    bgImages.forEach((img, i) => {
      img.classList.toggle('active', i === current);
    });
  }

  prevBtn.addEventListener('click', () => goTo(current - 1));
  nextBtn.addEventListener('click', () => goTo(current + 1));

  function startAutoplay() {
    autoplay = setInterval(() => goTo(current + 1), 6000);
  }

  function stopAutoplay() {
    clearInterval(autoplay);
  }

  const carousel = document.getElementById('heroCarousel');
  carousel.addEventListener('mouseenter', stopAutoplay);
  carousel.addEventListener('mouseleave', startAutoplay);

  startAutoplay();
}

/* About section tabs */
function initAboutTabs() {
  const tabs = document.querySelectorAll('.about__tab');
  const panels = document.querySelectorAll('.about__panel');
  if (!tabs.length) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;

      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById(`panel-${target}`).classList.add('active');
    });
  });
}

/* Climate documents category tabs */
function initDocTabs() {
  const root = document.querySelector('[data-doc-tabs]');
  if (!root) return;

  const tabs = root.querySelectorAll('[data-doc-tab]');
  const panels = root.querySelectorAll('[data-doc-panel]');

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.docTab;

      tabs.forEach((btn) => {
        const isActive = btn.dataset.docTab === target;
        btn.classList.toggle('active', isActive);
        btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
      });

      panels.forEach((panel) => {
        const isActive = panel.dataset.docPanel === target;
        panel.classList.toggle('active', isActive);
        panel.hidden = !isActive;
      });
    });
  });
}

/* Scroll reveal animations */
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, index * 80);
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.15,
    rootMargin: '0px 0px -40px 0px'
  });

  reveals.forEach(el => observer.observe(el));
}

/* Animated counters */
function initCounters() {
  const counters = document.querySelectorAll('.stat__number');
  let animated = false;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !animated) {
        animated = true;
        counters.forEach(counter => {
          const target = parseInt(counter.dataset.target, 10);
          animateCounter(counter, target);
        });
      }
    });
  }, { threshold: 0.5 });

  const statsSection = document.querySelector('.stats');
  if (statsSection) observer.observe(statsSection);
}

function animateCounter(element, target) {
  const duration = 2000;
  const start = performance.now();

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    element.textContent = Math.floor(eased * target);

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.textContent = target;
    }
  }

  requestAnimationFrame(update);
}

/* Back to top button */
function initBackToTop() {
  const btn = document.getElementById('backToTop');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 500);
  });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/* Newsletter form */
function initNewsletter() {
  const form = document.getElementById('newsletterForm');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = form.querySelector('input');
    const btn = form.querySelector('button');
    const isAm = getMopdLanguage() === 'am';
    const originalText = btn.dataset.i18nDefault || btn.textContent;

    btn.textContent = isAm
      ? (window.MOPD_I18N?.am?.['contact.subscribed'] || 'ተመዝግበዋል!')
      : (btn.dataset.i18nDefault || 'Subscribed!');
    btn.style.background = 'var(--green-500)';
    input.value = '';

    setTimeout(() => {
      btn.textContent = originalText;
      btn.style.background = '';
    }, 3000);
  });

  window.addEventListener('mopd:language', () => {
    const btn = form.querySelector('button[data-i18n]');
    if (btn && !btn.dataset.i18nDefault) {
      btn.dataset.i18nDefault = btn.textContent;
    }
  });
}

/* Active nav link on scroll */
function initSmoothNav() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav__link');
  if (!sections.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }, {
    threshold: 0.3,
    rootMargin: '-80px 0px -50% 0px'
  });

  sections.forEach(section => observer.observe(section));
}

/* Language switch */
function initLanguageSwitch() {
  document.querySelectorAll('.lang-switch__btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      applyMopdLanguage(btn.dataset.lang);
    });
  });
}

/* Contact page form */
function initContactForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const isAm = getMopdLanguage() === 'am';
    const original = btn.dataset.i18nDefault || btn.textContent;

    btn.textContent = isAm ? 'ተልኳል!' : 'Message Sent!';
    btn.disabled = true;
    form.reset();

    setTimeout(() => {
      btn.textContent = original;
      btn.disabled = false;
    }, 3000);
  });
}

/* Gallery lightbox */
function initGalleryLightbox() {
  const items = document.querySelectorAll('.gallery__item');
  if (!items.length) return;

  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.innerHTML = '<button class="lightbox__close" aria-label="Close">&times;</button><img class="lightbox__img" alt="">';
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

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) close();
  });
  lightbox.querySelector('.lightbox__close').addEventListener('click', close);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') close();
  });
}

/* News listing — search, category & date filter */
function initNewsPage() {
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

  function getCardSearchText(card) {
    const parts = [card.dataset.search || '', card.dataset.date || ''];
    card.querySelectorAll('.bilingual').forEach((el) => {
      parts.push(el.dataset.en || '', el.dataset.am || '');
    });
    const title = card.querySelector('h3')?.textContent || '';
    const excerpt = card.querySelector('.news-card__excerpt')?.textContent || '';
    const tag = card.querySelector('.news-card__tag')?.textContent || '';
    parts.push(title, excerpt, tag);
    return parts.join(' ').toLowerCase();
  }

  function matchesSearch(query, text) {
    if (!query) return true;
    const terms = query.split(/\s+/).filter(Boolean);
    return terms.every((term) => text.includes(term));
  }

  function matchesDate(card) {
    const filterDate = dateFilterInput?.value;
    if (!filterDate) return true;
    return card.dataset.date === filterDate;
  }

  function hasSearchOrDateFilters() {
    return Boolean(
      searchInput.value.trim()
      || dateFilterInput?.value
    );
  }

  function hasActiveFilters() {
    return Boolean(
      hasSearchOrDateFilters()
      || activeCategory !== 'all'
    );
  }

  function syncResultsTemplate() {
    if (!resultsEl) return;
    const lang = document.documentElement.lang;
    const amTemplate = window.MOPD_I18N?.am?.['page.news.results'];
    resultsEl.dataset.template = lang === 'am' && amTemplate
      ? amTemplate
      : 'Showing {count} of {total} articles';
  }

  function updateClearButton() {
    if (clearBtn) {
      clearBtn.hidden = !hasSearchOrDateFilters();
    }
  }

  function updateResultsCount(visible) {
    if (!resultsEl) return;

    if (!hasActiveFilters()) {
      resultsEl.hidden = true;
      resultsEl.textContent = '';
      return;
    }

    resultsEl.hidden = false;
    const template = resultsEl.dataset.template || 'Showing {count} of {total} articles';
    resultsEl.textContent = template
      .replace('{count}', String(visible))
      .replace('{total}', String(cards.length));
  }

  function setCardVisible(card, show) {
    card.hidden = !show;
    card.classList.toggle('is-filtered-out', !show);
  }

  function filterNews() {
    const query = searchInput.value.trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const category = card.dataset.category || '';
      const matchesCategory = activeCategory === 'all' || category === activeCategory;
      const text = getCardSearchText(card);
      const show = matchesCategory
        && matchesSearch(query, text)
        && matchesDate(card);

      setCardVisible(card, show);
      if (show) visible += 1;
    });

    if (emptyEl) emptyEl.hidden = visible > 0;
    updateResultsCount(visible);
    updateClearButton();
  }

  function clearFilters() {
    searchInput.value = '';
    if (dateFilterInput) dateFilterInput.value = '';
    filterNews();
  }

  searchInput.addEventListener('input', filterNews);

  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      filterNews();
    });
  }

  dateFilterInput?.addEventListener('change', filterNews);

  clearBtn?.addEventListener('click', clearFilters);

  categoryBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      categoryBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = btn.dataset.newsCategory || 'all';
      filterNews();
    });
  });

  if (resultsEl) {
    syncResultsTemplate();
  }

  updateClearButton();

  window.addEventListener('mopd:language', () => {
    syncResultsTemplate();
    filterNews();
  });
}
