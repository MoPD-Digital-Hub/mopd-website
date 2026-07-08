import re
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from website.models import GalleryAlbum, GalleryImage

IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
SORT_PREFIX_RE = re.compile(r'^(\d+)_')


def sort_key(path: Path) -> tuple[int, str]:
    match = SORT_PREFIX_RE.match(path.name)
    if match:
        return int(match.group(1)), path.name.lower()
    return 9999, path.name.lower()


def collect_gallery_files(gallery_root: Path) -> list[Path]:
    files = [
        path
        for path in gallery_root.rglob('*')
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    return sorted(files, key=sort_key)


class Command(BaseCommand):
    help = 'Link gallery albums to image files already present in media/gallery/'

    def handle(self, *args, **options):
        gallery_root = Path(settings.MEDIA_ROOT) / 'gallery'
        if not gallery_root.is_dir():
            self.stderr.write(self.style.ERROR(f'Gallery media folder not found: {gallery_root}'))
            return

        files = collect_gallery_files(gallery_root)
        if not files:
            self.stderr.write(self.style.ERROR('No gallery images found in media/gallery/'))
            return

        album = GalleryAlbum.objects.filter(is_published=True).order_by('sort_order', 'id').first()
        if album is None:
            album = GalleryAlbum.objects.create(
                date_label_en='Photos from May 19, 2025',
                date_label_am='',
                event_date=date(2025, 5, 19),
                sort_order=0,
                is_published=True,
            )

        alt_en = 'MoPD event — May 19, 2025'
        album.images.all().delete()

        for idx, path in enumerate(files):
            match = SORT_PREFIX_RE.match(path.name)
            sort_order = int(match.group(1)) if match else idx
            media_name = path.relative_to(settings.MEDIA_ROOT).as_posix()
            image = GalleryImage(
                album=album,
                alt_en=alt_en,
                alt_am='',
                sort_order=sort_order,
            )
            image.image.name = media_name
            image.save()

        self.stdout.write(self.style.SUCCESS(
            f'Local gallery import complete: {len(files)} images linked to "{album.date_label_en}".'
        ))
