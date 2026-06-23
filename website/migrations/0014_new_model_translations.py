"""Add modeltranslation columns for new translatable models."""

from django.db import migrations, models


def copy_base_to_en(apps, schema_editor):
    for model_name, fields in (
        ('ProcurementNotice', ('title', 'description')),
        ('Department', ('name', 'description')),
        ('Vacancy', ('title', 'description', 'location')),
    ):
        Model = apps.get_model('website', model_name)
        for obj in Model.objects.all():
            changed = False
            for field in fields:
                base = getattr(obj, field, '') or ''
                en_field = f'{field}_en'
                if base and not getattr(obj, en_field, ''):
                    setattr(obj, en_field, base)
                    changed = True
            if changed:
                obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_site_features_expansion'),
    ]

    operations = [
        migrations.AddField(model_name='procurementnotice', name='title_en', field=models.CharField(max_length=300, null=True)),
        migrations.AddField(model_name='procurementnotice', name='title_am', field=models.CharField(max_length=300, null=True)),
        migrations.AddField(model_name='procurementnotice', name='description_en', field=models.TextField(blank=True, null=True)),
        migrations.AddField(model_name='procurementnotice', name='description_am', field=models.TextField(blank=True, null=True)),
        migrations.AddField(model_name='department', name='name_en', field=models.CharField(max_length=200, null=True)),
        migrations.AddField(model_name='department', name='name_am', field=models.CharField(max_length=200, null=True)),
        migrations.AddField(model_name='department', name='description_en', field=models.TextField(blank=True, null=True)),
        migrations.AddField(model_name='department', name='description_am', field=models.TextField(blank=True, null=True)),
        migrations.AddField(model_name='vacancy', name='title_en', field=models.CharField(max_length=300, null=True)),
        migrations.AddField(model_name='vacancy', name='title_am', field=models.CharField(max_length=300, null=True)),
        migrations.AddField(model_name='vacancy', name='description_en', field=models.TextField(blank=True, null=True)),
        migrations.AddField(model_name='vacancy', name='description_am', field=models.TextField(blank=True, null=True)),
        migrations.AddField(model_name='vacancy', name='location_en', field=models.CharField(blank=True, max_length=200, null=True)),
        migrations.AddField(model_name='vacancy', name='location_am', field=models.CharField(blank=True, max_length=200, null=True)),
        migrations.RunPython(copy_base_to_en, migrations.RunPython.noop),
    ]
