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

    if active_type in ('all', 'news'):
        results['news'] = (
            NewsArticle.objects.filter(is_published=True)
            .filter(
                Q(title__icontains=q)
                | Q(excerpt__icontains=q)
                | Q(body__icontains=q)
                | Q(search_keywords__icontains=q)
            )
            .distinct()[:limit]
        )

    if active_type in ('all', 'documents'):
        results['documents'] = (
            Document.objects.filter(is_published=True)
            .filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(file_url__icontains=q)
            )
            .distinct()[:limit]
        )

    if active_type in ('all', 'pages'):
        results['pages'] = (
            SiteTranslation.objects.filter(
                Q(key__icontains=q) | Q(text__icontains=q)
            )
            .exclude(text='')
            .distinct()[:limit]
        )

    if active_type in ('all', 'procurement'):
        results['procurement'] = (
            ProcurementNotice.objects.filter(is_published=True)
            .filter(
                Q(title__icontains=q)
                | Q(reference__icontains=q)
                | Q(description__icontains=q)
                | Q(file_url__icontains=q)
            )
            .distinct()[:limit]
        )

    if active_type in ('all', 'vacancies'):
        results['vacancies'] = (
            Vacancy.objects.filter(is_published=True)
            .filter(
                Q(title__icontains=q)
                | Q(reference__icontains=q)
                | Q(location__icontains=q)
                | Q(description__icontains=q)
                | Q(file_url__icontains=q)
            )
            .distinct()[:limit]
        )

    if active_type in ('all', 'departments'):
        results['departments'] = (
            Department.objects.filter(is_published=True)
            .filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
            )
            .distinct()[:limit]
        )

    return results
