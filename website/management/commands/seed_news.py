from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Deprecated — use seed_site instead'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('seed_news is deprecated; running seed_site instead.'))
        call_command('seed_site', *args, **options)
