from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .climate_documents import climate_doc_sections
from .forms import ContactForm, NewsletterForm
from .models import (
    CarouselSlide,
    ContactSubmission,
    Department,
    Document,
    GalleryAlbum,
    Leader,
    NewsArticle,
    NewsletterSubscriber,
    ProcurementNotice,
    SiteSettings,
    Vacancy,
)
from .search import run_site_search

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
    'procurement': 'website/pages/procurement.html',
    'vacancies': 'website/pages/vacancies.html',
    'privacy': 'website/pages/privacy.html',
    'accessibility': 'website/pages/accessibility.html',
    'faq': 'website/pages/faq.html',
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
    'procurement': 'procurement',
    'vacancies': 'vacancies',
    'privacy': 'privacy',
    'accessibility': 'accessibility',
    'faq': 'faq',
}

NEWS_PER_PAGE = 12
CONTACT_RATE_LIMIT = 5
CONTACT_RATE_WINDOW = 3600


def _page_context(page_id):
    ctx = {'current_page': PAGE_NAV_IDS.get(page_id, page_id.replace('-', '_')), 'page_id': page_id}
    if page_id == 'leadership':
        ctx['leaders'] = Leader.objects.filter(is_published=True)
    elif page_id == 'about':
        ctx['departments'] = Department.objects.filter(is_published=True, parent__isnull=True).prefetch_related(
            'children'
        )
    elif page_id == 'gallery':
        ctx['albums'] = GalleryAlbum.objects.filter(is_published=True).prefetch_related('images')
    elif page_id == 'climate-documents':
        climate_docs = Document.objects.filter(
            is_published=True,
            doc_type=Document.DocType.CLIMATE,
        ).order_by('sort_order', 'id')
        ctx['climate_doc_sections'] = climate_doc_sections(climate_docs)
        ctx['document_filters'] = [
            {'code': section['code'], 'label': section['label'], 'count': len(section['documents'])}
            for section in ctx['climate_doc_sections']
        ]
        ctx['document_count'] = sum(filter_item['count'] for filter_item in ctx['document_filters'])
    elif page_id == 'statistics-documents':
        documents = Document.objects.filter(is_published=True, doc_type=Document.DocType.STATISTICS)
        ctx['documents'] = documents
        ctx['document_filters'] = [
            {'code': 'statistics', 'label': 'Statistics', 'count': documents.count()},
        ]
        ctx['document_count'] = documents.count()
    elif page_id == 'procurement':
        today = timezone.localdate()
        ctx['notices'] = ProcurementNotice.objects.filter(is_published=True).filter(
            Q(closing_date__isnull=True) | Q(closing_date__gte=today)
        )
    elif page_id == 'vacancies':
        today = timezone.localdate()
        ctx['vacancies'] = Vacancy.objects.filter(is_published=True).filter(
            Q(deadline__isnull=True) | Q(deadline__gte=today)
        )
    return ctx


def _contact_rate_limited(request):
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = f'contact_rate:{ip}'
    count = cache.get(key, 0)
    if count >= CONTACT_RATE_LIMIT:
        return True
    cache.set(key, count + 1, CONTACT_RATE_WINDOW)
    return False


def _flash(request, key, en_msg, am_msg):
    lang = request.COOKIES.get('mopd_lang', request.GET.get('lang', 'en'))
    messages.success(request, am_msg if lang == 'am' else en_msg)


def home(request):
    featured_articles = NewsArticle.objects.filter(
        is_published=True,
        is_featured_home=True,
        article_type='news',
    )[:3]
    if not featured_articles.exists():
        featured_articles = NewsArticle.objects.filter(is_published=True, article_type='news')[:3]
    return render(
        request,
        'website/pages/home.html',
        {
            'current_page': 'home',
            'carousel_slides': CarouselSlide.objects.filter(is_active=True),
            'featured_articles': featured_articles,
            'leaders': Leader.objects.filter(is_published=True)[:4],
            'newsletter_form': NewsletterForm(),
        },
    )


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST':
        if _contact_rate_limited(request):
            messages.error(
                request,
                'Too many messages sent recently. Please try again later.',
            )
            return redirect('contact')
        if form.is_valid():
            submission = form.save()
            _notify_contact_submission(submission)
            _flash(
                request,
                'success',
                'Your message has been sent. We will get back to you soon.',
                'መልዕክትዎ ተልኳል። በተቻለ ፍጥነት እንመልስልዎታለን።',
            )
            return redirect('contact')
        messages.error(
            request,
            'Please correct the errors below.',
        )

    return render(
        request,
        'website/pages/contact.html',
        {
            'current_page': 'contact',
            'page_id': 'contact',
            'form': form,
        },
    )


@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    redirect_to = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    if form.is_valid():
        email = form.cleaned_data['email']
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'source': request.POST.get('source', 'homepage')},
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=['is_active'])
        _flash(
            request,
            'newsletter',
            'Thank you for subscribing to our newsletter.',
            'ለዜና መጽሔታችን ለመመዝገብ እናመሰግናለን።',
        )
    else:
        messages.error(request, 'Please enter a valid email address.')
    return redirect(redirect_to)


def _notify_contact_submission(submission):
    from django.conf import settings

    recipient = getattr(settings, 'CONTACT_FORM_NOTIFY_EMAIL', '') or SiteSettings.load().email
    if not recipient:
        return

    subject = f'[MoPD Contact] {submission.subject}'
    body = (
        f'Name: {submission.name}\n'
        f'Email: {submission.email}\n'
        f'Phone: {submission.phone or "—"}\n'
        f'Subject: {submission.subject}\n\n'
        f'{submission.details}\n'
    )
    send_mail(
        subject,
        body,
        getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@mopd.gov.et'),
        [recipient],
        fail_silently=False,
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


def _paginated_articles(request, queryset):
    paginator = Paginator(queryset, NEWS_PER_PAGE)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    return page_obj


def news_list(request):
    articles_qs = NewsArticle.objects.filter(is_published=True, article_type='news')
    page_obj = _paginated_articles(request, articles_qs)
    return render(
        request,
        'website/news/list.html',
        {
            'current_page': 'news',
            'page_obj': page_obj,
            'articles': page_obj.object_list,
            'recent_articles': articles_qs[:3],
        },
    )


def press_list(request):
    articles_qs = NewsArticle.objects.filter(is_published=True, article_type='press_release')
    page_obj = _paginated_articles(request, articles_qs)
    return render(
        request,
        'website/pages/press-release.html',
        {
            'current_page': 'press',
            'page_id': 'press',
            'page_obj': page_obj,
            'articles': page_obj.object_list,
        },
    )


def news_detail(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    return render(
        request,
        'website/news/detail.html',
        {'current_page': 'news_detail', 'article': article},
    )


def site_search(request):
    query = request.GET.get('q', '')
    result_type = request.GET.get('type', 'all')
    results = run_site_search(query, result_type=result_type)
    result_keys = ['news', 'documents', 'pages', 'procurement', 'vacancies', 'departments']
    total = sum(len(results[key]) for key in result_keys)
    return render(
        request,
        'website/pages/search.html',
        {
            'current_page': 'search',
            'page_id': 'search',
            'query': results['query'],
            'results': results,
            'total': total,
        },
    )


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        'Sitemap: ' + request.build_absolute_uri('/sitemap.xml'),
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
