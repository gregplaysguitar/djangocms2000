# -*- coding: utf-8 -*-

import os
import functools

from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.conf import settings

try:
    import easy_thumbnails.files
    easy = True
except ImportError:
    try:
        import sorl.thumbnail
        easy = False
    except ImportError:
        pass

from .models import Block, Image, Video, Page
from .utils import is_editing, generate_cache_key, key_from_ctype, \
    strip_i18n_prefix
from . import settings as cms_settings


def thumbnail(image, geometry, crop, bw):
    if easy:
        if len(geometry) == 1:
            # if only width given, assume an arbitrary large height constraint
            geometry = (geometry[0], geometry[0] * 4)
        thumbnailer = easy_thumbnails.files.get_thumbnailer(image)
        return thumbnailer.get_thumbnail({
            'size': geometry,
            'crop': crop,
            'bw': bw,
        })
    else:
        return sorl.thumbnail.get_thumbnail(
            image, 'x'.join([str(g) for g in geometry]), crop=crop,
            colorspace=('GRAY' if bw else None))


def is_language_aware(model_cls):
    return False
    # return model_cls is Block


def get_obj_details(url=None, site_id=None, related_object=None):
    """Get ContentType instance and primary key for an object, based on the
       arguments. """

    if url:
        ctype = ContentType.objects.get_for_model(Page)
        object_id = Page.objects.get_for_url(url).pk
    elif site_id:
        ctype = ContentType.objects.get(app_label='sites', model='site')
        object_id = site_id
    elif related_object:
        ctype = ContentType.objects.get_for_model(related_object)
        object_id = related_object.id
    else:
        err = u'One of url, site_id or related_object is required'
        raise TypeError(err)
    return ctype, object_id


def get_obj_dict(model_cls, url=None, site_id=None, related_object=None):
    """Get a dict of blocks or images for an object, determined by the
       arguments, with a (label, language) tuple as the dict key for Block,
       or just label for Image. """

    key = generate_cache_key(model_cls, url=url, site_id=site_id,
                             related_object=related_object)
    obj_dict = cache.get(key)

    if obj_dict is None:
        ctype, object_id = get_obj_details(url, site_id, related_object)
        obj_dict = {}
        # TODO optimise with .values() ?
        qs = model_cls.objects.filter(content_type=key_from_ctype(ctype),
                                      object_id=object_id)

        language_aware = is_language_aware(model_cls)
        for obj in qs:
            if language_aware:
                obj_dict['%s.%s' % (obj.label, obj.language)] = obj
            else:
                obj_dict[obj.label] = obj

        cache.set(key, obj_dict)

    return obj_dict


def get_block_or_image(model_cls, label, url=None, site_id=None,
                       related_object=None, editing=False, defaults={}):
    """Get a page, site or generic block/image, based on any one of the
       optional arguments. If editing, go direct to the database, otherwise
       use the cached obj_dict. """

    # since Block objects are language-aware, strip any language code from the
    # url before creating the Page object
    if url:
        url = strip_i18n_prefix(url)
    language = get_language()
    language_aware = is_language_aware(model_cls)
    translated = language_aware and (language != settings.LANGUAGE_CODE)

    def obj_from_db():
        ctype, object_id = get_obj_details(url, site_id, related_object)
        lookup = {
            'label': label,
            'content_type': key_from_ctype(ctype),
            'object_id': object_id,
        }
        if language_aware:
            lookup['language'] = language

        # fall back to default language when not editing
        if translated and not editing:
            try:
                # fall back for non-existent *and* empty blocks
                return model_cls.objects.exclude(content='').get(**lookup)
            except model_cls.DoesNotExist:
                lookup['language'] = settings.LANGUAGE_CODE

        obj, __ = model_cls.objects.get_or_create(defaults=defaults, **lookup)
        return obj

    if editing:
        return obj_from_db()

    obj_dict = get_obj_dict(model_cls, url=url, site_id=site_id,
                            related_object=related_object)

    dict_key = (label, language) if language_aware else label

    # fall back to default language for empty blocks
    obj_from_dict = obj_dict.get(dict_key)
    if obj_from_dict and translated and obj_from_dict.content == '':
        dict_key = (label, settings.LANGUAGE_CODE)

    # Handle any edge case where the obj isn't in the cache
    if not obj_dict.get(dict_key):
        obj = obj_from_db()
        obj_dict[dict_key] = obj
        key = generate_cache_key(model_cls, url=url, site_id=site_id,
                                 related_object=related_object)
        cache.set(key, obj_dict)

    return obj_dict[dict_key]


get_block = functools.partial(get_block_or_image, Block)
get_image = functools.partial(get_block_or_image, Image)
get_video = functools.partial(get_block_or_image, Video)


def get_lookup_kwargs(site_id=None, related_object=None, request=None):
    '''Converts arguments passed through from a template into a dict of
       arguments suitable for passing to the get_block_or_image function.'''

    if related_object:
        return {'related_object': related_object}
    elif site_id:
        return {'site_id': site_id}
    elif request:
        return {'url': request.path_info}
    else:
        err = u"You must provide one of request, site_id or related_object."
        raise TypeError(err)


def default_block_renderer(block, filters=None):
    '''Renders a cms.block as html for display on the site.'''

    content = block.display_content()
    if filters and content:
        for f in filters.split('|'):
            content = getattr(template.defaultfilters, f)(content)
    return mark_safe(content)


def set_block_format(block, format):
    '''Sets block format, naively assuming that the same block is not defined
       elsewhere with a different format (which would be idiotic anyway.)'''

    if block.format != format:
        block.format = format
        block.save()


