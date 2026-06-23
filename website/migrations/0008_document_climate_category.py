"""Add climate document categories matching the official MoPD site tabs."""

from django.db import migrations, models

URL_CATEGORY = {
    'Climate_Change_Declaration.pdf': 'multilateral',
    '45822-pr-African_Leaders_Addis_Ababa_Declaration_on_Climate_Change_and_hU6SHOs.pdf': 'multilateral',
    'UNFCCC_United_Nations_Framework_Convention_on_Climate_Change.pdf': 'multilateral',
    'Kyoto_Protocol.pdf': 'multilateral',
    'Paris_Agreement.pdf': 'multilateral',
    'Ethiopia_Carbon-Market-Strategy_2025.pdf': 'strategies',
    'NAP-ETH_2019.pdf': 'strategies',
    'Ethiopias_updated_NDC_JULY_2021_Submission_.pdf': 'strategies',
    'ETHIOPIA__LONG_TERM_LOW_EMISSION_AND_CLIMATE_RESILIENT_DEVELOPMENT_STR_RGJXrpV.pdf': 'strategies',
    'CRGE_Sector-Region_Mainstreaming_Guideline-Final_Jan_2019.pdf': 'strategies',
    'crge-strategy_2011.pdf': 'strategies',
    '25.7.24._GEFGCF_projects_profile_in_Ethiopia_WlleSLV.pdf': 'projects',
    'List_of_Implemented_Projects_CRGE_Progress_in_Implementing_the_CRGE_ND_UumPJzB.pdf': 'projects',
    'GEFGCF_projects_profile_in_Ethiopia_July_2023.pdf': 'projects',
    'CRGE_Strategy___Progress_in_Implementing_-_2011-2019__2020.pdf': 'reports',
    'Ethiopias_2nd_National_Communication.pdf': 'reports',
    'Ethiopias_3rd_National_Communication_2023.pdf': 'reports',
    'Ethiopias_Initial_National_Communication_2001.pdf': 'reports',
    'List_of_Side_Events_Ethiopia_9_Nov_2023.pdf': 'cop28',
}


def _category_for_url(file_url):
    for filename, category in URL_CATEGORY.items():
        if filename in file_url:
            return category
    return 'reports'


def assign_climate_categories(apps, schema_editor):
    Document = apps.get_model('website', 'Document')
    for doc in Document.objects.filter(doc_type='climate').order_by('id'):
        doc.climate_category = _category_for_url(doc.file_url)
        doc.save(update_fields=['climate_category'])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_modeltranslation_base_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='climate_category',
            field=models.CharField(
                blank=True,
                choices=[
                    ('multilateral', 'Multilateral Agreements'),
                    ('strategies', 'Strategies & Plans'),
                    ('projects', 'Projects & Programs'),
                    ('reports', 'Reports and Submissions'),
                    ('cop28', 'COP28'),
                ],
                help_text='Used for climate documents only (tab grouping on the climate documents page).',
                max_length=20,
            ),
        ),
        migrations.RunPython(assign_climate_categories, migrations.RunPython.noop),
    ]
