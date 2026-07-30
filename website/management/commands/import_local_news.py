import re
from datetime import date, datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from website.models import NewsArticle

HASH_SUFFIX_RE = re.compile(r'_[A-Za-z0-9]{6,8}$')
IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

TITLE_OVERRIDES = {
    'un-guterres': (
        'UN Secretary-General António Guterres praised Ethiopia\'s commitment '
        'in aligning food policy with climate and environmental goals'
    ),
    'acs2': '#ACS2 Call for flagship initiatives is open!',
    'state-minister-acs2': (
        'Ethiopia\'s State Minister Calls for United African Leadership Ahead of ACS2'
    ),
    'france-acs2': 'Ethiopia and France to Collaborate on the Second Africa Climate Summit',
    'aprm-session': (
        'The First Extraordinary Session of the African Peer Review Focal Points '
        'Steering Committee Convened'
    ),
}

FEATURED_SLUGS = ('un-guterres', 'acs2', 'state-minister-acs2')

CATEGORY_KEYWORDS = {
    'climate': ('climate', 'acs2', 'cop', 'green', 'carbon', 'environment'),
    'economic': ('economic', 'growth', 'poverty', 'trade', 'finance'),
    'policy': ('policy', 'sdg', 'planning', 'vnr', 'hlpf', 'governance'),
    'politics': ('minister', 'bilateral', 'diplomatic', 'prime-minister', 'african-union'),
    'social': ('social', 'education', 'health', 'community'),
    'demography': ('population', 'demograph', 'census'),
}


def normalize_slug(stem: str) -> str:
    slug = HASH_SUFFIX_RE.sub('', stem).strip('-')
    return slug[:200] or slugify(stem)[:200]


def slug_to_title(slug: str) -> str:
    if slug in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[slug]
    words = slug.replace('-', ' ').split()
    titled = []
    for word in words:
        upper = word.upper()
        if upper in {'UN', 'SDG', 'SDGS', 'HLPF', 'ACS2', 'COP29', 'AU', 'UAE', 'NARC', 'ID4AFRICA', 'FDRE', 'MOPD', 'CRGE', 'AMCEN', 'VNR', 'ILO', 'GEF', 'GCF'}:
            titled.append(upper if upper != 'ACS2' else 'ACS2')
        elif word.lower() in {'and', 'at', 'for', 'in', 'on', 'the', 'to', 'a', 'an', 'of', 'with'}:
            titled.append(word.lower())
        else:
            titled.append(word.capitalize())
    if titled:
        titled[0] = titled[0].capitalize()
    return ' '.join(titled)


def guess_category(slug: str, title: str) -> str:
    haystack = f'{slug} {title}'.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category
    return 'others'


def pick_canonical_files(news_dir: Path) -> dict[str, Path]:
    grouped: dict[str, list[Path]] = {}
    for path in news_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        slug = normalize_slug(path.stem)
        grouped.setdefault(slug, []).append(path)

    chosen: dict[str, Path] = {}
    for slug, paths in grouped.items():
        exact = [p for p in paths if normalize_slug(p.stem) == slug and HASH_SUFFIX_RE.search(p.stem) is None]
        if exact:
            chosen[slug] = sorted(exact, key=lambda p: p.stat().st_size, reverse=True)[0]
            continue
        chosen[slug] = sorted(paths, key=lambda p: (len(p.stem), -p.stat().st_size))[0]
    return chosen


class Command(BaseCommand):
    help = 'Import news articles from image files already present in media/news/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--featured',
            type=int,
            default=3,
            help='Number of articles to mark as homepage featured',
        )

    def handle(self, *args, **options):
        news_dir = Path(settings.MEDIA_ROOT) / 'news'
        if not news_dir.is_dir():
            self.stderr.write(self.style.ERROR(f'News media folder not found: {news_dir}'))
            return

        files = pick_canonical_files(news_dir)
        if not files:
            self.stderr.write(self.style.ERROR('No news images found in media/news/'))
            return

        created = updated = 0
        for slug, path in sorted(files.items()):
            title = slug_to_title(slug)
            category = guess_category(slug, title)
            published_at = date.fromtimestamp(path.stat().st_mtime)
            media_name = f'news/{path.name}'

            article = NewsArticle.objects.filter(slug=slug).first()
            is_new = article is None
            if is_new:
                article = NewsArticle(slug=slug)

            article.title_en = title[:500]
            article.title_am = article.title_am or title[:500]
            article.category = category
            article.tag_en = article.get_category_display()
            article.excerpt_en = title[:300]
            article.excerpt_am = article.excerpt_am or title[:300]
            article.body_en = title
            article.body_am = article.body_am or title
            article.published_at = published_at
            article.search_keywords = f'{title} {category}'.lower()
            article.is_published = True
            article.article_type = 'news'
            article.image.name = media_name
            article.save()

            if is_new:
                created += 1
            else:
                updated += 1

        featured_count = options['featured']
        NewsArticle.objects.update(is_featured_home=False)
        featured = []
        for slug in FEATURED_SLUGS:
            article = NewsArticle.objects.filter(slug=slug, is_published=True).first()
            if article:
                featured.append(article)
        if len(featured) < featured_count:
            for article in NewsArticle.objects.filter(is_published=True).order_by('-published_at', '-created_at'):
                if article not in featured:
                    featured.append(article)
                if len(featured) >= featured_count:
                    break
        for article in featured[:featured_count]:
            article.is_featured_home = True
            article.save(update_fields=['is_featured_home'])

        self.stdout.write(self.style.SUCCESS(
            f'Local news import complete: {created} created, {updated} updated, '
            f'{len(files)} images, {min(featured_count, len(featured))} featured.'
        ))
