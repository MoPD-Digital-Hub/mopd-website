import html
import re
from datetime import date, datetime
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from website.media_utils import assign_image_from_url
from website.models import NewsArticle

BASE_URL = 'https://mopd.gov.et'

SLUG_OVERRIDES = {
    'un-secretary-general-antonio-guterress-praisedethiopias-commitment-in-aligning-food-policy-with-climate-and-environmental-goals': 'un-guterres',
    'acs2-call-for-flagship-initiatives-is-open': 'acs2',
    'ethiopias-state-minister-calls-for-united-african-leadership-ahead-of-acs2': 'state-minister-acs2',
    'ethiopia-and-france-to-collaborate-on-the-second-africa-climate-summit': 'france-acs2',
    'the-first-extraordinary-session-of-the-african-peer-review-focal-points-steering-committee-convened-today-february-13-2025': 'aprm-session',
}

CATEGORY_MAP = {
    'poltics': 'politics',
    'politics': 'politics',
    'climate': 'climate',
    'economic': 'economic',
    'policy': 'policy',
    'demography': 'demography',
    'social': 'social',
    'others': 'others',
}

LISTING_CARD_RE = re.compile(
    r'<div class="kode_news_list">.*?'
    r'<img src="(?P<image>[^"]+)".*?'
    r'<span>(?P<category>[^<]+)</span>.*?'
    r'href="/en/news/articles/(?P<path>[^"]+)".*?>'
    r'(?P<title>.*?)</a>',
    re.DOTALL | re.IGNORECASE,
)

DATE_RE = re.compile(
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+\d{1,2},\s+\d{4}\b',
    re.IGNORECASE,
)


def fetch(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 MoPD-Sync/1.0'})
    with urlopen(request, timeout=45) as response:
        return response.read().decode('utf-8', errors='ignore')


def clean_text(value):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', value or '')).strip())


def path_to_slug(path):
    raw = re.sub(r'nonenone$', '', path.strip('/'))
    base = SLUG_OVERRIDES.get(raw, slugify(raw))
    return base[:200] or slugify(path)[:200]


def map_category(label):
    return CATEGORY_MAP.get(label.strip().lower(), 'others')


def parse_published_at(paragraphs):
    for paragraph in paragraphs[:6]:
        match = DATE_RE.search(paragraph)
        if match:
            try:
                return datetime.strptime(match.group(0), '%B %d, %Y').date()
            except ValueError:
                try:
                    return datetime.strptime(match.group(0), '%b %d, %Y').date()
                except ValueError:
                    continue
    return date.today()


def collect_article_paths():
    paths = set()
    for page in range(1, 20):
        html_doc = fetch(f'{BASE_URL}/en/news/?page={page}')
        found = re.findall(r'href="/en/news/articles/([^"]+)"', html_doc)
        article_paths = [p for p in found if 'articles_category' not in p]
        if not article_paths:
            break
        paths.update(article_paths)
    for category_id in range(1, 8):
        html_doc = fetch(f'{BASE_URL}/en/news/articles_category_list/{category_id}/')
        paths.update(
            p for p in re.findall(r'href="/en/news/articles/([^"]+)"', html_doc)
            if 'articles_category' not in p
        )
    return sorted(paths)


def scrape_listing_meta():
    meta = {}
    for page in range(1, 20):
        html_doc = fetch(f'{BASE_URL}/en/news/?page={page}')
        cards = LISTING_CARD_RE.findall(html_doc)
        if not cards:
            break
        for image, category, path, title in cards:
            meta[path] = {
                'category': map_category(category),
                'title_en': clean_text(title),
                'image_src': urljoin(BASE_URL, image),
            }
    return meta


def scrape_article_detail(path):
    html_doc = fetch(f'{BASE_URL}/en/news/articles/{path}')
    detail_match = re.search(r'<div class="kode_news_detail">(.*?)</div>\s*<!--Recommended', html_doc, re.DOTALL | re.IGNORECASE)
    if not detail_match:
        detail_match = re.search(r'<div class="kode_news_detail">(.*?)</div>\s*<div class="kode_related_event">', html_doc, re.DOTALL | re.IGNORECASE)
    if not detail_match:
        return None

    block = detail_match.group(1)
    title_match = re.search(r'<h4>(.*?)</h4>', block, re.DOTALL | re.IGNORECASE)
    image_match = re.search(r'<figure>\s*<img src="([^"]+)"', block, re.DOTALL | re.IGNORECASE)
    paragraphs = [
        clean_text(p)
        for p in re.findall(r'<p[^>]*>(.*?)</p>', block, re.DOTALL | re.IGNORECASE)
    ]
    paragraphs = [
        p for p in paragraphs
        if p and not set(p) <= {'='} and p.lower() != clean_text(title_match.group(1) if title_match else '').lower()
    ]

    title = clean_text(title_match.group(1)) if title_match else ''
    return {
        'title_en': title,
        'image_src': urljoin(BASE_URL, image_match.group(1)) if image_match else '',
        'body_en': '\n\n'.join(paragraphs),
        'published_at': parse_published_at(paragraphs),
        'excerpt_en': paragraphs[0][:300] if paragraphs else '',
    }


class Command(BaseCommand):
    help = 'Import or update news articles from mopd.gov.et'

    def add_arguments(self, parser):
        parser.add_argument(
            '--featured',
            type=int,
            default=3,
            help='Number of newest articles to mark as homepage featured',
        )

    def handle(self, *args, **options):
        paths = collect_article_paths()
        listing_meta = scrape_listing_meta()
        self.stdout.write(f'Found {len(paths)} articles on mopd.gov.et')

        created = updated = skipped = 0
        for path in paths:
            detail = scrape_article_detail(path)
            listing = listing_meta.get(path, {})
            if not detail and not listing:
                skipped += 1
                continue

            title = (detail or {}).get('title_en') or listing.get('title_en', '')
            if not title:
                skipped += 1
                continue

            slug = path_to_slug(path)
            article = NewsArticle.objects.filter(source_path=path).first()
            if article is None:
                article = NewsArticle.objects.filter(slug=slug).first()
            if article is None:
                article = NewsArticle(source_path=path, slug=slug)
                is_new = True
            else:
                is_new = False
                article.source_path = path
                if not article.slug:
                    article.slug = slug

            article.title_en = title[:500]
            article.category = listing.get('category', article.category or 'others')
            article.tag_en = article.get_category_display()
            article.body_en = (detail or {}).get('body_en', article.body_en or title)
            article.excerpt_en = (detail or {}).get('excerpt_en', article.excerpt_en or title[:300])
            article.published_at = (detail or {}).get('published_at', article.published_at or date.today())
            article.search_keywords = f'{title} {article.category}'.lower()
            article.is_published = True

            image_src = (detail or {}).get('image_src') or listing.get('image_src', '')
            if image_src:
                assign_image_from_url(article, 'image', image_src)
            article.save()

            if is_new:
                created += 1
            else:
                updated += 1

        featured_count = options['featured']
        if featured_count:
            NewsArticle.objects.update(is_featured_home=False)
            for article in NewsArticle.objects.filter(is_published=True).order_by('-published_at', '-created_at')[:featured_count]:
                article.is_featured_home = True
                article.save(update_fields=['is_featured_home'])

        self.stdout.write(self.style.SUCCESS(
            f'Sync complete: {created} created, {updated} updated, {skipped} skipped.'
        ))
