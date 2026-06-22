from modeltranslation.translator import TranslationOptions, translator

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


class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ('site_name', 'topbar_tag', 'address', 'copyright_text', 'footer_desc')


class SiteTranslationTranslationOptions(TranslationOptions):
    fields = ('text',)


class NewsArticleTranslationOptions(TranslationOptions):
    fields = ('tag', 'title', 'excerpt', 'body')


class LeaderTranslationOptions(TranslationOptions):
    fields = ('name', 'role', 'short_bio')


class LeaderParagraphTranslationOptions(TranslationOptions):
    fields = ('text',)


class GalleryAlbumTranslationOptions(TranslationOptions):
    fields = ('date_label',)


class GalleryImageTranslationOptions(TranslationOptions):
    fields = ('alt',)


class DocumentTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


class CarouselSlideTranslationOptions(TranslationOptions):
    fields = ('tag', 'title')


class AffiliateLinkTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(SiteSettings, SiteSettingsTranslationOptions)
translator.register(SiteTranslation, SiteTranslationTranslationOptions)
translator.register(NewsArticle, NewsArticleTranslationOptions)
translator.register(Leader, LeaderTranslationOptions)
translator.register(LeaderParagraph, LeaderParagraphTranslationOptions)
translator.register(GalleryAlbum, GalleryAlbumTranslationOptions)
translator.register(GalleryImage, GalleryImageTranslationOptions)
translator.register(Document, DocumentTranslationOptions)
translator.register(CarouselSlide, CarouselSlideTranslationOptions)
translator.register(AffiliateLink, AffiliateLinkTranslationOptions)
