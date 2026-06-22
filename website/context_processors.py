import json

from .models import AffiliateLink, SiteSettings, SiteTranslation


def navigation(request):
    page_id = ''
    if request.resolver_match:
        page_id = request.resolver_match.kwargs.get('page_id', '')
        if not page_id:
            page_id = request.resolver_match.url_name or ''
    return {'current_page': page_id}


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
