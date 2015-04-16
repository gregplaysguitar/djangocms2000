from django.contrib.auth.forms import AuthenticationForm
from django.template import RequestContext
from django.template.loader import render_to_string
from django import template

from cms.utils import is_editing
from cms import settings as adhoc_settings


register = template.Library()


def cms_editor(context):
    '''Lazily loads the cms editor. This should be called at the bottom of an html document to
       allow frontend editing. '''
    
    if 'edit' in context['request'].GET:
        return render_to_string("adhoc/cms/login_top.html", RequestContext(context['request'], {
            'login_form': AuthenticationForm(),
            'adhoc_settings': adhoc_settings,
        }))
    else:
        return render_to_string("adhoc/cms/editor_script.html", RequestContext(context['request'], {
            'adhoc_settings': adhoc_settings,
        }))

register.simple_tag(cms_editor, takes_context=True)



def cms_is_editing(context):
    return is_editing(context['request'])

register.assignment_tag(takes_context=True)(cms_is_editing)
