"""Sync document translation columns from base title/description fields."""

from django.db import migrations


def sync_document_titles(apps, schema_editor):
    Document = apps.get_model('website', 'Document')
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            'UPDATE website_document SET title_en = title '
            "WHERE (title_en IS NULL OR title_en = '') AND title != ''"
        )
        cursor.execute(
            'UPDATE website_document SET description_en = description '
            "WHERE (description_en IS NULL OR description_en = '') AND description != ''"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_add_african_leaders_climate_doc'),
    ]

    operations = [
        migrations.RunPython(sync_document_titles, migrations.RunPython.noop),
    ]
