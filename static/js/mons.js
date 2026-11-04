/**
 * MoNS motion layer — Awwwards-inspired choreography for the ministry site.
 * Respects prefers-reduced-motion. No heavy libraries.
 */
(function () {
  if (document.body.dataset.brand !== 'mons' && !document.body.classList.contains('site-mons')) {
    return;
  }

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ease = 'cubic-bezier(0.22, 1, 0.36, 1)';

  function onReady(fn) {
    if (document.documentElement.classList.contains('mp-page-ready') || document.body.classList.contains('mp-page-ready')) {
      fn();
      return;
    }
    const obs = new MutationObserver(() => {
      if (document.documentElement.classList.contains('mp-page-ready') || document.body.classList.contains('mp-page-ready')) {
        obs.disconnect();
        fn();
      }
    });
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    obs.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    // Fallback if loader already gone
    window.setTimeout(fn, 5200);
  }

  function initHeroChoreography() {
    const content = document.querySelector('.mp-hero__content');
    if (!content) return;

    const lines = content.querySelectorAll('.mp-hero__title span');
    const desc = content.querySelector('.mp-hero__desc');
    const actions = content.querySelector('.mp-hero__actions');
    const accent = document.querySelector('.mp-hero__accent-line');
    const ticker = document.querySelector('.mp-hero__ticker');
    const scroll = document.querySelector('.mp-hero__scroll');

    const cast = [...lines, desc, actions, accent, ticker, scroll].filter(Boolean);
    cast.forEach((el) => el.classList.add('mons-hero-piece'));

    if (reduced) {
      cast.forEach((el) => el.classList.add('is-in'));
      return;
    }

    cast.forEach((el, i) => {
      window.setTimeout(() => el.classList.add('is-in'), 120 + i * 110);
    });
  }

  function initStaggerReveals() {
    const groups = document.querySelectorAll('.mp-reveal, [data-reveal-group]');
    if (!groups.length) return;

    if (reduced) {
      groups.forEach((g) => {
        g.classList.add('is-in', 'visible');
        g.querySelectorAll('.mp-stagger > *, .mons-stagger-child').forEach((c) => c.classList.add('is-in'));
      });
      return;
    }

    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const root = entry.target;
          root.classList.add('is-in', 'visible');

          const kids = root.querySelectorAll(
            '.mp-stagger > *, .mp-metric, .mp-leader, .mp-news__card, .mp-command__card, .mp-bento__card, .mp-partners__item'
          );
          kids.forEach((kid, i) => {
            kid.classList.add('mons-stagger-child');
            window.setTimeout(() => kid.classList.add('is-in'), Math.min(80 + i * 70, 560));
          });

          const media = root.querySelectorAll('img, .mp-bento__media, .mp-devplan__document, .mp-climate__visual');
          media.forEach((m, i) => {
            m.classList.add('mons-media-reveal');
            window.setTimeout(() => m.classList.add('is-in'), 140 + i * 90);
          });

          obs.unobserve(root);
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
    );

    groups.forEach((g) => obs.observe(g));
  }

  function initMagneticButtons() {
    if (reduced || window.matchMedia('(pointer: coarse)').matches) return;
    const buttons = document.querySelectorAll(
      '.mp-hero__actions .mp-btn, body.site-mons .mp-btn--fill, body.site-mons .mp-header .mp-btn--fill'
    );

    buttons.forEach((btn) => {
      btn.classList.add('mons-magnetic');
      const strength = 14;

      btn.addEventListener('pointermove', (e) => {
        const r = btn.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        btn.style.transform = `translate(${(x / r.width) * strength}px, ${(y / r.height) * strength}px)`;
      });

      btn.addEventListener('pointerleave', () => {
        btn.style.transform = '';
      });
    });
  }

  function initHeroParallax() {
    if (reduced) return;
    const media = document.querySelector('.mp-hero__media');
    const hero = document.querySelector('.mp-hero');
    if (!media || !hero) return;

    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const y = window.scrollY;
        const h = hero.offsetHeight || 1;
        if (y < h * 1.2) {
          const p = Math.min(y / h, 1);
          media.style.transform = `translate3d(0, ${p * 12}%, 0) scale(${1.04 + p * 0.04})`;
        }
        ticking = false;
      });
    };

    media.classList.add('mons-parallax-media');
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  function initNavUnderline() {
    const links = document.querySelectorAll('.mp-header .mp-nav__link, .mp-header .sx-nav a');
    links.forEach((link) => link.classList.add('mons-nav-link'));
  }

  function initProgressPolish() {
    const bar = document.getElementById('scrollProgress');
    if (!bar) return;
    bar.classList.add('mons-progress');
  }

  function initImageHover() {
    if (reduced || window.matchMedia('(pointer: coarse)').matches) return;
    document.querySelectorAll('.mp-news__card img, .mp-leader__photo img, .mp-bento__media img').forEach((img) => {
      img.classList.add('mons-img-zoom');
    });
  }

  onReady(() => {
    initHeroChoreography();
    initStaggerReveals();
    initMagneticButtons();
    initHeroParallax();
    initNavUnderline();
    initProgressPolish();
    initImageHover();
    document.documentElement.style.setProperty('--mons-ease-js', ease);
  });
})();
