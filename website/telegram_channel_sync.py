"""Import channel posts from Telegram into unpublished NewsArticle drafts."""

from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime, timezone as dt_timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify

from website.models import NewsArticle
from website.telegram_news import telegram_configured

logger = logging.getLogger(__name__)

TELEGRAM_API = 'https://api.telegram.org/bot{token}/{method}'
TITLE_MAX = 120
OFFSET_FILENAME = '.telegram_channel_update_offset'


class SyncResult:
    def __init__(self):
        self.created = 0
        self.skipped = 0
        self.errors = 0
        self.messages: list[str] = []

    def note(self, message: str):
        self.messages.append(message)


def source_channel_id() -> int | None:
    raw = str(getattr(settings, 'TELEGRAM_SOURCE_CHANNEL_ID', '') or '').strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def source_path_for(message_id: int, channel_id: int) -> str:
    return f'tg:pdc:{channel_id}:{message_id}'


def _offset_path() -> Path:
    return Path(settings.MEDIA_ROOT) / OFFSET_FILENAME


def load_update_offset() -> int:
    path = _offset_path()
    if not path.is_file():
        return 0
    try:
        return max(0, int(path.read_text(encoding='utf-8').strip() or '0'))
    except (OSError, ValueError):
        return 0


def save_update_offset(offset: int) -> None:
    path = _offset_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(offset), encoding='utf-8')


def _api_get(method: str, params: dict | None = None) -> dict | None:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return None
    query = urlencode(params or {})
    url = TELEGRAM_API.format(token=token, method=method)
    if query:
        url = f'{url}?{query}'
    request = Request(url, headers={'User-Agent': 'MoPD-TelegramSync/1.0'}, method='GET')
    try:
        with urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning('Telegram API %s failed: %s', method, exc)
        return None
    if not result.get('ok'):
        logger.warning('Telegram API %s error: %s', method, result.get('description', result))
        return None
    return result


def fetch_channel_updates(*, offset: int = 0, limit: int = 100) -> list[dict]:
    """Poll Bot API getUpdates for channel_post events."""
    params = {
        'offset': offset,
        'limit': min(100, max(1, limit)),
        'timeout': 0,
        'allowed_updates': json.dumps(['channel_post']),
    }
    result = _api_get('getUpdates', params)
    if not result:
        return []
    return result.get('result') or []


def _message_text(message: dict) -> str:
    text = (message.get('text') or message.get('caption') or '').strip()
    return text


def _title_and_body(text: str) -> tuple[str, str]:
    cleaned = re.sub(r'\r\n?', '\n', (text or '').strip())
    if not cleaned:
        return 'Channel update', ''

    first_line = cleaned.split('\n', 1)[0].strip()
    title = first_line
    if len(title) > TITLE_MAX:
        title = title[: TITLE_MAX - 1].rsplit(' ', 1)[0].rstrip('.,;:') + '…'
    if not title:
        title = cleaned[:TITLE_MAX].strip() or 'Channel update'

    body = cleaned
    return title, body


def _excerpt_from_body(body: str) -> str:
    flat = ' '.join((body or '').split())
    if len(flat) <= 280:
        return flat
    return flat[:279].rsplit(' ', 1)[0] + '…'


def _published_date(message: dict) -> date:
    stamp = message.get('date')
    if isinstance(stamp, int):
        return datetime.fromtimestamp(stamp, tz=dt_timezone.utc).date()
    return date.today()


def _largest_photo_file_id(message: dict) -> str | None:
    photos = message.get('photo') or []
    if not photos:
        return None
    # Telegram sends sizes ascending; last is largest.
    file_id = photos[-1].get('file_id')
    return file_id or None


def download_telegram_file(file_id: str) -> tuple[bytes, str] | None:
    meta = _api_get('getFile', {'file_id': file_id})
    if not meta:
        return None
    file_path = (meta.get('result') or {}).get('file_path') or ''
    if not file_path:
        return None
    token = settings.TELEGRAM_BOT_TOKEN
    url = f'https://api.telegram.org/file/bot{token}/{file_path}'
    request = Request(url, headers={'User-Agent': 'MoPD-TelegramSync/1.0'}, method='GET')
    try:
        with urlopen(request, timeout=60) as response:
            content = response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        logger.warning('Telegram file download failed: %s', exc)
        return None
    name = Path(file_path).name or 'telegram-photo.jpg'
    if not Path(name).suffix:
        name = f'{name}.jpg'
    return content, name


