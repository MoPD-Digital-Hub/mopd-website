from django.db import migrations, models

import website.models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_news_source_and_dev_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliatelink',
            name='logo',
            field=models.ImageField(blank=True, upload_to=website.models.affiliate_logo_upload),
        ),
    ]
