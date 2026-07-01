from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from website.models import NewsArticle
from website.telegram_news import send_article_to_telegram, telegram_configured


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