def get_rendered_block(label, format='plain', related_object=None,
                       filters=None, editable=None, renderer=None,
                       site_id=None, request=None, default=''):
    """Get the rendered html for a block, wrapped in editing bits if
       appropriate. `renderer` is a callable taking a block object and
       returning rendered html for the block. """

    if format not in [t[0] for t in Block.FORMAT_CHOICES]:
        raise LookupError('%s is not a valid block format.' % format)

    if editable is None:
        editable = (format != Block.FORMAT_ATTR)

    editing = editable and renderer != 'raw' and request and \
        is_editing(request, 'block')
    block_kwargs = get_lookup_kwargs(site_id, related_object, request)
    block_kwargs['defaults'] = {'content': default}

    if renderer == 'raw':
        def renderer(obj):
            return obj
    elif not renderer:
        renderer = functools.partial(default_block_renderer, filters=filters)

    if editing:
        block = get_block(label, editing=True, **block_kwargs)
        set_block_format(block, format)
        return template.loader.render_to_string("cms/cms/block_editor.html", {
            'block': block,
            'filters': filters or '',
            'rendered_content': renderer(block),
        })
    else:
        block = get_block(label, **block_kwargs)
        set_block_format(block, format)
        return renderer(block)


class RenderedImage:
    '''A wrapper class for Image which can optionally be resized, via the
       geometry and crop arguments. If these are given, the url, height and
       width are derived from a generated thumbnail; otherwise the
       original image is used. The height and width are also divided by the
       scale argument, if provided, to enable retina images. The optional
       bw argument is passed directly to the thumbnail engine and has no
       effect if the image is not resized. '''

    def __init__(self, image, geometry=None, crop=None, scale=1,
                 bw=False):

        # normalise geometry to either (w, h) or (w, )
        if geometry:
            geometry = str(geometry)
            geometry = list(map(int, geometry.split('x')))

        self.image = image
        self.geometry = geometry
        self.crop = crop
        self.scale = scale
        self.bw = bw

    def get_thumbnail(self):
        if self.geometry:
            # thumb = sorl.thumbnail.get_thumbnail(self.image.file,
            #                                      self.geometry,
            #                                      colorspace=self.colorspace,
            #                                      crop=self.crop)
            thumb = thumbnail(self.image.file, self.geometry, bw=self.bw,
                              crop=self.crop)
            return thumb
        else:
            return None

    def get_image_attr(self, attr):
        if self.image.file:
            thumb = self.get_thumbnail()
            return getattr(thumb, attr) if thumb \
                else getattr(self.image.file, attr)
        else:
            return None

    @property
    def url(self):
        return self.get_image_attr('url')

    @property
    def description(self):
        return self.image.description

    @property
    def width(self):
        img_width = self.get_image_attr('width')
        return (img_width / self.scale) if img_width else None

    @property
    def height(self):
        img_height = self.get_image_attr('height')
        return (img_height / self.scale) if img_height else None


class DummyImage(object):
    def __init__(self, geometry):
        width, height = (list(geometry) + [0])[:2]
        self.url = cms_settings.DUMMY_IMAGE_SOURCE % {
            'width': width or height,
            'height': height or width,
        }
        self.width = width
        self.height = height
        self.description = 'Placeholder image'


def default_image_renderer(img):
    '''Renders a RenderedImage object as html for display on the site.'''

    if img.url:
        return mark_safe('<img src="%s" alt="%s" width="%s" height="%s">' % (
            img.url, img.description, img.width, img.height))
    else:
        return ''


def get_rendered_image(label, geometry=None, related_object=None, crop=None,
                       editable=True, renderer=default_image_renderer,
                       site_id=None, request=None, scale=1, bw=False):
    """Get the rendered html for an image, wrapped in editing bits if
       appropriate. `renderer` is a callable taking an image object, geometry
       and crop options, and returning rendered html for the image. """

    editing = editable and renderer != 'raw' and request and \
        is_editing(request, 'image')
    lookup_kwargs = get_lookup_kwargs(site_id, related_object, request)

    image_obj = get_image(label, editing=editing, **lookup_kwargs)
    image = RenderedImage(image_obj, geometry, crop, scale, bw)

    if renderer == 'raw':
        def renderer(obj):
            return obj

    if cms_settings.DUMMY_IMAGE_SOURCE and \
       (not image.image.file or not os.path.exists(image.image.file.path)):
        # arbitrary small image if no geometry supplied
        rendered = renderer(DummyImage(image.geometry or (100, 100)))
    else:
        rendered = renderer(image)

    if editing:
        return template.loader.render_to_string("cms/cms/image_editor.html", {
            'image': image,
            'rendered_content': rendered,
        })
    else:
        return rendered


def default_video_renderer(video):
    '''Renders a Video object as html for display on the site.'''

    if video.source:
        return mark_safe("""
            <video playsinline webkit-playsinline
                       preload="auto"
                       controls
                       poster="%(poster)s"
                       muted %(loop)s>
              <source src="%(source)s" type="%(type)s" />
            </video>
        """ % {
            'loop': 'loop' if video.loop else '',
            'source': video.source.url,
            'type': video.type,
            'poster': video.poster.url if video.poster else None,
        })
    else:
        return ''


def get_rendered_video(label, geometry=None, related_object=None,
                       editable=True, renderer=default_video_renderer,
                       site_id=None, request=None):
    """Get the rendered html for a video. `renderer` is a callable taking a
       video object and geometry option, and returning rendered html for the
       video. """

    editing = editable and renderer != 'raw' and request and \
        is_editing(request, 'video')
    lookup_kwargs = get_lookup_kwargs(site_id, related_object, request)

    video_obj = get_video(label, editing=editing, **lookup_kwargs)

    if renderer == 'raw':
        def renderer(obj):
            return obj

    rendered = renderer(video_obj)

    return rendered