def _unique_slug(base: str, message_id: int) -> str:
    root = slugify(base)[:140] or f'pdc-channel-{message_id}'
    candidate = f'{root}-{message_id}'
    if not NewsArticle.objects.filter(slug=candidate).exists():
        return candidate
    n = 2
    while NewsArticle.objects.filter(slug=f'{candidate}-{n}').exists():
        n += 1
    return f'{candidate}-{n}'


def create_draft_from_channel_post(
    message: dict,
    *,
    channel_id: int,
    dry_run: bool = False,
) -> tuple[str, NewsArticle | None]:
    """
    Create an unpublished NewsArticle from a channel_post message.
    Returns (status, article) where status is created|skipped|error.
    """
    message_id = message.get('message_id')
    if not isinstance(message_id, int):
        return 'error', None

    if NewsArticle.objects.filter(telegram_message_id=message_id).exists():
        return 'skipped', None

    path = source_path_for(message_id, channel_id)
    if NewsArticle.objects.filter(source_path=path).exists():
        return 'skipped', None

    text = _message_text(message)
    photo_id = _largest_photo_file_id(message)
    if not text and not photo_id:
        return 'skipped', None

    title, body = _title_and_body(text)
    if not body and photo_id:
        body = title

    if dry_run:
        return 'created', None

    article = NewsArticle(
        source_path=path,
        telegram_message_id=message_id,
        slug=_unique_slug(title, message_id),
        category='others',
        tag='News',
        title=title,
        title_en=title,
        excerpt=_excerpt_from_body(body),
        excerpt_en=_excerpt_from_body(body),
        body=body,
        body_en=body,
        published_at=_published_date(message),
        is_published=False,
        is_featured_home=False,
        article_type='news',
    )

    if photo_id:
        downloaded = download_telegram_file(photo_id)
        if downloaded:
            content, filename = downloaded
            article.image.save(filename, ContentFile(content), save=False)

    article.save()
    return 'created', article


def process_update(update: dict, *, dry_run: bool = False) -> tuple[str, str]:
    """
    Handle one Telegram update payload (from getUpdates or webhook).
    Returns (status, detail) where status is created|skipped|ignored|error.
    """
    channel_id = source_channel_id()
    if channel_id is None:
        return 'error', 'TELEGRAM_SOURCE_CHANNEL_ID is missing or invalid.'

    message = update.get('channel_post')
    if not isinstance(message, dict):
        return 'ignored', 'not a channel_post'

    chat = message.get('chat') or {}
    if chat.get('id') != channel_id:
        return 'ignored', f'chat_id={chat.get("id")}'

    try:
        status, article = create_draft_from_channel_post(
            message,
            channel_id=channel_id,
            dry_run=dry_run,
        )
    except Exception as exc:
        logger.exception('Failed importing Telegram message %s', message.get('message_id'))
        return 'error', str(exc)

    if status == 'created':
        label = article.slug if article else message.get('message_id')
        return 'created', f'{"would create" if dry_run else "created"} draft {label}'
    if status == 'skipped':
        return 'skipped', f'skipped message_id={message.get("message_id")}'
    return 'error', f'error message_id={message.get("message_id")}'


def webhook_secret() -> str:
    return str(getattr(settings, 'TELEGRAM_WEBHOOK_SECRET', '') or '').strip()


def webhook_public_url() -> str:
    secret = webhook_secret()
    if not secret:
        return ''
    base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
    return f'{base}/webhooks/telegram/{secret}/'


def _api_post(method: str, payload: dict | None = None) -> dict | None:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return None
    url = TELEGRAM_API.format(token=token, method=method)
    data = json.dumps(payload or {}).encode('utf-8')
    request = Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json', 'User-Agent': 'MoPD-TelegramSync/1.0'},
        method='POST',
    )
    try:
        with urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning('Telegram API %s failed: %s', method, exc)
        return None
    if not result.get('ok'):
        logger.warning('Telegram API %s error: %s', method, result.get('description', result))
        return None
    return result


