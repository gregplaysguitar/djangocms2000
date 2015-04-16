from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.conf import settings
from django.test.client import Client

from .. import settings as adhoc_settings
from ..models import Page, Block, Image, PageSite
from ..utils import public_key
from ..forms import get_page_form_cls
from .filters import ContentTypeFilter, PageSiteFilter
from .inlines import ContentInline, BlockInline, ImageInline
from .admin_forms import BlockForm, ImageForm


admin_js = (
    adhoc_settings.STATIC_URL + 'lib/jquery-1.10.2.min.js',
    adhoc_settings.STATIC_URL + 'tinymce/js/tinymce/tinymce.min.js',
    adhoc_settings.STATIC_URL + 'js/page_admin.js',
    reverse_lazy('cms.views.linklist'),
    reverse_lazy('cms.views.block_admin_init'),
)
admin_css = {
    'all': (adhoc_settings.STATIC_URL + 'css/page_admin.css',),
}


class CMSBaseAdmin(admin.ModelAdmin):
    inlines = [BlockInline, ImageInline, ]
    list_display=['url',]
    save_on_top = True
    
    def view_on_site(self, obj):
        site = Site.objects.get_current()
        return 'http://' + site.domain + obj.get_absolute_url()
    
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
        returnval = super(CMSBaseAdmin, self).save_model(request, obj, form, 
                                                         change)
        
        if getattr(obj, 'get_absolute_url', None):
            c = Client()
            site = Site.objects.get_current()
            response = c.get(unicode(obj.get_absolute_url()), 
                             {'cms_dummy_render': public_key()},
                             HTTP_HOST=site.domain,
                             follow=True)
        return returnval


show_sites = adhoc_settings.USE_SITES_FRAMEWORK

class PageAdmin(CMSBaseAdmin):
    list_display = ('__unicode__', 'url', 'template', 'is_live', 
                    'creation_date', 'view_on_site_link', ) + \
                   (('get_sites', ) if show_sites else ())
    list_display_links=['__unicode__', 'url', ]
    list_filter = ((PageSiteFilter, ) if show_sites else ()) + \
                  ('template', 'is_live', 'creation_date',)
    form = get_page_form_cls()
    search_fields = ['url', 'template',]

    def view_on_site_link(self, instance):
        url = instance.get_absolute_url()

        if instance.sites.count():
            try:
                site = instance.sites.get(site_id=settings.SITE_ID)
            except PageSite.DoesNotExist:
                site = instance.sites.all()[0]
        else:
            site = None
        
        if site:
            url = 'http://%s%s' % (site.site.domain, url)
        
        return '<a href="%s" target="_blank">view page</a>' % url
    view_on_site_link.allow_tags = True
    view_on_site_link.short_description = ' '
    
    def get_sites(self, obj):
        return ', '.join([unicode(s) for s in obj.sites.all()])
    get_sites.short_description = 'sites'
    get_sites.admin_order_field = 'sites'
    
    def save_related(self, request, form, formsets, change):
        super(PageAdmin, self).save_related(request, form, formsets, change)
        form.save_sites()

admin.site.register(Page, PageAdmin)


class ContentAdmin(admin.ModelAdmin):
    def label_display(self, obj):
        return obj.label.replace('-', ' ').replace('_', ' ').capitalize()
    label_display.short_description = 'label'
    label_display.admin_order_field = 'label'


class BlockAdmin(ContentAdmin):
    form = BlockForm
    list_display = ['label_display', 'content_object', 'format', 
                    'content_snippet', ]
    search_fields = ['label', ]
    list_filter = [ContentTypeFilter]
    
    def content_snippet(self, obj):
        return Truncator(strip_tags(obj.content)).words(10, truncate=' ...')
        
    class Media:
        js = admin_js
        css = admin_css

admin.site.register(Block, BlockAdmin)


class ImageAdmin(ContentAdmin):
    list_display = ['label_display', 'content_object', 'file', 'description', ]
    form = ImageForm
    search_fields = ['label', ]
    list_filter = [ContentTypeFilter]

admin.site.register(Image, ImageAdmin)
