"""Add second Addis Ababa declaration PDF from the official climate documents page."""

from django.db import migrations


def add_african_leaders_declaration(apps, schema_editor):
    Document = apps.get_model('website', 'Document')
    url = (
        'https://mopd.gov.et/media/climate-documents/'
        '45822-pr-African_Leaders_Addis_Ababa_Declaration_on_Climate_Change_and_hU6SHOs.pdf'
    )
    if Document.objects.filter(file_url=url).exists():
        return
    Document.objects.create(
        doc_type='climate',
        climate_category='multilateral',
        title='The Addis Ababa Declaration on Climate Change & Call to Action (African Leaders)',
        file_url=url,
        sort_order=1,
        is_published=True,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_document_translation_columns'),
    ]

    operations = [
        migrations.RunPython(add_african_leaders_declaration, migrations.RunPython.noop),
    ]
