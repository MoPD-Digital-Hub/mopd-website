import json

from django.conf import settings

from config.i18n import LANG_BUTTON_LABELS

from .brand import MONS_I18N, get_brand
from .models import AffiliateLink, SiteSettings, SiteTranslation


def site_globals(request):
    settings_obj = SiteSettings.load()
    lang_codes = [code for code, _ in settings.LANGUAGES]
    translations = {
        t.key: {
            code: getattr(t, f'text_{code}', '') or ''
            for code in lang_codes
        }
        for t in SiteTranslation.objects.all()
    }
    brand = get_brand()
    if brand['id'] == 'mons':
        for key, texts in MONS_I18N.items():
            bucket = translations.setdefault(key, {})
            for code, text in texts.items():
                bucket[code] = text
    site_languages = [
        {
            'code': code,
            'label': LANG_BUTTON_LABELS.get(code, code.upper()),
            'name': str(label),
        }
        for code, label in settings.LANGUAGES
    ]
    return {
        'site_settings': settings_obj,
        'affiliates': AffiliateLink.objects.filter(is_published=True),
        'translations_json': json.dumps(translations, ensure_ascii=False),
        'site_languages': site_languages,
        'site_languages_json': json.dumps(site_languages),
        'brand': brand,
        'site_brand': brand['id'],
    }
