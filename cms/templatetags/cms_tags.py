# -*- coding: utf-8 -*-

from django import template
from django.conf import settings

from cms.application import get_rendered_block, get_rendered_image
from base import BaseNode

register = template.Library()


class BaseBlockNode(BaseNode):
    '''Node which renders a cms Block.'''
    
    required_params = ('label',)
    
    def is_empty(self, obj):
        return not obj.content.strip()
    
    def render(self, context):
        return get_rendered_block(**self.get_options(context))


class BaseImageNode(BaseNode):
    '''Node which renders a cms Image.'''

    required_params = ('label',)
    optional_params = ('geometry',)
    
    def is_empty(self, obj):
        return not obj.image.file
    
    def render(self, context):
        return get_rendered_image(**self.get_options(context))


class PageMixin(BaseNode):
    '''Works with blocks or images related to a Page object, which is determined via the 
       request. Requires an HttpRequest instance to be present in the template context.'''
    
    def get_options(self, context):
        options = {'request': context['request']}
        options.update(super(PageMixin, self).get_options(context))
        return options


class SiteMixin(BaseNode):
    '''Works with blocks or images related to a Site, which is determined via django 
       settings.'''
    
    def get_options(self, context):
        options = {'site_id': settings.SITE_ID}
        options.update(super(SiteMixin, self).get_options(context))
        return options
        
        
class GenericMixin:
    '''Works with blocks or images related to any model object, which should be passed
       in as an argument after 'label'.'''

    required_params = ('object', 'label',)


def node_factory(base_node, lookup_mixin):
    '''Shortcut to return a TemplateNode for the given base_node (corresponding to either
       Block or Image) and lookup mixin (page, site or generic)'''
    
    class _Node(base_node, lookup_mixin):
        pass
            
    return _Node


@register.tag
def cmsblock(parser, token):
    return node_factory(BaseBlockNode, PageMixin)(parser, token)
    
@register.tag
def cmssiteblock(parser, token):
    return node_factory(BaseBlockNode, SiteMixin)(parser, token)

@register.tag
def cmsgenericblock(parser, token):
    return node_factory(BaseBlockNode, GenericMixin)(parser, token)

@register.tag
def cmsimage(parser, token):
    return node_factory(BaseImageNode, PageMixin)(parser, token)

@register.tag
def cmssiteimage(parser, token):
    return node_factory(BaseImageNode, SiteMixin)(parser, token)
    
@register.tag
def cmsgenericimage(parser, token):
    return node_factory(BaseImageNode, GenericMixin)(parser, token)

