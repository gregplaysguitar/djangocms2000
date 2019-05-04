import re
import os

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import post_save

from . import settings as cms_settings
from .utils import generate_cache_key, ctype_from_key, key_from_obj


@python_2_unicode_compatible
class ContentModel(models.Model):
    class Meta:
        abstract = True
        unique_together = ('content_type', 'object_id', 'label')

    content_type = models.CharField(max_length=190)
    object_id = models.PositiveIntegerField()
    label = models.CharField(max_length=100)

    @property
    def content_object(self):
        ctype = ctype_from_key(self.content_type)
        return ctype.model_class().objects.get(pk=self.object_id)

    def __str__(self):
        return self.label


ATTR_REPLACE_CHARS = (
    ('"', '&quot;'),
    ("'", '&#39;'),
)


class Block(ContentModel):
    FORMAT_ATTR = 'attr'
    FORMAT_PLAIN = 'plain'
    FORMAT_HTML = 'html'
    FORMAT_CHOICES = (
        (FORMAT_ATTR, 'Attribute'),
        (FORMAT_PLAIN, 'Plain text'),
        (FORMAT_HTML, 'HTML'),
    )
    language = models.CharField(max_length=10, choices=cms_settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES,
                              default=FORMAT_PLAIN)
    content = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('content_type', 'object_id', 'language', 'label')

    def display_content(self):
        '''Returns content, marked safe if necessary'''
        if self.format == self.FORMAT_HTML:
            return mark_safe(self.content)
        elif self.format == self.FORMAT_ATTR:
            content = self.content
            for replacement in ATTR_REPLACE_CHARS:
                content.replace(*replacement)
            return content
        else:
            return self.content


class Image(ContentModel):
    # placeholder value since images are not language-aware
    language = settings.LANGUAGE_CODE

    file = models.ImageField(upload_to=cms_settings.UPLOAD_PATH, blank=True)
    description = models.CharField(max_length=255, blank=True)


def get_file_type(path):
    ext = os.path.splitext(path)[1]
    return ext.lstrip('.').lower()


VALID_TYPES = ['mp4', 'webm', 'ogg']
UNSUPPORTED_ERROR = \
    'Unsupported file type. Supported types: %s' % ', '.join(VALID_TYPES)