def set_webhook() -> tuple[bool, str]:
    """Point Telegram at this site so new channel posts arrive automatically."""
    if not telegram_configured():
        return False, 'TELEGRAM_BOT_TOKEN is not configured.'
    url = webhook_public_url()
    if not url:
        return False, 'Set TELEGRAM_WEBHOOK_SECRET and SITE_URL first.'
    if not url.startswith('https://'):
        return False, 'Telegram webhooks require HTTPS SITE_URL (e.g. https://site.mopd.gov.et).'

    result = _api_post(
        'setWebhook',
        {
            'url': url,
            'allowed_updates': ['channel_post'],
            'drop_pending_updates': False,
            'secret_token': webhook_secret()[:256],
        },
    )
    if not result:
        return False, 'setWebhook failed — check bot token and SITE_URL reachability.'
    return True, f'Webhook set to {url}'


def delete_webhook() -> tuple[bool, str]:
    if not telegram_configured():
        return False, 'TELEGRAM_BOT_TOKEN is not configured.'
    result = _api_post('deleteWebhook', {'drop_pending_updates': False})
    if not result:
        return False, 'deleteWebhook failed.'
    return True, 'Webhook removed.'


def fetch_channel_updates_long_poll(*, offset: int = 0, limit: int = 100, timeout: int = 25) -> list[dict]:
    params = {
        'offset': offset,
        'limit': min(100, max(1, limit)),
        'timeout': max(0, timeout),
        'allowed_updates': json.dumps(['channel_post']),
    }
    result = _api_get('getUpdates', params)
    if not result:
        return []
    return result.get('result') or []


def watch_telegram_channel(*, stop_after: int | None = None) -> SyncResult:
    """
    Long-poll getUpdates forever (or until stop_after creates).
    Use when webhook cannot be configured; run under systemd/supervisor.
    """
    result = SyncResult()
    if not telegram_configured():
        result.errors += 1
        result.note('TELEGRAM_BOT_TOKEN is not configured.')
        return result
    if source_channel_id() is None:
        result.errors += 1
        result.note('TELEGRAM_SOURCE_CHANNEL_ID is missing or invalid.')
        return result

    # Webhooks and getUpdates cannot be used together.
    delete_webhook()

    offset = load_update_offset()
    created_total = 0
    result.note(f'Watching channel {source_channel_id()} from offset {offset}…')

    while True:
        updates = fetch_channel_updates_long_poll(offset=offset, timeout=25)
        max_update_id = offset - 1 if offset else -1

        for update in updates:
            update_id = update.get('update_id')
            if isinstance(update_id, int):
                max_update_id = max(max_update_id, update_id)

            status, detail = process_update(update)
            result.note(detail)
            if status == 'created':
                result.created += 1
                created_total += 1
            elif status == 'skipped':
                result.skipped += 1
            elif status == 'error':
                result.errors += 1

        if max_update_id >= 0:
            offset = max_update_id + 1
            save_update_offset(offset)

        if stop_after is not None and created_total >= stop_after:
            break

    return result


def sync_telegram_channel(*, dry_run: bool = False, limit: int | None = None) -> SyncResult:
    result = SyncResult()

    if not telegram_configured():
        result.errors += 1
        result.note('TELEGRAM_BOT_TOKEN is not configured.')
        return result

    channel_id = source_channel_id()
    if channel_id is None:
        result.errors += 1
        result.note('TELEGRAM_SOURCE_CHANNEL_ID is missing or invalid.')
        return result

    offset = load_update_offset()
    updates = fetch_channel_updates(offset=offset, limit=100 if limit is None else max(limit, 1))
    if not updates and offset == 0:
        result.note(
            'No channel_post updates received. Confirm the bot is an admin of the source channel.'
        )

    max_update_id = offset - 1 if offset else -1
    processed = 0

    for update in updates:
        update_id = update.get('update_id')
        if isinstance(update_id, int):
            max_update_id = max(max_update_id, update_id)

        message = update.get('channel_post')
        if not isinstance(message, dict):
            continue
        chat = message.get('chat') or {}
        if chat.get('id') != channel_id:
            continue

        if limit is not None and processed >= limit:
            continue

        processed += 1
        status, detail = process_update(update, dry_run=dry_run)
        result.note(detail)
        if status == 'created':
            result.created += 1
        elif status == 'skipped':
            result.skipped += 1
        elif status == 'error':
            result.errors += 1

    if not dry_run and max_update_id >= 0:
        save_update_offset(max_update_id + 1)

    return result
