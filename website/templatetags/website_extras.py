from django import template

register = template.Library()


@register.filter
def nav_active(current, page_id):
    about_pages = {'about', 'leadership', 'leader', 'leader_detail'}
    news_pages = {'news', 'news_detail', 'gallery', 'press'}
    climate_pages = {'climate', 'climate_docs', 'green_tech'}
    data_pages = {'stats'}

    if page_id == 'about':
        return current in about_pages
    if page_id == 'news':
        return current in news_pages
    if page_id == 'climate':
        return current in climate_pages
    if page_id == 'data':
        return current in data_pages
    return current == page_id


@register.simple_tag
def bilingual(obj, field):
    """Return dict with en/am for template data-bilingual usage."""
    en = getattr(obj, f'{field}_en', '') or ''
    am = getattr(obj, f'{field}_am', '') or en
    return {'en': en, 'am': am}
