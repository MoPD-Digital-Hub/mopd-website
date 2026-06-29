from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0017_newsarticle_telegram_notified_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactsubmission',
            name='assigned_to',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='contactsubmission',
            name='internal_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='contactsubmission',
            name='status',
            field=models.CharField(
                choices=[
                    ('new', 'New'),
                    ('in_progress', 'In progress'),
                    ('resolved', 'Resolved'),
                ],
                default='new',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='contactsubmission',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
