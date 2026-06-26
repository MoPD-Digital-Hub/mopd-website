from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0016_dev_plan_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='telegram_notified_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When this article was posted to Telegram',
                null=True,
            ),
        ),
    ]
