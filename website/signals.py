from django.db.models.signals import post_save
from django.dispatch import receiver

from website.models import NewsArticle
from website.telegram_news import send_article_to_telegram, telegram_configured


@receiver(post_save, sender=NewsArticle)
def notify_telegram_on_news_publish(sender, instance, **kwargs):
    if not telegram_configured():
        return
    if not instance.is_published or instance.article_type != 'news':
        return
    if instance.telegram_notified_at:
        return
    send_article_to_telegram(instance)
