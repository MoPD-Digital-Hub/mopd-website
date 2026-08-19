from io import BytesIO

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from PIL import Image, ImageOps

from website.models import NewsArticle
from website.telegram_news import send_article_to_telegram, telegram_configured

# Max width for news images; quality for JPEG/WebP.
_NEWS_IMAGE_MAX_WIDTH = 1600
_NEWS_IMAGE_QUALITY = 80


def _compress_image_field(instance, field_name: str, max_width: int, quality: int) -> None:
    """Resize + compress an ImageField in-memory before the file is written to disk."""
    field = getattr(instance, field_name)
    if not field or not hasattr(field, 'file'):
        return
    # Only act on freshly-attached in-memory files (not existing stored paths).
    try:
        field.file.seek(0)
        raw = field.file.read()
        field.file.seek(0)
    except Exception:
        return

    try:
        img = Image.open(BytesIO(raw))
    except Exception:
        return

    img = ImageOps.exif_transpose(img)
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, max(1, round(img.height * ratio))), Image.Resampling.LANCZOS)

    buf = BytesIO()
    original_name = field.name or ''
    ext = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else 'jpg'

    if ext in ('jpg', 'jpeg'):
        img.save(buf, format='JPEG', quality=quality, optimize=True, progressive=True)
        content_type = 'image/jpeg'
    elif ext == 'webp':
        img.save(buf, format='WEBP', quality=quality, method=6)
        content_type = 'image/webp'
    else:
        # PNG, gif, etc. — convert to JPEG for smaller size
        img.save(buf, format='JPEG', quality=quality, optimize=True, progressive=True)
        ext = 'jpg'
        content_type = 'image/jpeg'  # noqa: F841

    compressed = buf.getvalue()
    # Only replace if we actually made it smaller.
    if len(compressed) >= len(raw):
        return

    base_name = original_name.rsplit('.', 1)[0] if '.' in original_name else original_name
    new_name = f'{base_name}.{ext}'
    field.save(new_name, ContentFile(compressed), save=False)


@receiver(pre_save, sender=NewsArticle)
def compress_news_image_on_upload(sender, instance, **kwargs):
    """Compress a newly-uploaded news image before it hits disk."""
    if not instance.image:
        return
    # Skip if the image name already exists in DB (not a new upload).
    if instance.pk:
        try:
            old = NewsArticle.objects.get(pk=instance.pk)
            if old.image and old.image.name == instance.image.name:
                return
        except NewsArticle.DoesNotExist:
            pass
    _compress_image_field(instance, 'image', _NEWS_IMAGE_MAX_WIDTH, _NEWS_IMAGE_QUALITY)


@receiver(pre_save, sender=NewsArticle)
def reset_telegram_if_image_changed(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = NewsArticle.objects.get(pk=instance.pk)
    except NewsArticle.DoesNotExist:
        return

    old_image = previous.image.name if previous.image else ''
    new_image = instance.image.name if instance.image else ''
    if new_image and new_image != old_image and previous.telegram_notified_at:
        instance.telegram_notified_at = None


@receiver(post_save, sender=NewsArticle)
def notify_telegram_on_news_publish(sender, instance, **kwargs):
    if not telegram_configured():
        return
    if not instance.is_published or instance.article_type != 'news':
        return
    if instance.telegram_notified_at:
        return

    article_id = instance.pk

    def _send():
        article = NewsArticle.objects.get(pk=article_id)
        if article.telegram_notified_at:
            return
        send_article_to_telegram(article)

    transaction.on_commit(_send)
