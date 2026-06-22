import html
import re
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from website.models import (
    AffiliateLink,
    CarouselSlide,
    Document,
    GalleryAlbum,
    GalleryImage,
    Leader,
    LeaderParagraph,
    NewsArticle,
    SiteSettings,
    SiteTranslation,
)

I18N_PATTERN = re.compile(
    r'data-i18n(?:-html)?="([^"]+)"[^>]*>(.*?)</',
    re.DOTALL | re.IGNORECASE,
)

CLIMATE_DOCS = [
    ('The Addis Ababa Declaration on Climate Change & Call to Action', 'https://mopd.gov.et/media/climate-documents/Climate_Change_Declaration.pdf'),
    ('UNFCCC — United Nations Framework Convention on Climate Change', 'https://mopd.gov.et/media/climate-documents/UNFCCC_United_Nations_Framework_Convention_on_Climate_Change.pdf'),
    ('Kyoto Protocol', 'https://mopd.gov.et/media/climate-documents/Kyoto_Protocol.pdf'),
    ('Paris Agreement', 'https://mopd.gov.et/media/climate-documents/Paris_Agreement.pdf'),
    ('Ethiopia Carbon Market Strategy (2025)', 'https://mopd.gov.et/media/climate-documents/Ethiopia_Carbon-Market-Strategy_2025.pdf'),
    ('NAP-ETH 2019', 'https://mopd.gov.et/media/climate-documents/NAP-ETH_2019.pdf'),
    ("Ethiopia's Updated NDC — July 2021 Submission", 'https://mopd.gov.et/media/climate-documents/Ethiopias_updated_NDC_JULY_2021_Submission_.pdf'),
    ('Ethiopia Long-Term Low Emission and Climate Resilient Development Strategy', 'https://mopd.gov.et/media/climate-documents/ETHIOPIA__LONG_TERM_LOW_EMISSION_AND_CLIMATE_RESILIENT_DEVELOPMENT_STR_RGJXrpV.pdf'),
    ('CRGE Sector-Region Mainstreaming Guideline — Jan 2019', 'https://mopd.gov.et/media/climate-documents/CRGE_Sector-Region_Mainstreaming_Guideline-Final_Jan_2019.pdf'),
    ('CRGE Strategy 2011', 'https://mopd.gov.et/media/climate-documents/crge-strategy_2011.pdf'),
    ('Profiles of GEF and GCF Projects in Ethiopia', 'https://mopd.gov.et/media/climate-documents/25.7.24._GEFGCF_projects_profile_in_Ethiopia_WlleSLV.pdf'),
    ('List of Implemented Projects — CRGE Progress 2011–2019', 'https://mopd.gov.et/media/climate-documents/List_of_Implemented_Projects_CRGE_Progress_in_Implementing_the_CRGE_ND_UumPJzB.pdf'),
    ('GEF & GCF Projects Profile in Ethiopia — July 2023', 'https://mopd.gov.et/media/climate-documents/GEFGCF_projects_profile_in_Ethiopia_July_2023.pdf'),
    ('CRGE Strategy — Progress in Implementing 2011–2019', 'https://mopd.gov.et/media/climate-documents/CRGE_Strategy___Progress_in_Implementing_-_2011-2019__2020.pdf'),
    ("Ethiopia's 2nd National Communication", 'https://mopd.gov.et/media/climate-documents/Ethiopias_2nd_National_Communication.pdf'),
    ("Ethiopia's 3rd National Communication (2023)", 'https://mopd.gov.et/media/climate-documents/Ethiopias_3rd_National_Communication_2023.pdf'),
    ("Ethiopia's Initial National Communication (2001)", 'https://mopd.gov.et/media/climate-documents/Ethiopias_Initial_National_Communication_2001.pdf'),
    ('Side Events at the Ethiopian Pavilion on COP28', 'https://mopd.gov.et/media/climate-documents/List_of_Side_Events_Ethiopia_9_Nov_2023.pdf'),
]

STATS_DOCS = [
    ('Ethiopian Statistical Development Program', 'https://mopd.gov.et/media/data-documents/ETHIOPIAN_STATISTICAL_DEVELOPMENT_PROGRAM.pdf'),
    ('Code of Practice for Official Statistics in Ethiopia', 'https://mopd.gov.et/media/data-documents/Code_of_Practice_for_Official_Statistics_in_Ethiopia.pdf'),
    ('User Manual for Regional DpMES', 'https://mopd.gov.et/media/data-documents/DPMES_-_user_manual.pdf'),
]

