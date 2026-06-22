# MoPD — Ministry of Planning and Development

Django website for the Ministry of Planning and Development (Ethiopia).

## Quick start

```bash
cd /home/mopd/Desktop/MOPD
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_site
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Admin

Manage all site content at **http://127.0.0.1:8000/admin/** after creating a superuser:

```bash
python manage.py createsuperuser
```

| Section | What you can edit |
|---------|-------------------|
| Site settings | Phone, email, social links, footer text |
| Translations | All UI labels and static page copy (EN/AM) |
| News articles | Full articles with bilingual body text (sync from mopd.gov.et via `sync_official_news`) |
| Leadership profiles | Minister & state ministers with bio paragraphs |
| Gallery albums | Photo albums and images |
| Documents | Climate & statistics PDF links |
| Homepage carousel slides | Hero carousel tags, titles, images, links |
| Affiliate links | Footer partner organizations |

Re-seed default content:

```bash
python manage.py seed_site --clear
```

Sync news only from the official site:

```bash
python manage.py sync_official_news
```

## Project layout

```
MOPD/
├── config/           # Django settings & root URLs
├── website/          # Main app (views, models, templates)
├── static/           # CSS, JS, images (picture/)
├── media/            # Uploaded CMS images (gitignored)
└── manage.py
```

## URLs

| Page | URL |
|------|-----|
| Home | `/` |
| News listing | `/news/` |
| News article | `/news/<slug>/` |
| About | `/about/` |
| Contact | `/contact/` |

Old `.html` paths redirect automatically (e.g. `/news.html` → `/news/`).

## Language

The site uses [django-modeltranslation](https://django-modeltranslation.readthedocs.io/en/latest/) for CMS content (news, leaders, settings, etc.) and client-side switching via `static/js/i18n.js` for UI labels.

**Current languages:** English (`en`) and Amharic (`am`), configured in `config/i18n.py`.

### Adding a language

1. Edit `config/i18n.py`:
   - Add the code to `MODELTRANSLATION_LANGUAGES` (keep `en` first).
   - Add a `('code', _('Name'))` entry to `LANGUAGES`.
   - If Django does not recognize the code, add it to `EXTRA_LANG_INFO` (see the `am` example).
   - Optionally set a short label in `LANG_BUTTON_LABELS` for the top-bar switcher.
2. Create database columns for the new language:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
   If you prefer raw SQL (e.g. third-party apps), you can use `python manage.py sync_translation_fields --noinput` instead of makemigrations.
3. Open Django admin — translatable models show a tab per language. Fill in the new fields.
4. For static UI strings (nav, buttons, etc.), add a block under that code in `static/js/i18n.js` (same shape as the existing `am` object).
5. Templates that use `data-en` / `data-am` on `.bilingual` elements may need `data-<code>` attributes for the new language.

Re-seed or sync commands (`seed_site`, `sync_official_news`) continue to work; they write English via `*_en` fields and Amharic via `*_am` where available.
