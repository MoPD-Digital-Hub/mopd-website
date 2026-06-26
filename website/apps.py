from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'
    verbose_name = 'Website content'

    def ready(self):
        from . import signals  # noqa: F401
        from . import translation  # noqa: F401
