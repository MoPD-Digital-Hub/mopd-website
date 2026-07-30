from urllib.parse import urlparse

from django.conf import settings

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
