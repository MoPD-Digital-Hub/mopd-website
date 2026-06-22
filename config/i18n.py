"""
Site languages for django-modeltranslation.

To add a language:
  1. Add a tuple to LANGUAGES below (and MODELTRANSLATION_LANGUAGES).
  2. If Django does not know the code, add an entry to EXTRA_LANG_INFO below.
  3. Run: python manage.py makemigrations && python manage.py migrate
     (or: python manage.py sync_translation_fields --noinput)
  4. Fill translations in Django admin (fields appear per language).
  5. Add client UI strings to static/js/i18n.js under the new language code.
  6. Optionally add a short label to LANG_BUTTON_LABELS for the top-bar switcher.
"""
import django.conf.locale
from django.utils.translation import gettext_lazy as _

# Default language must be first in MODELTRANSLATION_LANGUAGES.
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'

MODELTRANSLATION_LANGUAGES = ('en', 'am')

LANGUAGES = [
    ('en', _('English')),
    ('am', _('Amharic')),
]

# Languages not in Django's built-in LANG_INFO (required for admin / get_language_info).
EXTRA_LANG_INFO = {
    'am': {
        'bidi': False,
        'code': 'am',
        'name': 'Amharic',
        'name_local': 'አማርኛ',
    },
}

django.conf.locale.LANG_INFO = dict(django.conf.locale.LANG_INFO, **EXTRA_LANG_INFO)

# Short labels for the client-side language switcher (top bar).
LANG_BUTTON_LABELS = {
    'en': 'EN',
    'am': 'አማ',
}
