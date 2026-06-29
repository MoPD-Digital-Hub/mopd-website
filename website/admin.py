from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from .models import (
    AffiliateLink,
    CarouselSlide,
    ContactSubmission,
    Department,
    Document,
    GalleryAlbum,
    GalleryImage,
    Leader,
    LeaderParagraph,
    NewsletterSubscriber,
    NewsArticle,
    ProcurementNotice,
    SiteSettings,
    SiteTranslation,
    Vacancy,
)
from .models import _fill_missing_amharic


def _image_thumb(image_field, height=40):
    if image_field:
        return format_html(
            '<img src="{}" style="height:{}px;border-radius:4px;object-fit:cover;" />',
            image_field.url,
            height,
        )
    return '—'


def _lang_preview(obj, field_base, lang_code, max_len=80):
    value = getattr(obj, f'{field_base}_{lang_code}', '') or ''
    return (value[:max_len] + '…') if len(value) > max_len else value


@admin.register(SiteSettings)
class SiteSettingsAdmin(TabbedTranslationAdmin):
    fieldsets = (
        ('Site identity', {'fields': ('site_name', 'topbar_tag')}),
        ('Contact', {'fields': ('phone', 'email', 'address')}),
        ('Social media', {'fields': ('facebook_url', 'twitter_url', 'linkedin_url')}),
        ('Footer', {'fields': ('footer_desc', 'copyright_text')}),
        ('Downloads', {'fields': ('development_plan_pdf_url', 'development_plan_cover_url')}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteTranslation)
class SiteTranslationAdmin(TabbedTranslationAdmin):
    list_display = ('key', 'preview_en', 'preview_am', 'notes')
    list_filter = ('key',)
    search_fields = ('key', 'text_en', 'text_am', 'notes')
    ordering = ('key',)
    fields = ('key', 'text', 'notes')

    @admin.display(description='English')
    def preview_en(self, obj):
        return _lang_preview(obj, 'text', 'en')

    @admin.display(description='Amharic')
    def preview_am(self, obj):
        return _lang_preview(obj, 'text', 'am')


class LeaderParagraphInline(TranslationTabularInline):
    model = LeaderParagraph
    extra = 1
    fields = ('sort_order', 'text')


@admin.register(Leader)
class LeaderAdmin(TabbedTranslationAdmin):
    list_display = ('name_en', 'role_en', 'sort_order', 'is_published', 'thumb')
    list_editable = ('sort_order', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('name_en', 'name_am', 'role_en')
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [LeaderParagraphInline]
    fieldsets = (
        (None, {'fields': ('slug', 'sort_order', 'is_published', 'wide_photo')}),
        ('Profile', {'fields': ('name', 'role', 'photo', 'photo_preview')}),
        ('Listing card bio', {'fields': ('short_bio',)}),
    )
    readonly_fields = ('photo_preview',)

    @admin.display(description='Current photo')
    def photo_preview(self, obj):
        return _image_thumb(obj.photo, 120)

    @admin.display(description='Photo')
    def thumb(self, obj):
        return _image_thumb(obj.photo)


class GalleryImageInline(TranslationTabularInline):
    model = GalleryImage
    extra = 3
    fields = ('sort_order', 'image', 'alt')


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(TabbedTranslationAdmin):
    list_display = ('date_label_en', 'event_date', 'image_count', 'sort_order', 'is_published')
    list_editable = ('sort_order', 'is_published')
    list_filter = ('is_published',)
    fields = ('date_label', 'event_date', 'sort_order', 'is_published')
    inlines = [GalleryImageInline]

    @admin.display(description='Images')
    def image_count(self, obj):
        return obj.images.count()


@admin.register(Document)
class DocumentAdmin(TabbedTranslationAdmin):
    list_display = ('title_en', 'doc_type', 'climate_category', 'sort_order', 'is_published')
    list_editable = ('sort_order', 'is_published')
    list_filter = ('doc_type', 'climate_category', 'is_published')
    search_fields = ('title_en', 'title_am', 'description_en')
    fields = ('doc_type', 'climate_category', 'title', 'description', 'file_url', 'sort_order', 'is_published')


@admin.register(CarouselSlide)
class CarouselSlideAdmin(TabbedTranslationAdmin):
    list_display = ('title_en', 'tag_en', 'sort_order', 'is_active', 'thumb')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('sort_order', 'is_active', 'link_url')}),
        ('Slide content', {'fields': ('tag', 'title')}),
        ('Image', {'fields': ('image', 'image_preview')}),
    )
    readonly_fields = ('image_preview',)

    @admin.display(description='Current image')
    def image_preview(self, obj):
        return _image_thumb(obj.image, 120)

    @admin.display(description='Image')
    def thumb(self, obj):
        return _image_thumb(obj.image, 36)


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(TabbedTranslationAdmin):
    list_display = ('name_en', 'url', 'sort_order', 'is_published', 'logo_preview')
    list_editable = ('sort_order', 'is_published')
    search_fields = ('name_en', 'name_am')
    readonly_fields = ('logo_preview',)
    fields = ('name', 'url', 'logo', 'logo_preview', 'sort_order', 'is_published')

    @admin.display(description='Logo')
    def logo_preview(self, obj):
        return _image_thumb(obj.logo, 80)


