from __future__ import unicode_literals

from functools import partial

from django.contrib.admin.checks import InlineModelAdminChecks
from django.contrib.admin.options import InlineModelAdmin, flatten_fieldsets
from django.core import checks
from django.db.models.fields import FieldDoesNotExist
from django.forms import ALL_FIELDS
from django.forms.models import modelform_defines_fields

from admin_forms import content_inlineformset_factory, BaseContentFormSet


class ContentInlineChecks(InlineModelAdminChecks):
    def _check_exclude_of_parent_model(self, cls, parent_model):
        return []

    def _check_relation(self, cls, parent_model):
        return []


class ContentInline(InlineModelAdmin):
    template = 'admin/edit_inline/tabular.html'

    ct_field = "content_type_id"
    ct_fk_field = "object_id"
    formset = BaseContentFormSet

    checks_class = ContentInlineChecks

    def has_add_permission(self, request):
        return False

    def get_formset(self, request, obj=None, **kwargs):
        if 'fields' in kwargs:
            fields = kwargs.pop('fields')
        else:
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(self.get_readonly_fields(request, obj))
        if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # GenericInlineModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        exclude = exclude or None
        can_delete = self.can_delete and self.has_delete_permission(request, obj)
        defaults = {
            "form": self.form,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            "formset": self.formset,
            "extra": self.get_extra(request, obj),
            "can_delete": can_delete,
            "can_order": False,
            "fields": fields,
            "min_num": self.get_min_num(request, obj),
            "max_num": self.get_max_num(request, obj),
            "exclude": exclude
        }
        defaults.update(kwargs)
        
        if defaults['fields'] is None and not modelform_defines_fields(defaults['form']):
            defaults['fields'] = ALL_FIELDS
        
        return content_inlineformset_factory(self.model, **defaults)

