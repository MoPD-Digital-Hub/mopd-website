from django.core.management.base import BaseCommand

from website.telegram_channel_sync import delete_webhook, set_webhook, webhook_public_url


class Command(BaseCommand):
    help = (
        'Register (or remove) the Telegram webhook so new PDC_Ethiopia channel posts '
        'are imported automatically as unpublished news drafts.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Remove the webhook (use with cron/--watch polling instead).',
        )

    def handle(self, *args, **options):
        if options['delete']:
            ok, message = delete_webhook()
        else:
            self.stdout.write(f'Target URL: {webhook_public_url() or "(not configured)"}')
            ok, message = set_webhook()

        if ok:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stderr.write(self.style.ERROR(message))
            raise SystemExit(1)
