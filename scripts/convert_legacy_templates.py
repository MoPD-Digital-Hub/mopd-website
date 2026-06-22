#!/usr/bin/env python3
"""Convert legacy HTML files to Django templates."""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
LEGACY = BASE / 'legacy_html'
OUT_PAGES = BASE / 'website' / 'templates' / 'website' / 'pages'

URL_MAP = {
    'index.html': "{% url 'home' %}",
    'about.html': "{% url 'about' %}",
    'contact.html': "{% url 'contact' %}",
    'news.html': "{% url 'news' %}",
    'leadership.html': "{% url 'leadership' %}",
    'leader-1.html': "{% url 'leader_1' %}",
    'leader-2.html': "{% url 'leader_2' %}",
    'leader-3.html': "{% url 'leader_3' %}",
    'leader-4.html': "{% url 'leader_4' %}",
    'gallery.html': "{% url 'gallery' %}",
    'press-release.html': "{% url 'press' %}",
    'about-climate.html': "{% url 'climate' %}",
    'climate-documents.html': "{% url 'climate_docs' %}",
    'green-technology.html': "{% url 'green_tech' %}",
    'statistics-documents.html': "{% url 'stats' %}",
    'development-planning.html': "{% url 'devplan' %}",
    'news-un-guterres.html': "{% url 'news_detail' 'un-guterres' %}",
    'news-acs2.html': "{% url 'news_detail' 'acs2' %}",
    'news-state-minister-acs2.html': "{% url 'news_detail' 'state-minister-acs2' %}",
    'news-france-acs2.html': "{% url 'news_detail' 'france-acs2' %}",
    'news-donors-green.html': "{% url 'news_detail' 'donors-green' %}",
    'news-aprm-session.html': "{% url 'news_detail' 'aprm-session' %}",
    'news-procurement.html': "{% url 'news_detail' 'procurement' %}",
    'news-finance-cop28.html': "{% url 'news_detail' 'finance-cop28' %}",
}

PAGE_META = {
    'about.html': ('About MoPD — Ministry of Planning and Development', 'about', 'Learn about the Ministry of Planning and Development (MoPD).'),
    'contact.html': ('Contact — Ministry of Planning and Development', 'contact', 'Contact the Ministry of Planning and Development, Ethiopia.'),
    'leadership.html': ('Leadership — MoPD', 'leadership', 'Ministry leadership and management.'),
    'leader-1.html': ('Minister Profile — MoPD', 'leader', ''),
    'leader-2.html': ('State Minister Profile — MoPD', 'leader', ''),
    'leader-3.html': ('State Minister Profile — MoPD', 'leader', ''),
    'leader-4.html': ('Minister Advisor Profile — MoPD', 'leader', ''),
    'gallery.html': ('Gallery — MoPD', 'gallery', 'Photo gallery from MoPD events.'),
    'press-release.html': ('Press Release — MoPD', 'press', 'Official press releases.'),
    'about-climate.html': ('About Climate — MoPD', 'climate', 'Climate action in Ethiopia.'),
    'climate-documents.html': ('Climate Documents — MoPD', 'climate_docs', 'Official climate policy documents.'),
    'green-technology.html': ('Green Technology — MoPD', 'green_tech', 'Green technology initiatives.'),
    'statistics-documents.html': ('Statistics Documents — MoPD', 'stats', 'Statistics and data documents.'),
    'development-planning.html': ('Development Planning — MoPD', 'devplan', 'National development planning.'),
}


def replace_links(html: str) -> str:
    for old, new in URL_MAP.items():
        html = html.replace(f'href="{old}"', f'href="{new}"')
        html = html.replace(f"href='{old}'", f"href='{new}'")
    html = re.sub(r'src="picture/([^"]+)"', r"src=\"{% static 'picture/\1' %}\"", html)
    html = re.sub(r'href="picture/([^"]+)"', r'href="{% static \'picture/\1\' %}"', html)
    return html


def extract_main(html: str) -> str:
    m = re.search(r'<main class="page">(.*?)</main>', html, re.DOTALL)
    return m.group(1).strip() if m else ''


def wrap_page(filename: str, body: str, title: str, page_id: str, desc: str = '') -> str:
    load = "{% load static %}"
    extends = "{% extends 'website/base.html' %}"
    block_title = f"{{% block title %}}{title}{{% endblock %}}"
    block_desc = f"{{% block meta_description %}}{desc}{{% endblock %}}" if desc else ''
    block_page = f"{{% block page_id %}}{page_id}{{% endblock %}}"
    return f"""{extends}
{load}
{block_title}
{block_desc}
{block_page}

{{% block content %}}
<main class="page">
{body}
</main>
{{% endblock %}}
"""


def convert_pages():
    OUT_PAGES.mkdir(parents=True, exist_ok=True)
    for filename, (title, page_id, desc) in PAGE_META.items():
        path = LEGACY / filename
        if not path.exists():
            continue
        body = replace_links(extract_main(path.read_text(encoding='utf-8')))
        out_name = filename.replace('.html', '.html')
        (OUT_PAGES / out_name).write_text(wrap_page(filename, body, title, page_id, desc), encoding='utf-8')
        print('converted', out_name)


def convert_home():
    html = (LEGACY / 'index.html').read_text(encoding='utf-8')
    m = re.search(r'</header>\s*(.*?)\s*<!-- Footer -->', html, re.DOTALL)
    if not m:
        raise SystemExit('Could not extract home content')
    body = replace_links(m.group(1).strip())
    # Fix news links in home for featured articles
    content = wrap_page(
        'index.html',
        body,
        'Ministry of Planning and Development — Ethiopia',
        'home',
        "Official website of the Ministry of Planning and Development (MoPD), Ethiopia.",
    )
    # Home uses dynamic news - will patch manually in template
    (OUT_PAGES / 'home.html').write_text(content, encoding='utf-8')
    print('converted home.html')


if __name__ == '__main__':
    convert_pages()
    convert_home()
