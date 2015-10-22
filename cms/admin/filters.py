from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from ..utils import key_from_ctype, ctype_from_key


def site_ctype():
    return ContentType.objects.get_for_model(Site)


class ContentTypeFilter(SimpleListFilter):
    '''Filter on related content type, defaulting to sites.Site instead of
       'all'. Assumes a foreignkey to contenttypes.ContentType called
       content_type exists on the model.'''

    title = _('Content Type')
    parameter_name = 'ctype'

    def lookups(self, request, model_admin):
        '''Return filter lookup options. Site is first, and on by default,
           other content types follow, then all.'''

        lookup_list = [
            (None, _('Site')),
        ]

        others = model_admin.model.objects \
            .exclude(content_type=key_from_ctype(site_ctype())) \
            .order_by().values_list('content_type', flat=True).distinct()

        for ctype_key in others:
            ctype = ctype_from_key(ctype_key)
            lookup_list.append((str(ctype.id), str(ctype).title()))

        lookup_list.append(('all', _('All')))

        return lookup_list

    def choices(self, cl):
        '''Iterator returning choices for the filter, based on the lookup
           list.'''

        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        '''Return a filtered queryset based on the selected choice.'''

        val = self.value()
        if val is None:
            return queryset.filter(content_type=key_from_ctype(site_ctype()))
        elif val == 'all':
            return queryset
        else:
            ctype = ContentType.objects.get(pk=val)
            return queryset.filter(content_type=key_from_ctype(ctype))


class PageSiteFilter(SimpleListFilter):
    '''Filter on related Site, via the PageSite model.'''

    title = _('site')
    parameter_name = 'sites'

    def lookups(self, request, model_admin):
        return [(s.id, s.domain) for s in Site.objects.all()]

    # def choices(self, cl):
    #     '''Iterator returning choices for the filter, based on the lookup
    #        list.'''
    #
    #     for lookup, title in self.lookup_choices:
    #         yield {
    #             'selected': self.value() == lookup,
    #             'query_string': cl.get_query_string({
    #                 self.parameter_name: lookup,
    #             }, []),
    #             'display': title,
    #         }

    def queryset(self, request, queryset):
        '''Return a filtered queryset based on the selected choice.'''

        val = self.value()
        if val:
            return queryset.filter(sites__site_id=val)
        return queryset
