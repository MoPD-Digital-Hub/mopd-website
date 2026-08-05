from urllib.parse import urlparse

from django.conf import settings

from .analytics import (
    VISITOR_COOKIE,
    VISITOR_COOKIE_MAX_AGE,
    get_or_create_visitor_key,
    record_page_visit,
    should_track_request,
)

TUNNEL_ORIGIN_SUFFIXES = (
    '.trycloudflare.com',
    '.loca.lt',
    '.ngrok-free.app',
    '.ngrok.io',
)


def _trust_origin(origin: str) -> None:
    if origin and origin not in settings.CSRF_TRUSTED_ORIGINS:
        settings.CSRF_TRUSTED_ORIGINS.append(origin)


class DevTunnelTrustedOriginMiddleware:
    """In DEBUG, trust common tunnel hostnames for CSRF origin checks."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            origin = request.META.get('HTTP_ORIGIN') or ''
            if any(origin.endswith(suffix) for suffix in TUNNEL_ORIGIN_SUFFIXES):
                _trust_origin(origin)

            referer = request.META.get('HTTP_REFERER') or ''
            if referer:
                parsed = urlparse(referer)
                if parsed.scheme and parsed.netloc:
                    ref_origin = f'{parsed.scheme}://{parsed.netloc}'
                    if any(ref_origin.endswith(suffix) for suffix in TUNNEL_ORIGIN_SUFFIXES):
                        _trust_origin(ref_origin)

        return self.get_response(request)


class PageVisitMiddleware:
    """Record public page impressions for the admin analytics dashboard."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        track = should_track_request(request)
        visitor_key = None
        set_cookie = False
        if track:
            visitor_key, set_cookie = get_or_create_visitor_key(request)

        response = self.get_response(request)

        if track and visitor_key:
            try:
                record_page_visit(request, response.status_code, visitor_key=visitor_key)
            except Exception:
                # Never break page responses because analytics failed.
                pass
            if set_cookie and response.status_code < 500:
                response.set_cookie(
                    VISITOR_COOKIE,
                    visitor_key,
                    max_age=VISITOR_COOKIE_MAX_AGE,
                    samesite='Lax',
                    httponly=True,
                )
        return response
