# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def convert_content_type(apps, schema_editor):
    '''Convert content_type_id integer fields to content_type char fields,
       with their data in the format app_label-model.'''
    
    from cms.settings import DB_ALIAS
    
    db_alias = schema_editor.connection.alias
    if db_alias != DB_ALIAS:
        return
    
    ContentType = apps.get_model("contenttypes", "ContentType")
    ctype_map = {}
    for ctype in ContentType.objects.all():
        ctype_map[ctype.pk] = ctype.app_label + '-' + ctype.model
    
    models = (apps.get_model("cms", "Block"), 
        apps.get_model("cms", "Image"))
            
    for model_cls in models:
        for obj in model_cls.objects.using(db_alias).all():
            # If the content_type_id isn't in the map, it must be pointing
            # to a stale content type, so just store the id so there's 
            # something there
            obj.content_type = ctype_map.get(obj.content_type_id, 
                                             obj.content_type_id)
            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0007_auto_20141119_1438'),
    ]

    operations = [
        # Add new fields (nullable for now)
        migrations.AddField(
            model_name='block',
            name='content_type',
            field=models.CharField(max_length=190, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='content_type',
            field=models.CharField(max_length=190, null=True),
            preserve_default=True,
        ),
        
        
        # Migrate data to new field
        migrations.RunPython(convert_content_type),
        
        
        # Remove old field and update new
        migrations.AlterField(
            model_name='block',
            name='content_type',
            field=models.CharField(max_length=190),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='image',
            name='content_type',
            field=models.CharField(max_length=190),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='block',
            unique_together=set([('content_type', 'object_id', 'label')]),
        ),
        migrations.RemoveField(
            model_name='block',
            name='content_type_id',
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together=set([('content_type', 'object_id', 'label')]),
        ),
        migrations.RemoveField(
            model_name='image',
            name='content_type_id',
        ),
    ]
