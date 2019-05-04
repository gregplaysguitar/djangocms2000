import hashlib

from django.contrib.contenttypes.models import ContentType
from django.conf import settings

try:
    from django.urls import resolve, Resolver404, \
        get_resolver
except ImportError:
    from django.core.urlresolvers import resolve, Resolver404, \
        get_resolver

try:
    # django 2.0a
    from django.urls import LocalePrefixPattern
except ImportError:
    # django < 2.0a
    from django.core.urlresolvers import LocaleRegexURLResolver as \
        LocalePrefixPattern
from django.utils import translation

from . import settings as cms_settings


def is_editing(request, obj_type=None):
    '''Test the request object to see if we're in edit mode'''
    if ('cms-edit_mode' in request.COOKIES):
        if obj_type == 'block':
            return request.user.has_perm("cms.change_block")
        elif obj_type == 'image':
            return request.user.has_perm("cms.change_image")
        else:
            return request.user.has_module_perms("cms")
    else:
        return False


def get_model_name(model_cls):
    if hasattr(model_cls._meta, 'model_name'):
        return model_cls._meta.model_name
    else:
        # Django < 1.7 fallback
        return model_cls._meta.module_name


def generate_cache_key(model_cls, site_id=None, related_object=None, url=None):
    """Generate a consistent unique cache key for a object, which may be
       a django Site (if site_id is passed), a cms.Page (if url passed),
       or any generic related_object. """

    if not (site_id or related_object or url):
        err = u'Required arguments: one of site_id, related_object or url.'
        raise TypeError(err)

    key_bits = [cms_settings.CACHE_PREFIX, get_model_name(model_cls)]

    if related_object:
        app_label = related_object._meta.app_label
        model_name = get_model_name(related_object)

        if app_label == 'sites' and model_name == 'site':
            # must actually be a site block, being referenced by the
            # sites.Site object
            site_id = related_object.pk
        elif app_label == 'cms' and model_name == 'page':
            # must be a cms.Page, ditto
            url = related_object.url

    if site_id:
        key_bits.append('site_id:%s' % site_id)
    elif url:
        # include site id, because there could be two pages with the same url
        # but attached to different sites
        key_bits.append('url:%s,%s' % (url, settings.SITE_ID))
    else:
        # must be a related_object present, otherwise we wouldn't have got here
        key_bits.append('object_pk:%s' % related_object.pk)

    return '|'.join(key_bits)


def public_key():
    '''Returns a consistent hash of the secret key which can be used in a
       public context, i.e. as a GET parameter.'''

    return hashlib.sha1(settings.SECRET_KEY.encode('utf-8')).hexdigest()[:10]


def key_from_ctype(ctype):
    return ctype.app_label + '-' + ctype.model


def key_from_obj(obj):
    if hasattr(obj, 'get_cms_key'):
        return obj.get_cms_key()
    return obj._meta.app_label + '-' + obj._meta.model_name


def ctype_from_key(key):
    app_label, model = key.split('-')
    return ContentType.objects.get(app_label=app_label, model=model)


def language_prefix_patterns_used():
    '''Returns `True` if the `LocalePrefixPattern` is used
       at root level of the urlpatterns, else it returns `False`. '''

    for url_pattern in get_resolver(None).url_patterns:
        if isinstance(url_pattern, LocalePrefixPattern):
            return True
    return False


def url_resolves(path):
    '''Test whether a path resolves successfully, taking language prefixes into
       account if necessary. Strip url parameters since resolve doesn't account
       for them correctly. '''
    resolved = None
    path = path.split('?')[0]
    try:
        resolved = resolve(path)
    except Resolver404:
        lang_code = translation.get_language()
        lang_from_path = translation.get_language_from_path(path)
        if not lang_from_path and language_prefix_patterns_used():
            lang_path = '/%s%s' % (lang_code, path)
            try:
                resolved = resolve(lang_path)
            except Resolver404:
                pass
    return bool(resolved)


def strip_i18n_prefix(path):
    """Returns path stripped of the language code prefix - i.e. /en/ - if one
       exists. """

    lang_code = translation.get_language_from_path(path)
    if lang_code:
        return path[len(lang_code) + 1:]

    return path
