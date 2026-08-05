"""Helpers for recording and summarizing public site visits."""

from __future__ import annotations

import re
import secrets
from datetime import timedelta
from urllib.parse import urlparse

from django.db.models import Count, Max, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import NewsArticle, NewsComment, NewsletterSubscriber, PageVisit

VISITOR_COOKIE = 'mopd_vid'
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

_SKIP_PREFIXES = (
    '/mopdadmin',
    '/static/',
    '/media/',
    '/captcha/',
    '/webhooks/',
    '/favicon',
    '/robots.txt',
    '/sitemap.xml',
    '/feed/',
)

_BOT_RE = re.compile(
    r'bot|crawl|spider|slurp|facebookexternalhit|preview|wget|curl|python-requests|httpclient',
    re.I,
)
_MOBILE_RE = re.compile(r'Mobile|Android|iPhone|iPod|webOS|BlackBerry|IEMobile', re.I)
_TABLET_RE = re.compile(r'iPad|Tablet|Kindle|Silk', re.I)


def should_track_request(request) -> bool:
    if request.method not in ('GET', 'HEAD'):
        return False
    path = request.path or '/'
    if any(path.startswith(prefix) for prefix in _SKIP_PREFIXES):
        return False
    if path.endswith((
        '.js', '.css', '.map', '.ico', '.png', '.jpg', '.jpeg',
        '.webp', '.svg', '.woff', '.woff2', '.gif',
    )):
        return False
    return True


def client_ip(request) -> str | None:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip() or None
    return request.META.get('REMOTE_ADDR') or None


def detect_device(user_agent: str) -> str:
    if not user_agent:
        return PageVisit.DEVICE_OTHER
    if _BOT_RE.search(user_agent):
        return PageVisit.DEVICE_BOT
    if _TABLET_RE.search(user_agent):
        return PageVisit.DEVICE_TABLET
    if _MOBILE_RE.search(user_agent):
        return PageVisit.DEVICE_MOBILE
    return PageVisit.DEVICE_DESKTOP


def get_or_create_visitor_key(request) -> tuple[str, bool]:
    existing = (request.COOKIES.get(VISITOR_COOKIE) or '').strip()
    if existing and 8 <= len(existing) <= 64:
        return existing, False
    return secrets.token_urlsafe(24), True


def referrer_host(referrer: str) -> str:
    if not referrer:
        return ''
    try:
        host = urlparse(referrer).netloc.lower()
        if host.startswith('www.'):
            host = host[4:]
        return host[:200]
    except Exception:
        return ''


def record_page_visit(request, status_code: int = 200, *, visitor_key: str) -> PageVisit | None:
    if not should_track_request(request):
        return None
    if status_code >= 500:
        return None

    user_agent = (request.META.get('HTTP_USER_AGENT') or '')[:400]
    referrer = (request.META.get('HTTP_REFERER') or '')[:500]
    path = (request.path or '/')[:500]
    query = (request.META.get('QUERY_STRING') or '')[:500]
    language = getattr(request, 'LANGUAGE_CODE', '') or ''
    session_key = ''
    if hasattr(request, 'session'):
        session_key = request.session.session_key or ''

    return PageVisit.objects.create(
        path=path,
        query_string=query,
        ip_address=client_ip(request),
        visitor_key=visitor_key[:64],
        session_key=session_key[:40],
        user_agent=user_agent,
        device_type=detect_device(user_agent),
        referrer=referrer,
        referrer_host=referrer_host(referrer),
        language=language[:16],
        status_code=status_code,
    )


def _day_bounds(days: int):
    now = timezone.now()
    start = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return start, now


def build_analytics_summary(*, include_bots: bool = False) -> dict:
    qs = PageVisit.objects.all()
    if not include_bots:
        qs = qs.exclude(device_type=PageVisit.DEVICE_BOT)

    today_start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start, _ = _day_bounds(7)
    month_start, _ = _day_bounds(30)

    today_qs = qs.filter(created_at__gte=today_start)
    week_qs = qs.filter(created_at__gte=week_start)
    month_qs = qs.filter(created_at__gte=month_start)

    def pack(filtered):
        return {
            'impressions': filtered.count(),
            'visitors': filtered.values('visitor_key').distinct().count(),
        }

    daily_rows = list(
        week_qs.annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(
            impressions=Count('id'),
            visitors=Count('visitor_key', distinct=True),
        )
        .order_by('day')
    )
    max_impressions = max((row['impressions'] for row in daily_rows), default=1)

    top_pages = list(
        month_qs.values('path')
        .annotate(views=Count('id'), visitors=Count('visitor_key', distinct=True))
        .order_by('-views')[:12]
    )

    devices = list(
        month_qs.values('device_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    referrers = list(
        month_qs.exclude(referrer_host='')
        .values('referrer_host')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    recent_visits = list(qs[:40])

    top_ips = list(
        month_qs.exclude(ip_address=None)
        .values('ip_address')
        .annotate(
            views=Count('id'),
            visitors=Count('visitor_key', distinct=True),
            last_seen=Max('created_at'),
        )
        .order_by('-views')[:15]
    )
    enriched_ips = []
    for row in top_ips:
        last = (
            month_qs.filter(ip_address=row['ip_address'])
            .order_by('-created_at')
            .values_list('path', 'user_agent', 'device_type')
            .first()
        )
        ua = last[1] if last else ''
        enriched_ips.append({
            'ip_address': row['ip_address'],
            'views': row['views'],
            'visitors': row['visitors'],
            'last_seen': row['last_seen'],
            'last_path': last[0] if last else '',
            'device_type': last[2] if last else '',
            'user_agent': (ua[:90] + '…') if ua and len(ua) > 90 else ua,
        })

    engagement = {
        'news_articles': NewsArticle.objects.filter(is_published=True).count(),
        'total_likes': NewsArticle.objects.aggregate(total=Sum('like_count'))['total'] or 0,
        'comments': NewsComment.objects.filter(is_approved=True).count(),
        'newsletter': NewsletterSubscriber.objects.count(),
    }

    return {
        'today': pack(today_qs),
        'week': pack(week_qs),
        'month': pack(month_qs),
        'all_time': pack(qs),
        'daily': [
            {
                **row,
                'bar': int(round((row['impressions'] / max_impressions) * 100)) if max_impressions else 0,
            }
            for row in daily_rows
        ],
        'top_pages': top_pages,
        'devices': devices,
        'referrers': referrers,
        'recent_visits': recent_visits,
        'top_visitors': enriched_ips,
        'engagement': engagement,
        'include_bots': include_bots,
    }
