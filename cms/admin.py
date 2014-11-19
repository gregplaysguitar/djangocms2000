from django import forms
from django.contrib import admin

# from django.contrib.contenttypes.admin import GenericTabularInline, GenericInlineModelAdminChecks
# from django.contrib.contenttypes.forms import BaseGenericInlineFormSet

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.conf import settings
from django.test.client import Client

import settings as cms_settings
from forms import PageForm, ReadonlyInput
from models import Page, Block, Image, PageSite
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


# class DummyCheck(GenericInlineModelAdminChecks):
#     def _check_relation(self, cls, parent_model):
#         return []
# 
# 
# class ContentFormset(BaseGenericInlineFormSet):
#     def __init__(self, data=None, files=None, instance=None, save_as_new=None,
#              prefix=None, queryset=None, **kwargs):
#         opts = self.model._meta
#         self.instance = instance
#         self.rel_name = '-'.join((
#             opts.app_label, opts.model_name,
#             self.ct_field.name, self.ct_fk_field.name,
#         ))
#         if self.instance is None or self.instance.pk is None:
#             qs = self.model._default_manager.none()
#         else:
#             if queryset is None:
#                 queryset = self.model._default_manager
#             qs = queryset.filter(**{
#                 self.ct_field.name: ContentType.objects.get_for_model(
#                     self.instance, for_concrete_model=self.for_concrete_model).pk,
#                 self.ct_fk_field.name: self.instance.pk,
#             })
#         super(BaseGenericInlineFormSet, self).__init__(
#             queryset=qs, data=data, files=files,
#             prefix=prefix,
#             **kwargs
#         )
# 
# 
# def content_inlineformset_factory(model, form=forms.ModelForm,
#                               formset=BaseGenericInlineFormSet,
#                               ct_field="content_type", fk_field="object_id",
#                               fields=None, exclude=None,
#                               extra=3, can_order=False, can_delete=True,
#                               max_num=None, formfield_callback=None,
#                               validate_max=False, for_concrete_model=True,
#                               min_num=None, validate_min=False):
#     """
#     Returns a ``GenericInlineFormSet`` for the given kwargs.
#     
#     You must provide ``ct_field`` and ``fk_field`` if they are different from
#     the defaults ``content_type`` and ``object_id`` respectively.
#     """
#     opts = model._meta
#     # if there is no field called `ct_field` let the exception propagate
#     ct_field = opts.get_field(ct_field)
#     fk_field = opts.get_field(fk_field)  # let the exception propagate
#     if exclude is not None:
#         exclude = list(exclude)
#         exclude.extend([ct_field.name, fk_field.name])
#     else:
#         exclude = [ct_field.name, fk_field.name]
#     FormSet = modelformset_factory(model, form=form,
#                                    formfield_callback=formfield_callback,
#                                    formset=formset,
#                                    extra=extra, can_delete=can_delete, can_order=can_order,
#                                    fields=fields, exclude=exclude, max_num=max_num,
#                                    validate_max=validate_max, min_num=min_num,
#                                    validate_min=validate_min)
#     FormSet.ct_field = ct_field
#     FormSet.ct_fk_field = fk_field
#     FormSet.for_concrete_model = for_concrete_model
#     return FormSet
# 
# class ContentInline(GenericTabularInline):
#     ct_field = "content_type_id"
#     max_num = 0
#     checks_class = DummyCheck
#     formset = ContentFormset
#     
#     def has_add_permission(self, request):
#         return False
#     
#     def get_formset(self, request, obj=None, **kwargs):
#         return ContentFormset()
#         
#         
#         if 'fields' in kwargs:
#             fields = kwargs.pop('fields')
#         else:
#             fields = flatten_fieldsets(self.get_fieldsets(request, obj))
#         if self.exclude is None:
#             exclude = []
#         else:
#             exclude = list(self.exclude)
#         exclude.extend(self.get_readonly_fields(request, obj))
#         if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
#             # Take the custom ModelForm's Meta.exclude into account only if the
#             # GenericInlineModelAdmin doesn't define its own.
#             exclude.extend(self.form._meta.exclude)
#         exclude = exclude or None
#         can_delete = self.can_delete and self.has_delete_permission(request, obj)
#         defaults = {
#             "ct_field": self.ct_field,
#             "fk_field": self.ct_fk_field,
#             "form": self.form,
#             "formfield_callback": partial(self.formfield_for_dbfield, request=request),
#             "formset": self.formset,
#             "extra": self.get_extra(request, obj),
#             "can_delete": can_delete,
#             "can_order": False,
#             "fields": fields,
#             "min_num": self.get_min_num(request, obj),
#             "max_num": self.get_max_num(request, obj),
#             "exclude": exclude
#         }
#         defaults.update(kwargs)
#     
#         if defaults['fields'] is None and not modelform_defines_fields(defaults['form']):
#             defaults['fields'] = ALL_FIELDS
#     
#         return content_inlineformset_factory(self.model, **defaults)


