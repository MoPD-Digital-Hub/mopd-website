from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import F, Prefetch, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import hmac
import json
import logging
from .forms import ContactForm, NewsCommentEditForm, NewsCommentForm, NewsletterForm
from .models import (
    CarouselSlide,
    ContactSubmission,
    Department,
    Document,
    GalleryAlbum,
    Leader,
    NewsArticle,
    NewsComment,
    NewsletterSubscriber,
    ProcurementNotice,
    SiteSettings,
    Vacancy,
)
from .search import run_site_search

COMMENT_OWNER_COOKIE_PREFIX = 'mopd_cown_'
COMMENT_OWNER_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


def _comment_owner_cookie_name(comment_id):
    return f'{COMMENT_OWNER_COOKIE_PREFIX}{comment_id}'


def _owns_comment(request, comment):
    if not comment.owner_token:
        return False
    cookie = request.COOKIES.get(_comment_owner_cookie_name(comment.pk), '')
    if not cookie or len(cookie) != len(comment.owner_token):
        return False
    return hmac.compare_digest(cookie, comment.owner_token)


def _set_comment_owner_cookie(response, comment):
    response.set_cookie(
        _comment_owner_cookie_name(comment.pk),
        comment.owner_token,
        max_age=COMMENT_OWNER_COOKIE_MAX_AGE,
        samesite='Lax',
        httponly=True,
    )
    return response


def _clear_comment_owner_cookie(response, comment_id):
    response.delete_cookie(_comment_owner_cookie_name(comment_id), samesite='Lax')
    return response


def _collect_owner_flags(request, top_comments):
    owned = set()
    editable = set()
    for comment in top_comments:
        candidates = [comment, *list(comment.replies.all())]
        for item in candidates:
            if _owns_comment(request, item):
                owned.add(item.pk)
                if item.can_edit():
                    editable.add(item.pk)
    return owned, editable


