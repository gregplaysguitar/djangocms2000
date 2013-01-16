import re

from django import forms
from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.utils.safestring import mark_safe

from models import Page, template_choices



class ReadonlyInput(forms.widgets.HiddenInput):
    is_hidden = False
    def __init__(self, attrs=None, model=None):
        super(ReadonlyInput, self).__init__(attrs)
        self.model = model
        
    def render(self, name, value, attrs=None):
        if self.model:
            text_value = self.model.objects.get(pk=value)
        else:
            text_value = value
        return mark_safe("<p>%s</p>%s" % (text_value, super(ReadonlyInput, self).render(name, value, attrs)))



class BlockForm(forms.Form):
	block_id = forms.CharField(widget=forms.HiddenInput)
	format = forms.CharField(widget=forms.HiddenInput)
	
	raw_content = forms.CharField(widget=forms.Textarea)


class ImageForm(forms.Form):
	image_id = forms.CharField(widget=forms.HiddenInput)
	redirect_to = forms.CharField(widget=forms.HiddenInput)
	
	description = forms.CharField(widget=forms.TextInput)
	file = forms.FileField()




URL_STRIP_REGEX = re.compile('[^A-z0-9\-_\/\.]')
URL_DASH_REGEX = re.compile('--+')
class PageForm(forms.ModelForm):
    template = forms.CharField(
        widget=forms.Select(choices=template_choices()),
        #help_text="Choose from Static Templates unless you're sure of what you're doing.",
        required=False
    )
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        
        # just in case a template has been added/changed since last server restart
        self.fields['template'].widget.choices = template_choices()
                
        # if the page is rendered by an actual django url, make template and url read-only
        instance = kwargs.get('instance', None)
        if instance:
            try:
                resolve(instance.url)
            except Resolver404, e:
                # must be an admin-created page, rendered by the middleware
                pass
            else:
                # must be a django-created page, rendered by a urlconf
                self.fields['url'].widget = ReadonlyInput()
                self.fields['url'].help_text = ''
                self.fields['template'].widget = ReadonlyInput()
                #self.fields['template'].help_text = ''
        
    class Meta:
        model = Page
    
    def clean(self):
        data = self.cleaned_data
        if not data.get('template', None) and data.get('url', None):
            try:
                resolve(data['url'])
            except Resolver404, e:
                self._errors['template'] = self.error_class(['This field is required for admin-created pages.'])
        
        # validate url/site uniqueness
        url = URL_STRIP_REGEX.sub('', data['url'].replace(' ', '-')).lower()
        url = URL_DASH_REGEX.sub('-', url).strip('-')
        
        url = ("/%s" % (url.lstrip('/'))).replace('//', '/')
        
        if settings.APPEND_SLASH and url[-1] != '/':
            url = "%s/" % url
        
        site_pages = Page.objects.filter(site=data['site'])
        test_urls = [url.rstrip('/'), "%s/" % url.rstrip('/')]
        if site_pages.exclude(pk=self.instance and self.instance.pk).filter(url__in=test_urls):
            self._errors['url'] = self.error_class(['A page with this url already exists'])
        
        data['url'] = url
        
        return data
        



class PublicPageForm(PageForm):
    class Meta(PageForm.Meta):
        exclude = ['site',]
    
    
    