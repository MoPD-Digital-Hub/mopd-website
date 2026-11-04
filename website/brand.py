"""Site brand identity (MoPD vs MoNS theme)."""

from __future__ import annotations

from django.conf import settings


BRANDS = {
    'mopd': {
        'id': 'mopd',
        'short': 'MoPD',
        'full_en': 'Ministry of Planning and Development',
        'full_am': 'የፕላንና ልማት ሚኒስቴር',
        'title_en': 'Ministry of Planning and Development — Ethiopia',
        'title_am': 'የፕላንና ልማት ሚኒስቴር — ኢትዮጵያ',
        'meta_en': 'Official website of the Ministry of Planning and Development (MoPD), Ethiopia.',
        'meta_am': 'የኢትዮጵያ ፌዴራላዊ ዴሞክራሲያዊ ሪፐብሊክ የፕላንና ልማት ሚኒስቴር (MoPD) ኦፊሴላዊ ድረ-ገጽ — ብሔራዊ እቅድ፣ ልማት እና ዘላቂ እድገት',
        'about_nav_en': 'About MoPD',
        'about_nav_am': 'ስለ የፕላንና ልማት ሚኒስቴር',
        'logo': 'picture/EPDM-Illustration-SideText_Green.png',
        'brand_mark': 'picture/EPDM-Illustration-SideText_Green.png',
        'favicon': 'picture/favicon-32.png',
        'theme_css': None,
        'body_class': '',
    },
    'mons': {
        'id': 'mons',
        'short': 'MoNS',
        'full_en': 'Ministry of National Strategy',
        'full_am': 'የብሔራዊ ስትራቴጂ ሚኒስቴር',
        'title_en': 'Ministry of National Strategy — Ethiopia',
        'title_am': 'የብሔራዊ ስትራቴጂ ሚኒስቴር — ኢትዮጵያ',
        'meta_en': 'Official website of the Ministry of National Strategy (MoNS), Ethiopia.',
        'meta_am': 'የኢትዮጵያ ፌዴራላዊ ዴሞክራሲያዊ ሪፐብሊክ የብሔራዊ ስትራቴጂ ሚኒስቴር (MoNS) ኦፊሴላዊ ድረ-ገጽ — ብሔራዊ ስትራቴጂ፣ እቅድ እና ዘላቂ እድገት',
        'about_nav_en': 'About MoNS',
        'about_nav_am': 'ስለ የብሔራዊ ስትራቴጂ ሚኒስቴር',
        # Keep the established side-text wordmark; MoNS mark stays available as brand_mark.
        'logo': 'picture/EPDM-Illustration-SideText_Green.png',
        'brand_mark': 'img/brand/mons-logo.png',
        # Keep the established MoPD browser icon (user-requested restore)
        'favicon': 'picture/favicon-32.png',
        'theme_css': 'css/mons.css',
        'body_class': 'site-mons',
    },
}


def get_brand() -> dict:
    return BRANDS.get(getattr(settings, 'SITE_BRAND', 'mopd'), BRANDS['mopd'])


