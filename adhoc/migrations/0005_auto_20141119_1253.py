# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    """Converts content_type foreignkey to a plain positiveintegerfield - this
       underlying field remains identical but we need this migration so django
       doesn't get confused."""
    
    dependencies = [
        ('cms', '0004_auto_20141119_1209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='content_type',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.RenameField(
            model_name='block',
            old_name='content_type',
            new_name='content_type_id',
        ),
        migrations.AlterField(
            model_name='image',
            name='content_type',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.RenameField(
            model_name='image',
            old_name='content_type',
            new_name='content_type_id',
        ),
        migrations.AlterUniqueTogether(
            name='block',
            unique_together=set([('content_type_id', 'object_id', 'label')]),
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together=set([('content_type_id', 'object_id', 'label')]),
        ),
    ]
