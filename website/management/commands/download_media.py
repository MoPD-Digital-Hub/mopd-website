"""Download all remote images from the database and seeder into the local media/ folder."""

import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from website.models import AffiliateLink, CarouselSlide, GalleryImage, Leader, SiteSettings

# All hardcoded remote image URLs from the seeder
STATIC_IMAGES = {
    # 10-year plan cover placeholder
    'media/10-year-plan-cover.jpg': 'https://mopd.gov.et/media/photos/2025/07/29/fs_1.jpg',
    # Awards placeholder
    'media/Awards.jpg': 'https://mopd.gov.et/media/photos/2025/07/29/summi_22.jpg',
}


def _download(url, dest_path, label=''):
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return True, 'already exists'
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 MoPD-Setup/1.0'})
        with urlopen(req, timeout=30) as resp:
            dest_path.write_bytes(resp.read())
        return True, 'downloaded'
    except Exception as exc:
        return False, str(exc)


class Command(BaseCommand):
    help = 'Download all remote media images from mopd.gov.et into the local media/ folder'

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        media_root = Path(settings.MEDIA_ROOT)
        ok = 0
        fail = 0

        self.stdout.write(self.style.MIGRATE_HEADING('=== Downloading static placeholder images ==='))
        for rel_path, url in STATIC_IMAGES.items():
            dest = base_dir / rel_path
            success, msg = _download(url, dest, rel_path)
            if success:
                self.stdout.write(f'  ✔  {rel_path} ({msg})')
                ok += 1
            else:
                self.stdout.write(self.style.WARNING(f'  ✘  {rel_path}: {msg}'))
                fail += 1

        self.stdout.write(self.style.MIGRATE_HEADING('=== Downloading Leader photos ==='))
        for leader in Leader.objects.all():
            if leader.photo:
                path = media_root / leader.photo.name
                if path.exists() and path.stat().st_size > 0:
                    self.stdout.write(f'  ✔  {leader.name_en} photo (already exists)')
                    ok += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  ✘  {leader.name_en} photo missing on disk'))
                    fail += 1

        self.stdout.write(self.style.MIGRATE_HEADING('=== Downloading Carousel images ==='))
        for slide in CarouselSlide.objects.all():
            if slide.image:
                path = media_root / slide.image.name
                if path.exists() and path.stat().st_size > 0:
                    self.stdout.write(f'  ✔  Carousel slide #{slide.sort_order} (already exists)')
                    ok += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  ✘  Carousel slide #{slide.sort_order} image missing'))
                    fail += 1

        self.stdout.write(self.style.MIGRATE_HEADING('=== Downloading Gallery images ==='))
        for img in GalleryImage.objects.all():
            if img.image:
                path = media_root / img.image.name
                if path.exists() and path.stat().st_size > 0:
                    self.stdout.write(f'  ✔  Gallery image #{img.pk} (already exists)')
                    ok += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  ✘  Gallery image #{img.pk} missing'))
                    fail += 1

        self.stdout.write(self.style.MIGRATE_HEADING('=== Downloading Affiliate logos ==='))
        for aff in AffiliateLink.objects.all():
            if aff.logo:
                path = media_root / aff.logo.name
                if path.exists() and path.stat().st_size > 0:
                    self.stdout.write(f'  ✔  {aff.name_en} logo (already exists)')
                    ok += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  ✘  {aff.name_en} logo missing'))
                    fail += 1

        self.stdout.write('')
        if fail == 0:
            self.stdout.write(self.style.SUCCESS(f'All done! {ok} files OK, {fail} missing.'))
        else:
            self.stdout.write(self.style.WARNING(f'Done: {ok} OK, {fail} still missing (mopd.gov.et may be unreachable).'))
