from models import Page, Block, Image, MenuItem
from django.contrib import admin
from django.contrib.contenttypes import generic
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

import settings as djangocms2000_settings

from django.forms.widgets import HiddenInput
from django.utils.safestring import mark_safe
from forms import PageForm


class ReadonlyInput(HiddenInput):
    def __init__(self, attrs=None, model=None):
        super(ReadonlyInput, self).__init__(attrs)
        self.model = model
        
    def render(self, name, value, attrs=None):
        if self.model:
            text_value = self.model.objects.get(pk=value)
        else:
            text_value = value
        return mark_safe("<p>%s</p>%s" % (text_value, super(ReadonlyInput, self).render(name, value, attrs)))




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
            self.base_fields['raw_content'].widget.attrs['class'] = "%s %s djangocms2000" % (self.base_fields['raw_content'].widget.attrs['class'], kwargs['instance'].format)
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
    exclude = ('label',)

class CMSBaseAdmin(admin.ModelAdmin):
    inlines=[BlockInline,ImageInline,]
    list_display=['get_title',]
    class Media:
        js = djangocms2000_settings.ADMIN_JS
        css = djangocms2000_settings.ADMIN_CSS
    class Meta:
        abstract=True

    
class PageAdmin(CMSBaseAdmin):
    list_display=['page_title', 'uri', 'template', 'is_live', 'creation_date', 'view_on_site',]
    list_display_links=['page_title', 'uri', ]

    list_filter=['site', 'template', 'is_live', 'creation_date',]
    
    def view_on_site(self, instance):
        return '<a href="%s" target="_blank">view page</a>' % (instance.get_absolute_url())
    view_on_site.allow_tags = True
    view_on_site.short_description = ' '
    
    
    search_fields = ['uri', 'blocks__compiled_content', 'template',]
    form = PageForm
    exclude = []
    
    
if not djangocms2000_settings.USE_SITES_FRAMEWORK:
    PageAdmin.exclude.append('site')
        
admin.site.register(Page, PageAdmin)


admin.site.register(MenuItem, list_display=['__unicode__','page','sort'])






# Block/Image admin - restrict to just "site" blocks to avoid confusing the user
# Note - end users should only be given change permissions on these

class BlockFormSite(BlockForm):
    label = forms.CharField(widget=ReadonlyInput)

class BlockAdmin(admin.ModelAdmin):
    def queryset(self, request):
        if False and request.user.is_superuser:
            return Block.objects.all()
        else:
            return Block.objects.filter(content_type=ContentType.objects.get_for_model(Site))

    form = BlockFormSite
    fields = ['label', 'raw_content',]
    list_display = ['label_display', 'format', 'content_display',]
    search_fields = ['label', ]

    class Media:
        js = djangocms2000_settings.ADMIN_JS
        css = djangocms2000_settings.ADMIN_CSS
    
admin.site.register(Block, BlockAdmin)


class ImageFormSite(forms.ModelForm):
    class Meta:
        model = Image
    label = forms.CharField(widget=ReadonlyInput)

class ImageAdmin(admin.ModelAdmin):
    def queryset(self, request):
        if False and request.user.is_superuser:
            return Image.objects.all()
        else:
            return Image.objects.filter(content_type=ContentType.objects.get_for_model(Site))

    fields = ['label', 'file', 'description', ]
    list_display = ['label_display',]
    form = ImageFormSite
    search_fields = ['label', ]
    
admin.site.register(Image, ImageAdmin)
