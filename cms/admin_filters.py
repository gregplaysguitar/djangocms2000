from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site


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
        
        others = model_admin.model.objects.exclude(content_type_id=site_ctype().id) \
                .order_by().values_list('content_type_id', flat=True).distinct()
        
        for ctype_id in others:
            ctype = ContentType.objects.get(pk=ctype_id)
            lookup_list.append((str(ctype_id), str(ctype).title()))
        
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
        if val == None:
            return queryset.filter(content_type_id=site_ctype().id)
        elif val == 'all':
            return queryset
        else:
            return queryset.filter(content_type_id=ContentType.objects.get(pk=val).id)


