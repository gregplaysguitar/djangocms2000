import os

from django import template
from django.contrib.auth.forms import AuthenticationForm
from django.template import RequestContext
from django.conf import settings

from cms.utils import is_editing
from cms.models import Page
from cms.forms import BlockForm, ImageForm, PublicPageForm
from cms import settings as cms_settings


register = template.Library()


@register.simple_tag(takes_context=True)
def cmseditor(context):
    if context['request'].user.has_module_perms("cms"):
        if is_editing(context['request']):
            try:
                page = Page.objects.get(url=context['request'].path_info, site_id=settings.SITE_ID)
            except Page.DoesNotExist:
                page = False
            
            css = cms_settings.TINYMCE_CONTENT_CSS
            tinymce_content_css = css() if callable(css) else css
            
            return template.loader.render_to_string("cms/cms/editor.html", RequestContext(context['request'], {
                'page': page,
                'cms_settings': cms_settings,
                'editor_form': BlockForm(prefix='plain'),
                'html_editor_form': BlockForm(prefix='html'),
                'image_form': ImageForm(),
                'page_form': page and PublicPageForm(instance=page) or None,
                'new_page_form': PublicPageForm(prefix='new'),
                'tinymce_content_css': tinymce_content_css,
            }))
        else:
            return template.loader.render_to_string("cms/cms/logged_in.html", RequestContext(context['request'], {
                'cms_settings': cms_settings,
            }))
    elif 'edit' in context['request'].GET:
        return template.loader.render_to_string("cms/cms/login_top.html", RequestContext(context['request'], {
            'login_form': AuthenticationForm(),
            'cms_settings': cms_settings,
        }))
    else:
        return ''


@register.assignment_tag(takes_context=True)
def cmsediting(context):
    return is_editing(context['request'])





