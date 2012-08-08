# -*- coding: utf-8 -*-

import re

from django import template
from django.utils.encoding import smart_str


kwarg_re = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')


class BaseNode(template.Node):
    '''An abstract node which allows the following formats:
    
    {% TAGNAME [params key1=val1 key2=val2...] as var %}
        {{ var }}
    {% empty %}
        DEFAULT CONTENT
    {% endTAGNAME %}
    
    {% TAGNAME [params key1=val1 key2=val2...] as var %}
        {{ var }}
    {% endTAGNAME %}
    
    {% TAGNAME [params key1=val1 key2=val2...] %}
    
    Subclasses must define
    
    - self.required_params (tuple of param name strings)
    - self.default_template (Template object to render for the simple format.)
    - get_obj(self, **options) (gets object for insertion into the context)
    
    Optional:
    
    - is_empty(self, obj) tests whether we should render the default content
    '''

    #child_nodelists = ('nodelist_content', 'nodelist_empty') # this came from sorl, not sure what it does...?
    error_msg = ('Syntax error. Expected: ``%s label [key1=val1 key2=val2...] [as var]``')
    
    nodelist_content = template.NodeList()
    nodelist_empty = template.NodeList()
    
    def __init__(self, parser, token):
        bits = token.split_contents()
        required_length = len(self.required_params) + 1
        tagname = bits[0]
        
        if bits[-2] == 'as':
            # presence of 'as' means that the last bit is the varname, there
            # is definitely an end tag, and there might be an empty too
            if len(bits) < (required_length + 2):
                raise template.TemplateSyntaxError(self.error_msg % tagname)
            
            option_bits = bits[required_length:-2]
            self.varname = bits[-1]
            
            self.nodelist_content = parser.parse(('empty', 'end%s' % tagname,))
            if parser.next_token().contents == 'empty':
                self.nodelist_empty = parser.parse(('end%s' % tagname,))
                parser.delete_first_token()
        else:
            # no 'as', so must be the simpler format
            if len(bits) < required_length:
                raise template.TemplateSyntaxError(self.error_msg % tagname)
            option_bits = bits[required_length:]
            self.varname = None
        
        required_bits = bits[1:required_length]
        
        # required params are the ones immediately after the tag itself
        self.options = zip(self.required_params, [parser.compile_filter(b) for b in required_bits])

        # all other params are treated as kwarg-like pairs
        for bit in option_bits:
            match = kwarg_re.match(bit)
            if not match:
                raise template.TemplateSyntaxError(self.error_msg % tagname)
            key = smart_str(match.group('key'))
            expr = parser.compile_filter(match.group('value'))
            self.options.append((key, expr))
    
    def get_options(self, context):
        resolved_options = {}
        for key, expr in self.options:
            noresolve = {u'1': True, u'0': False}
            value = noresolve.get(unicode(expr), expr.resolve(context))
            resolved_options[key] = value
        
        return resolved_options
    
    def get_rendered_content(self, obj, context):
        if self.is_empty(obj):
            output = self.nodelist_empty.render(context)
        else:
            context.push()
            if self.varname:
                context[self.varname] = obj
                output = self.nodelist_content.render(context)
            else:
                context['obj'] = obj
                output = self.default_template.render(context)
            context.pop()        

        return output
    
    def render(self, context):
        obj = self.get_obj(**self.get_options(context))
        return get_rendered_content(obj, context)
        
    
    def __iter__(self):
        for node in self.nodelist_content:
            yield node
        for node in self.nodelist_empty:
            yield node
    
    def is_empty(self, obj):
        '''Override this in subclasses for smarter 'empty' behaviour'''
        return not obj

