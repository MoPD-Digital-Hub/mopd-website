from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import NewsArticle


class LatestNewsFeed(Feed):
    title = 'MoPD News'
    link = '/news/'
    description = 'Latest news from the Ministry of Planning and Development, Ethiopia.'

    def items(self):
        return NewsArticle.objects.filter(is_published=True, article_type='news')[:25]

    def item_title(self, item):
        return item.title_en

    def item_description(self, item):
        return item.card_excerpt_en

    def item_pubdate(self, item):
        from datetime import datetime
        from django.utils import timezone
        return timezone.make_aware(datetime.combine(item.published_at, datetime.min.time()))

    def item_link(self, item):
        return reverse('news_detail', args=[item.slug])
