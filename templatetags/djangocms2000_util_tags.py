from django import template
from django.utils.functional import allow_lazy
import re
from django.utils.encoding import force_unicode


register = template.Library()




class ZealousSpacelessNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return self.strip_spaces_between_tags(self.nodelist.render(context).strip())
    
    def strip_spaces_between_tags(self, value):
        value = re.sub(r'\s+<', '<', force_unicode(value))
        value = re.sub(r'>\s+', '>', force_unicode(value))
        return value
    strip_spaces_between_tags = allow_lazy(strip_spaces_between_tags, unicode)

@register.tag
def zealousspaceless(parser, token):
    """like spaceless, but removes space between text and tags also"""
    nodelist = parser.parse(('endzealousspaceless',))
    parser.delete_first_token()
    return ZealousSpacelessNode(nodelist)


