import os

from django.db import models
from django.utils.text import slugify

from website.news_content import card_excerpt, filter_paragraphs, is_junk_paragraph


def _fill_missing_amharic(instance, fields, *, max_lengths=None, defaults=None):
    """Ensure *_en / *_am / base columns are non-null before insert."""
    max_lengths = max_lengths or {}
    defaults = defaults or {}
    for field in fields:
        base = getattr(instance, field, None)
        en = getattr(instance, f'{field}_en', None)
        am = getattr(instance, f'{field}_am', None)

        primary = en if en not in (None, '') else base
        if primary in (None, '') or (isinstance(primary, str) and not primary.strip()):
            primary = defaults.get(field, '')

        if en in (None, '') or (isinstance(en, str) and not en.strip()):
            en = primary
        if base in (None, '') or (isinstance(base, str) and not base.strip()):
            base = en or primary
        if am in (None, '') or (isinstance(am, str) and not am.strip()):
            am = en or base or defaults.get(field, '')

        limit = max_lengths.get(field)
        if limit:
            base = (base or '')[:limit]
            en = (en or '')[:limit]
            am = (am or '')[:limit]

        setattr(instance, field, base or '')
        setattr(instance, f'{field}_en', en or '')
        setattr(instance, f'{field}_am', am or '')


def _ext(filename):
    return os.path.splitext(filename)[1] or '.jpg'


def news_image_upload(instance, filename):
    return f'news/{instance.slug}{_ext(filename)}'


def leader_photo_upload(instance, filename):
    return f'leaders/{instance.slug}{_ext(filename)}'


def gallery_image_upload(instance, filename):
    return f'gallery/{instance.album_id}/{instance.sort_order}_{os.path.basename(filename)}'


def carousel_image_upload(instance, filename):
    return f'carousel/{instance.sort_order}_{os.path.basename(filename)}'


def affiliate_logo_upload(instance, filename):
    slug = slugify(instance.name_en) or 'affiliate'
    return f'affiliates/{slug}{_ext(filename)}'


class SiteSettings(models.Model):
    """Singleton site-wide settings (edit only the first row)."""
    site_name = models.CharField(max_length=200, default='Ministry of Planning and Development')
    topbar_tag = models.CharField(max_length=200, default='Federal Democratic Republic of Ethiopia')
    phone = models.CharField(max_length=40, default='011 140 3049')
    email = models.EmailField(default='info@mopd.gov.et')
    address = models.CharField(max_length=255, blank=True, default='6 Kilo, Addis Ababa, Ethiopia')
    facebook_url = models.URLField(blank=True, default='https://www.facebook.com/MoPDETH')
    twitter_url = models.URLField(blank=True, default='https://twitter.com/mopd_ethiopia')
    linkedin_url = models.URLField(blank=True, default='https://www.linkedin.com/company/ministry-of-planning-and-development-ethiopia/')
    copyright_text = models.CharField(max_length=255, default='© 2026 Ministry of Planning and Development. All rights reserved.')
    footer_desc = models.TextField(blank=True)
    development_plan_pdf_url = models.URLField(
        blank=True,
        default='/media/ten-year-document/ten_year_development_plan.pdf',
        help_text='10-Year Development Plan PDF (local /media/ path preferred)',
    )
    development_plan_cover_url = models.URLField(
        blank=True,
        default='',
        help_text='Cover image URL for the 10-Year Development Plan. Leave empty for the default bundled cover.',
    )

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return 'Site settings'

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def development_plan_cover(self):
        if self.development_plan_cover_url:
            return self.development_plan_cover_url
        return '/media/10-year-plan-cover.jpg'


class SiteTranslation(models.Model):
    """UI labels and static page copy — keys match data-i18n attributes."""
    key = models.CharField(max_length=120, unique=True, db_index=True)
    text = models.TextField(blank=True)
    notes = models.CharField(max_length=200, blank=True, help_text='Admin note only')

    class Meta:
        ordering = ['key']
        verbose_name = 'Translation'
        verbose_name_plural = 'Translations (UI & page copy)'

    def __str__(self):
        return self.key


