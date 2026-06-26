from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_news_translation_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='development_plan_cover_url',
            field=models.URLField(
                blank=True,
                default='',
                help_text='Cover image URL for the 10-Year Development Plan. Leave empty for the default bundled cover.',
            ),
        ),
    ]
