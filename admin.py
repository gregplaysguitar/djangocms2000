from models import *
from django.contrib import admin
from django.contrib.contenttypes import generic
import re
from django import forms
from django.utils.safestring import mark_safe

import settings as djangocms2000_settings



class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
    def __init__(self, *args, **kwargs):
        # change the raw_content widget based on the format of the block - a bit hacky but best we can do
        if 'instance' in kwargs:
            if kwargs['instance'].format == 'plain':
                self.base_fields['raw_content'].widget = admin.widgets.AdminTextInputWidget()
            else:
                self.base_fields['raw_content'].widget = admin.widgets.AdminTextareaWidget()
            self.base_fields['raw_content'].widget.attrs['class'] = "%s %s djangocms2000" %(self.base_fields['raw_content'].widget.attrs['class'], kwargs['instance'].format)
        super(BlockForm, self).__init__(*args, **kwargs)
        

class BlockFormSet(generic.generic_inlineformset_factory(Block)):
    def __init__(self, *args, **kwargs):
        super(BlockFormSet, self).__init__(*args, **kwargs)
        self.can_delete = djangocms2000_settings.ADMIN_CAN_DELETE_BLOCKS


class BlockInline(generic.GenericTabularInline):
    model = Block
    extra = 0
    formset = BlockFormSet
    fields = ('raw_content',)
    form = BlockForm


class ImageInline(generic.GenericTabularInline):
    model = Image
    extra = 0

class CMSBaseAdmin(admin.ModelAdmin):
    inlines=[BlockInline,ImageInline,]
    list_display=['page_title',]
    class Media:
        js = djangocms2000_settings.ADMIN_JS
        css = djangocms2000_settings.ADMIN_CSS
    class Meta:
        abstract=True


URL_STRIP_REGEX = re.compile('[^A-z0-9\-_\/]')
URL_DASH_REGEX = re.compile('--+')
class PageForm(forms.ModelForm):
    class Meta:
        model = Page
    
    def clean_uri(self):
        uri = URL_STRIP_REGEX.sub('', self.cleaned_data['uri'].replace(' ', '-')).lower()
        uri = URL_DASH_REGEX.sub('-', uri).strip('-')
        uri = ("/%s/" % uri.strip('/')).replace('//', '/')
        return uri
    
class PageAdmin(CMSBaseAdmin):
    list_display=['uri', 'page_title', 'template', 'site']
    list_display_links=['uri', 'page_title']

    list_filter=['site', 'template']

    search_fields = ['uri', 'blocks__compiled_content', 'template',]
    form = PageForm
        
admin.site.register(Page, PageAdmin)


admin.site.register(Block, list_display=['label','content_type','format', 'object_id',])
admin.site.register(Image, list_display=['label','content_type',])
admin.site.register(MenuItem, list_display=['__unicode__','page','sort'])












"""
from reversion.admin import VersionAdmin

class BlockVersionAdmin(VersionAdmin):
    pass

admin.site.register(Block, BlockVersionAdmin)
"""




"""

from django.contrib import admin
from django.contrib.contenttypes import generic

from myproject.myapp.models import Image, Product

class ImageInline(generic.GenericTabularInline):
    model = Image

class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline,
    ]

admin.site.register(Product, ProductAdmin)


"""
