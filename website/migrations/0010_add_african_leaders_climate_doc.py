"""Add second Addis Ababa declaration PDF from the official climate documents page."""

from django.db import migrations


def add_african_leaders_declaration(apps, schema_editor):
    url = (
        'https://mopd.gov.et/media/climate-documents/'
        '45822-pr-African_Leaders_Addis_Ababa_Declaration_on_Climate_Change_and_hU6SHOs.pdf'
    )
    title = 'The Addis Ababa Declaration on Climate Change & Call to Action (African Leaders)'
    # Raw insert: the historical model omits the *_en/*_am columns, which are
    # NOT NULL without a database default on freshly migrated databases.
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('SELECT 1 FROM website_document WHERE file_url = %s', [url])
        if cursor.fetchone():
            return
        cursor.execute(
            'INSERT INTO website_document '
            '(doc_type, climate_category, title, title_en, title_am, '
            'description, description_en, description_am, file_url, sort_order, is_published) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            ['climate', 'multilateral', title, title, '', '', '', '', url, 1, True],
        )


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_document_translation_columns'),
    ]

    operations = [
        migrations.RunPython(add_african_leaders_declaration, migrations.RunPython.noop),
    ]