# UI keys overridden when MoNS is active (ministry rename + hero).
MONS_I18N = {
    'meta.title': {
        'en': 'Ministry of National Strategy — Ethiopia',
        'am': 'የብሔራዊ ስትራቴጂ ሚኒስቴር — ኢትዮጵያ',
    },
    'meta.description': {
        'en': 'Official website of the Ministry of National Strategy (MoNS), Ethiopia.',
        'am': 'የኢትዮጵያ ፌዴራላዊ ዴሞክራሲያዊ ሪፐብሊክ የብሔራዊ ስትራቴጂ ሚኒስቴር (MoNS) ኦፊሴላዊ ድረ-ገጽ — ብሔራዊ ስትራቴጂ፣ እቅድ እና ዘላቂ እድገት',
    },
    'nav.sub.about_mopd': {
        'en': 'About MoNS',
        'am': 'ስለ የብሔራዊ ስትራቴጂ ሚኒስቴር',
    },
    'hero.title.line1': {
        'en': "Charting Ethiopia's",
        'am': 'የኢትዮጵያን',
    },
    'hero.title.line2': {
        'en': 'National Strategy',
        'am': 'ብሔራዊ ስትራቴጂ መቅረጽ',
    },
    'hero.desc': {
        'en': "The Ministry of National Strategy steers national policy, coordinates strategic programmes, and monitors progress toward Ethiopia's long-range development agenda.",
        'am': 'የብሔራዊ ስትራቴጂ ሚኒስቴር ብሔራዊ ፖሊሲዎችን ያስተባብራል፣ የስትራቴጂክ እቅዶችን ያመራል፣ እንዲሁም የኢትዮጵያን ዐሥር ዓመት የልማት እቅድ እድገት ይከታተላል።',
    },
    'hero.cta2': {
        'en': 'Learn About MoNS',
        'am': 'ስለ MoNS ይወቁ',
    },
    'about.tag': {
        'en': 'About MoNS',
        'am': 'ስለ የብሔራዊ ስትራቴጂ ሚኒስቴር',
    },
    'about.lead': {
        'en': 'Welcome to the official website of the Ministry of National Strategy (MoNS) in Ethiopia.',
        'am': 'በኢትዮጵያ የብሔራዊ ስትራቴጂ ሚኒስቴር (MoNS) ኦፊሴላዊ ድረ-ገጽ እንኳን በደህና መጡ።',
    },
    'about.p1': {
        'en': "As the primary government institution responsible for national strategy and planning, MoNS plays a vital role in shaping Ethiopia's sustainable growth.",
        'am': 'እንደ ብሔራዊ ስትራቴጂና እቅድ ዋና የመንግሥት ተቋም፣ MoNS የኢትዮጵያን ዘላቂ እድገት በመቅረጽ ረገድ ወሳኝ ሚና ይጫወታል።',
    },
    'about.p2': {
        'en': "Through this website, we provide comprehensive information about the MoNS's initiatives, projects, and services — including valuable resources, reports, and data related to our national development agenda.",
        'am': 'በዚህ ድረ-ገጽ በኩል ስለ MoNS ተነሳሽነቶች፣ ፕሮጀክቶችና አገልግሎቶች — እንዲሁም ከብሔራዊ የልማት አጀንዳ ጋር የተያያዙ ጠቃሚ ሀብቶች፣ ሪፖርቶችና መረጃዎች — አጠቃላይ መረጃ እናቀርባለን።',
    },
    'page.about.organogram_desc': {
        'en': 'Core directorates and units within the Ministry of National Strategy.',
        'am': 'በብሔራዊ ስትራቴጂ ሚኒስቴር ውስጥ ያሉ ዋና ዳይሬክቶሬቶችና ክፍሎች።',
    },
    'mission.cite': {
        'en': '— Ministry of National Strategy',
        'am': '— የብሔራዊ ስትራቴጂ ሚኒስቴር',
    },
    'contact.map_title': {
        'en': 'Ministry of National Strategy — 6 Kilo, Addis Ababa',
        'am': 'የብሔራዊ ስትራቴጂ ሚኒስቴር — 6 ኪሎ፣ አዲስ አበባ',
    },
    'footer.copyright': {
        'en': '© 2026 Ministry of National Strategy. All rights reserved.',
        'am': '© 2026 የብሔራዊ ስትራቴጂ ሚኒስቴር። ሁሉም መብቶች የተጠበቁ ናቸው።',
    },
    'page.about.title': {
        'en': 'About MoNS',
        'am': 'ስለ የብሔራዊ ስትራቴጂ ሚኒስቴር',
    },
    'page.gallery.alt': {
        'en': 'Ministry of National Strategy photo',
        'am': 'የብሔራዊ ስትራቴጂ ሚኒስቴር ፎቶ',
    },
    'loader.tagline': {
        'en': 'Ministry of National Strategy',
        'am': 'የብሔራዊ ስትራቴጂ ሚኒስቴር',
    },
    'portal.contact': {
        'en': 'Contact MoNS',
        'am': 'MoNSን ያግኙ',
    },
    'climate.desc': {
        'en': "MoNS leads Ethiopia's climate policy integration, green technology adoption, and alignment of development goals with environmental sustainability.",
        'am': 'MoNS የኢትዮጵያን የአየር ንብረት ፖሊሲ ውህደት፣ አረንጓዴ ቴክኖሎጂ ተቀባይነት እና የልማት ግቦችን ከአካባቢ ዘላቂነት ጋር ማስማማት ያመራል።',
    },
    'page.leadership.desc': {
        'en': "The minister and state ministers leading Ethiopia's national strategy agenda.",
        'am': 'የኢትዮጵያን ብሔራዊ ስትራቴጂ አጀንዳ የሚመሩ ሚኒስትርና ሚኒስቴር ዴታዎች።',
    },
}

# Back-compat alias
MONS_I18N_AM = {key: val['am'] for key, val in MONS_I18N.items()}