class NewsArticle(models.Model):
    CATEGORY_CHOICES = [
        ('politics', 'Politics'),
        ('climate', 'Climate'),
        ('economic', 'Economic'),
        ('policy', 'Policy'),
        ('demography', 'Demography'),
        ('social', 'Social'),
        ('others', 'Others'),
    ]

    source_path = models.CharField(
        max_length=300,
        unique=True,
        blank=True,
        null=True,
        help_text='Original article path on mopd.gov.et',
    )
    slug = models.SlugField(unique=True, max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    tag = models.CharField(max_length=80, default='News')
    title = models.CharField(max_length=500)
    excerpt = models.TextField(blank=True)
    body = models.TextField(help_text='Separate paragraphs with a blank line')
    image = models.ImageField(upload_to=news_image_upload, blank=True)
    published_at = models.DateField()
    search_keywords = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    is_featured_home = models.BooleanField(default=False, help_text='Show on homepage news section')
    article_type = models.CharField(
        max_length=20,
        choices=[('news', 'News'), ('press_release', 'Press release')],
        default='news',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    telegram_notified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this article was posted to Telegram',
    )

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'News article'
        verbose_name_plural = 'News articles'

    def __str__(self):
        title = (self.title_en or self.title or self.title_am or '').strip()
        if not title:
            if self.slug:
                return self.slug.replace('-', ' ').title()
            return f'Article #{self.pk}' if self.pk else 'New article'
        if len(title) > 80:
            return f'{title[:77]}…'
        return title

    def save(self, *args, **kwargs):
        _fill_missing_amharic(
            self,
            ('tag', 'title', 'excerpt', 'body'),
            max_lengths={'tag': 80, 'title': 500},
            defaults={'tag': 'News'},
        )
        super().save(*args, **kwargs)

    def body_paragraphs_en(self):
        return [p.strip() for p in self.body_en.split('\n\n') if p.strip()]

    def body_paragraphs_am(self):
        return [p.strip() for p in self.body_am.split('\n\n') if p.strip()]

    @property
    def card_excerpt_en(self):
        return card_excerpt(self.title_en, self.excerpt_en, filter_paragraphs(self.body_paragraphs_en()))

    @property
    def card_excerpt_am(self):
        if self.excerpt_am or self.body_am:
            return card_excerpt(
                self.title_am or self.title_en,
                self.excerpt_am,
                filter_paragraphs(self.body_paragraphs_am()),
            )
        return self.card_excerpt_en

    @property
    def body_pairs(self):
        en_parts = self.body_paragraphs_en()
        am_parts = self.body_paragraphs_am()
        pairs = [(e, am_parts[i] if i < len(am_parts) else e) for i, e in enumerate(en_parts)]
        return [(e, a) for e, a in pairs if not is_junk_paragraph(e)]


class Leader(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=120)
    short_bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to=leader_photo_upload, blank=True)
    wide_photo = models.BooleanField(default=False, help_text='Use landscape crop on listing card')
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name_en']
        verbose_name = 'Leader'
        verbose_name_plural = 'Leadership profiles'

    def __str__(self):
        return self.name_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)


class LeaderParagraph(models.Model):
    leader = models.ForeignKey(Leader, related_name='paragraphs', on_delete=models.CASCADE)
    text = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
        verbose_name = 'Profile paragraph'
        verbose_name_plural = 'Profile paragraphs'


class GalleryAlbum(models.Model):
    date_label = models.CharField(max_length=120, help_text='e.g. Photos from May 19, 2025')
    event_date = models.DateField(null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-event_date', 'sort_order']
        verbose_name = 'Gallery album'
        verbose_name_plural = 'Gallery albums'

    def __str__(self):
        return self.date_label_en


class GalleryImage(models.Model):
    album = models.ForeignKey(GalleryAlbum, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=gallery_image_upload, blank=True)
    alt = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
        verbose_name = 'Gallery image'
        verbose_name_plural = 'Gallery images'

    def __str__(self):
        return self.alt_en or (self.image.name if self.image else 'Gallery image')


class Document(models.Model):
    class DocType(models.TextChoices):
        CLIMATE = 'climate', 'Climate documents'
        STATISTICS = 'statistics', 'Statistics documents'

    class ClimateCategory(models.TextChoices):
        MULTILATERAL = 'multilateral', 'Multilateral Agreements'
        STRATEGIES = 'strategies', 'Strategies & Plans'
        PROJECTS = 'projects', 'Projects & Programs'
        REPORTS = 'reports', 'Reports and Submissions'
        COP28 = 'cop28', 'COP28'

    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    climate_category = models.CharField(
        max_length=20,
        choices=ClimateCategory.choices,
        blank=True,
        help_text='Used for climate documents only (tab grouping on the climate documents page).',
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    file_url = models.URLField()
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['doc_type', 'sort_order', 'title']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents (climate & statistics)'

    def __str__(self):
        return f'{self.get_doc_type_display()}: {self.display_title_en}'

    @property
    def display_title_en(self):
        return self.title_en or self.__dict__.get('title') or ''

    @property
    def display_title_am(self):
        return self.title_am or self.display_title_en


class ContactSubmission(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In progress'
        RESOLVED = 'resolved', 'Resolved'

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=200)
    details = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    assigned_to = models.CharField(max_length=120, blank=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact message'
        verbose_name_plural = 'Contact messages'

    def __str__(self):
        return f'{self.subject} — {self.name}'


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=40, default='homepage', blank=True)

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter subscriber'
        verbose_name_plural = 'Newsletter subscribers'

    def __str__(self):
        return self.email


class ProcurementNotice(models.Model):
    title = models.CharField(max_length=300)
    reference = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    file_url = models.URLField(blank=True)
    published_at = models.DateField()
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_at', 'sort_order']
        verbose_name = 'Procurement notice'
        verbose_name_plural = 'Procurement notices'

    def __str__(self):
        return self.title_en or self.title


class Department(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE,
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments (organogram)'

    def __str__(self):
        return self.name_en or self.name


class Vacancy(models.Model):
    title = models.CharField(max_length=300)
    reference = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    file_url = models.URLField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    published_at = models.DateField()
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_at', 'sort_order']
        verbose_name = 'Vacancy'
        verbose_name_plural = 'Vacancies'

    def __str__(self):
        return self.title_en or self.title


class CarouselSlide(models.Model):
    tag = models.CharField(max_length=80, blank=True)
    title = models.CharField(max_length=300)
    image = models.ImageField(upload_to=carousel_image_upload, blank=True)
    link_url = models.CharField(max_length=300, blank=True, help_text='Internal path or full URL')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order']
        verbose_name = 'Homepage carousel slide'
        verbose_name_plural = 'Homepage carousel slides'

    def __str__(self):
        return self.title_en


class AffiliateLink(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    logo = models.ImageField(upload_to=affiliate_logo_upload, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name_en']
        verbose_name = 'Affiliate link'
        verbose_name_plural = 'Affiliate links (footer)'

    def __str__(self):
        return self.name_en
