from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import NewsArticle


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return [
            'home',
            'about',
            'contact',
            'news',
            'press',
            'gallery',
            'leadership',
            'climate',
            'climate_docs',
            'green_tech',
            'stats',
            'devplan',
            'procurement',
            'vacancies',
            'privacy',
            'accessibility',
            'search',
        ]

    def location(self, item):
        return reverse(item)


class NewsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return NewsArticle.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
