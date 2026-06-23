"""Add modeltranslation columns for Document (title_en/am, description_en/am)."""

from django.db import migrations


TRANSLATION_FIELDS = [
    ('title_en', 'varchar(300)'),
    ('title_am', 'varchar(300)'),
    ('description_en', 'TEXT'),
    ('description_am', 'TEXT'),
]


def _table_columns(cursor, table):
    cursor.execute(f'PRAGMA table_info("{table}")')
    return {row[1] for row in cursor.fetchall()}


def add_document_translation_columns(apps, schema_editor):
    connection = schema_editor.connection
    table = 'website_document'
    with connection.cursor() as cursor:
        columns = _table_columns(cursor, table)
        for column, col_type in TRANSLATION_FIELDS:
            if column in columns:
                continue
            cursor.execute(
                f'ALTER TABLE "{table}" ADD COLUMN "{column}" {col_type} NOT NULL DEFAULT \'\''
            )
        if 'title' in columns:
            cursor.execute(f'UPDATE "{table}" SET "title_en" = "title" WHERE "title_en" = \'\'')
        if 'description' in columns:
            cursor.execute(
                f'UPDATE "{table}" SET "description_en" = "description" WHERE "description_en" = \'\''
            )


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_document_climate_category'),
    ]

    operations = [
        migrations.RunPython(add_document_translation_columns, migrations.RunPython.noop),
    ]
