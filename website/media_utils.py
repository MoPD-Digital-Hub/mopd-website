import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from django.core.files.base import ContentFile


def assign_image_from_url(instance, field_name, url):
    """Download a remote image and assign it to an ImageField (does not save the instance)."""
    if not url:
        return False
    try:
        if not str(url).startswith(('http://', 'https://')):
            from django.conf import settings
            local_path = Path(settings.BASE_DIR) / url
            if not local_path.is_file():
                return False
            filename = local_path.name
            with local_path.open('rb') as fh:
                getattr(instance, field_name).save(filename, ContentFile(fh.read()), save=False)
            return True
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path) or 'image.jpg'
        with urlopen(url, timeout=30) as response:
            content = ContentFile(response.read())
        getattr(instance, field_name).save(filename, content, save=False)
        return True
    except Exception:
        return False
