import re, os, sys, datetime

from django.db import models
from django.db.utils import IntegrityError
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

# try:
#     from django.contrib.contenttypes.fields import GenericForeignKey, \
#                                                    GenericRelation
# except ImportError:
#     # django pre-1.9
#     from django.contrib.contenttypes.generic import GenericForeignKey, \
#                                                     GenericRelation

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django import template
from django.utils.encoding import force_unicode
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.db.models.signals import class_prepared, post_save, pre_save, m2m_changed
from django.utils.functional import curry

import settings as cms_settings
from utils import generate_cache_key


class ContentModel(models.Model):
    class Meta:
        abstract = True
        unique_together = ('content_type_id', 'object_id', 'label')
    
    # content_type = models.ForeignKey(ContentType)
    content_type_id = models.PositiveIntegerField()
    object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey('content_type', 'object_id')
    label = models.CharField(max_length=255)
        
    @property
    def content_object(self):
        ctype = ContentType.objects.get(pk=self.content_type_id)
        return ctype.model_class().objects.get(pk=self.object_id)
    
    def __unicode__(self):
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
    
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default=FORMAT_PLAIN)
    content = models.TextField(blank=True, default='')
    
    def display_content(self):
        '''Returns content, marked safe if necessary'''
        if self.format == self.FORMAT_HTML:
            return mark_safe(self.content)
        elif self.format == self.FORMAT_ATTR:
            return reduce(lambda s, r: s.replace(*r), (self.content,) + ATTR_REPLACE_CHARS)
        else:
            return self.content
   

class Image(ContentModel):
    file = models.ImageField(upload_to=cms_settings.UPLOAD_PATH, blank=True)
    description = models.CharField(max_length=255, blank=True)
     
    # TODO these can be expensive for large images so should be cached
    def dimensions(self):
        return {
            'width': self.file.width,
            'height': self.file.height,
        }


def clear_cache(sender, instance, **kwargs):
    try:
        model_name = instance._meta.model_name
    except AttributeError:
        # Django < 1.7 fallback
        model_name = instance._meta.module_name
    
    key = generate_cache_key(model_name, instance.label,
                             related_object=instance.content_object)
    cache.delete(key)
post_save.connect(clear_cache, sender=Block)
post_save.connect(clear_cache, sender=Image)


TEMPLATE_DIR = settings.TEMPLATE_DIRS[0]

def get_templates_from_dir(dir, exclude=None):
    TEMPLATE_REGEX = re.compile('\.html$')
    templates = []
    for root, dirs, files in os.walk("%s/%s" % (TEMPLATE_DIR, dir)):
        for file in files:
            path = ("%s/%s" % (root.replace(TEMPLATE_DIR, ''), file)).strip('/')
            filename = path.replace(dir, '').strip('/')
            if TEMPLATE_REGEX.search(path) and (not exclude or not exclude.search(filename)):
                templates.append((path, filename))
    
    return templates


def template_choices():
    CMS_EXCLUDE_REGEX = re.compile('base\.html$|^cms/|\.inc\.html$')
    return [('', '---------')] + get_templates_from_dir("cms", CMS_EXCLUDE_REGEX)
    

def get_child_pages(parent_url, qs=None):
    if not parent_url.endswith('/'):
        parent_url += '/'
    return (qs or Page.live).filter(url__iregex=r'^' + parent_url + '[^/]+/?$')


class _CMSAbstractBaseModel(models.Model):
    class Meta:
        abstract = True
    
    # blocks = GenericRelation(Block)
    # images = GenericRelation(Image)
    
    def __unicode__(self):
        try:
            return self.blocks.exclude(content='').get(label='title').content
        # except Block.DoesNotExist:
        except:
            # TODO
            return self.url


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


class LivePageManager(models.Manager):
    def get_queryset(self):
        return super(LivePageManager, self).get_queryset().filter(is_live=True)
    
    # For backwards-compatibility
    def get_query_set(self):
        return super(LivePageManager, self).get_query_set().filter(is_live=True)


class Page(_CMSAbstractBaseModel):
    url = models.CharField(max_length=255, verbose_name='URL', 
                           help_text='e.g. /about/contact', db_index=True)
    template = models.CharField(max_length=255, default='')
    # sites = models.ManyToManyField(Site, default=[settings.SITE_ID])
    creation_date = models.DateTimeField(auto_now_add=True)
    is_live = models.BooleanField(default=True, help_text="If this is not checked, the page will only be visible to logged-in users.")
    
    objects = PageManager()
    live = LivePageManager()
    
    class Meta:
        ordering = ('url',)
    
    def get_children(self, qs=None):
        return get_child_pages(self.url, qs)
    
    def get_absolute_url(self):
        return self.url


class PageSite(models.Model):
    page = models.ForeignKey(Page, related_name='sites')
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
    
    def __unicode__(self):
        return unicode(self.site)


# def page_sanity_check(sender, **kwargs):
#     ''''Validate uniqueness of page url and sites - can't be a unique_together
#         because sites is a ManyToMany field, and can't go in a model validate
#         method because model validation occurs before m2m fields are saved'''
#     
#     page = kwargs['instance']
#     if kwargs['action'] == 'pre_add':
#         for site_id in kwargs['pk_set']:
#             if Page.objects.filter(url=page.url, sites__id=site_id):
#                 raise IntegrityError('Sites and url must be unique.')
#         
# m2m_changed.connect(page_sanity_check, sender=Page.sites.through)


class CMSBaseModel(_CMSAbstractBaseModel):
    """Abstract model for other apps that want to have related Blocks and Images"""
    
    BLOCK_LABELS = [] # list of tuples of the form ('name', 'format',), but will fall back if it's just a list of strings
    IMAGE_LABELS = [] # list of strings
    
    class Meta:
        abstract = True


# add extra blocks on save (dummy rendering happens too since CMSBaseModel extends _CMSAbstractBaseModel)
def add_blocks(sender, **kwargs):
    if isinstance(kwargs['instance'], CMSBaseModel):
        for label_tuple in kwargs['instance'].BLOCK_LABELS:
            if isinstance(label_tuple, str):
                label_tuple = (label_tuple, None,)
            block, created = Block.objects.get_or_create(
                label=label_tuple[0],
                content_type=ContentType.objects.get_for_model(kwargs['instance']),
                object_id=kwargs['instance'].id
            )
            # only set the format if the block was just created, or it's blank, and if a format is defined
            if (not block.format or created) and label_tuple[1]:
                block.format = label_tuple[1]
                block.save()
            
        for label in kwargs['instance'].IMAGE_LABELS:
            Image.objects.get_or_create(
                label=label,
                content_type=ContentType.objects.get_for_model(kwargs['instance']),
                object_id=kwargs['instance'].id
            )
post_save.connect(add_blocks)

