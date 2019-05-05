import re

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.sites.models import Site

from .models import Page, Block, Image, Video, template_choices, PageSite
from . import settings as cms_settings
from .utils import url_resolves


class ReadonlyInput(forms.widgets.HiddenInput):
    is_hidden = False

    def __init__(self, attrs=None, model=None, display_text=None):
        super(ReadonlyInput, self).__init__(attrs)
        self.model = model
        self.display_text = display_text

    def render(self, name, value, attrs=None, renderer=None):
        if self.display_text:
            text_value = self.display_text
        elif self.model:
            text_value = self.model.objects.get(pk=value)
        else:
            text_value = value
        return mark_safe("<p>%s</p>%s" % (
            text_value, super(ReadonlyInput, self).render(name, value, attrs)))


class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = ('content', )


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('file', 'description', )


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('source', 'poster', 'loop', 'description', )


URL_STRIP_REGEX = re.compile(r'[^A-z0-9\-_?=&\/\.]')
URL_DASH_REGEX = re.compile(r'-+')
URL_SLASH_REGEX = re.compile(r'\/+')


class PageForm(forms.ModelForm):
    template = forms.CharField(
        widget=forms.Select(choices=template_choices()),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)

        # just in case a template has been added/changed since last server
        # restart
        self.fields['template'].widget.choices = template_choices()

        # if the page is rendered by an actual django url, make template
        # url and is_live read-only
        instance = kwargs.get('instance', None)
        if instance and url_resolves(instance.url):
            # must be a django-created page, rendered by a urlconf
            self.fields['url'].widget = ReadonlyInput()
            self.fields['url'].help_text = ''

            self.fields['template'].widget = ReadonlyInput(display_text='n/a')
            self.fields['template'].help_text = ''
            if not instance.template:
                self.fields['is_live'].widget = ReadonlyInput(
                    display_text='n/a')
                self.fields['is_live'].help_text = ''

    class Meta:
        model = Page
        exclude = ()

    def clean(self):
        data = self.cleaned_data
        url = data.get('url')

        # assume we're editing a page for the current site if not otherwise
        # apparent
        sites = data.get('sites', [Site.objects.get_current()])

        if not url:
            return data

        # normalise url
        url = URL_STRIP_REGEX.sub('', data['url'].replace(' ', '-')).lower()
        url = URL_DASH_REGEX.sub('-', url).strip('-')
        url = URL_SLASH_REGEX.sub('/', "/%s" % (url.lstrip('/')))

        # check uniqueness of url/site
        site_ids = [s.id for s in sites]
        site_pages = Page.objects.filter(sites__site_id__in=site_ids)

        if self.instance:
            site_pages = site_pages.exclude(pk=self.instance.pk)

        # for the purposes of uniqueness and testing the url, treat both
        # slashed and non-slashed urls as the same
        test_urls = [url.rstrip('/'), "%s/" % url.rstrip('/')]

        clashes = site_pages.filter(url__in=test_urls)
        if clashes:
            # TODO: only show the site(s) with actual clashes
            sites = [s.domain for s in sites]
            err = 'A page with this url already exists for %s.' % (
                ', '.join(sites))
            self._errors['url'] = self.error_class([err])

        url_defined = any([url_resolves(u) for u in test_urls])
        own_site = not data.get('sites') or (settings.SITE_ID in data['sites'])

        # The following validation only applies to pages created in the admin,
        # and cannot be done reliably when editing a page for a different site
        if own_site and not url_defined:
            # Append a slash for consistency, but only if neither the original
            # of the slash-appended url is defined in a urlconf
            if settings.APPEND_SLASH and not url.endswith('/'):
                url = url + '/'

            # Require template for admin-created pages
            if not data.get('template'):
                err = 'This field is required for admin-created pages.'
                self._errors['template'] = self.error_class([err])

        data['url'] = url
        return data

    def save_sites(self, *args, **kwargs):
        if not self.instance.sites.count():
            # Add default site if no site already set
            PageSite.objects.create(site_id=settings.SITE_ID,
                                    page=self.instance)


class PageFormWithSites(PageForm):
    sites = forms.ModelMultipleChoiceField(queryset=Site.objects)

    def __init__(self, *args, **kwargs):
        super(PageFormWithSites, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)

        if instance:
            # initial value for sites comes from the related PageSite model
            self.fields['sites'].initial = [s.site for s in
                                            instance.sites.all()]

    def save_sites(self, *args, **kwargs):
        # update PageSite instances from sites field data
        sites = list(self.cleaned_data['sites'])
        for pagesite in self.instance.sites.all():
            if pagesite.site in sites:
                del sites[sites.index(pagesite.site)]
            else:
                pagesite.delete()

        for site in sites:
            PageSite.objects.create(page=self.instance, site_id=site.id)


def get_page_form_cls():
    if cms_settings.USE_SITES_FRAMEWORK:
        return PageFormWithSites
    else:
        return PageForm
