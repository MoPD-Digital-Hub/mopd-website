from django.db.models import Q

from .models import Document, NewsArticle, SiteTranslation


def run_site_search(query, limit=20):
    q = (query or '').strip()
    if len(q) < 2:
        return {'query': q, 'news': [], 'documents': [], 'pages': []}

    news = (
        NewsArticle.objects.filter(is_published=True)
        .filter(
            Q(title__icontains=q)
            | Q(excerpt__icontains=q)
            | Q(body__icontains=q)
            | Q(search_keywords__icontains=q)
        )
        .distinct()[:limit]
    )

    documents = (
        Document.objects.filter(is_published=True)
        .filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
        )
        .distinct()[:limit]
    )

    pages = (
        SiteTranslation.objects.filter(
            Q(key__icontains=q) | Q(text__icontains=q)
        )
        .exclude(text='')
        .distinct()[:limit]
    )

    return {'query': q, 'news': news, 'documents': documents, 'pages': pages}
