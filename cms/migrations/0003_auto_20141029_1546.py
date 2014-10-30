# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0002_auto_20141029_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='url',
            field=models.CharField(help_text=b'e.g. /about/contact', max_length=255, verbose_name=b'URL', db_index=True),
        ),
    ]
