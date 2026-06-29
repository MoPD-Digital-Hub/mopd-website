from django.core.management.base import BaseCommand

from website.models import Document, NewsArticle, ProcurementNotice, SiteSettings, Vacancy
from website.remote_assets import localize_article_fields, localize_file_url_field


class Command(BaseCommand):
    help = 'Download remote mopd.gov.et files and rewrite URLs to local /media/ paths.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--news-only',
            action='store_true',
            help='Only localize news article text fields.',
        )
        parser.add_argument(
            '--documents-only',
            action='store_true',
            help='Only localize document and settings file URLs.',
        )

    def handle(self, *args, **options):
        cache: dict[str, str] = {}
        do_news = not options['documents_only']
        do_docs = not options['news_only']

        if do_docs:
            self._localize_documents(cache)
            self._localize_site_settings(cache)
            self._localize_procurement(cache)
            self._localize_vacancies(cache)
            self._verify_uploaded_images()

        if do_news:
            self._localize_news(cache)

        self.stdout.write(self.style.SUCCESS('Remote asset localization complete.'))

    def _localize_documents(self, cache):
        updated = 0
        for doc in Document.objects.all():
            new_url = localize_file_url_field(doc.file_url, cache)
            if new_url != doc.file_url:
                doc.file_url = new_url
                doc.save(update_fields=['file_url'])
                updated += 1
                self.stdout.write(f'  document → {new_url}')
        self.stdout.write(f'Documents updated: {updated}/{Document.objects.count()}')

    def _localize_site_settings(self, cache):
        settings_obj = SiteSettings.load()
        changed_fields = []
        for field in ('development_plan_pdf_url', 'development_plan_cover_url'):
            value = getattr(settings_obj, field, '') or ''
            if not value:
                continue
            new_value = localize_file_url_field(value, cache)
            if new_value != value:
                setattr(settings_obj, field, new_value)
                changed_fields.append(field)
                self.stdout.write(f'  settings.{field} → {new_value}')
        # Point external PDF default at local path when still on mopd.gov.et
        if settings_obj.development_plan_pdf_url and 'mopd.gov.et' in settings_obj.development_plan_pdf_url:
            settings_obj.development_plan_pdf_url = '/media/ten-year-document/ten_year_development_plan.pdf'
            if 'development_plan_pdf_url' not in changed_fields:
                changed_fields.append('development_plan_pdf_url')
                self.stdout.write('  settings.development_plan_pdf_url → /media/ten-year-document/ten_year_development_plan.pdf')
        if changed_fields:
            settings_obj.save(update_fields=changed_fields)

    def _localize_procurement(self, cache):
        updated = 0
        for notice in ProcurementNotice.objects.exclude(file_url=''):
            new_url = localize_file_url_field(notice.file_url, cache)
            if new_url != notice.file_url:
                notice.file_url = new_url
                notice.save(update_fields=['file_url'])
                updated += 1
        if updated:
            self.stdout.write(f'Procurement notices updated: {updated}')

    def _localize_vacancies(self, cache):
        updated = 0
        for vacancy in Vacancy.objects.exclude(file_url=''):
            new_url = localize_file_url_field(vacancy.file_url, cache)
            if new_url != vacancy.file_url:
                vacancy.file_url = new_url
                vacancy.save(update_fields=['file_url'])
                updated += 1
        if updated:
            self.stdout.write(f'Vacancies updated: {updated}')

    def _localize_news(self, cache):
        updated = 0
        for article in NewsArticle.objects.all():
            if localize_article_fields(article, cache):
                article.save()
                updated += 1
        self.stdout.write(f'News articles updated: {updated}/{NewsArticle.objects.count()}')

    def _verify_uploaded_images(self):
        from pathlib import Path

        from django.conf import settings

        from website.models import AffiliateLink, CarouselSlide, GalleryImage, Leader, NewsArticle

        missing = []
        checks = (
            ('news', NewsArticle.objects.exclude(image='')),
            ('leaders', Leader.objects.exclude(photo='')),
            ('affiliates', AffiliateLink.objects.exclude(logo='')),
            ('carousel', CarouselSlide.objects.exclude(image='')),
            ('gallery', GalleryImage.objects.exclude(image='')),
        )
        for label, qs in checks:
            for obj in qs:
                field = 'image' if hasattr(obj, 'image') else 'photo' if hasattr(obj, 'photo') else 'logo'
                file_field = getattr(obj, field)
                if not file_field or not file_field.name:
                    continue
                path = Path(settings.MEDIA_ROOT) / file_field.name
                if not path.is_file():
                    missing.append(f'{label}:{obj.pk}:{file_field.name}')
        if missing:
            self.stdout.write(self.style.WARNING(f'Missing image files on disk: {len(missing)}'))
            for item in missing[:10]:
                self.stdout.write(f'  {item}')
        else:
            self.stdout.write('All uploaded images present on disk.')