class DummyCheck(admin.checks.InlineModelAdminChecks):
    def _check_relation(self, cls, parent_model):
        return []
    def _check_exclude_of_parent_model(self, cls, parent_model):
        return []


class ContentInline(admin.options.InlineModelAdmin):
    template = 'admin/edit_inline/tabular.html'
    # ct_field = "content_type_id"
    # max_num = 0
    checks_class = DummyCheck
    # formset = ContentFormset
    
    def has_add_permission(self, request):
        return False
    
    def get_formset(self, request, obj=None, **kwargs):
        """Returns a BaseInlineFormSet class for use in admin add/change views."""
        
        print '>>', obj, kwargs
        
        class Form(forms.ModelForm):
            needs_explicit_pk_field = False
            class Meta:
                model = Block
        
        class FormSet(forms.BaseFormSet):
            form = Form
            min_num = 0
            extra = 0
            max_num = 0
            can_order = False
            can_delete = False
            
            
            def get_queryset(self):
                return self.queryset
            
            def __init__(self, instance, queryset, *args, **kwargs):
                self.queryset = queryset
                print instance, queryset, args, kwargs
                super(FormSet, self).__init__(*args, **kwargs)
        
        return FormSet
        
        
        # if 'fields' in kwargs:
        #     fields = kwargs.pop('fields')
        # else:
        #     fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        # if self.exclude is None:
        #     exclude = []
        # else:
        #     exclude = list(self.exclude)
        # exclude.extend(self.get_readonly_fields(request, obj))
        # if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
        #     # Take the custom ModelForm's Meta.exclude into account only if the
        #     # InlineModelAdmin doesn't define its own.
        #     exclude.extend(self.form._meta.exclude)
        # # If exclude is an empty list we use None, since that's the actual
        # # default.
        # exclude = exclude or None
        # can_delete = self.can_delete and self.has_delete_permission(request, obj)
        # defaults = {
        #     "form": self.form,
        #     "formset": self.formset,
        #     "fk_name": self.fk_name,
        #     "fields": fields,
        #     "exclude": exclude,
        #     "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        #     "extra": self.get_extra(request, obj, **kwargs),
        #     "min_num": self.get_min_num(request, obj, **kwargs),
        #     "max_num": self.get_max_num(request, obj, **kwargs),
        #     "can_delete": can_delete,
        # }
        # 
        # defaults.update(kwargs)
        # base_model_form = defaults['form']
        # 
        # class DeleteProtectedModelForm(base_model_form):
        #     def hand_clean_DELETE(self):
        #         """
        #         We don't validate the 'DELETE' field itself because on
        #         templates it's not rendered using the field information, but
        #         just using a generic "deletion_field" of the InlineModelAdmin.
        #         """
        #         if self.cleaned_data.get(DELETION_FIELD_NAME, False):
        #             using = router.db_for_write(self._meta.model)
        #             collector = NestedObjects(using=using)
        #             collector.collect([self.instance])
        #             if collector.protected:
        #                 objs = []
        #                 for p in collector.protected:
        #                     objs.append(
        #                         # Translators: Model verbose name and instance representation, suitable to be an item in a list
        #                         _('%(class_name)s %(instance)s') % {
        #                             'class_name': p._meta.verbose_name,
        #                             'instance': p}
        #                     )
        #                 params = {'class_name': self._meta.model._meta.verbose_name,
        #                           'instance': self.instance,
        #                           'related_objects': get_text_list(objs, _('and'))}
        #                 msg = _("Deleting %(class_name)s %(instance)s would require "
        #                         "deleting the following protected related objects: "
        #                         "%(related_objects)s")
        #                 raise ValidationError(msg, code='deleting_protected', params=params)
        # 
        #     def is_valid(self):
        #         result = super(DeleteProtectedModelForm, self).is_valid()
        #         self.hand_clean_DELETE()
        #         return result
        # 
        # defaults['form'] = DeleteProtectedModelForm
        # 
        # if defaults['fields'] is None and not modelform_defines_fields(defaults['form']):
        #     defaults['fields'] = forms.ALL_FIELDS
        # 
        # return inlineformset_factory(self.parent_model, self.model, **defaults)


