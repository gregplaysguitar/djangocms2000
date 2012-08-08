import re, os, sys, datetime

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.loader import get_template
from django import template
from django.utils.encoding import force_unicode
from django.utils.html import strip_tags
from django.utils.text import truncate_words
from django.db.models.signals import class_prepared, post_save, pre_save
from django.utils.functional import curry
from django.test.client import Client
from django.template import defaultfilters

import settings as cms_settings



BLOCK_TYPE_CHOICES = (
    ('plain', 'Plain text'),
    ('html', 'HTML'),
)

class Block(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    label = models.CharField(max_length=255)
    format = models.CharField(max_length=10, choices=BLOCK_TYPE_CHOICES, default='', blank=False)
    content = models.TextField(blank=True, default='')
    
    def __unicode__(self):
        return self.label
        #return "'%s' on %s" % (self.label, self.page.url)
    
    def get_filtered_content(self, filters=None):
        content = self.content
        non_default_filters = []
        if filters:
            for f in filters:
                if hasattr(defaultfilters, f):
                    content = getattr(defaultfilters, f)(content)
                else:
                    non_default_filters.append(f)
                
        for f, shortname, default in cms_settings.FILTERS:
            if (shortname in non_default_filters) or (not filters and default):
                try:
                    module = __import__(f)
                    content = sys.modules[f].filter(content, self)
                except ImportError:
                    bits = f.split(".")
                    module = __import__(".".join(bits[0:-1]), fromlist=[bits[-1]])
                    fn = getattr(module, bits[-1])
                    content = fn(content, self)
        return content
        
    
    class Meta:
       ordering = ['id',]
       unique_together = ('content_type', 'object_id', 'label')
    

class Image(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def label_display(self):
        return self.label.replace('-', ' ').replace('_', ' ').title()
    
    
    #page = models.ForeignKey(Page)
    label = models.CharField(max_length=255)
    file = models.ImageField(upload_to=cms_settings.UPLOAD_PATH, blank=True)
    description = models.CharField(max_length=255, blank=True)
    def __unicode__(self):
        return self.label
 
 
    # TODO these can be expensive for large images so should be cached
    # sorl should handle it though, need to hook into it somehow
    def dimensions(self):
        return {
            'width': self.file.width,
            'height': self.file.height,
        }
    
    class Meta:
       unique_together = ('content_type', 'object_id', 'label')
    


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

    #OTHER_EXCLUDE_REGEX = re.compile('(?:^404\.html|^500\.html|^base\.html|^admin|^cms/|base\.html$)')
#    return (
#        ('', '---------'),
#        ('Static Templates', get_templates_from_dir("cms", CMS_EXCLUDE_REGEX)),
#        ('Other Templates', get_templates_from_dir("", OTHER_EXCLUDE_REGEX)),
#    )
    

def get_child_pages(parent_url, qs=None):
    return (qs or Page.live).filter(url__iregex=r'^' + parent_url + '[^/]+/$')
    #return (qs or Page.objects).filter(url__iregex=r'^' + parent_url + '.+$')


class _CMSAbstractBaseModel(models.Model):
    class Meta:
        abstract = True

    blocks = generic.GenericRelation(Block)
    images = generic.GenericRelation(Image)
        
    

# add blocks on save via dummy render
def dummy_render(sender, **kwargs):
    if isinstance(kwargs['instance'], _CMSAbstractBaseModel):
        if getattr(kwargs['instance'], 'get_absolute_url', False):
            # dummy-render the object's absolute url to generate blocks
            c = Client()
            response = c.get(str(kwargs['instance'].get_absolute_url()), {'cms_dummy_render': cms_settings.SECRET_KEY}, HTTP_COOKIE='')   
post_save.connect(dummy_render)




class PageManager(models.Manager):
    def get_for_url(self, url):
        return Page.objects.get_or_create(url=url)[0]


class LivePageManager(models.Manager):
    def get_query_set(self):
        return super(LivePageManager, self).get_query_set().filter(is_live=True)



class Page(_CMSAbstractBaseModel):
    url = models.CharField(max_length=255, unique=True, verbose_name='URL', help_text='e.g. "/about/contact/"')
    template = models.CharField(max_length=255, default='')
    site = models.ForeignKey(Site, default=1)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_live = models.BooleanField(default=True, help_text="If this is not checked, the page will only be visible to logged-in users.")
    
    objects = PageManager()
    live = LivePageManager()
    
    class Meta:
        ordering = ('url',)
    
    def get_children(self, qs=None):
        return get_child_pages(self.url, qs)

    def __unicode__(self):
        return self.url

    def get_absolute_url(self):
        return self.url


def page_pre(sender, **kwargs):
    if not kwargs['instance'].site:
        kwargs['instance'].site = Site.objects.all()[0]
pre_save.connect(page_pre, sender=Page)


"""
Abstract model for other apps that want to have related Blocks and Images
"""
class CMSBaseModel(_CMSAbstractBaseModel):

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

