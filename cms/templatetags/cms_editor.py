from django import template
from django.contrib.auth.forms import AuthenticationForm
from django.template import RequestContext
from django.template.loader import render_to_string

from cms.utils import is_editing
from cms import settings as cms_settings


register = template.Library()


@register.simple_tag(takes_context=True)
def cmseditor(context):
    if 'edit' in context['request'].GET:
        return render_to_string("cms/cms/login_top.html", RequestContext(context['request'], {
            'login_form': AuthenticationForm(),
            'cms_settings': cms_settings,
        }))
    else:
        return render_to_string("cms/cms/editor_script.html", RequestContext(context['request'], {
            'cms_settings': cms_settings,
        }))


@register.assignment_tag(takes_context=True)
def cmsediting(context):
    return is_editing(context['request'])