GALLERY_IMAGES = [
    'https://mopd.gov.et/media/493212426_1001404048808490_3182080715549727532_n.jpg',
    'https://mopd.gov.et/media/492570380_994507082831520_8549139107595449985_n.jpg',
    'https://mopd.gov.et/media/490729992_987012810247614_150012963914782554_n.jpg',
    'https://mopd.gov.et/media/490066947_984741500474745_4878081392294499637_n.jpg',
    'https://mopd.gov.et/media/482302027_959816579633904_810442191452592327_n.jpg',
]

NEWS_ARTICLES = [
    {
        'slug': 'un-guterres',
        'category': 'economic',
        'tag_key': 'news.0.tag',
        'title_key': 'news.0.title',
        'excerpt_key': 'news.0.excerpt',
        'image_url': 'https://mopd.gov.et/media/photos/2025/07/29/fs_1.jpg',
        'published_at': '2025-07-29',
        'search_keywords': 'un secretary-general antonio guterres ethiopia climate food policy economic',
        'body_keys': ['page.article.un.p1', 'page.article.un.p2', 'page.article.un.p3', 'page.article.un.p4', 'page.article.un.p5'],
        'is_featured_home': True,
        'is_featured_carousel': True,
        'carousel_tag_key': 'carousel.0.tag',
        'carousel_title_key': 'carousel.0.title',
    },
    {
        'slug': 'acs2',
        'category': 'climate',
        'tag_key': 'news.1.tag',
        'title_key': 'news.1.title',
        'image_url': 'https://mopd.gov.et/media/photos/2025/07/29/summi_22.jpg',
        'published_at': '2025-07-29',
        'search_keywords': 'acs2 flagship initiatives africa climate summit',
        'body_keys': ['page.article.acs2.p1', 'page.article.acs2.p2'],
        'is_featured_home': True,
        'is_featured_carousel': True,
        'carousel_tag_key': 'carousel.1.tag',
        'carousel_title_key': 'carousel.1.title',
    },
    {
        'slug': 'state-minister-acs2',
        'category': 'climate',
        'tag_key': 'news.2.tag',
        'title_key': 'news.2.title',
        'image_url': 'https://mopd.gov.et/media/photos/2025/07/29/msur.jpg',
        'published_at': '2025-07-29',
        'search_keywords': 'state minister seyoum african leadership acs2 climate',
        'body_keys': ['page.article.seyoum.p1', 'page.article.seyoum.p2', 'page.article.seyoum.p3'],
        'is_featured_home': True,
        'is_featured_carousel': True,
        'carousel_tag_key': 'carousel.2.tag',
        'carousel_title_key': 'carousel.2.title',
    },
    {
        'slug': 'france-acs2',
        'category': 'climate',
        'tag_key': 'news.1.tag',
        'title_key': 'page.news.5.title',
        'image_url': 'https://mopd.gov.et/media/photos/2025/05/16/_92A1642.jpg',
        'published_at': '2025-05-16',
        'search_keywords': 'ethiopia france africa climate summit acs2 collaboration',
        'body_keys': ['page.article.france.p1', 'page.article.france.p2', 'page.article.france.p3'],
    },
    {
        'slug': 'donors-green',
        'category': 'climate',
        'tag_key': 'news.1.tag',
        'title_key': 'page.news.7.title',
        'image_url': 'https://mopd.gov.et/media/photos/2025/05/16/_92A1642.jpg',
        'published_at': '2025-05-10',
        'search_keywords': 'donors green economy crge cop29 amcen',
        'body_keys': ['page.article.donors.p1', 'page.article.donors.p2', 'page.article.donors.p3'],
    },
    {
        'slug': 'aprm-session',
        'category': 'policy',
        'tag_key': 'news.0.tag',
        'title_key': 'page.news.3.title',
        'image_url': 'https://mopd.gov.et/media/photos/2025/02/13/aprm.jpg',
        'published_at': '2025-02-13',
        'search_keywords': 'african peer review focal points steering committee aprm',
        'body_keys': ['page.article.aprm.p1', 'page.article.aprm.p2', 'page.article.aprm.p3', 'page.article.aprm.p4'],
    },
    {
        'slug': 'procurement',
        'category': 'policy',
        'tag_key': 'news.0.tag',
        'title_key': 'page.news.4.title',
        'image_url': 'https://mopd.gov.et/media/photos/2025/01/15/procurement.jpg',
        'published_at': '2025-01-15',
        'search_keywords': 'electronic public procurement ethiopia supervision',
        'body_keys': ['page.article.proc.p1', 'page.article.proc.p2', 'page.article.proc.p3', 'page.article.proc.p4'],
    },
    {
        'slug': 'finance-cop28',
        'category': 'climate',
        'tag_key': 'news.1.tag',
        'title_key': 'page.news.6.title',
        'image_url': 'https://mopd.gov.et/media/photos/2023/12/01/cop28.jpg',
        'published_at': '2023-12-01',
        'search_keywords': 'finance minister cop28 uae climate crge green legacy',
        'body_keys': ['page.article.cop28.p1', 'page.article.cop28.p2', 'page.article.cop28.p3'],
    },
]

