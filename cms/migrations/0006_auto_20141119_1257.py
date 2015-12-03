# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_sites(apps, schema_editor):
    from cms.settings import DB_ALIAS

    db_alias = schema_editor.connection.alias
    if db_alias != DB_ALIAS:
        return

    Page = apps.get_model("cms", "Page")
    PageSite = apps.get_model("cms", "PageSite")
    for page in Page.objects.using(db_alias).all():
        for site in page.sites.all():
            PageSite.objects.create(page=page, site_id=site.id)


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
        migrations.RunPython(
            migrate_sites,
        ),
        migrations.AlterUniqueTogether(
            name='pagesite',
            unique_together=set([('page', 'site_id')]),
        ),
        migrations.RemoveField(
            model_name='page',
            name='sites',
        ),
    ]
