# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('label', models.CharField(max_length=255)),
                ('format', models.CharField(default=b'plain', max_length=10, choices=[(b'attr', b'Attribute'), (b'plain', b'Plain text'), (b'html', b'HTML')])),
                ('content', models.TextField(default=b'', blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('label', models.CharField(max_length=255)),
                ('file', models.ImageField(upload_to=b'uploads/%Y_%m', blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(help_text=b'e.g. "/about/contact/"', max_length=255, verbose_name=b'URL')),
                ('template', models.CharField(default=b'', max_length=255)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('is_live', models.BooleanField(default=True, help_text=b'If this is not checked, the page will only be visible to logged-in users.')),
                ('sites', models.ManyToManyField(default=[1], to='sites.Site')),
            ],
            options={
                'ordering': ('url',),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together=set([('content_type', 'object_id', 'label')]),
        ),
        migrations.AlterUniqueTogether(
            name='block',
            unique_together=set([('content_type', 'object_id', 'label')]),
        ),
    ]
