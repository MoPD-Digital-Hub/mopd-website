"""Add missing modeltranslation columns for NewsArticle."""

from django.db import migrations


NEWS_COLS = [
    ('tag_en', 'varchar(80)'),
    ('tag_am', 'varchar(80)'),
    ('title_en', 'varchar(500)'),
    ('title_am', 'varchar(500)'),
    ('excerpt_en', 'TEXT'),
    ('excerpt_am', 'TEXT'),
    ('body_en', 'TEXT'),
    ('body_am', 'TEXT'),
]

BASE_MAP = (
    ('tag', 'tag_en'),
    ('title', 'title_en'),
    ('excerpt', 'excerpt_en'),
    ('body', 'body_en'),
)


def add_news_translation_columns(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('PRAGMA table_info("website_newsarticle")')
        existing = {row[1] for row in cursor.fetchall()}
        for col, col_type in NEWS_COLS:
            if col not in existing:
                cursor.execute(
                    f'ALTER TABLE "website_newsarticle" ADD COLUMN "{col}" {col_type} NOT NULL DEFAULT \'\''
                )
        for base, en_col in BASE_MAP:
            if base in existing or en_col in existing:
                cursor.execute(
                    f'UPDATE "website_newsarticle" SET "{en_col}" = "{base}" '
                    f'WHERE ("{en_col}" IS NULL OR "{en_col}" = \'\') AND "{base}" != \'\''
                )


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0014_new_model_translations'),
    ]

    operations = [
        migrations.RunPython(add_news_translation_columns, migrations.RunPython.noop),
    ]
