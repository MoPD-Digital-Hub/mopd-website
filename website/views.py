from django.http import Http404
from django.shortcuts import get_object_or_404, render

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


def home(request):
    carousel_slides = CarouselSlide.objects.filter(is_active=True)
    featured_articles = NewsArticle.objects.filter(is_published=True, is_featured_home=True)[:3]
    if featured_articles.count() < 1:
        featured_articles = NewsArticle.objects.filter(is_published=True)[:3]
    leaders = Leader.objects.filter(is_published=True)[:4]
    return render(
        request,
        'website/pages/home.html',
        {
            'current_page': 'home',
            'carousel_slides': carousel_slides,
            'featured_articles': featured_articles,
            'leaders': leaders,
        },
    )


def page(request, page_id):
    template = PAGE_TEMPLATES.get(page_id)
    if not template:
        raise Http404('Page not found')
    ctx = {'current_page': page_id.replace('-', '_'), 'page_id': page_id}
    if page_id == 'leadership':
        ctx['leaders'] = Leader.objects.filter(is_published=True)
        ctx['current_page'] = 'leadership'
    elif page_id == 'gallery':
        ctx['albums'] = GalleryAlbum.objects.filter(is_published=True).prefetch_related('images')
        ctx['current_page'] = 'gallery'
    elif page_id == 'climate-documents':
        ctx['documents'] = Document.objects.filter(is_published=True, doc_type=Document.DocType.CLIMATE)
        ctx['current_page'] = 'climate_docs'
    elif page_id == 'statistics-documents':
        ctx['documents'] = Document.objects.filter(is_published=True, doc_type=Document.DocType.STATISTICS)
        ctx['current_page'] = 'stats'
    elif page_id == 'about-climate':
        ctx['current_page'] = 'climate'
    elif page_id == 'green-technology':
        ctx['current_page'] = 'green_tech'
    elif page_id == 'press-release':
        ctx['current_page'] = 'press'
    elif page_id == 'development-planning':
        ctx['current_page'] = 'devplan'
    return render(request, template, ctx)


def leader_detail(request, slug):
    leader = get_object_or_404(Leader, slug=slug, is_published=True)
    return render(
        request,
        'website/pages/leader_detail.html',
        {'current_page': 'leader', 'leader': leader},
    )


def news_list(request):
    articles = NewsArticle.objects.filter(is_published=True)
    recent_articles = articles[:3]
    return render(
        request,
        'website/news/list.html',
        {
            'current_page': 'news',
            'articles': articles,
            'recent_articles': recent_articles,
        },
    )


def news_detail(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    return render(
        request,
        'website/news/detail.html',
        {'current_page': 'news_detail', 'article': article},
    )