PAGE_TEMPLATES = {
    'about': 'website/pages/about.html',
    'contact': 'website/pages/contact.html',
    'leadership': 'website/pages/leadership.html',
    'gallery': 'website/pages/gallery.html',
    'press-release': 'website/pages/press-release.html',
    'about-climate': 'website/pages/about-climate.html',
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
    top_comments = (
        article.comments.filter(is_approved=True, parent__isnull=True)
        .prefetch_related(
            Prefetch(
                'replies',
                queryset=NewsComment.objects.filter(is_approved=True).order_by('created_at'),
            )
        )
        .order_by('created_at')
    )
    related_articles = (
        NewsArticle.objects.filter(
            is_published=True,
            article_type=article.article_type or 'news',
            category=article.category,
        )
        .exclude(pk=article.pk)
        .order_by('-published_at', '-created_at')[:4]
    )

    liked = request.COOKIES.get(f'mopd_liked_{article.pk}') == '1'
    comment_form = NewsCommentForm()

    if request.method == 'POST' and request.POST.get('form_type') == 'comment':
        comment_form = NewsCommentForm(request.POST)
        cache_key = f'news_comment_rate:{request.META.get("REMOTE_ADDR", "unknown")}:{article.pk}'
        if cache.get(cache_key):
            messages.warning(request, 'Please wait a moment before posting another comment.')
        elif comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.email = ''
            comment.is_approved = True
            parent_id = comment_form.cleaned_data.get('parent_id')
            if parent_id:
                parent = article.comments.filter(
                    pk=parent_id,
                    is_approved=True,
                    parent__isnull=True,
                ).first()
                if parent:
                    comment.parent = parent
            comment.save()
            cache.set(cache_key, True, 20)
            messages.success(request, 'Your comment was posted.')
            response = redirect(f'{request.path}#comment-{comment.pk}')
            return _set_comment_owner_cookie(response, comment)
        else:
            for errs in comment_form.errors.values():
                for err in errs:
                    messages.error(request, err)
                    break
                break
            else:
                messages.error(request, 'Please correct the errors in the comment form.')

    liked_comments = set()
    for key, value in request.COOKIES.items():
        if key.startswith('mopd_cliked_') and value == '1':
            try:
                liked_comments.add(int(key.replace('mopd_cliked_', '')))
            except ValueError:
                pass

    owned_comments, editable_comments = _collect_owner_flags(request, top_comments)

    return render(
        request,
        'website/news/detail.html',
        {
            'current_page': 'news_detail',
            'article': article,
            'comments': top_comments,
            'related_articles': related_articles,
            'comment_form': comment_form,
            'liked': liked,
            'liked_comments': liked_comments,
            'owned_comments': owned_comments,
            'editable_comments': editable_comments,
            'comment_edit_minutes': int(NewsComment.EDIT_WINDOW.total_seconds() // 60),
        },
    )


@require_POST
def news_like(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    cookie_name = f'mopd_liked_{article.pk}'
    if request.COOKIES.get(cookie_name) == '1':
        return JsonResponse({
            'ok': True,
            'liked': True,
            'like_count': article.like_count,
            'already': True,
        })

    NewsArticle.objects.filter(pk=article.pk).update(like_count=F('like_count') + 1)
    article.refresh_from_db(fields=['like_count'])
    response = JsonResponse({
        'ok': True,
        'liked': True,
        'like_count': article.like_count,
        'already': False,
    })
    response.set_cookie(
        cookie_name,
        '1',
        max_age=60 * 60 * 24 * 365,
        samesite='Lax',
        httponly=False,
    )
    return response


@require_POST
def news_comment_like(request, slug, comment_id):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    comment = get_object_or_404(
        NewsComment,
        pk=comment_id,
        article=article,
        is_approved=True,
    )
    cookie_name = f'mopd_cliked_{comment.pk}'
    if request.COOKIES.get(cookie_name) == '1':
        return JsonResponse({
            'ok': True,
            'liked': True,
            'like_count': comment.like_count,
            'already': True,
        })

    NewsComment.objects.filter(pk=comment.pk).update(like_count=F('like_count') + 1)
    comment.refresh_from_db(fields=['like_count'])
    response = JsonResponse({
        'ok': True,
        'liked': True,
        'like_count': comment.like_count,
        'already': False,
    })
    response.set_cookie(
        cookie_name,
        '1',
        max_age=60 * 60 * 24 * 365,
        samesite='Lax',
        httponly=False,
    )
    return response


@require_POST
def news_comment_edit(request, slug, comment_id):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    comment = get_object_or_404(NewsComment, pk=comment_id, article=article, is_approved=True)
    detail_url = reverse('news_detail', args=[article.slug])
    if not _owns_comment(request, comment):
        messages.error(request, 'You can only edit your own comment from this browser.')
        return redirect(f'{detail_url}#comments')
    if not comment.can_edit():
        messages.error(
            request,
            f'Editing is only allowed within {int(NewsComment.EDIT_WINDOW.total_seconds() // 60)} minutes of posting.',
        )
        return redirect(f'{detail_url}#comment-{comment.pk}')

    form = NewsCommentEditForm(request.POST)
    if form.is_valid():
        comment.body = form.cleaned_data['body']
        comment.save(update_fields=['body', 'updated_at'])
        messages.success(request, 'Your comment was updated.')
    else:
        for errs in form.errors.values():
            for err in errs:
                messages.error(request, err)
                break
            break
    return redirect(f'{detail_url}#comment-{comment.pk}')


@require_POST
def news_comment_delete(request, slug, comment_id):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    comment = get_object_or_404(NewsComment, pk=comment_id, article=article)
    detail_url = reverse('news_detail', args=[article.slug])
    is_staff = request.user.is_authenticated and request.user.is_staff
    was_owner = _owns_comment(request, comment)
    if not is_staff and not was_owner:
        messages.error(request, 'You can only delete your own comment from this browser.')
        return redirect(f'{detail_url}#comments')

    comment_pk = comment.pk
    comment.delete()
    if is_staff and not was_owner:
        messages.success(request, 'Comment deleted by admin.')
    else:
        messages.success(request, 'Your comment was deleted.')
    response = redirect(f'{detail_url}#comments')
    return _clear_comment_owner_cookie(response, comment_pk)


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


@csrf_exempt
@require_POST
def telegram_webhook(request, secret):
    """
    Receive Telegram channel_post updates instantly when a new channel message is posted.
    URL includes a shared secret; Telegram also sends X-Telegram-Bot-Api-Secret-Token.
    """
    from django.http import JsonResponse

    from website.telegram_channel_sync import process_update, webhook_secret

    expected = webhook_secret()
    if not expected or secret != expected:
        return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)

    header_secret = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
    if header_secret and header_secret != expected:
        return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'invalid json'}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({'ok': False, 'error': 'invalid payload'}, status=400)

    status, detail = process_update(payload)
    logging.getLogger(__name__).info('Telegram webhook %s: %s', status, detail)
    # Always 200 so Telegram does not retry forever on skipped/ignored posts.
    return JsonResponse({'ok': True, 'status': status, 'detail': detail})