@admin.register(NewsArticle)
class NewsArticleAdmin(TabbedTranslationAdmin):
    class NewsArticleAdminForm(forms.ModelForm):
        class Meta:
            model = NewsArticle
            fields = '__all__'

        def clean(self):
            cleaned = super().clean()
            title = (
                (cleaned.get('title') or '')
                or (cleaned.get('title_en') or '')
                or (cleaned.get('title_am') or '')
            ).strip()
            if not title:
                raise ValidationError('Please enter a title on the English or Amharic tab.')
            return cleaned

    form = NewsArticleAdminForm
    list_display = ('title_en', 'article_type', 'category', 'published_at', 'is_published', 'is_featured_home', 'thumb')
    list_editable = ('is_published', 'is_featured_home')
    list_filter = ('article_type', 'category', 'is_published', 'published_at')
    search_fields = ('title_en', 'title_am', 'slug', 'search_keywords')
    prepopulated_fields = {'slug': ('title_en',)}
    date_hierarchy = 'published_at'
    fieldsets = (
        (None, {'fields': ('slug', 'article_type', 'category', 'published_at', 'is_published', 'image', 'image_preview', 'search_keywords')}),
        ('Article content', {'fields': ('title', 'excerpt', 'body')}),
        ('Tags', {'fields': ('tag',)}),
        ('Homepage', {
            'fields': ('is_featured_home',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('image_preview',)

    def save_model(self, request, obj, form, change):
        _fill_missing_amharic(
            obj,
            ('tag', 'title', 'excerpt', 'body'),
            max_lengths={'tag': 80, 'title': 500},
            defaults={'tag': 'News'},
        )
        super().save_model(request, obj, form, change)

    @admin.display(description='Current image')
    def image_preview(self, obj):
        return _image_thumb(obj.image, 120)

    @admin.display(description='Image')
    def thumb(self, obj):
        return _image_thumb(obj.image, 36)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'status', 'assigned_to', 'created_at', 'is_read')
    list_filter = ('status', 'is_read', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'subject', 'details', 'phone', 'assigned_to', 'internal_notes')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'details', 'created_at', 'updated_at')
    list_editable = ('status', 'assigned_to', 'is_read')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    actions = ('mark_new', 'mark_in_progress', 'mark_resolved', 'mark_read', 'mark_unread')
    fieldsets = (
        ('Message', {'fields': ('name', 'email', 'phone', 'subject', 'details')}),
        ('Workflow', {'fields': ('status', 'assigned_to', 'internal_notes', 'is_read')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def has_add_permission(self, request):
        return False

    @admin.action(description='Mark selected messages as new')
    def mark_new(self, request, queryset):
        updated = queryset.update(status=ContactSubmission.Status.NEW, is_read=False)
        self.message_user(request, f'{updated} message(s) marked as new.')

    @admin.action(description='Mark selected messages as in progress')
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status=ContactSubmission.Status.IN_PROGRESS, is_read=True)
        self.message_user(request, f'{updated} message(s) marked as in progress.')

    @admin.action(description='Mark selected messages as resolved')
    def mark_resolved(self, request, queryset):
        updated = queryset.update(status=ContactSubmission.Status.RESOLVED, is_read=True)
        self.message_user(request, f'{updated} message(s) marked as resolved.')

    @admin.action(description='Mark selected messages as read')
    def mark_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')

    @admin.action(description='Mark selected messages as unread')
    def mark_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'source', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'source', 'subscribed_at')
    search_fields = ('email',)
    ordering = ('-subscribed_at',)

    def has_add_permission(self, request):
        return False


@admin.register(ProcurementNotice)
class ProcurementNoticeAdmin(TabbedTranslationAdmin):
    list_display = ('title_en', 'reference', 'published_at', 'sort_order', 'is_published')
    list_editable = ('sort_order', 'is_published')
    list_filter = ('is_published', 'published_at')
    search_fields = ('title_en', 'reference', 'description_en')
    fields = ('title', 'reference', 'description', 'file_url', 'published_at', 'sort_order', 'is_published')


@admin.register(Department)
class DepartmentAdmin(TabbedTranslationAdmin):
    list_display = ('name_en', 'parent', 'sort_order', 'is_published')
    list_editable = ('sort_order', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('name_en', 'name_am')
    fields = ('name', 'description', 'parent', 'sort_order', 'is_published')


@admin.register(Vacancy)
class VacancyAdmin(TabbedTranslationAdmin):
    list_display = ('title_en', 'reference', 'deadline', 'published_at', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'published_at')
    search_fields = ('title_en', 'reference', 'location_en')
    fields = ('title', 'reference', 'location', 'description', 'file_url', 'deadline', 'published_at', 'sort_order', 'is_published')


admin.site.site_header = 'MoPD Site Administration'
admin.site.site_title = 'MoPD Admin'
admin.site.index_title = 'Manage website content'
