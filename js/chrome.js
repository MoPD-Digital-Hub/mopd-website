/* Shared site chrome for inner pages */
(function () {
  const base = document.body.dataset.base || '';
  const page = document.body.dataset.page || '';
  const CDN = 'https://mopd.gov.et';

  const nav = {
    about: { href: `${base}about.html`, sub: { about: `${base}about.html`, leadership: `${base}leadership.html` } },
    news: { href: `${base}news.html`, sub: { news: `${base}news.html`, press: `${base}press-release.html`, gallery: `${base}gallery.html` } },
    data: { href: `${base}statistics-documents.html`, sub: { stats: `${base}statistics-documents.html`, params: 'https://national-parameters.mopd.gov.et/', sdg: 'https://sdg.mopd.gov.et/' } },
    climate: { href: `${base}about-climate.html`, sub: { about: `${base}about-climate.html`, docs: `${base}climate-documents.html`, green: `${base}green-technology.html`, portal: 'https://climate.mopd.gov.et/' } },
    devplan: `${base}development-planning.html`,
    contact: `${base}contact.html`,
    home: `${base}index.html`,
  };

  function isActive(section) {
    if (page === section) return true;
    if (section === 'about' && (page === 'leadership' || page === 'leader')) return true;
    if (section === 'news' && (page === 'gallery' || page === 'press')) return true;
    if (section === 'data' && page === 'stats') return true;
    if (section === 'climate' && (page === 'climate' || page === 'climate-docs' || page === 'green-tech')) return true;
    if (section === 'devplan' && page === 'devplan') return true;
    return false;
  }

  function external(href) {
    return href.startsWith('http') ? ' target="_blank" rel="noopener"' : '';
  }

  window.injectMopdChrome = function injectMopdChrome() {
    const main = document.querySelector('main.page');
    if (!main) return;

    const topBar = `
  <div class="top-bar">
    <div class="container top-bar__inner">
      <span class="top-bar__tag" data-i18n="topbar.tag">Federal Democratic Republic of Ethiopia</span>
      <div class="top-bar__actions">
        <a href="tel:0111403049" class="top-bar__link">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>
          <span class="top-bar__text">011 140 3049</span>
        </a>
        <a href="mailto:info@mopd.gov.et" class="top-bar__link">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          <span class="top-bar__text">info@mopd.gov.et</span>
        </a>
        <div class="lang-switch">
          <button class="lang-switch__btn active" data-lang="en">EN</button>
          <button class="lang-switch__btn" data-lang="am">አማ</button>
        </div>
      </div>
    </div>
  </div>`;

    const header = `
  <header class="header header--inner scrolled" id="header">
    <div class="container header__inner">
      <a href="${nav.home}" class="logo" aria-label="Ministry of Planning and Development">
        <img class="logo__img" src="${base}picture/EPDM-Illustration-SideText_Green.png" alt="Ministry of Planning and Development">
      </a>
      <nav class="nav" id="nav">
        <ul class="nav__list">
          <li class="nav__dropdown">
            <a href="${nav.about.href}" class="nav__link${isActive('about') ? ' active' : ''}" data-i18n="nav.about">About</a>
            <ul class="nav__submenu">
              <li><a href="${nav.about.sub.about}" data-i18n="nav.sub.about_mopd">About MoPD</a></li>
              <li><a href="${nav.about.sub.leadership}" data-i18n="nav.sub.management">Management</a></li>
            </ul>
          </li>
          <li class="nav__dropdown">
            <a href="${nav.news.href}" class="nav__link${isActive('news') ? ' active' : ''}" data-i18n="nav.news">News &amp; Media</a>
            <ul class="nav__submenu">
              <li><a href="${nav.news.sub.news}" data-i18n="nav.sub.news">News</a></li>
              <li><a href="${nav.news.sub.press}" data-i18n="nav.sub.press">Press Release</a></li>
              <li><a href="${nav.news.sub.gallery}" data-i18n="nav.sub.gallery">Gallery</a></li>
            </ul>
          </li>
          <li class="nav__dropdown">
            <a href="${nav.data.href}" class="nav__link" data-i18n="nav.data">Data &amp; Links</a>
            <ul class="nav__submenu">
              <li><a href="${nav.data.sub.stats}" data-i18n="nav.sub.stats">Statistics Documents</a></li>
              <li><a href="${nav.data.sub.params}" target="_blank" rel="noopener" data-i18n="nav.sub.national_params">National Parameters</a></li>
              <li><a href="${nav.data.sub.sdg}" target="_blank" rel="noopener" data-i18n="nav.sub.sdg">SDG Goal-Tracker</a></li>
            </ul>
          </li>
          <li class="nav__dropdown">
            <a href="${nav.climate.href}" class="nav__link${isActive('climate') ? ' active' : ''}" data-i18n="nav.climate">Climate</a>
            <ul class="nav__submenu">
              <li><a href="${nav.climate.sub.about}" data-i18n="nav.sub.about_climate">About Climate</a></li>
              <li><a href="${nav.climate.sub.docs}" data-i18n="nav.sub.climate_docs">Documents</a></li>
              <li><a href="${nav.climate.sub.green}" data-i18n="nav.sub.green_tech">Green Technology</a></li>
              <li><a href="${nav.climate.sub.portal}" target="_blank" rel="noopener" data-i18n="nav.sub.climate_portal">Climate Knowledge Portal</a></li>
            </ul>
          </li>
          <li><a href="${nav.devplan}" class="nav__link${page === 'devplan' ? ' active' : ''}" data-i18n="nav.devplan">Development Planning</a></li>
          <li><a href="${nav.contact}" class="nav__link nav__link--cta${page === 'contact' ? ' active' : ''}" data-i18n="nav.contact">Contact Us</a></li>
        </ul>
      </nav>
      <button class="menu-toggle" id="menuToggle" aria-label="Toggle menu" data-i18n-aria="aria.menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>`;

    const footer = `
  <footer class="footer">
    <div class="container">
      <div class="footer__grid">
        <div class="footer__brand">
          <a href="${nav.home}" class="logo logo--footer" aria-label="Ministry of Planning and Development">
            <img class="logo__img" src="${base}picture/EPDM-Illustration-SideText_Green.png" alt="Ministry of Planning and Development">
          </a>
          <p data-i18n="footer.desc">The primary government institution responsible for national planning and development, shaping Ethiopia's sustainable growth.</p>
        </div>
        <div class="footer__links">
          <h4 data-i18n="footer.about">About</h4>
          <ul>
            <li><a href="${nav.about.sub.about}" data-i18n="nav.sub.about_mopd">About MoPD</a></li>
            <li><a href="${nav.about.sub.leadership}" data-i18n="nav.sub.management">Management</a></li>
            <li><a href="${nav.about.sub.about}" data-i18n="footer.link.about_page">About Page</a></li>
            <li><a href="${nav.contact}" data-i18n="nav.contact">Contact Us</a></li>
          </ul>
        </div>
        <div class="footer__links">
          <h4 data-i18n="footer.news">News &amp; Media</h4>
          <ul>
            <li><a href="${nav.news.sub.news}" data-i18n="nav.sub.news">News</a></li>
            <li><a href="${nav.news.sub.press}" data-i18n="nav.sub.press">Press Release</a></li>
            <li><a href="${nav.news.sub.gallery}" data-i18n="nav.sub.gallery">Gallery</a></li>
          </ul>
        </div>
        <div class="footer__links">
          <h4 data-i18n="footer.data">Data &amp; Climate</h4>
          <ul>
            <li><a href="${nav.data.sub.stats}" data-i18n="nav.sub.stats">Statistics Documents</a></li>
            <li><a href="${nav.data.sub.params}" target="_blank" rel="noopener" data-i18n="nav.sub.national_params">National Parameters</a></li>
            <li><a href="${nav.data.sub.sdg}" target="_blank" rel="noopener" data-i18n="nav.sub.sdg">SDG Goal-Tracker</a></li>
            <li><a href="${nav.climate.sub.about}" data-i18n="nav.sub.about_climate">About Climate</a></li>
            <li><a href="${nav.climate.sub.docs}" data-i18n="nav.sub.climate_docs">Climate Documents</a></li>
            <li><a href="${nav.climate.sub.green}" data-i18n="nav.sub.green_tech">Green Technology</a></li>
            <li><a href="${nav.climate.sub.portal}" target="_blank" rel="noopener" data-i18n="nav.sub.climate_portal">Climate Knowledge Portal</a></li>
            <li><a href="${nav.devplan}" data-i18n="nav.devplan">Development Planning</a></li>
          </ul>
        </div>
        <div class="footer__links">
          <h4 data-i18n="footer.affiliates">MoPD Affiliates</h4>
          <ul>
            <li><a href="https://www.epa.gov.et/" target="_blank" rel="noopener" data-i18n="affiliate.epa">Environmental Protection Authority</a></li>
            <li><a href="http://www.csa.gov.et/" target="_blank" rel="noopener" data-i18n="affiliate.csa">Central Statistics Service</a></li>
            <li><a href="https://psi.org.et" target="_blank" rel="noopener" data-i18n="affiliate.psi">Policy Study Institute</a></li>
            <li><a href="${nav.data.sub.params}" target="_blank" rel="noopener" data-i18n="nav.sub.national_params">National Parameters</a></li>
          </ul>
        </div>
      </div>
      <div class="footer__bottom">
        <p data-i18n="footer.copyright">&copy; 2026 Ministry of Planning and Development. All rights reserved.</p>
        <div class="footer__social">
          <a href="https://www.facebook.com/MoPDETH" target="_blank" rel="noopener" aria-label="Facebook"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg></a>
          <a href="https://twitter.com/mopd_ethiopia" target="_blank" rel="noopener" aria-label="Twitter"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"/></svg></a>
          <a href="https://www.linkedin.com/company/ministry-of-planning-and-development-ethiopia/" target="_blank" rel="noopener" aria-label="LinkedIn"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg></a>
        </div>
      </div>
    </div>
  </footer>
  <button class="back-to-top" id="backToTop" aria-label="Back to top" data-i18n-aria="aria.back_top">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 15l-6-6-6 6"/></svg>
  </button>`;

    main.insertAdjacentHTML('beforebegin', topBar + header);
    main.insertAdjacentHTML('afterend', footer);
    window.MOPD_CHROME_INJECTED = true;
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.injectMopdChrome);
  } else {
    window.injectMopdChrome();
  }
})();