LEADERS = [
    {
        'slug': 'fitsum-assefa',
        'name_key': 'leader.0.name',
        'role_key': 'leader.0.role',
        'bio_key': 'leader.0.bio',
        'photo_url': 'https://mopd.gov.et/media/photos/2025/06/25/G92A3209_fVjDvC6.jpg',
        'paragraph_keys': ['page.leader1.p1', 'page.leader1.p2', 'page.leader1.p3'],
        'sort_order': 0,
    },
    {
        'slug': 'bereket-fesehatsion',
        'name_key': 'leader.1.name',
        'role_key': 'leader.1.role',
        'bio_key': 'leader.1.bio',
        'photo_url': 'https://mopd.gov.et/media/photos/2024/10/08/photo_2024-12320-08_11-20-54.png',
        'paragraph_keys': ['leader.1.bio', 'page.leader2.p1'],
        'sort_order': 1,
    },
    {
        'slug': 'tirumar-abate',
        'name_key': 'leader.2.name',
        'role_key': 'leader.2.role',
        'bio_key': 'leader.2.bio',
        'photo_url': 'https://mopd.gov.et/media/photos/2023/06/27/Tirumar-Abate-1-768x609.jpg',
        'paragraph_keys': ['page.leader4.p1', 'leader.2.bio'],
        'wide_photo': True,
        'sort_order': 2,
    },
    {
        'slug': 'seyum-mekonen',
        'name_key': 'leader.3.name',
        'role_key': 'leader.3.role',
        'bio_key': 'leader.3.bio',
        'photo_url': 'https://mopd.gov.et/media/photos/2024/03/06/WhatsApp_Image_2024-02-16_at_14.15.47_7c28a19d.jpg',
        'paragraph_keys': ['leader.3.bio', 'page.leader3.p1'],
        'sort_order': 3,
    },
]

AFFILIATES = [
    ('Environmental Protection Authority', 'https://www.epa.gov.et/', 'affiliate.epa'),
    ('Central Statistics Service', 'http://www.csa.gov.et/', 'affiliate.csa'),
    ('Policy Study Institute', 'https://psi.org.et', 'affiliate.psi'),
]


def load_am_dict():
    path = Path(settings.BASE_DIR) / 'static/js/i18n.js'
    text = path.read_text(encoding='utf-8')
    am = {}
    in_am = False
    for line in text.splitlines():
        if not in_am and re.search(r'\bam\s*:\s*\{', line):
            in_am = True
            continue
        if in_am:
            if line.strip() == '},' or line.strip() == '}':
                break
            match = re.match(r"\s+'([^']+)':\s*'(.*)',\s*$", line)
            if match:
                am[match.group(1)] = match.group(2).replace("\\'", "'")
    return am