def validate_video_type(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower().lstrip('.') in VALID_TYPES:
        raise ValidationError(UNSUPPORTED_ERROR)


class Video(ContentModel):
    source = models.FileField(upload_to=cms_settings.UPLOAD_PATH,
                              validators=[validate_video_type], blank=True)

    @property
    def type(self):
        return 'video/%s' % get_file_type(self.source.url)

    poster = models.ImageField(upload_to=cms_settings.UPLOAD_PATH, blank=True)
    description = models.CharField(max_length=255, blank=True)
    loop = models.BooleanField(default=False)


def clear_cache(sender, instance, **kwargs):
    """Clear the cache of blocks/images for an object, when any of them
       changes. """

    key = generate_cache_key(sender, related_object=instance.content_object)
    cache.delete(key)


post_save.connect(clear_cache, sender=Block)
post_save.connect(clear_cache, sender=Image)
post_save.connect(clear_cache, sender=Video)


def get_templates_from_dir(dirname, exclude=None):
    TEMPLATE_REGEX = re.compile(r'\.html$')
    templates = []
    for template_dir in cms_settings.TEMPLATE_DIRS:
        template_path = os.path.join(template_dir, dirname)
        for root, dirs, files in os.walk(template_path):
            for file in files:
                rel_root = root.replace(template_dir, '')
                path = os.path.join(rel_root, file).strip('/')
                filename = path.replace(dirname, '').strip('/')
                if TEMPLATE_REGEX.search(path) and \
                   (not exclude or not exclude.search(filename)):
                    templates.append((path, filename))

    return templates


def template_choices():
    EXCLUDE_RE = re.compile(r'base\.html|^cms/')
    return [('', '---------')] + get_templates_from_dir("cms", EXCLUDE_RE)


def get_child_pages(parent_url, qs=None):
    if not parent_url.endswith('/'):
        parent_url += '/'
    if not qs:
        qs = Page.objects.live()
    return qs.filter(url__iregex=r'^' + parent_url + '[^/]+/?$')


class _CMSAbstractBaseModel(models.Model):
    class Meta:
        abstract = True

    # blocks = GenericRelation(Block)
    # images = GenericRelation(Image)

    def get_blocks(self):
        return Block.objects.filter(content_type=key_from_obj(self),
                                    object_id=self.id)

    def get_images(self):
        return Image.objects.filter(content_type=key_from_obj(self),
                                    object_id=self.id)


class PageManager(models.Manager):
    def get_for_url(self, url):
        try:
            return self.get(sites__site_id=settings.SITE_ID, url=url)
        except Page.DoesNotExist:
            page = Page(url=url)
            page.save()
            PageSite.objects.create(page=page, site_id=settings.SITE_ID)
            # page.sites.add(Site.objects.get_current())
            page.save()
            return page

    def live(self):
        return self.filter(is_live=True)


@python_2_unicode_compatible
class Page(_CMSAbstractBaseModel):
    url = models.CharField(max_length=255, verbose_name='URL',
                           help_text='e.g. /about/contact', db_index=True)
    template = models.CharField(max_length=255, default='')
    # sites = models.ManyToManyField(Site, default=[settings.SITE_ID])
    creation_date = models.DateTimeField(auto_now_add=True)
    is_live = models.BooleanField(
        default=getattr(settings, 'IS_LIVE_DEFAULT', True),
        help_text="If this is not checked, the page will only "
                  "be visible to logged-in users.")

    objects = PageManager()

    class Meta:
        ordering = ('url',)

    def get_children(self, qs=None):
        return get_child_pages(self.url, qs)

    def get_absolute_url(self):
        return self.url

    def __str__(self):
        block = self.get_blocks().exclude(content='').filter(label='title') \
                    .first()
        return block.content if block else ('Page: %s' % self.url)


@python_2_unicode_compatible
class PageSite(models.Model):
    page = models.ForeignKey(Page, related_name='sites',
                             on_delete=models.CASCADE)
    site_id = models.PositiveIntegerField()

    @property
    def site(self):
        return Site.objects.get(pk=self.site_id)

    class Meta:
        unique_together = ('page', 'site_id')

    def clean(self):
        others = PageSite.objects.exclude(pk=self.pk)
        if others.filter(site_id=self.site_id, page__url=self.page.url):
            raise ValidationError(u'Page url and site_id must be unique.')

    def __str__(self):
        return str(self.site)


class CMSBaseModel(_CMSAbstractBaseModel):
    """Abstract model for other apps that want to have related Blocks and
       Images"""

    # list of tuples of the form ('name', 'format',), but will fall back if
    # it's just a list of strings
    BLOCK_LABELS = []
    IMAGE_LABELS = []  # list of strings

    class Meta:
        abstract = True


def add_blocks(sender, **kwargs):
    """add extra blocks on save (dummy rendering happens too since CMSBaseModel
       extends _CMSAbstractBaseModel). """

    if isinstance(kwargs['instance'], CMSBaseModel):
        ctype = ContentType.objects.get_for_model(kwargs['instance'])
        for label_tuple in kwargs['instance'].BLOCK_LABELS:
            if isinstance(label_tuple, str):
                label_tuple = (label_tuple, None,)
            block, created = Block.objects.get_or_create(
                label=label_tuple[0],
                content_type=ctype,
                object_id=kwargs['instance'].id
            )
            # only set the format if the block was just created, or it's blank,
            # and if a format is defined
            if (not block.format or created) and label_tuple[1]:
                block.format = label_tuple[1]
                block.save()

        for label in kwargs['instance'].IMAGE_LABELS:
            Image.objects.get_or_create(
                label=label,
                content_type=ctype,
                object_id=kwargs['instance'].id
            )
post_save.connect(add_blocks)
