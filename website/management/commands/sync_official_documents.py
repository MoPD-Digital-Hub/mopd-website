"""Import or update statistics documents from mopd.gov.et (never climate)."""
import html
import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand

from website.models import Document, SiteSettings
from website.remote_assets import localize_file_url_field

BASE_URL = 'https://mopd.gov.et'

TEN_YEAR_PLAN_URL = f'{BASE_URL}/media/ten-year-document/ten_year_development_plan.pdf'
TEN_YEAR_PLAN_LOCAL = '/media/ten-year-document/ten_year_development_plan.pdf'

# Always include these PDFs even if they are not listed on the data page.
EXTRA_DOCUMENTS = (
    {
        'doc_type': Document.DocType.STATISTICS,
        'title_en': '10-Year Development Plan',
        'description_en': (
            'Ethiopia\'s Ten-Year Development Plan — official MoPD document.'
        ),
        'file_url': TEN_YEAR_PLAN_URL,
        'sort_order': 0,
    },
)

SOURCES = (
    {
        'url': f'{BASE_URL}/en/MoPDcoreDivision/data/',
        'doc_type': Document.DocType.STATISTICS,
    },
)

CARD_RE = re.compile(
    r'<h3[^>]*>(?P<title>.*?)</h3>\s*'
    r'(?:<p[^>]*>(?P<description>.*?)</p>\s*)?'
    r'.*?href="(?P<href>[^"]+\.pdf)"',
    re.DOTALL | re.IGNORECASE,
)


def fetch(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 MoPD-Sync/1.0'})
    with urlopen(request, timeout=45) as response:
        return response.read().decode('utf-8', errors='ignore')


def clean_text(value):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', value or '')).strip())


def scrape_documents(source):
    html_doc = fetch(source['url'])
    docs = []
    seen = set()
    for match in CARD_RE.finditer(html_doc):
        href = match.group('href')
        file_url = urljoin(BASE_URL, href)
        if file_url in seen:
            continue
        seen.add(file_url)
        title = clean_text(match.group('title')) or clean_text(href.rsplit('/', 1)[-1].replace('_', ' '))
        description = clean_text(match.group('description') or '')
        if description.lower() == title.lower():
            description = ''
        docs.append({
            'doc_type': source['doc_type'],
            'title_en': title[:300],
            'description_en': description,
            'file_url': file_url,
        })

    # Fallback: capture any PDF links the card regex missed.
    for href in re.findall(r'href="([^"]+\.pdf)"', html_doc, re.I):
        file_url = urljoin(BASE_URL, href)
        if file_url in seen:
            continue
        seen.add(file_url)
        title = clean_text(href.rsplit('/', 1)[-1].replace('_', ' ').replace('-', ' '))
        docs.append({
            'doc_type': source['doc_type'],
            'title_en': title[:300],
            'description_en': '',
            'file_url': file_url,
        })
    return docs


def upsert_document(item, cache, sort_order):
    """Create or update a Document from a sync item. Returns (status, local_url)."""
    local_url = localize_file_url_field(item['file_url'], cache) or item['file_url']
    candidates = [local_url, item['file_url']]
    if item['file_url'] == TEN_YEAR_PLAN_URL:
        candidates.extend([
            TEN_YEAR_PLAN_URL,
            '/media/ten-year-document/ten_year_development_plan.pdf',
        ])

    article = None
    for url in candidates:
        article = Document.objects.filter(file_url=url).first()
        if article:
            break

    title = item['title_en']
    if not title:
        return 'skipped', local_url

    if article is None:
        article = Document(file_url=local_url)
        is_new = True
    else:
        is_new = False

    article.doc_type = item['doc_type']
    article.title_en = title
    if not article.title_am:
        article.title_am = title
    # description_en is NOT NULL — always set a string (empty OK when
    # the source page has no blurb / fallback PDF-only scrape).
    description = item.get('description_en') or ''
    if is_new or description:
        article.description_en = description
        article.description = description
    if not getattr(article, 'description_am', None):
        article.description_am = article.description_en or ''
    article.file_url = local_url
    article.sort_order = item.get('sort_order', sort_order)
    article.is_published = True
    article.save()
    return ('created' if is_new else 'updated'), local_url


class Command(BaseCommand):
    help = (
        'Import or update statistics documents from mopd.gov.et data page '
        'plus the 10-Year Development Plan PDF (climate excluded)'
    )

    def handle(self, *args, **options):
        created = updated = skipped = 0
        cache = {}
        items = []

        self.stdout.write('Adding fixed documents (10-Year Development Plan)')
        items.extend(EXTRA_DOCUMENTS)

        for source in SOURCES:
            self.stdout.write(f'Scraping {source["url"]}')
            try:
                scraped = scrape_documents(source)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'Failed to scrape {source["url"]}: {exc}'))
                continue
            self.stdout.write(f'  Found {len(scraped)} documents')
            # Keep scraped items after extras; bump sort so plan stays first.
            for offset, scraped_item in enumerate(scraped, start=1):
                scraped_item = dict(scraped_item)
                scraped_item['sort_order'] = offset
                items.append(scraped_item)

        ten_year_local = None
        for sort_order, item in enumerate(items):
            status, local_url = upsert_document(item, cache, sort_order)
            if item['file_url'] == TEN_YEAR_PLAN_URL:
                ten_year_local = local_url
            if status == 'created':
                created += 1
            elif status == 'updated':
                updated += 1
            else:
                skipped += 1

        # Keep the homepage "Open document" card pointed at a working PDF.
        from pathlib import Path
        from django.conf import settings as dj_settings

        plan_disk = (
            Path(dj_settings.MEDIA_ROOT)
            / 'ten-year-document'
            / 'ten_year_development_plan.pdf'
        )
        settings_obj = SiteSettings.load()
        if plan_disk.is_file() and plan_disk.stat().st_size > 0:
            plan_href = TEN_YEAR_PLAN_LOCAL
            self.stdout.write(
                f'10-Year plan ready on disk ({plan_disk.stat().st_size} bytes) -> {plan_href}'
            )
        else:
            plan_href = ten_year_local if ten_year_local and ten_year_local.startswith('http') else TEN_YEAR_PLAN_URL
            self.stderr.write(self.style.WARNING(
                f'10-Year plan missing locally; homepage will use {plan_href}'
            ))

        if settings_obj.development_plan_pdf_url != plan_href:
            settings_obj.development_plan_pdf_url = plan_href
            settings_obj.save(update_fields=['development_plan_pdf_url'])
            self.stdout.write(f'Updated site settings plan PDF -> {plan_href}')

        # Ensure the Document row also uses the same openable href.
        Document.objects.filter(
            file_url__in=[
                TEN_YEAR_PLAN_URL,
                TEN_YEAR_PLAN_LOCAL,
                ten_year_local or '',
                '//media/ten-year-document/ten_year_development_plan.pdf',
            ]
        ).exclude(file_url=plan_href).update(file_url=plan_href)

        self.stdout.write(self.style.SUCCESS(
            f'Document sync complete: {created} created, {updated} updated, {skipped} skipped.'
        ))
