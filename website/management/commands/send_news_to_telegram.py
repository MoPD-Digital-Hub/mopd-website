import time

from django.core.management.base import BaseCommand

from website.models import NewsArticle
from website.telegram_news import send_article_to_telegram, telegram_chat_ids, telegram_configured


class Command(BaseCommand):
    help = 'Send published news articles to Telegram (backfill or retry).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Resend articles that were already notified.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Maximum number of articles to send (0 = all).',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Seconds to wait between messages (Telegram rate limits).',
        )

    def handle(self, *args, **options):
        if not telegram_configured():
            self.stderr.write(self.style.ERROR(
                'TELEGRAM_BOT_TOKEN is not set. Add it to your environment and restart the server.'
            ))
            return

        chats = telegram_chat_ids()
        if not chats:
            self.stderr.write(self.style.ERROR(
                'No Telegram destinations configured (TELEGRAM_GROUP_ID / TELEGRAM_CHAT_ID).'
            ))
            return

        qs = NewsArticle.objects.filter(is_published=True, article_type='news').order_by(
            '-published_at', '-created_at'
        )
        if not options['force']:
            qs = qs.filter(telegram_notified_at__isnull=True)

        if options['limit']:
            qs = qs[: options['limit']]

        articles = list(qs)
        if not articles:
            self.stdout.write(self.style.SUCCESS('No news articles to send.'))
            return

        self.stdout.write(f'Sending {len(articles)} article(s) to {len(chats)} destination(s)…')

        sent = 0
        failed = 0
        for index, article in enumerate(articles):
            if options['force']:
                NewsArticle.objects.filter(pk=article.pk).update(telegram_notified_at=None)

            if send_article_to_telegram(article, force=options['force']):
                sent += 1
                self.stdout.write(f'  ✓ {article.title_en or article.title}')
            else:
                failed += 1
                self.stdout.write(self.style.WARNING(f'  ✗ {article.title_en or article.title}'))

            if index < len(articles) - 1 and options['delay']:
                time.sleep(options['delay'])

        self.stdout.write(self.style.SUCCESS(f'Done. Sent: {sent}, failed: {failed}.'))
