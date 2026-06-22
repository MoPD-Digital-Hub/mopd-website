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
| News articles | Full articles with bilingual body text |
| Leadership profiles | Minister & state ministers with bio paragraphs |
| Gallery albums | Photo albums and images |
| Documents | Climate & statistics PDF links |
| Homepage carousel slides | Hero carousel tags, titles, images, links |
| Affiliate links | Footer partner organizations |

Re-seed default content from legacy files:

```bash
python manage.py seed_site --clear
```

## Project layout

```
MOPD/
├── config/           # Django settings & root URLs
├── website/          # Main app (views, models, templates)
├── static/           # CSS, JS, images
├── legacy_html/      # Original static HTML (reference)
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

Client-side Amharic/English switching via `static/js/i18n.js` (unchanged from static site).
