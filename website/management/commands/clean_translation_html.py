from django.core.management.base import BaseCommand

from website.models import SiteTranslation
from website.translation_text import plain_translation_text


class Command(BaseCommand):
    help = 'Strip HTML markup from all SiteTranslation values'

    def handle(self, *args, **options):
        updated = 0
        removed = 0
        for translation in SiteTranslation.objects.all():
            if translation.key == 'hero.title':
                translation.delete()
                removed += 1
                continue
            before = (
                translation.text or '',
                translation.text_en or '',
                translation.text_am or '',
            )
            translation.text = plain_translation_text(translation.text)
            translation.text_en = plain_translation_text(translation.text_en)
            translation.text_am = plain_translation_text(translation.text_am)
            after = (translation.text, translation.text_en, translation.text_am)
            if before != after:
                updated += 1
            translation.save()
        self.stdout.write(self.style.SUCCESS(
            f'Cleaned {updated} translation(s); removed {removed} deprecated key(s).'
        ))
