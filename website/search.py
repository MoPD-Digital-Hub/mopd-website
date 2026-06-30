from django.db.models import Q

from .models import Department, Document, NewsArticle, ProcurementNotice, SiteTranslation, Vacancy


SEARCH_FILTERS = [
    ('all', 'All'),
    ('news', 'News'),
    ('documents', 'Documents'),
    ('pages', 'Pages'),
    ('procurement', 'Procurement'),
    ('vacancies', 'Vacancies'),
    ('departments', 'Departments'),
]


def run_site_search(query, result_type='all', limit=20):
    q = (query or '').strip()
    active_type = result_type if result_type in dict(SEARCH_FILTERS) else 'all'
    results = {
        'query': q,
        'active_type': active_type,
        'filters': SEARCH_FILTERS,
        'news': [],
        'documents': [],
        'pages': [],
        'procurement': [],
        'vacancies': [],
        'departments': [],
    }
    if len(q) < 2:
        return results

    # The site switches language client-side, so Django's active language may
    # not match the visitor's selected language. Search both translation
    # columns explicitly so English and Amharic content are both discoverable.
    if active_type in ('all', 'news'):
        results['news'] = (
            NewsArticle.objects.filter(is_published=True)
            .filter(
                Q(title_en__icontains=q)
                | Q(title_am__icontains=q)
                | Q(excerpt_en__icontains=q)
                | Q(excerpt_am__icontains=q)
                | Q(body_en__icontains=q)
                | Q(body_am__icontains=q)
                | Q(search_keywords__icontains=q)
            )
            .distinct()[:limit]
        )

    if active_type in ('all', 'documents'):
        results['documents'] = (
            Document.objects.filter(is_published=True)
            .filter(
                Q(title_en__icontains=q)
                | Q(title_am__icontains=q)
                | Q(description_en__icontains=q)
                | Q(description_am__icontains=q)
                | Q(file_url__icontains=q)
            )
            .distinct()[:limit]
        )

    if active_type in ('all', 'pages'):
        results['pages'] = (
            SiteTranslation.objects.filter(
                Q(key__icontains=q)
                | Q(text_en__icontains=q)
                | Q(text_am__icontains=q)
            )
            .exclude(text_en='', text_am='')
            .distinct()[:limit]
        )

    if active_type in ('all', 'procurement'):
        results['procurement'] = (
            ProcurementNotice.objects.filter(is_published=True)
            .filter(
                Q(title_en__icontains=q)
                | Q(title_am__icontains=q)
                | Q(reference__icontains=q)
                | Q(description_en__icontains=q)
                | Q(description_am__icontains=q)
                | Q(file_url__icontains=q)
            )
            .distinct()[:limit]
        )

    if active_type in ('all', 'vacancies'):
        results['vacancies'] = (
            Vacancy.objects.filter(is_published=True)
            .filter(
                Q(title_en__icontains=q)
                | Q(title_am__icontains=q)
                | Q(reference__icontains=q)
                | Q(location_en__icontains=q)
                | Q(location_am__icontains=q)
                | Q(description_en__icontains=q)
                | Q(description_am__icontains=q)
                | Q(file_url__icontains=q)
            )
            .distinct()[:limit]
        )

    if active_type in ('all', 'departments'):
        results['departments'] = (
            Department.objects.filter(is_published=True)
            .filter(
                Q(name_en__icontains=q)
                | Q(name_am__icontains=q)
                | Q(description_en__icontains=q)
                | Q(description_am__icontains=q)
            )
            .distinct()[:limit]
        )

    return results
