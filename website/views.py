from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .climate_documents import climate_doc_sections
from .models import CarouselSlide, Document, GalleryAlbum, Leader, NewsArticle

PAGE_TEMPLATES = {
    'about': 'website/pages/about.html',
    'contact': 'website/pages/contact.html',
    'leadership': 'website/pages/leadership.html',
    'gallery': 'website/pages/gallery.html',
    'press-release': 'website/pages/press-release.html',
    'about-climate': 'website/pages/about-climate.html',
    'climate-documents': 'website/pages/climate-documents.html',
    'green-technology': 'website/pages/green-technology.html',
    'statistics-documents': 'website/pages/statistics-documents.html',
    'development-planning': 'website/pages/development-planning.html',
}

PAGE_NAV_IDS = {
    'about': 'about',
    'contact': 'contact',
    'leadership': 'leadership',
    'gallery': 'gallery',
    'press-release': 'press',
    'about-climate': 'climate',
    'climate-documents': 'climate_docs',
    'green-technology': 'green_tech',
    'statistics-documents': 'stats',
    'development-planning': 'devplan',
}


def _page_context(page_id):
    ctx = {'current_page': PAGE_NAV_IDS.get(page_id, page_id.replace('-', '_')), 'page_id': page_id}
    if page_id == 'leadership':
        ctx['leaders'] = Leader.objects.filter(is_published=True)
    elif page_id == 'gallery':
        ctx['albums'] = GalleryAlbum.objects.filter(is_published=True).prefetch_related('images')
    elif page_id == 'climate-documents':
        climate_docs = Document.objects.filter(
            is_published=True,
            doc_type=Document.DocType.CLIMATE,
        ).order_by('sort_order', 'id')
        ctx['climate_doc_sections'] = climate_doc_sections(climate_docs)
    elif page_id == 'statistics-documents':
        ctx['documents'] = Document.objects.filter(is_published=True, doc_type=Document.DocType.STATISTICS)
    return ctx


def home(request):
    featured_articles = NewsArticle.objects.filter(is_published=True, is_featured_home=True)[:3]
    if not featured_articles.exists():
        featured_articles = NewsArticle.objects.filter(is_published=True)[:3]
    return render(
        request,
        'website/pages/home.html',
        {
            'current_page': 'home',
            'carousel_slides': CarouselSlide.objects.filter(is_active=True),
            'featured_articles': featured_articles,
            'leaders': Leader.objects.filter(is_published=True)[:4],
        },
    )


def page(request, page_id):
    template = PAGE_TEMPLATES.get(page_id)
    if not template:
        raise Http404('Page not found')
    return render(request, template, _page_context(page_id))


def leader_detail(request, slug):
    leader = get_object_or_404(Leader, slug=slug, is_published=True)
    return render(
        request,
        'website/pages/leader_detail.html',
        {'current_page': 'leader', 'leader': leader},
    )


def news_list(request):
    articles = NewsArticle.objects.filter(is_published=True)
    return render(
        request,
        'website/news/list.html',
        {
            'current_page': 'news',
            'articles': articles,
            'recent_articles': articles[:3],
        },
    )


def news_detail(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    return render(
        request,
        'website/news/detail.html',
        {'current_page': 'news_detail', 'article': article},
    )
