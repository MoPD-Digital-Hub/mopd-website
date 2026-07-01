"""Download remote MoPD assets and rewrite URLs to local /media/ paths."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)

MOPD_HOSTS = frozenset({'mopd.gov.et', 'www.mopd.gov.et'})
URL_PATTERN = re.compile(r'https?://[^\s\)<>"\'\]]+', re.IGNORECASE)
PAREN_URL_PATTERN = re.compile(r'\s*\(https?://[^)]+\)', re.IGNORECASE)
DOWNLOADABLE_SUFFIXES = (
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
)


def _media_web_path(relative: str) -> str:
    return f'/{settings.MEDIA_URL.rstrip("/")}/{relative.lstrip("/")}'


def _site_hosts() -> set[str]:
    hosts = {'127.0.0.1', 'localhost'}
    site_host = urlparse(getattr(settings, 'SITE_URL', '') or '').netloc
    if site_host:
        hosts.add(site_host.lower())
    return hosts


def is_mopd_url(url: str) -> bool:
    return urlparse(url).netloc.lower() in MOPD_HOSTS


def is_local_url(url: str) -> bool:
    parsed = urlparse(url)
    if not parsed.netloc:
        return url.startswith('/media/') or url.startswith('media/')
    return parsed.netloc.lower() in _site_hosts()


def _safe_filename(url: str) -> str:
    path = unquote(urlparse(url).path)
    name = os.path.basename(path) or 'download'
    name = re.sub(r'[^\w.\-]+', '_', name)
    return name[:180] or 'download'


def _subdir_for_url(url: str) -> str:
    path = urlparse(url).path.lower()
    if '/climate-documents/' in path:
        return 'documents/climate'
    if '/data-documents/' in path:
        return 'documents/statistics'
    if '/ten-year-document/' in path:
        return 'ten-year-document'
    if '/media/photos/' in path or path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
        return 'imports/images'
    if path.endswith('.pdf'):
        return 'documents/misc'
    return 'imports'


def download_remote_file(url: str, cache: dict[str, str] | None = None) -> str | None:
    """Download a remote file into MEDIA_ROOT; return a /media/... web path."""
    if not url or is_local_url(url):
        return url if is_local_url(url) else None

    cache = cache if cache is not None else {}
    if url in cache:
        return cache[url]

    subdir = _subdir_for_url(url)
    filename = _safe_filename(url)
    dest_dir = Path(settings.MEDIA_ROOT) / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename

    if not dest_path.is_file() or dest_path.stat().st_size == 0:
        try:
            request = Request(url, headers={'User-Agent': 'Mozilla/5.0 MoPD-Localizer/1.0'})
            with urlopen(request, timeout=60) as response:
                dest_path.write_bytes(response.read())
        except Exception as exc:
            logger.warning('Failed to download %s: %s', url, exc)
            return None

    local_url = _media_web_path(f'{subdir}/{filename}')
    cache[url] = local_url
    return local_url


def should_download_url(url: str) -> bool:
    if is_mopd_url(url):
        return True
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in DOWNLOADABLE_SUFFIXES)


def localize_url(url: str, cache: dict[str, str] | None = None) -> str | None:
    """Return a local /media/ path for downloadable remote URLs, else None."""
    if not url:
        return None
    if is_local_url(url):
        return url
    if should_download_url(url):
        return download_remote_file(url, cache)
    return None


def strip_external_urls(text: str) -> str:
    """Remove external http(s) links; keep only local /media/ and site URLs."""
    if not text:
        return ''

    def _replace(match: re.Match[str]) -> str:
        url = match.group(0).rstrip('.,;:)')
        if is_local_url(url):
            return match.group(0)
        return ''

    text = URL_PATTERN.sub(_replace, text)
    text = PAREN_URL_PATTERN.sub('', text)
    return re.sub(r'\s{2,}', ' ', text).strip()


def localize_text(text: str, cache: dict[str, str] | None = None) -> str:
    """Rewrite mopd.gov.et (and other downloadable) URLs to local /media/ paths."""
    if not text:
        return ''

    cache = cache if cache is not None else {}

    def _replace(match: re.Match[str]) -> str:
        raw = match.group(0)
        url = raw.rstrip('.,;:)')
        trailing = raw[len(url):]
        if is_local_url(url):
            return raw
        local = localize_url(url, cache)
        if local:
            return local + trailing
        return ''

    text = URL_PATTERN.sub(_replace, text)
    text = PAREN_URL_PATTERN.sub('', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def localize_article_fields(article, cache: dict[str, str] | None = None) -> bool:
    """Localize text fields on a NewsArticle instance. Returns True if changed."""
    cache = cache if cache is not None else {}
    changed = False
    for field in ('title_en', 'title_am', 'excerpt_en', 'excerpt_am', 'body_en', 'body_am'):
        value = getattr(article, field, '') or ''
        localized = localize_text(value, cache)
        if localized != value:
            setattr(article, field, localized)
            changed = True
    return changed


def localize_file_url_field(url: str, cache: dict[str, str] | None = None) -> str:
    """Localize a single file URL field (documents, PDFs, etc.)."""
    if not url:
        return url
    if is_local_url(url):
        return url
    local = localize_url(url, cache)
    return local or url
