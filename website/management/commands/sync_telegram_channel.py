from django.core.management.base import BaseCommand

from website.telegram_channel_sync import sync_telegram_channel, watch_telegram_channel


class Command(BaseCommand):
    help = (
        'Import new posts from the configured Telegram source channel '
        '(TELEGRAM_SOURCE_CHANNEL_ID) into unpublished news drafts.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse updates and report actions without saving articles or advancing the offset.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Maximum number of channel posts to import this run.',
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help=(
                'Long-poll continuously for new channel posts (automatic fallback when webhook '
                'is not available). Removes any active webhook.'
            ),
        )

    def handle(self, *args, **options):
        if options['watch']:
            self.stdout.write('Starting continuous Telegram channel watch…')
            try:
                watch_telegram_channel()
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Watch stopped.'))
            return

        dry_run = options['dry_run']
        limit = options['limit']
        result = sync_telegram_channel(dry_run=dry_run, limit=limit)

        for message in result.messages:
            self.stdout.write(f'  {message}')

        summary = (
            f'{"Dry run - " if dry_run else ""}'
            f'created={result.created} skipped={result.skipped} errors={result.errors}'
        )
        if result.errors:
            self.stdout.write(self.style.WARNING(summary))
        else:
            self.stdout.write(self.style.SUCCESS(summary))