def collect_en_defaults():
    en = {}
    roots = [
        Path(settings.BASE_DIR) / 'legacy_html',
        Path(settings.BASE_DIR) / 'website/templates',
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob('*.html'):
            text = path.read_text(encoding='utf-8', errors='ignore')
            for match in I18N_PATTERN.finditer(text):
                key = match.group(1)
                value = html.unescape(re.sub(r'\s+', ' ', match.group(2).strip()))
                if value and key not in en:
                    en[key] = value
    return en


def text_for(key, en, am, field='en'):
    if field == 'am':
        return am.get(key, '')
    return en.get(key, '')


def join_paragraphs(keys, en, am, field='en'):
    source = am if field == 'am' else en
    parts = [source.get(k, '').strip() for k in keys]
    return '\n\n'.join(p for p in parts if p)


class Command(BaseCommand):
    help = 'Seed site settings, translations, news, leaders, gallery, documents, carousel, and affiliates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing content before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing site content...')
            LeaderParagraph.objects.all().delete()
            Leader.objects.all().delete()
            GalleryImage.objects.all().delete()
            GalleryAlbum.objects.all().delete()
            Document.objects.all().delete()
            CarouselSlide.objects.all().delete()
            AffiliateLink.objects.all().delete()
            NewsArticle.objects.all().delete()
            SiteTranslation.objects.all().delete()

        en = collect_en_defaults()
        am = load_am_dict()

        self.seed_settings(en, am)
        self.seed_translations(en, am)
        self.seed_news(en, am)
        self.seed_leaders(en, am)
        self.seed_gallery(en, am)
        self.seed_documents()
        self.seed_carousel(en, am)
        self.seed_affiliates(en, am)

        self.stdout.write(self.style.SUCCESS('Site content seeded successfully.'))

    def seed_settings(self, en, am):
        settings_obj = SiteSettings.load()
        settings_obj.footer_desc_en = (
            'The primary government institution responsible for national planning and development, '
            "shaping Ethiopia's sustainable growth."
        )
        settings_obj.footer_desc_am = am.get(
            'footer.desc',
            'የብሔራዊ እቅድ እና ልማት ላይ ኃላፊነት ያለው ዋና የመንግሥት ተቋም፣ የኢትዮጵያን ዘላቂ እድገት ያቀርባል።',
        )
        settings_obj.copyright_text_en = en.get(
            'footer.copyright',
            '© 2026 Ministry of Planning and Development. All rights reserved.',
        )
        settings_obj.copyright_text_am = am.get('footer.copyright', '')
        settings_obj.topbar_tag_am = am.get('topbar.tag', '')
        settings_obj.save()
        self.stdout.write('  Site settings')

    def seed_translations(self, en, am):
        keys = sorted(set(en) | set(am))
        created = 0
        for key in keys:
            _, was_created = SiteTranslation.objects.update_or_create(
                key=key,
                defaults={
                    'text_en': en.get(key, ''),
                    'text_am': am.get(key, ''),
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f'  Translations ({len(keys)} keys, {created} new)')

    def seed_news(self, en, am):
        for item in NEWS_ARTICLES:
            pub = date.fromisoformat(item['published_at'])
            NewsArticle.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'category': item['category'],
                    'tag_en': text_for(item['tag_key'], en, am),
                    'tag_am': text_for(item['tag_key'], en, am, 'am'),
                    'title_en': text_for(item['title_key'], en, am),
                    'title_am': text_for(item['title_key'], en, am, 'am'),
                    'excerpt_en': text_for(item.get('excerpt_key', ''), en, am) if item.get('excerpt_key') else '',
                    'excerpt_am': text_for(item.get('excerpt_key', ''), en, am, 'am') if item.get('excerpt_key') else '',
                    'body_en': join_paragraphs(item['body_keys'], en, am),
                    'body_am': join_paragraphs(item['body_keys'], en, am, 'am'),
                    'image_url': item['image_url'],
                    'published_at': pub,
                    'search_keywords': item['search_keywords'],
                    'is_published': True,
                    'is_featured_home': item.get('is_featured_home', False),
                    'is_featured_carousel': item.get('is_featured_carousel', False),
                    'carousel_tag_en': text_for(item.get('carousel_tag_key', ''), en, am),
                    'carousel_tag_am': text_for(item.get('carousel_tag_key', ''), en, am, 'am'),
                    'carousel_title_en': text_for(item.get('carousel_title_key', ''), en, am),
                    'carousel_title_am': text_for(item.get('carousel_title_key', ''), en, am, 'am'),
                },
            )
        self.stdout.write(f'  News articles ({len(NEWS_ARTICLES)})')

    def seed_leaders(self, en, am):
        for item in LEADERS:
            leader, _ = Leader.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'name_en': text_for(item['name_key'], en, am),
                    'name_am': text_for(item['name_key'], en, am, 'am'),
                    'role_en': text_for(item['role_key'], en, am),
                    'role_am': text_for(item['role_key'], en, am, 'am'),
                    'short_bio_en': text_for(item['bio_key'], en, am),
                    'short_bio_am': text_for(item['bio_key'], en, am, 'am'),
                    'photo_url': item['photo_url'],
                    'wide_photo': item.get('wide_photo', False),
                    'sort_order': item['sort_order'],
                    'is_published': True,
                },
            )
            leader.paragraphs.all().delete()
            for idx, key in enumerate(item['paragraph_keys']):
                LeaderParagraph.objects.create(
                    leader=leader,
                    text_en=en.get(key, ''),
                    text_am=am.get(key, ''),
                    sort_order=idx,
                )
        self.stdout.write(f'  Leaders ({len(LEADERS)})')

    def seed_gallery(self, en, am):
        album, _ = GalleryAlbum.objects.update_or_create(
            date_label_en='Photos from May 19, 2025',
            defaults={
                'date_label_am': am.get('page.gallery.date_may19', ''),
                'event_date': date(2025, 5, 19),
                'sort_order': 0,
                'is_published': True,
            },
        )
        album.images.all().delete()
        alt_en = en.get('page.gallery.alt', 'MoPD event — May 19, 2025')
        alt_am = am.get('page.gallery.alt', '')
        for idx, url in enumerate(GALLERY_IMAGES):
            GalleryImage.objects.create(
                album=album,
                image_url=url,
                alt_en=alt_en,
                alt_am=alt_am,
                sort_order=idx,
            )
        self.stdout.write('  Gallery album')

    def seed_documents(self):
        for idx, (title, url) in enumerate(CLIMATE_DOCS):
            Document.objects.update_or_create(
                doc_type=Document.DocType.CLIMATE,
                file_url=url,
                defaults={
                    'title_en': title,
                    'sort_order': idx,
                    'is_published': True,
                },
            )
        for idx, (title, url) in enumerate(STATS_DOCS):
            Document.objects.update_or_create(
                doc_type=Document.DocType.STATISTICS,
                file_url=url,
                defaults={
                    'title_en': title,
                    'sort_order': idx,
                    'is_published': True,
                },
            )
        self.stdout.write(f'  Documents ({len(CLIMATE_DOCS)} climate, {len(STATS_DOCS)} statistics)')

    def seed_carousel(self, en, am):
        slides = [
            {
                'tag_key': 'carousel.0.tag',
                'title_key': 'carousel.0.title',
                'image_url': 'https://mopd.gov.et/media/photos/2025/07/29/fs_1.jpg',
                'link_url': '/news/un-guterres/',
                'sort_order': 0,
            },
            {
                'tag_key': 'carousel.1.tag',
                'title_key': 'carousel.1.title',
                'image_url': 'https://mopd.gov.et/media/photos/2025/07/29/summi_22.jpg',
                'link_url': '/news/acs2/',
                'sort_order': 1,
            },
            {
                'tag_key': 'carousel.2.tag',
                'title_key': 'carousel.2.title',
                'image_url': 'https://mopd.gov.et/media/photos/2025/07/29/msur.jpg',
                'link_url': '/news/state-minister-acs2/',
                'sort_order': 2,
            },
        ]
        CarouselSlide.objects.all().delete()
        for slide in slides:
            CarouselSlide.objects.create(
                tag_en=text_for(slide['tag_key'], en, am),
                tag_am=text_for(slide['tag_key'], en, am, 'am'),
                title_en=text_for(slide['title_key'], en, am),
                title_am=text_for(slide['title_key'], en, am, 'am'),
                image_url=slide['image_url'],
                link_url=slide['link_url'],
                sort_order=slide['sort_order'],
                is_active=True,
            )
        self.stdout.write(f'  Carousel slides ({len(slides)})')

    def seed_affiliates(self, en, am):
        AffiliateLink.objects.all().delete()
        for idx, (name_en, url, name_key) in enumerate(AFFILIATES):
            AffiliateLink.objects.create(
                name_en=name_en,
                name_am=am.get(name_key, ''),
                url=url,
                sort_order=idx,
                is_published=True,
            )
        self.stdout.write(f'  Affiliate links ({len(AFFILIATES)})')
