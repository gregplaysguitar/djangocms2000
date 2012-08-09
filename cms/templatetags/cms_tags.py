# -*- coding: utf-8 -*-

from django import template
from django.conf import settings

from cms.models import Block
from cms.application import get_rendered_block
from base import BaseNode

register = template.Library()


class BaseBlockNode(BaseNode):
    '''Node providing generic functionality for blocks.'''
    
    required_params = ('label',)
    default_template = template.Template('{{ obj.safe_content }}')
    
    def is_empty(self, obj):
        return not obj.content.strip()
    
    def render(self, context):
        def renderer(block):
            return self.get_rendered_content(block, context)
        return get_rendered_block(renderer=renderer, **self.get_options(context))


class BlockNode(BaseBlockNode):
    '''Works with blocks related to a Page object, which is determined via the request.
       Requires an HttpRequest instance to be present in the template context.'''
    
    def get_options(self, context):
        options = {'request': context['request']}
        options.update(super(BlockNode, self).get_options(context))
        return options

@register.tag
def cmsblock(parser, token):
    return BlockNode(parser, token)


class SiteBlockNode(BaseBlockNode):
    '''Works with blocks related to a Site, which is determined via django settings.'''
    
    def get_options(self, context):
        options = {'site_id': settings.SITE_ID}
        options.update(super(SiteBlockNode, self).get_options(context))
        return options
    
@register.tag
def cmssiteblock(parser, token):
    return SiteBlockNode(parser, token)


class GenericBlockNode(BaseBlockNode):
    '''Works with blocks related to any model object, which should be passed
       in as an argument after 'label'.'''

    required_params = ('label', 'object')
    
@register.tag
def cmsgenericblock(parser, token):
    return GenericBlockNode(parser, token)


