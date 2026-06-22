"""
Add base translation columns expected by django-modeltranslation.

Existing data lives in *_en columns from the hand-rolled bilingual schema;
modeltranslation also queries the base field column (e.g. title + title_en + title_am).
"""

from django.db import migrations


TRANSLATABLE = {
    'website_sitesettings': [
        ('site_name', 'varchar(200)'),
        ('topbar_tag', 'varchar(200)'),
        ('address', 'varchar(255)'),
        ('copyright_text', 'varchar(255)'),
        ('footer_desc', 'TEXT'),
    ],
    'website_sitetranslation': [
        ('text', 'TEXT'),
    ],
    'website_newsarticle': [
        ('tag', 'varchar(80)'),
        ('title', 'varchar(500)'),
        ('excerpt', 'TEXT'),
        ('body', 'TEXT'),
    ],
    'website_leader': [
        ('name', 'varchar(200)'),
        ('role', 'varchar(200)'),
        ('short_bio', 'TEXT'),
    ],
    'website_leaderparagraph': [
        ('text', 'TEXT'),
    ],
    'website_galleryalbum': [
        ('date_label', 'varchar(120)'),
    ],
    'website_galleryimage': [
        ('alt', 'varchar(200)'),
    ],
    'website_document': [
        ('title', 'varchar(200)'),
        ('description', 'TEXT'),
    ],
    'website_carouselslide': [
        ('tag', 'varchar(80)'),
        ('title', 'varchar(200)'),
    ],
    'website_affiliatelink': [
        ('name', 'varchar(120)'),
    ],
}


def _table_columns(cursor, table):
    cursor.execute(f'PRAGMA table_info("{table}")')
    return {row[1] for row in cursor.fetchall()}


def add_base_columns(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        for table, fields in TRANSLATABLE.items():
            columns = _table_columns(cursor, table)
            for base, col_type in fields:
                if base in columns:
                    continue
                en_col = f'{base}_en'
                if en_col not in columns:
                    continue
                cursor.execute(
                    f'ALTER TABLE "{table}" ADD COLUMN "{base}" {col_type} NOT NULL DEFAULT \'\''
                )
                cursor.execute(f'UPDATE "{table}" SET "{base}" = "{en_col}"')


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_modeltranslation_fields'),
    ]

    operations = [
        migrations.RunPython(add_base_columns, migrations.RunPython.noop),
    ]
