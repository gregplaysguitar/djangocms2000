from django import forms
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.conf import settings
from django.test.client import Client

import settings as cms_settings
from forms import PageForm, ReadonlyInput
from models import Page, Block, Image
from admin_filters import ContentTypeFilter
from utils import public_key


admin_js = (
    cms_settings.STATIC_URL + 'lib/jquery-1.10.2.min.js',
    cms_settings.STATIC_URL + 'tinymce/js/tinymce/tinymce.min.js',
    cms_settings.STATIC_URL + 'js/page_admin.js',
    reverse_lazy('cms.views.linklist'),
    reverse_lazy('cms.views.block_admin_init'),
)
admin_css = {
    'all': (cms_settings.STATIC_URL + 'css/page_admin.css',),
}

class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        exclude = ()
    
    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)

        # change the content widget based on the format of the block - a bit hacky but best we can do
        if 'instance' in kwargs:
            format = kwargs['instance'].format
            if format == 'attr':
                self.fields['content'].widget = forms.TextInput()                
            self.fields['content'].widget.attrs['class'] = " cms cms-%s" % format
        
        required_cb = cms_settings.BLOCK_REQUIRED_CALLBACK
        if callable(required_cb) and 'instance' in kwargs:
            self.fields['content'].required = required_cb(kwargs['instance'])


class BlockInline(generic.GenericTabularInline):
    model = Block
    max_num = 0
    fields = ('content',)
    form = BlockForm
    
    def has_add_permission(self, request):
        return False


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        exclude = ()
    
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)

        required_cb = cms_settings.IMAGE_REQUIRED_CALLBACK
        if callable(required_cb) and 'instance' in kwargs:
            self.fields['file'].required = required_cb(kwargs['instance'])


class ImageInline(generic.GenericTabularInline):
    model = Image
    max_num = 0
    exclude = ('label',)
    form = ImageForm
    
    def has_add_permission(self, request):
        return False


class CMSBaseAdmin(admin.ModelAdmin):
    inlines=[BlockInline,ImageInline,]
    list_display=['url',]
    save_on_top = True
    
    class Media:
        js = admin_js
        css = admin_css
    class Meta:
        abstract=True
        
    def save_model(self, request, obj, form, change):
        '''Save model, then add blocks/images via dummy rendering.
           
           NOTE: This will naively attempt to render the page using the 
           *current*  django Site object, so if you're in the admin of one site
           editing pages on another, the dummy render will silently fail.
        
        '''
        returnval = super(CMSBaseAdmin, self).save_model(request, obj, form, change)
        
        if getattr(obj, 'get_absolute_url', None):
            c = Client()
            response = c.get(unicode(obj.get_absolute_url()), 
                             {'cms_dummy_render': public_key()},
                             HTTP_COOKIE='')
        return returnval


class PageAdmin(CMSBaseAdmin):
    list_display=['__unicode__', 'url', 'template', 'is_live', 'creation_date', 'view_on_site',]
    list_display_links=['__unicode__', 'url', ]

    list_filter=['sites', 'template', 'is_live', 'creation_date',]
    
    def view_on_site(self, instance):
        url = instance.get_absolute_url()

        if instance.sites.count():
            try:
                site = instance.sites.get(id=settings.SITE_ID)
            except Site.DoesNotExist:
                site = instance.sites.all()[0]
        else:
            site = None
        
        if site:
            url = 'http://%s%s' % (site.domain, url)
        
        return '<a href="%s" target="_blank">view page</a>' % url
    view_on_site.allow_tags = True
    view_on_site.short_description = ' '
    
    def get_sites(self, obj):
        return ', '.join([unicode(s) for s in obj.sites.all()])
    get_sites.short_description = 'sites'
    get_sites.admin_order_field = 'sites'
    
    search_fields = ['url', 'blocks__content', 'template',]
    form = PageForm
    exclude = []
    
    def save_related(self, request, form, formsets, change):
        super(PageAdmin, self).save_related(request, form, formsets, change)
        
        # If the sites field is hidden, and no site is set, add the default one
        if not cms_settings.USE_SITES_FRAMEWORK and not form.instance.sites.count():
            form.instance.sites.add(Site.objects.get_current())
    
if cms_settings.USE_SITES_FRAMEWORK:
    PageAdmin.list_display.append('get_sites')
else:
    PageAdmin.exclude.append('sites')

     
admin.site.register(Page, PageAdmin)


class BlockFormSite(BlockForm):
    label = forms.CharField(widget=ReadonlyInput)

class BlockAdmin(admin.ModelAdmin):
    form = BlockFormSite
    fields = ['label', 'content',]
    list_display = ['label_display', 'content_object', 'format', 'content_snippet', ]
    search_fields = ['label', ]
    list_filter = [ContentTypeFilter]
    
    def label_display(self, obj):
        return obj.label.replace('-', ' ').replace('_', ' ').capitalize()
    label_display.short_description = 'label'
    label_display.admin_order_field = 'label'
    
    def content_snippet(self, obj):
        return Truncator(strip_tags(obj.content)).words(10, truncate=' ...')
        
    class Media:
        js = admin_js
        css = admin_css

admin.site.register(Block, BlockAdmin)


class ImageFormSite(forms.ModelForm):
    class Meta:
        model = Image
        exclude = ()
    
    label = forms.CharField(widget=ReadonlyInput)

class ImageAdmin(admin.ModelAdmin):
    fields = ['label', 'file', 'description', ]
    list_display = ['label_display', 'content_object', 'file', 'description', ]
    form = ImageFormSite
    search_fields = ['label', ]
    list_filter = [ContentTypeFilter]

admin.site.register(Image, ImageAdmin)
