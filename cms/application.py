# -*- coding: utf-8 -*-

import functools

from django import template
from django.contrib.contenttypes.models import ContentType

from models import Block, Image, Page
from utils import is_editing



def get_block_or_image(model_cls, label, url=None, site_id=None, object=None):
    '''Get a page, site or generic block/image, based on any one of the optional arguments.'''
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
    
    return model_cls.objects.get_or_create(label=label, content_type=ctype,
                                       object_id=object_id)[0]

get_block = functools.partial(get_block_or_image, Block)
get_image = functools.partial(get_block_or_image, Image)


def get_lookup_kwargs(site_id=None, object=None, request=None):
    if site_id:
        return {'site_id': site_id}
    elif object:
        return {'object': object}
    elif request:
        return {'url': request.path_info}
    else:
        raise TypeError('One of site_id, object or request is required.')
        

def get_rendered_block(label, editable=True, renderer=lambda b: b.display_content(), 
                       site_id=None, object=None, request=None, 
                       format='plain'):
    '''Get the rendered html for a block, wrapped in editing bits if appropriate.
       `renderer` is a callable taking a block object and returning rendered html
       for the block.'''

    editing = editable and request and is_editing(request)
    lookup_kwargs = get_lookup_kwargs(site_id, object, request)
                                       
    if editing:
        block = get_block(label, **lookup_kwargs)
            
        # This step naively assumes that the same block is not defined somewhere
        # else with a different format (which would be idiotic anyway.)
        if block.format != format:
            block.format = format
            block.save()
            
        return template.loader.render_to_string("cms/cms/block_editor.html", {
            'block': block,
            'rendered_content': renderer(block),
        })
    else:
        # TODO cache here
        return renderer(get_block(label, **lookup_kwargs))


class RenderedImage:
    '''A wrapper class for Image which can optionally be resized, via the geometry and 
       crop arguments. If these are given, the url, height and width are derived from a 
       generated sorl thumbnail; otherwise the original image is used.'''
    
    def __init__(self, image, geometry=None, crop=None):
        self.image = image
        self.geometry = geometry
        self.crop = crop
        
    def get_thumbnail(self):
        if self.geometry:
            from sorl.thumbnail import get_thumbnail
            return get_thumbnail(self.image.file, self.geometry, crop=self.crop)
        else:
            return None
    
    def get_image_attr(self, attr):
        if self.image.file:
            thumb = self.get_thumbnail()
            return getattr(thumb, attr) if thumb else getattr(self.image.file, attr)
        else:
            return None
    
    @property
    def url(self):
        return self.get_image_attr('url')
    
    @property
    def width(self):
        return self.get_image_attr('width')
    
    @property
    def height(self):
        return self.get_image_attr('height')


def default_image_renderer(img):
    if img.url:
        return '<img src="%s" alt="%s" width="%s" height="%s">' % (img.url, 
                                                                   img.image.description,
                                                                   img.width,
                                                                   img.height)
    else:
        return ''

def get_rendered_image(label, editable=True, renderer=default_image_renderer, 
                       site_id=None, object=None, request=None, 
                       geometry=None, crop=None):
    '''Get the rendered html for an image, wrapped in editing bits if appropriate.
       `renderer` is a callable taking an image object, geometry and crop options,
       and returning rendered html for the image.'''

    editing = editable and request and is_editing(request)
    lookup_kwargs = get_lookup_kwargs(site_id, object, request)

    if editing:
        image = get_image(label, **lookup_kwargs)
        return template.loader.render_to_string("cms/cms/image_editor.html", {
            'image': image,
            'rendered_content': renderer(RenderedImage(image, geometry, crop)),
        })
    else:
        # TODO cache here
        return renderer(RenderedImage(get_image(label, **lookup_kwargs), geometry, crop))
