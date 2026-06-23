# Generated manually for feature expansion

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0012_contact_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='article_type',
            field=models.CharField(
                choices=[('news', 'News'), ('press_release', 'Press release')],
                default='news',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('source', models.CharField(blank=True, default='homepage', max_length=40)),
            ],
            options={
                'verbose_name': 'Newsletter subscriber',
                'verbose_name_plural': 'Newsletter subscribers',
                'ordering': ['-subscribed_at'],
            },
        ),
        migrations.CreateModel(
            name='ProcurementNotice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('reference', models.CharField(blank=True, max_length=120)),
                ('description', models.TextField(blank=True)),
                ('file_url', models.URLField(blank=True)),
                ('published_at', models.DateField()),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Procurement notice',
                'verbose_name_plural': 'Procurement notices',
                'ordering': ['-published_at', 'sort_order'],
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='website.department')),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments (organogram)',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('reference', models.CharField(blank=True, max_length=120)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('file_url', models.URLField(blank=True)),
                ('deadline', models.DateField(blank=True, null=True)),
                ('published_at', models.DateField()),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Vacancy',
                'verbose_name_plural': 'Vacancies',
                'ordering': ['-published_at', 'sort_order'],
            },
        ),
    ]
