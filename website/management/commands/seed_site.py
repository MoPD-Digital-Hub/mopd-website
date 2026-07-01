import html
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from website.media_utils import assign_image_from_url
from website.models import (
    AffiliateLink,
    CarouselSlide,
    Department,
    Document,
    GalleryAlbum,
    GalleryImage,
    Leader,
    LeaderParagraph,
    NewsArticle,
    ProcurementNotice,
    SiteSettings,
    SiteTranslation,
)

I18N_PATTERN = re.compile(
    r'data-i18n(?:-html)?="([^"]+)"[^>]*>(.*?)</',
    re.DOTALL | re.IGNORECASE,
)

CLIMATE_DOCS = [
    ('The Addis Ababa Declaration on Climate Change & Call to Action', 'https://mopd.gov.et/media/climate-documents/Climate_Change_Declaration.pdf', 'multilateral'),
    ('The Addis Ababa Declaration on Climate Change & Call to Action (African Leaders)', 'https://mopd.gov.et/media/climate-documents/45822-pr-African_Leaders_Addis_Ababa_Declaration_on_Climate_Change_and_hU6SHOs.pdf', 'multilateral'),
    ('UNFCCC — United Nations Framework Convention on Climate Change', 'https://mopd.gov.et/media/climate-documents/UNFCCC_United_Nations_Framework_Convention_on_Climate_Change.pdf', 'multilateral'),
    ('Kyoto Protocol', 'https://mopd.gov.et/media/climate-documents/Kyoto_Protocol.pdf', 'multilateral'),
    ('Paris Agreement', 'https://mopd.gov.et/media/climate-documents/Paris_Agreement.pdf', 'multilateral'),
    ('Ethiopia Carbon Market Strategy (2025)', 'https://mopd.gov.et/media/climate-documents/Ethiopia_Carbon-Market-Strategy_2025.pdf', 'strategies'),
    ('NAP-ETH 2019', 'https://mopd.gov.et/media/climate-documents/NAP-ETH_2019.pdf', 'strategies'),
    ("Ethiopia's Updated NDC — July 2021 Submission", 'https://mopd.gov.et/media/climate-documents/Ethiopias_updated_NDC_JULY_2021_Submission_.pdf', 'strategies'),
    ('Ethiopia Long-Term Low Emission and Climate Resilient Development Strategy', 'https://mopd.gov.et/media/climate-documents/ETHIOPIA__LONG_TERM_LOW_EMISSION_AND_CLIMATE_RESILIENT_DEVELOPMENT_STR_RGJXrpV.pdf', 'strategies'),
    ('CRGE Sector-Region Mainstreaming Guideline — Jan 2019', 'https://mopd.gov.et/media/climate-documents/CRGE_Sector-Region_Mainstreaming_Guideline-Final_Jan_2019.pdf', 'strategies'),
    ('CRGE Strategy 2011', 'https://mopd.gov.et/media/climate-documents/crge-strategy_2011.pdf', 'strategies'),
    ('Profiles of GEF and GCF Projects in Ethiopia', 'https://mopd.gov.et/media/climate-documents/25.7.24._GEFGCF_projects_profile_in_Ethiopia_WlleSLV.pdf', 'projects'),
    ('List of Implemented Projects — CRGE Progress 2011–2019', 'https://mopd.gov.et/media/climate-documents/List_of_Implemented_Projects_CRGE_Progress_in_Implementing_the_CRGE_ND_UumPJzB.pdf', 'projects'),
    ('GEF & GCF Projects Profile in Ethiopia — July 2023', 'https://mopd.gov.et/media/climate-documents/GEFGCF_projects_profile_in_Ethiopia_July_2023.pdf', 'projects'),
    ('CRGE Strategy — Progress in Implementing 2011–2019', 'https://mopd.gov.et/media/climate-documents/CRGE_Strategy___Progress_in_Implementing_-_2011-2019__2020.pdf', 'reports'),
    ("Ethiopia's 2nd National Communication", 'https://mopd.gov.et/media/climate-documents/Ethiopias_2nd_National_Communication.pdf', 'reports'),
    ("Ethiopia's 3rd National Communication (2023)", 'https://mopd.gov.et/media/climate-documents/Ethiopias_3rd_National_Communication_2023.pdf', 'reports'),
    ("Ethiopia's Initial National Communication (2001)", 'https://mopd.gov.et/media/climate-documents/Ethiopias_Initial_National_Communication_2001.pdf', 'reports'),
    ('Side Events at the Ethiopian Pavilion on COP28', 'https://mopd.gov.et/media/climate-documents/List_of_Side_Events_Ethiopia_9_Nov_2023.pdf', 'cop28'),
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

LEADERS = [
    {
        'slug': 'fitsum-assefa',
        'name_key': 'leader.0.name',
        'role_key': 'leader.0.role',
        'bio_key': 'leader.0.bio',
        'photo_src': 'https://mopd.gov.et/media/photos/2025/06/25/G92A3209_fVjDvC6.jpg',
        'paragraph_keys': ['page.leader1.p1', 'page.leader1.p2', 'page.leader1.p3'],
        'sort_order': 0,
    },
    {
        'slug': 'bereket-fesehatsion',
        'name_key': 'leader.1.name',
        'role_key': 'leader.1.role',
        'bio_key': 'leader.1.bio',
        'photo_src': 'https://mopd.gov.et/media/photos/2024/10/08/photo_2024-12320-08_11-20-54.png',
        'paragraph_keys': ['leader.1.bio', 'page.leader2.p1'],
        'sort_order': 1,
    },
    {
        'slug': 'tirumar-abate',
        'name_key': 'leader.2.name',
        'role_key': 'leader.2.role',
        'bio_key': 'leader.2.bio',
        'photo_src': 'https://mopd.gov.et/media/photos/2023/06/27/Tirumar-Abate-1-768x609.jpg',
        'paragraph_keys': ['page.leader4.p1', 'leader.2.bio'],
        'wide_photo': True,
        'sort_order': 2,
    },
    {
        'slug': 'seyum-mekonen',
        'name_key': 'leader.3.name',
        'role_key': 'leader.3.role',
        'bio_key': 'leader.3.bio',
        'photo_src': 'https://mopd.gov.et/media/photos/2024/03/06/WhatsApp_Image_2024-02-16_at_14.15.47_7c28a19d.jpg',
        'paragraph_keys': ['leader.3.bio', 'page.leader3.p1'],
        'sort_order': 3,
    },
]

AFFILIATES = [
    (
        'Environmental Protection Authority',
        'https://www.epa.gov.et/',
        'affiliate.epa',
        'https://mopd.gov.et/media/photos/2025/01/09/epa-removebg-preview.png',
    ),
    (
        'Central Statistics Service',
        'http://www.csa.gov.et/',
        'affiliate.csa',
        'https://mopd.gov.et/media/photos/2025/01/09/photo_2025-01-09_13-42-42-removebg-preview.png',
    ),
    (
        'Policy Study Institute',
        'https://psi.org.et',
        'affiliate.psi',
        'https://mopd.gov.et/media/photos/2025/01/09/logo-psi-400x100-1-removebg-preview.png',
    ),
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
    root = Path(settings.BASE_DIR) / 'website' / 'templates'
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


def local_leader_photo_name(slug, source_url):
    suffix = Path(urlparse(source_url).path).suffix or '.jpg'
    media_name = f'leaders/{slug}{suffix}'
    if (Path(settings.MEDIA_ROOT) / media_name).exists():
        return media_name
    return ''


class Command(BaseCommand):
    help = 'Seed site settings, translations, news, leaders, gallery, documents, carousel, and affiliates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing content before seeding',
        )
        parser.add_argument(
            '--skip-news',
            action='store_true',
            help='Skip syncing news from mopd.gov.et (useful when offline)',
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
        if not options.get('skip_news'):
            self.seed_news()
        else:
            self.stdout.write('  News (skipped — --skip-news flag set)')
        self.seed_leaders(en, am)
        self.seed_gallery(en, am)
        self.seed_documents()
        self.seed_departments()
        self.seed_procurement()
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
        settings_obj.development_plan_pdf_url = (
            'https://mopd.gov.et/media/ten-year-document/ten_year_development_plan.pdf'
        )
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

    def seed_news(self):
        call_command('sync_official_news', featured=3)

    def seed_leaders(self, en, am):
        for item in LEADERS:
            leader = Leader.objects.filter(slug=item['slug']).first()
            if leader is None:
                leader = Leader(slug=item['slug'])
            leader.name_en = text_for(item['name_key'], en, am)
            leader.name_am = text_for(item['name_key'], en, am, 'am')
            leader.role_en = text_for(item['role_key'], en, am)
            leader.role_am = text_for(item['role_key'], en, am, 'am')
            leader.short_bio_en = text_for(item['bio_key'], en, am)
            leader.short_bio_am = text_for(item['bio_key'], en, am, 'am')
            leader.wide_photo = item.get('wide_photo', False)
            leader.sort_order = item['sort_order']
            leader.is_published = True
            if item.get('photo_src'):
                local_photo = local_leader_photo_name(item['slug'], item['photo_src'])
                if local_photo:
                    leader.photo.name = local_photo
                elif not assign_image_from_url(leader, 'photo', item['photo_src']):
                    leader.photo = ''
            leader.save()
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
            image = GalleryImage(
                album=album,
                alt_en=alt_en,
                alt_am=alt_am,
                sort_order=idx,
            )
            assign_image_from_url(image, 'image', url)
            image.save()
        self.stdout.write('  Gallery album')

    def seed_documents(self):
        for idx, (title, url, category) in enumerate(CLIMATE_DOCS):
            Document.objects.update_or_create(
                doc_type=Document.DocType.CLIMATE,
                file_url=url,
                defaults={
                    'title': title,
                    'title_en': title,
                    'title_am': '',
                    'description': '',
                    'description_en': '',
                    'description_am': '',
                    'climate_category': category,
                    'sort_order': idx,
                    'is_published': True,
                },
            )
        for idx, (title, url) in enumerate(STATS_DOCS):
            Document.objects.update_or_create(
                doc_type=Document.DocType.STATISTICS,
                file_url=url,
                defaults={
                    'title': title,
                    'title_en': title,
                    'title_am': '',
                    'description': '',
                    'description_en': '',
                    'description_am': '',
                    'sort_order': idx,
                    'is_published': True,
                },
            )
        self.stdout.write(f'  Documents ({len(CLIMATE_DOCS)} climate, {len(STATS_DOCS)} statistics)')

    def seed_departments(self):
        if Department.objects.exists():
            self.stdout.write('  Departments (skipped — already exist)')
            return
        core, _ = Department.objects.get_or_create(
            name_en='Office of the Minister',
            defaults={'name': 'Office of the Minister', 'sort_order': 0, 'is_published': True},
        )
        units = [
            ('Macroeconomic Planning Directorate', 'National macro planning and policy coordination.'),
            ('Sectoral Planning Directorate', 'Sector development plans and program alignment.'),
            ('Monitoring & Evaluation Directorate', 'Project and program performance tracking.'),
            ('Climate Change & Green Economy Directorate', 'Climate policy integration and CRGE implementation.'),
        ]
        for idx, (name, desc) in enumerate(units, start=1):
            Department.objects.create(
                name=name,
                name_en=name,
                description=desc,
                description_en=desc,
                parent=core,
                sort_order=idx,
                is_published=True,
            )
        self.stdout.write(f'  Departments ({1 + len(units)} units)')

    def seed_procurement(self):
        if ProcurementNotice.objects.exists():
            self.stdout.write('  Procurement (skipped — already exist)')
            return
        ProcurementNotice.objects.create(
            title='Public Procurement Notice — Planning Systems Upgrade',
            title_en='Public Procurement Notice — Planning Systems Upgrade',
            reference='MoPD/PROC/2025/01',
            description_en='Invitation for qualified suppliers to participate in the national planning information systems upgrade.',
            published_at=date(2025, 3, 15),
            is_published=True,
        )
        self.stdout.write('  Procurement (1 notice)')

    def seed_carousel(self, en, am):
        slides = [
            {
                'tag_key': 'carousel.0.tag',
                'title_key': 'carousel.0.title',
                'image_src': 'https://mopd.gov.et/media/photos/2025/07/29/fs_1.jpg',
                'link_url': '/news/un-guterres/',
                'sort_order': 0,
            },
            {
                'tag_key': 'carousel.1.tag',
                'title_key': 'carousel.1.title',
                'image_src': 'https://mopd.gov.et/media/photos/2025/07/29/summi_22.jpg',
                'link_url': '/news/acs2/',
                'sort_order': 1,
            },
            {
                'tag_key': 'carousel.2.tag',
                'title_key': 'carousel.2.title',
                'image_src': 'https://mopd.gov.et/media/photos/2025/07/29/msur.jpg',
                'link_url': '/news/state-minister-acs2/',
                'sort_order': 2,
            },
        ]
        CarouselSlide.objects.all().delete()
        for slide in slides:
            obj = CarouselSlide(
                tag_en=text_for(slide['tag_key'], en, am),
                tag_am=text_for(slide['tag_key'], en, am, 'am'),
                title_en=text_for(slide['title_key'], en, am),
                title_am=text_for(slide['title_key'], en, am, 'am'),
                link_url=slide['link_url'],
                sort_order=slide['sort_order'],
                is_active=True,
            )
            assign_image_from_url(obj, 'image', slide['image_src'])
            obj.save()
        self.stdout.write(f'  Carousel slides ({len(slides)})')

    def seed_affiliates(self, en, am):
        AffiliateLink.objects.all().delete()
        for idx, (name_en, url, name_key, logo_url) in enumerate(AFFILIATES):
            affiliate = AffiliateLink(
                name_en=name_en,
                name_am=am.get(name_key, ''),
                url=url,
                sort_order=idx,
                is_published=True,
            )
            assign_image_from_url(affiliate, 'logo', logo_url)
            affiliate.save()
        self.stdout.write(f'  Affiliate links ({len(AFFILIATES)})')
