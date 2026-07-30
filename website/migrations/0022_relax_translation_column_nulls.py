"""Drop NOT NULL on *_en / *_am columns to match the model state.

Migration 0018 added the modeltranslation fields to Django's state as
null=True, but the physical columns created by 0001 are NOT NULL, so any
insert that leaves a translation field unset (e.g. SiteSettings.load() on
a fresh database) violates the constraint.
"""

from django.db import migrations


def relax_translation_nulls(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != 'postgresql':
        # SQLite cannot drop NOT NULL in place; legacy SQLite databases
        # already contain the singleton rows this protects against.
        return
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name LIKE 'website_%%' "
            "AND column_name ~ '_(en|am)$' AND is_nullable = 'NO'"
        )
        for table, column in cursor.fetchall():
            cursor.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" DROP NOT NULL')


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0021_alter_sitesettings_development_plan_pdf_url'),
    ]

    operations = [
        migrations.RunPython(relax_translation_nulls, migrations.RunPython.noop),
    ]
