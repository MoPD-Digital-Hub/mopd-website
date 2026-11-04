/* MoNS brand overlay — merges EN/AM ministry rename into static + DB i18n tables */
(function () {
  if (window.SITE_BRAND !== 'mons') return;

  const overlay = {
    'meta.title': {
      en: 'Ministry of National Strategy — Ethiopia',
      am: 'የብሔራዊ ስትራቴጂ ሚኒስቴር — ኢትዮጵያ',
    },
    'meta.description': {
      en: 'Official website of the Ministry of National Strategy (MoNS), Ethiopia.',
      am: 'የኢትዮጵያ ፌዴራላዊ ዴሞክራሲያዊ ሪፐብሊክ የብሔራዊ ስትራቴጂ ሚኒስቴር (MoNS) ኦፊሴላዊ ድረ-ገጽ — ብሔራዊ ስትራቴጂ፣ እቅድ እና ዘላቂ እድገት',
    },
    'nav.sub.about_mopd': { en: 'About MoNS', am: 'ስለ የብሔራዊ ስትራቴጂ ሚኒስቴር' },
    'hero.title.line1': { en: "Charting Ethiopia's", am: 'የኢትዮጵያን' },
    'hero.title.line2': { en: 'National Strategy', am: 'ብሔራዊ ስትራቴጂ መቅረጽ' },
    'hero.desc': {
      en: "The Ministry of National Strategy steers national policy, coordinates strategic programmes, and monitors progress toward Ethiopia's long-range development agenda.",
      am: 'የብሔራዊ ስትራቴጂ ሚኒስቴር ብሔራዊ ፖሊሲዎችን ያስተባብራል፣ የስትራቴጂክ እቅዶችን ያመራል፣ እንዲሁም የኢትዮጵያን ዐሥር ዓመት የልማት እቅድ እድገት ይከታተላል።',
    },
    'hero.cta2': { en: 'Learn About MoNS', am: 'ስለ MoNS ይወቁ' },
    'about.tag': { en: 'About MoNS', am: 'ስለ የብሔራዊ ስትራቴጂ ሚኒስቴር' },
    'about.lead': {
      en: 'Welcome to the official website of the Ministry of National Strategy (MoNS) in Ethiopia.',
      am: 'በኢትዮጵያ የብሔራዊ ስትራቴጂ ሚኒስቴር (MoNS) ኦፊሴላዊ ድረ-ገጽ እንኳን በደህና መጡ።',
    },
    'about.p1': {
      en: "As the primary government institution responsible for national strategy and planning, MoNS plays a vital role in shaping Ethiopia's sustainable growth.",
      am: 'እንደ ብሔራዊ ስትራቴጂና እቅድ ዋና የመንግሥት ተቋም፣ MoNS የኢትዮጵያን ዘላቂ እድገት በመቅረጽ ረገድ ወሳኝ ሚና ይጫወታል።',
    },
    'about.p2': {
      en: "Through this website, we provide comprehensive information about the MoNS's initiatives, projects, and services — including valuable resources, reports, and data related to our national development agenda.",
      am: 'በዚህ ድረ-ገጽ በኩል ስለ MoNS ተነሳሽነቶች፣ ፕሮጀክቶችና አገልግሎቶች — እንዲሁም ከብሔራዊ የልማት አጀንዳ ጋር የተያያዙ ጠቃሚ ሀብቶች፣ ሪፖርቶችና መረጃዎች — አጠቃላይ መረጃ እናቀርባለን።',
    },
    'page.about.organogram_desc': {
      en: 'Core directorates and units within the Ministry of National Strategy.',
      am: 'በብሔራዊ ስትራቴጂ ሚኒስቴር ውስጥ ያሉ ዋና ዳይሬክቶሬቶችና ክፍሎች።',
    },
    'mission.quote': {
      en: 'To build efficient, data-driven, and accountable public systems that transform macroeconomic potential into inclusive, long-term development outcomes.',
      am: 'ብቃት ያላቸው፣ በመረጃ የሚመሩ እና ተጠያቂ የሕዝብ ስርዓቶችን መገንባት — የማክሮ ኢኮኖሚ አቅምን ወደ አካታችና የረጅም ጊዜ የልማት ውጤቶች ለመቀየር።',
    },
    'mission.cite': { en: '— Ministry of National Strategy', am: '— የብሔራዊ ስትራቴጂ ሚኒስቴር' },
    'loader.tagline': { en: 'Ministry of National Strategy', am: 'የብሔራዊ ስትራቴጂ ሚኒስቴር' },
    'portal.contact': { en: 'Contact MoNS', am: 'MoNSን ያግኙ' },
    'climate.desc': {
      en: "MoNS leads Ethiopia's climate policy integration, green technology adoption, and alignment of development goals with environmental sustainability.",
      am: 'MoNS የኢትዮጵያን የአየር ንብረት ፖሊሲ ውህደት፣ አረንጓዴ ቴክኖሎጂ ተቀባይነት እና የልማት ግቦችን ከአካባቢ ዘላቂነት ጋር ማስማማት ያመራል።',
    },
    'page.about.title': { en: 'About MoNS', am: 'ስለ የብሔራዊ ስትራቴጂ ሚኒስቴር' },
    'page.leadership.desc': {
      en: "The minister and state ministers leading Ethiopia's national strategy agenda.",
      am: 'የኢትዮጵያን ብሔራዊ ስትራቴጂ አጀንዳ የሚመሩ ሚኒስትርና ሚኒስቴር ዴታዎች።',
    },
    'footer.copyright': {
      en: '© 2026 Ministry of National Strategy. All rights reserved.',
      am: '© 2026 የብሔራዊ ስትራቴጂ ሚኒስቴር። ሁሉም መብቶች የተጠበቁ ናቸው።',
    },
  };

  if (window.MOPD_I18N && window.MOPD_I18N.am) {
    Object.keys(overlay).forEach((key) => {
      window.MOPD_I18N.am[key] = overlay[key].am;
    });
  }

  window.MOPD_I18N_DB = window.MOPD_I18N_DB || {};
  Object.keys(overlay).forEach((key) => {
    window.MOPD_I18N_DB[key] = Object.assign({}, window.MOPD_I18N_DB[key] || {}, overlay[key]);
  });

  const reapply = () => {
    if (typeof window.applyMopdLanguage !== 'function') return;
    const params = new URLSearchParams(window.location.search);
    const forced = params.get('lang');
    if (forced === 'en' || forced === 'am') {
      try { localStorage.setItem('mopd-lang', forced); } catch (_) {}
      window.applyMopdLanguage(forced);
      return;
    }
    const lang = (document.documentElement.lang === 'am' || localStorage.getItem('mopd-lang') === 'am') ? 'am' : 'en';
    window.applyMopdLanguage(lang);
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', reapply);
  } else {
    reapply();
  }
})();
