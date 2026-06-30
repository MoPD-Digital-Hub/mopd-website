from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0018_contact_workflow'),
    ]

    operations = [
        migrations.AddField(
            model_name='procurementnotice',
            name='closing_date',
            field=models.DateField(
                blank=True,
                null=True,
                help_text='Bid submission deadline. Leave blank for notices with no fixed closing date.',
            ),
        ),
    ]
