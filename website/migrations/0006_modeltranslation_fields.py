"""
Align Django model state with django-modeltranslation.

Database columns stay as *_en / *_am; modeltranslation maps base fields
(e.g. title) to those columns at runtime.
"""

from django.db import migrations, models


def _rename_and_drop_am(model_name, fields):
    ops = []
    for base in fields:
        ops.append(migrations.RemoveField(model_name=model_name, name=f'{base}_am'))
        ops.append(migrations.RenameField(model_name=model_name, old_name=f'{base}_en', new_name=base))
    return ops


STATE_OPS = [
    *_rename_and_drop_am('sitesettings', ('site_name', 'topbar_tag', 'address', 'copyright_text', 'footer_desc')),
    *_rename_and_drop_am('sitetranslation', ('text',)),
    *_rename_and_drop_am('newsarticle', ('tag', 'title', 'excerpt', 'body')),
    *_rename_and_drop_am('leader', ('name', 'role', 'short_bio')),
    *_rename_and_drop_am('leaderparagraph', ('text',)),
    *_rename_and_drop_am('galleryalbum', ('date_label',)),
    *_rename_and_drop_am('galleryimage', ('alt',)),
    *_rename_and_drop_am('document', ('title', 'description')),
    *_rename_and_drop_am('carouselslide', ('tag', 'title')),
    *_rename_and_drop_am('affiliatelink', ('name',)),
]


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_affiliatelink_logo'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=STATE_OPS,
            database_operations=[],
        ),
    ]
