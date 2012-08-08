# -*- coding: utf-8 -*-

from django import template
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from cms.models import Block, Page
from cms.utils import is_editing
from base import BaseNode

register = template.Library()


class BaseBlockNode(BaseNode):
    '''Abstract node providing generic functionality for blocks;
       subclasses must define `get_block`.'''
    
    required_params = ('label',)
    default_template = template.Template('{{ obj.content }}')
    
    def is_empty(self, obj):
        return not obj.content.strip()
    
    def get_block(self, context, options):
        raise NotImplementedError()
    
    def render(self, context):
        options = self.get_options(context)
        editing = options.get('editable', True) and is_editing(context['request'])
        
        if editing:
            block = self.get_block(context, options)
                
            # This step naively assumes that the same block is not defined somewhere
            # else with a different format.  
            if options.get('format', None) and block.format != options['format']:
                block.format = options['format']
                block.save()
                
            return template.loader.render_to_string("cms/cms/block.html", {
                'block': block,
                'rendered_content': self.get_rendered_content(block, context),
            })
        else:
            # TODO cache here
            return self.get_rendered_content(self.get_block(context, options), context)


class BlockNode(BaseBlockNode):
    '''Works with blocks related to a Page, which is determined from the request.'''
    
    def get_block(self, context, options):
        page = Page.objects.get_for_url(context['request'].path_info)
        ctype = ContentType.objects.get_for_model(page)
        return Block.objects.get_or_create(label=options['label'], content_type=ctype, object_id=page.id)[0]
 
@register.tag
def cmsblock(parser, token):
    return BlockNode(parser, token)


class SiteBlockNode(BlockNode):
    '''Works with blocks related to a Site, which is determined via django settings.'''
    
    def get_block(self, context, options):
        ctype = ContentType.objects.get(app_label='sites', model='site')
        return Block.objects.get_or_create(label=options['label'], content_type=ctype, object_id=settings.SITE_ID)[0]

@register.tag
def cmssiteblock(parser, token):
    return SiteBlockNode(parser, token)


class GenericBlockNode(BlockNode):
    '''Works with blocks related to any model object, which should be passed in after 'label'.'''

    required_params = ('label', 'object')
    def get_block(self, context, options):
        ctype = ContentType.objects.get_for_model(options['object'])
        return Block.objects.get_or_create(label=options['label'], content_type=ctype, object_id=options['object'].id)[0]

@register.tag
def cmsgenericblock(parser, token):
    return GenericBlockNode(parser, token)