class BlockInline(ContentInline):
    model = Block
    fields = ('content',)
    form = BlockForm


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        exclude = ()
    
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)

        required_cb = cms_settings.IMAGE_REQUIRED_CALLBACK
        if callable(required_cb) and 'instance' in kwargs:
            self.fields['file'].required = required_cb(kwargs['instance'])


class ImageInline(ContentInline):
    model = Image
    exclude = ('label',)
    form = ImageForm


class PageSiteInline(admin.TabularInline):
    model = PageSite
    extra = 0

class CMSBaseAdmin(admin.ModelAdmin):
    # inlines=[BlockInline,ImageInline,]
    inlines = [PageSiteInline]
    list_display=['url',]
    save_on_top = True
    
    class Media:
        js = admin_js
        css = admin_css
    class Meta:
        abstract=True
    
    def get_form(self, request, *args, **kwargs):
        class _Form(super(CMSBaseAdmin, self).get_form(*args, **kwargs)):
            pass
            # def __init__(self, *args, **kwargs):
            #     super(_Form, self).__init__(*args, **kwargs)
        
        # instance = kwargs['instance']
        print self.model
        ctype = ContentType.objects.get_for_model(self.model)
        for block in Block.objects.filter(content_type_id=ctype.id, 
                                          object_id=instance.id):
            self.fields['block_%s' % block.label] = forms.CharField()
        
                
        return _Form
    
    def save_model(self, request, obj, form, change):
        '''Save model, then add blocks/images via dummy rendering.
           
           NOTE: This will naively attempt to render the page using the 
           *current*  django Site object, so if you're in the admin of one site
           editing pages on another, the dummy render will silently fail.
        
        '''
        returnval = super(CMSBaseAdmin, self).save_model(request, obj, form, change)
        
        if getattr(obj, 'get_absolute_url', None):
            c = Client()
            site = Site.objects.get_current()
            response = c.get(unicode(obj.get_absolute_url()), 
                             {'cms_dummy_render': public_key()},
                             HTTP_HOST=site.domain,
                             follow=True)
        return returnval


class PageAdmin(CMSBaseAdmin):
    list_display=['__unicode__', 'url', 'template', 'is_live', 'creation_date',
                  'view_on_site_link',]
    list_display_links=['__unicode__', 'url', ]

    list_filter=['sites', 'template', 'is_live', 'creation_date',]
    
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
    
    # search_fields = ['url', 'blocks__content', 'template',]
    search_fields = ['url', 'template',]
    form = PageForm
    exclude = []
    
    def save_related(self, request, form, formsets, change):
        super(PageAdmin, self).save_related(request, form, formsets, change)
        
        # If the sites field is hidden, and no site is set, add the default one
        if not cms_settings.USE_SITES_FRAMEWORK and not form.instance.sites.count():
            PageSite.objects.create(site_id=settings.SITE_ID, page=form.instance)
    
if cms_settings.USE_SITES_FRAMEWORK:
    PageAdmin.list_display.append('get_sites')
else:
    PageAdmin.exclude.append('sites')

     
admin.site.register(Page, PageAdmin)


class ContentAdmin(admin.ModelAdmin):
    def label_display(self, obj):
        return obj.label.replace('-', ' ').replace('_', ' ').capitalize()
    label_display.short_description = 'label'
    label_display.admin_order_field = 'label'

class BlockFormSite(BlockForm):
    label = forms.CharField(widget=ReadonlyInput)

class BlockAdmin(ContentAdmin):
    form = BlockFormSite
    fields = ['label', 'content',]
    list_display = ['label_display', 'content_object', 'format', 'content_snippet', ]
    search_fields = ['label', ]
    list_filter = [ContentTypeFilter]
    
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

class ImageAdmin(ContentAdmin):
    fields = ['label', 'file', 'description', ]
    list_display = ['label_display', 'content_object', 'file', 'description', ]
    form = ImageFormSite
    search_fields = ['label', ]
    list_filter = [ContentTypeFilter]

admin.site.register(Image, ImageAdmin)
