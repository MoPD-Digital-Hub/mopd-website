/* MoPD — corporate motion & micro-interactions */

function initMopdMotion() {
  initScrollProgress();
  initHeroEntrance();
  initRevealGroups();
  initSubtleParallax();
  initCardTilt();
}

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function initScrollProgress() {
  const bar = document.getElementById('scrollProgress');
  if (!bar || prefersReducedMotion()) return;

  let ticking = false;
  const update = () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = `${progress}%`;
    ticking = false;
  };

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(update);
      ticking = true;
    }
  }, { passive: true });

  update();
}

function initHeroEntrance() {
  if (prefersReducedMotion()) {
    document.querySelectorAll('.hero [data-entrance]').forEach((el) => {
      el.classList.add('is-visible');
    });
    return;
  }

  const items = document.querySelectorAll('.hero [data-entrance]');
  items.forEach((el, i) => {
    setTimeout(() => el.classList.add('is-visible'), 120 + i * 90);
  });
}

function initRevealGroups() {
  const groups = document.querySelectorAll('[data-reveal-group]');
  if (!groups.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const children = entry.target.querySelectorAll('.reveal, [data-reveal]');
      children.forEach((child, i) => {
        setTimeout(() => child.classList.add('visible'), prefersReducedMotion() ? 0 : i * 70);
      });
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -32px 0px' });

  groups.forEach((g) => observer.observe(g));
}

function initSubtleParallax() {
  if (prefersReducedMotion()) return;
  const hero = document.getElementById('hero');
  const bg = hero?.querySelector('.hero__bg');
  if (!hero || !bg) return;

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        const rect = hero.getBoundingClientRect();
        if (rect.bottom > 0 && rect.top < window.innerHeight) {
          const offset = Math.min(window.scrollY * 0.28, 120);
          bg.style.transform = `translate3d(0, ${offset}px, 0)`;
        }
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

function initCardTilt() {
  if (prefersReducedMotion() || window.innerWidth < 1024) return;

  document.querySelectorAll('[data-tilt]').forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      card.style.transform = `perspective(900px) rotateX(${-y * 4}deg) rotateY(${x * 4}deg) translateY(-4px)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });
}

window.initMopdMotion = initMopdMotion;
