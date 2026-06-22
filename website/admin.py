import json

from django.contrib import admin
from django.utils.html import format_html

from .models import (
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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Site identity', {'fields': ('site_name_en', 'site_name_am', 'topbar_tag_en', 'topbar_tag_am')}),
        ('Contact', {'fields': ('phone', 'email', 'address_en', 'address_am')}),
        ('Social media', {'fields': ('facebook_url', 'twitter_url', 'linkedin_url')}),
        ('Footer', {'fields': ('footer_desc_en', 'footer_desc_am', 'copyright_text_en', 'copyright_text_am')}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteTranslation)
class SiteTranslationAdmin(admin.ModelAdmin):
    list_display = ('key', 'preview_en', 'preview_am', 'notes')
    list_filter = ('key',)
    search_fields = ('key', 'text_en', 'text_am', 'notes')
    ordering = ('key',)

    @admin.display(description='English')
    def preview_en(self, obj):
        return (obj.text_en[:80] + '…') if len(obj.text_en) > 80 else obj.text_en

    @admin.display(description='Amharic')
    def preview_am(self, obj):
        return (obj.text_am[:80] + '…') if len(obj.text_am) > 80 else obj.text_am


class LeaderParagraphInline(admin.TabularInline):
    model = LeaderParagraph
    extra = 1
    fields = ('sort_order', 'text_en', 'text_am')


@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'role_en', 'sort_order', 'is_published', 'thumb')
    list_editable = ('sort_order', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('name_en', 'name_am', 'role_en')
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [LeaderParagraphInline]
    fieldsets = (
        (None, {'fields': ('slug', 'sort_order', 'is_published', 'wide_photo')}),
        ('Profile', {'fields': ('name_en', 'name_am', 'role_en', 'role_am', 'photo_url')}),
        ('Listing card bio', {'fields': ('short_bio_en', 'short_bio_am')}),
    )

    @admin.display(description='Photo')
    def thumb(self, obj):
        return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', obj.photo_url)


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 3
    fields = ('sort_order', 'image_url', 'alt_en', 'alt_am')


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ('date_label_en', 'event_date', 'image_count', 'sort_order', 'is_published')
    list_editable = ('sort_order', 'is_published')
    list_filter = ('is_published',)
    inlines = [GalleryImageInline]

    @admin.display(description='Images')
    def image_count(self, obj):
        return obj.images.count()


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'doc_type', 'sort_order', 'is_published')
    list_editable = ('sort_order', 'is_published')
    list_filter = ('doc_type', 'is_published')
    search_fields = ('title_en', 'title_am', 'description_en')


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'tag_en', 'sort_order', 'is_active', 'thumb')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('is_active',)

    @admin.display(description='Image')
    def thumb(self, obj):
        return format_html('<img src="{}" style="height:36px;border-radius:4px;" />', obj.image_url)


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'url', 'sort_order', 'is_published')
    list_editable = ('sort_order', 'is_published')
    search_fields = ('name_en', 'name_am')


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'category', 'published_at', 'is_published', 'is_featured_home', 'is_featured_carousel', 'thumb')
    list_editable = ('is_published', 'is_featured_home', 'is_featured_carousel')
    list_filter = ('category', 'is_published', 'published_at')
    search_fields = ('title_en', 'title_am', 'slug', 'search_keywords')
    prepopulated_fields = {'slug': ('title_en',)}
    date_hierarchy = 'published_at'
    fieldsets = (
        (None, {'fields': ('slug', 'category', 'published_at', 'is_published', 'image_url', 'search_keywords')}),
        ('Tags', {'fields': ('tag_en', 'tag_am')}),
        ('Article content', {'fields': ('title_en', 'title_am', 'excerpt_en', 'excerpt_am', 'body_en', 'body_am')}),
        ('Homepage placement', {
            'fields': ('is_featured_home', 'is_featured_carousel', 'carousel_tag_en', 'carousel_tag_am', 'carousel_title_en', 'carousel_title_am'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Image')
    def thumb(self, obj):
        return format_html('<img src="{}" style="height:36px;border-radius:4px;" />', obj.image_url)


admin.site.site_header = 'MoPD Site Administration'
admin.site.site_title = 'MoPD Admin'
admin.site.index_title = 'Manage website content'
