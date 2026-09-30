"""Sync committed static leader portraits into MEDIA_ROOT and fix Tirumar flags."""

from pathlib import Path

from django.conf import settings
from django.db import migrations


def sync_leader_portraits(apps, schema_editor):
    Leader = apps.get_model('website', 'Leader')
    media_root = Path(settings.MEDIA_ROOT)
    static_dir = Path(settings.BASE_DIR) / 'static' / 'img' / 'leaders'
    if not static_dir.is_dir():
        return

    for path in static_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
            continue
        dest = media_root / 'leaders' / path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())

    Leader.objects.filter(slug='tirumar-abate').update(wide_photo=False)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0030_alter_sitesettings_development_plan_pdf_url'),
    ]

    operations = [
        migrations.RunPython(sync_leader_portraits, noop),
    ]
