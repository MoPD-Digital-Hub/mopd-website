import json

from .models import AffiliateLink, SiteSettings, SiteTranslation


def site_globals(request):
    settings = SiteSettings.load()
    translations = {
        t.key: {'en': t.text_en, 'am': t.text_am}
        for t in SiteTranslation.objects.all()
    }
    return {
        'site_settings': settings,
        'affiliates': AffiliateLink.objects.filter(is_published=True),
        'translations_json': json.dumps(translations),
    }
