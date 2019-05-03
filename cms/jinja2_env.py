# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.safestring import mark_safe

from jinja2 import contextfunction

from .application import get_rendered_block, get_rendered_image, \
    get_rendered_video
from .templatetags.cms_editor import cms_editor
from .utils import is_editing, strip_i18n_prefix
from .models import Page


def process_kwargs(context, kwargs):
    '''Pre-process  the arguments from the jinja2 template function call so
       they make sense to the cms.'''

    # cms will make use of the request, if available
    if 'request' in context and 'request' not in kwargs:
        kwargs['request'] = context['request']

    # The site kwarg resolves ambiguity between site and page blocks,
    # without needing to pass SITE_ID from the template
    site = kwargs.pop('site', False)
    if site and not kwargs.get('site_id', None):
        kwargs['site_id'] = settings.SITE_ID

    # If an explicit url is passed, use it to find the related object
    url = kwargs.pop('url', None)
    if url:
        url = strip_i18n_prefix(url)
        kwargs['related_object'] = Page.objects.get_for_url(url)

    return kwargs


def conditional_escape(obj):
    if isinstance(obj, str):
        return mark_safe(obj)
    else:
        return obj


@contextfunction
def cms_block(context, *args, **kwargs):
    rendered = get_rendered_block(*args, **process_kwargs(context, kwargs))
    return conditional_escape(rendered)


@contextfunction
def cms_default_block(context, label, *args, **kwargs):
    kwargs['default'] = label
    rendered = get_rendered_block(label, *args,
                                  **process_kwargs(context, kwargs))
    return conditional_escape(rendered)


@contextfunction
def cms_image(context, *args, **kwargs):
    rendered = get_rendered_image(*args, **process_kwargs(context, kwargs))
    return conditional_escape(rendered)


@contextfunction
def cms_video(context, *args, **kwargs):
    rendered = get_rendered_video(*args, **process_kwargs(context, kwargs))
    return conditional_escape(rendered)


template_globals = {
    'cms_block': cms_block,
    'cms_default_block': cms_default_block,
    'cms_image': cms_image,
    'cms_video': cms_video,
    'cms_editor': contextfunction(lambda c: mark_safe(cms_editor(c))),
    'cms_editing': is_editing,
}
