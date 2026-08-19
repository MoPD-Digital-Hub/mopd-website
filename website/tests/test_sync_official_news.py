from datetime import date
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from website.management.commands.sync_official_news import (
    parse_media_date,
    parse_published_at,
    should_repair_published_at,
)
from website.models import NewsArticle


class OfficialNewsDateTests(SimpleTestCase):
    def test_parses_month_first_date(self):
        self.assertEqual(
            parse_published_at(['Published April 23, 2025']),
            date(2025, 4, 23),
        )

    def test_parses_day_first_date(self):
        self.assertEqual(
            parse_published_at(['Published 23 April 2025']),
            date(2025, 4, 23),
        )

    def test_missing_article_date_does_not_become_today(self):
        self.assertIsNone(parse_published_at(['Article text without a date.']))

    def test_extracts_date_from_media_url(self):
        self.assertEqual(
            parse_media_date('https://mopd.gov.et/media/photos/2025/04/23/photo.jpg'),
            date(2025, 4, 23),
        )

    def test_rejects_invalid_media_date(self):
        self.assertIsNone(
            parse_media_date('https://mopd.gov.et/media/photos/2025/13/45/photo.jpg')
        )

    def test_preserves_an_existing_legitimate_date(self):
        article = SimpleNamespace(
            published_at=date(2025, 4, 25),
            updated_at=timezone.make_aware(timezone.datetime(2026, 8, 19)),
        )
        self.assertFalse(
            should_repair_published_at(article, date(2025, 4, 23))
        )

    def test_repairs_date_written_by_previous_sync(self):
        article = SimpleNamespace(
            published_at=date(2026, 8, 19),
            updated_at=timezone.make_aware(timezone.datetime(2026, 8, 19)),
        )
        self.assertTrue(
            should_repair_published_at(article, date(2025, 4, 23))
        )

    def test_force_repair_replaces_any_different_date(self):
        article = SimpleNamespace(
            published_at=date(2025, 4, 25),
            updated_at=timezone.make_aware(timezone.datetime(2026, 8, 19)),
        )
        self.assertTrue(
            should_repair_published_at(article, date(2025, 4, 23), force=True)
        )


@patch(
    'website.management.commands.sync_official_news.localize_article_fields',
    return_value=None,
)
@patch(
    'website.management.commands.sync_official_news.scrape_listing_meta',
    return_value={},
)
@patch(
    'website.management.commands.sync_official_news.collect_article_paths',
    return_value=['source-article'],
)
class OfficialNewsCommandTests(TestCase):
    def create_article(self, published_at):
        return NewsArticle.objects.create(
            source_path='source-article',
            slug='source-article',
            category='others',
            tag='News',
            title='Existing title',
            excerpt='Existing excerpt',
            body='Existing body',
            published_at=published_at,
        )

    @staticmethod
    def detail(published_at):
        return {
            'title_en': 'Source title',
            'image_src': '',
            'body_en': 'Source body',
            'published_at': published_at,
            'excerpt_en': 'Source excerpt',
        }

    def test_sync_repairs_date_written_by_previous_sync(
        self,
        _collect_paths,
        _listing_meta,
        _localize_fields,
    ):
        article = self.create_article(timezone.localdate())

        with patch(
            'website.management.commands.sync_official_news.scrape_article_detail',
            return_value=self.detail(date(2025, 4, 23)),
        ):
            call_command('sync_official_news', featured=0, stdout=StringIO())

        article.refresh_from_db()
        self.assertEqual(article.published_at, date(2025, 4, 23))

    def test_sync_preserves_existing_legitimate_date(
        self,
        _collect_paths,
        _listing_meta,
        _localize_fields,
    ):
        article = self.create_article(date(2025, 4, 25))

        with patch(
            'website.management.commands.sync_official_news.scrape_article_detail',
            return_value=self.detail(date(2025, 4, 23)),
        ):
            call_command('sync_official_news', featured=0, stdout=StringIO())

        article.refresh_from_db()
        self.assertEqual(article.published_at, date(2025, 4, 25))

    def test_sync_skips_new_article_when_no_date_can_be_recovered(
        self,
        _collect_paths,
        _listing_meta,
        _localize_fields,
    ):
        with patch(
            'website.management.commands.sync_official_news.scrape_article_detail',
            return_value=self.detail(None),
        ):
            call_command(
                'sync_official_news',
                featured=0,
                stdout=StringIO(),
                stderr=StringIO(),
            )

        self.assertFalse(
            NewsArticle.objects.filter(source_path='source-article').exists()
        )
