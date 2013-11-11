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
    
    Subclasses must define:
    - self.required_params
      tuple of param name strings
    - self.render(self, context)
      renders the tag
    
    Optional:
    - optional_params
      tuple of optional params to come after required_params
    - is_empty(self, obj, request) 
      tests whether we should render the {% empty %} section
    '''

    #child_nodelists = ('nodelist_content', 'nodelist_empty') # this is in sorl, not sure what it does...?
    
    nodelist_content = template.NodeList()
    nodelist_empty = None
    optional_params = []
    takes_request = False
    
    def __init__(self, parser, token):
        bits = token.split_contents()
        required_length = len(self.required_params) + 1
        tagname = bits[0]
        
        if bits[-2] == 'as':
            # presence of 'as' means that the last bit is the varname, there
            # is definitely an end tag, and there might be an empty too
            if len(bits) < (required_length + 2):
                raise template.TemplateSyntaxError(self.error_msg(tagname))
            
            option_bits = bits[required_length:-2]
            self.varname = bits[-1]
            
            self.nodelist_content = parser.parse(('empty', 'end%s' % tagname,))
            if parser.next_token().contents == 'empty':
                self.nodelist_empty = parser.parse(('end%s' % tagname,))
                parser.delete_first_token()
        else:
            # no 'as', so must be the simpler format
            if len(bits) < required_length:
                raise template.TemplateSyntaxError(self.error_msg(tagname))
            option_bits = bits[required_length:]
            self.varname = None
        
        required_bits = bits[1:required_length]
        
        # required params are the ones immediately after the tag itself
        self.options = zip(self.required_params, [parser.compile_filter(b) for b in required_bits])
        
        # zero or more optional_params come next.
        optional_param_values = []
        for b in option_bits:
            if not kwarg_re.match(b):
                optional_param_values.append(parser.compile_filter(b))
            else:
                break
        self.options += zip(self.optional_params, optional_param_values)
                
        # all other params are treated as kwarg-like pairs
        for bit in option_bits[len(optional_param_values):]:
            match = kwarg_re.match(bit)
            if not match:
                raise template.TemplateSyntaxError(self.error_msg(tagname))
            key = smart_str(match.group('key'))
            expr = parser.compile_filter(match.group('value'))
            self.options.append((key, expr))
    
    def error_msg(self, tagname):
        return 'Syntax error. Expected: ``%s [%s key1=val1 key2=val2...] [as var]``' % \
            (tagname, ' '.join(self.required_params), ' '.join(self.optional_params))
    
    def get_options(self, context):
        resolved_options = {}
        
        if self.takes_request:
            resolved_options['request'] = context.get('request', None)            
        
        count = 0
        for key, expr in self.options:
            noresolve = {u'1': True, u'0': False}
            value = noresolve.get(unicode(expr), expr.resolve(context))
            if count < len(self.required_params) and not value:
                # TODO currently assuming that falsy values are invalid here; 
                # ideally we'd raise a VariableDoesNotExist only if the expr 
                # doesn't resolve, but django doesn't seem to want to let us 
                # when using parser.compile_filter(...) instead of 
                # template.Variable(...)
                raise template.VariableDoesNotExist('No value supplied for argument %s' % key)
                
            resolved_options[key] = value
            count += 1
        
        renderer = self.get_renderer(context)
        if renderer:
            resolved_options['renderer'] = renderer
        
        return resolved_options
    
    def get_renderer(self, context):
        if self.varname:
            def renderer(obj):
                if self.is_empty(obj, context['request']):
                    if self.nodelist_empty:
                        output = self.nodelist_empty.render(context)
                    else:
                        output = ''
                else:
                    context.push()
                    context[self.varname] = obj
                    output = self.nodelist_content.render(context)
                    context.pop()        
                return output
            return renderer
        else:
            return None
    
    def render(self, context):
        raise NotImplementedError
    
    def __iter__(self):
        for node in self.nodelist_content:
            yield node
        for node in self.nodelist_empty:
            yield node
    
    def is_empty(self, obj, request):
        '''Override this in subclasses for smarter 'empty' behaviour'''
        return not obj

