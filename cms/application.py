# -*- coding: utf-8 -*-

from django import template
from django.contrib.contenttypes.models import ContentType

from models import Block, Page
from utils import is_editing


def get_block(label, url=None, site_id=None, object=None):
    '''Get a page, site or generic block, based on any one of the optional arguments.'''
    if url:
        ctype = ContentType.objects.get_for_model(Page)
        object_id = Page.objects.get_for_url(url).pk
    elif site_id:
        ctype = ContentType.objects.get(app_label='sites', model='site')
        object_id = site_id
    elif object:
        ctype = ContentType.objects.get_for_model(object)
        object_id = object.id
    else:
        raise TypeError(u'One of url, site_id or object is required')

    return Block.objects.get_or_create(label=label, content_type=ctype,
                                       object_id=object_id)[0]
    

def get_rendered_block(request, label, renderer=lambda b: b.safe_content(), 
                       format='plain', editable=True, site_id=None, object=None):
    '''Get the rendered html for a block, wrapped in editing bits if appropriate.
       `renderer` is a callable taking a block object and returning rendered html
       for the block.'''

    editing = editable and is_editing(request)
    
    if site_id:
        block_kwargs = {'site_id': site_id}
    elif object:
        block_kwargs = {'object': object}
    else:
        block_kwargs = {'url': request.path_info}
        
    if editing:
        block = get_block(label, **block_kwargs)
            
        # This step naively assumes that the same block is not defined somewhere
        # else with a different format (which would be idiotic anyway.)
        if block.format != format:
            block.format = format
            block.save()
            
        return template.loader.render_to_string("cms/cms/block.html", {
            'block': block,
            'rendered_content': renderer(block),
        })
    else:
        # TODO cache here
        return renderer(get_block(label, **block_kwargs))
