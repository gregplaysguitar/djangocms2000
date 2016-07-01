# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_auto_20141119_1253'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site_id', models.PositiveIntegerField()),
                ('page', models.ForeignKey(related_name='sites', to='cms.Page', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RunSQL("INSERT INTO cms_pagesite (site_id, page_id) "
                          "SELECT site_id, page_id from cms_page_sites;"),
        migrations.AlterUniqueTogether(
            name='pagesite',
            unique_together=set([('page', 'site_id')]),
        ),
        migrations.RemoveField(
            model_name='page',
            name='sites',
        ),
    ]
