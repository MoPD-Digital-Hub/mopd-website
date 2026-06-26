"""Send published news articles to Telegram in a clean, professional format."""

from __future__ import annotations

import html
import json
import logging
import mimetypes
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from website.remote_assets import strip_external_urls

logger = logging.getLogger(__name__)

TELEGRAM_API = 'https://api.telegram.org/bot{token}/{method}'
CAPTION_MAX = 1024
MESSAGE_MAX = 4096


def telegram_configured() -> bool:
    return bool(getattr(settings, 'TELEGRAM_BOT_TOKEN', ''))


def telegram_chat_ids() -> list[int | str]:
    ids: list[int | str] = []
    group_id = getattr(settings, 'TELEGRAM_GROUP_ID', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
    if group_id:
        ids.append(int(group_id) if str(group_id).lstrip('-').isdigit() else group_id)
    if chat_id:
        parsed = int(chat_id) if str(chat_id).lstrip('-').isdigit() else chat_id
        if parsed not in ids:
            ids.append(parsed)
    return ids


def _escape(text: str) -> str:
    return html.escape((text or '').strip(), quote=False)


def _truncate(text: str, limit: int) -> str:
    text = ' '.join((text or '').split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(' ', 1)[0] + '…'


def article_public_url(article) -> str:
    path = reverse('news_detail', kwargs={'slug': article.slug})
    base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
    return f'{base}{path}'


def format_article_message(article, *, for_caption: bool = False) -> str:
    title = _escape(strip_external_urls(article.title_en or article.title))
    category = _escape(article.get_category_display())
    tag = _escape(strip_external_urls(getattr(article, 'tag_en', None) or article.tag or 'News'))
    date_str = article.published_at.strftime('%d %B %Y') if article.published_at else ''
    excerpt = _escape(strip_external_urls(article.card_excerpt_en or article.excerpt_en or ''))
    url = article_public_url(article)

    excerpt_limit = 220 if for_caption else 380
    excerpt = _truncate(excerpt, excerpt_limit)

    lines = [
        '<b>Ministry of Planning and Development</b>',
        '<i>News &amp; Media</i>',
        '',
        f'<b>{title}</b>',
        f'<i>{category} · {date_str}</i>',
    ]
    if tag and tag.lower() not in {category.lower(), 'news'}:
        lines.append(f'<i>{tag}</i>')
    if excerpt:
        lines.extend(['', excerpt])
    lines.extend(['', f'<a href="{_escape(url)}">Read full article</a>'])

    message = '\n'.join(lines)
    limit = CAPTION_MAX if for_caption else MESSAGE_MAX
    if len(message) > limit:
        message = format_article_message(article, for_caption=True)
        if len(message) > limit:
            message = _truncate(message.replace('\n', ' '), limit - 50)
            message += f'\n\n<a href="{_escape(url)}">Read full article</a>'
    return message


def _api_request(method: str, payload: dict | None = None, files: dict | None = None) -> dict | None:
    token = settings.TELEGRAM_BOT_TOKEN
    url = TELEGRAM_API.format(token=token, method=method)

    if files:
        boundary = uuid.uuid4().hex
        body_parts: list[bytes] = []

        for key, value in (payload or {}).items():
            body_parts.append(f'--{boundary}\r\n'.encode())
            body_parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
            body_parts.append(f'{value}\r\n'.encode())

        for field_name, file_path in files.items():
            path = Path(file_path)
            mime_type = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
            body_parts.append(f'--{boundary}\r\n'.encode())
            body_parts.append(
                f'Content-Disposition: form-data; name="{field_name}"; filename="{path.name}"\r\n'.encode()
            )
            body_parts.append(f'Content-Type: {mime_type}\r\n\r\n'.encode())
            body_parts.append(path.read_bytes())
            body_parts.append(b'\r\n')

        body_parts.append(f'--{boundary}--\r\n'.encode())
        data = b''.join(body_parts)
        headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
    else:
        data = json.dumps(payload or {}).encode('utf-8')
        headers = {'Content-Type': 'application/json'}

    request = Request(url, data=data, headers=headers, method='POST')
    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning('Telegram API %s failed: %s', method, exc)
        return None

    if not result.get('ok'):
        logger.warning('Telegram API %s error: %s', method, result.get('description', result))
        return None
    return result


def _send_to_chat(chat_id: int | str, article, caption: str) -> bool:
    image_field = getattr(article, 'image', None)
    if image_field and getattr(image_field, 'name', ''):
        image_path = Path(settings.MEDIA_ROOT) / image_field.name
        if image_path.is_file():
            result = _api_request(
                'sendPhoto',
                {
                    'chat_id': chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML',
                },
                files={'photo': image_path},
            )
            if result:
                return True

    text = format_article_message(article, for_caption=False)
    result = _api_request(
        'sendMessage',
        {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        },
    )
    return bool(result)


def send_article_to_telegram(article, *, force: bool = False) -> bool:
    """Post one article to all configured Telegram destinations."""
    if not telegram_configured():
        logger.info('Telegram bot token not configured; skipping notification.')
        return False
    if not article.is_published or article.article_type != 'news':
        return False
    if article.telegram_notified_at and not force:
        return False

    chat_ids = telegram_chat_ids()
    if not chat_ids:
        logger.warning('No Telegram chat IDs configured.')
        return False

    caption = format_article_message(article, for_caption=bool(article.image))
    sent_any = False
    for chat_id in chat_ids:
        if _send_to_chat(chat_id, article, caption):
            sent_any = True
        else:
            logger.warning('Failed to send article %s to Telegram chat %s', article.pk, chat_id)

    if sent_any:
        from website.models import NewsArticle

        NewsArticle.objects.filter(pk=article.pk).update(telegram_notified_at=timezone.now())
        return True
    return False
