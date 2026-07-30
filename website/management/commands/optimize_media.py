"""Compress oversized images in MEDIA_ROOT for faster production delivery."""

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp'}
PROFILE_RULES = (
    ('leaders', 1200, 82),
    ('news', 1600, 80),
    ('gallery', 1600, 80),
    ('carousel', 1600, 80),
    ('affiliates', 800, 85),
)
DEFAULT_MAX_WIDTH = 1400
DEFAULT_QUALITY = 82


def _rule_for(path: Path) -> tuple[int, int]:
    parts = {part.lower() for part in path.parts}
    for folder, max_width, quality in PROFILE_RULES:
        if folder in parts:
            return max_width, quality
    return DEFAULT_MAX_WIDTH, DEFAULT_QUALITY


def _optimize_image(path: Path, *, dry_run: bool) -> tuple[bool, int, int]:
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        return False, 0, 0

    original_size = path.stat().st_size
    if original_size < 250_000:
        return False, original_size, original_size

    max_width, quality = _rule_for(path)
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')

        if image.width > max_width:
            ratio = max_width / image.width
            new_height = max(1, round(image.height * ratio))
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

        if dry_run:
            return True, original_size, original_size

        suffix = path.suffix.lower()
        buffer = BytesIO()
        if suffix in {'.jpg', '.jpeg'}:
            image.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
        elif suffix == '.webp':
            image.save(buffer, format='WEBP', quality=quality, method=6)
        else:
            image.save(buffer, format='PNG', optimize=True)

        optimized = buffer.getvalue()
        if len(optimized) >= original_size:
            return False, original_size, original_size

        path.write_bytes(optimized)
        return True, original_size, len(optimized)


class Command(BaseCommand):
    help = 'Compress large images in MEDIA_ROOT for production deployment.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report savings without writing files.',
        )

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        dry_run = options['dry_run']
        optimized_count = 0
        before_total = 0
        after_total = 0

        for path in sorted(media_root.rglob('*')):
            if not path.is_file():
                continue

            changed, before_size, after_size = _optimize_image(path, dry_run=dry_run)
            if not changed:
                continue

            optimized_count += 1
            before_total += before_size
            after_total += after_size
            saved = before_size - after_size
            self.stdout.write(
                f"  {'would optimize' if dry_run else 'optimized'} "
                f"{path.relative_to(media_root)} "
                f"({before_size // 1024} KB -> {after_size // 1024} KB, -{saved // 1024} KB)"
            )

        if optimized_count == 0:
            self.stdout.write(self.style.SUCCESS('No oversized images needed optimization.'))
            return

        saved_total = before_total - after_total
        label = 'Estimated savings' if dry_run else 'Saved'
        self.stdout.write(
            self.style.SUCCESS(
                f'{label}: {optimized_count} files, '
                f'{before_total // (1024 * 1024)} MB -> {after_total // (1024 * 1024)} MB '
                f'(-{saved_total // (1024 * 1024)} MB)'
            )
        )
