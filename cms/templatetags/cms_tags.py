import os

try:
    import sorl
except ImportError:
    sorl = None

from django import template
from django.contrib.auth.forms import AuthenticationForm
from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.utils.safestring import mark_safe

from cms.utils import is_editing
from cms.models import Block, Page, Image, MenuItem, get_child_pages
from cms.forms import BlockForm, ImageForm, PublicPageForm
from cms import settings as cms_settings
from cms.decorators import easy_tag


register = template.Library()


class CMSBlockNode(template.Node):
    def __init__(self, label, format, editable, content_object=None, alias=None, filters=None):
        self.label = label
        self.format = format
        self.editable = editable
        self.content_object = content_object
        self.alias = alias
        self.filters = filters
        
    def render(self, context):
        
        if isinstance(self.content_object, unicode):
            content_object = template.Variable(self.content_object).resolve(context)
        else:
            content_object = self.content_object
        
        # note the `label = kwargs['parser'].compile_filter(label)` below
        label = self.label.resolve(context)

        if isinstance(self.format, str):
            format = self.format
        else:
            format = template.Variable(self.format).resolve(context)
        
        if self.editable == True:
            editable = True
        else:
            editable = template.Variable(self.editable).resolve(context)
        
        
        if not content_object:
            content_object = Page.objects.get_for_url(context['request'].path_info)
                
        block, created = Block.objects.get_or_create(
            label=label,
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.id
        )
        if created:
            block.format = format
            block.save()
        
        
        if self.filters:
            filters = template.Variable(self.filters).resolve(context).split(',')
        else:
            filters = []
            
        filtered_content = block.get_filtered_content(filters)
        
        if block.format != 'plain':
            filtered_content = mark_safe(filtered_content)
                       
        if 'request' in context and context['request'].user.has_perm("cms.change_page") and editable and cms_settings.EDIT_IN_PLACE and is_editing(context['request']):
            returnval = mark_safe(template.loader.render_to_string("cms/cms/block.html", {
                'format': format,
                'filters': ','.join(filters),
                'label': label,
                'request': context['request'],
                'sitewide': isinstance(content_object, Site),
                'filtered_content': filtered_content,
                'block': block
            }))
        else:
            returnval = filtered_content


        if self.alias:
            context[self.alias] = returnval
            return ""
        else:
            return returnval
    
    
@register.tag
@easy_tag
def cmsblock(_tag, label, format="plain", editable=True, _as='', alias=None, filters=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSBlockNode(label, format, editable, None, alias, filters)


@register.tag
@easy_tag
def cmsgenericblock(_tag, label, content_object_variable, format="plain", editable=True, _as='', alias=None, filters=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSBlockNode(label, format, editable, content_object_variable, alias, filters)

@register.tag
@easy_tag
def cmssiteblock(_tag, label, format="plain", editable=True, _as='', alias=None, filters=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    content_object = Site.objects.get(pk=settings.SITE_ID)
    return CMSBlockNode(label, format, editable, content_object, alias, filters)







try:
    from django.template.defaulttags import csrf_token
except ImportError:
    @register.tag
    def csrf_token(parser, token):
        return template.Node()




class CMSImageNode(template.Node):
    def __init__(self, label, content_object=False, constraint=None, crop="", defaultimage=False, editable=True, format='', colorspace='', alias=None):
        self.label = label
        self.content_object = content_object
        self.constraint = constraint
        self.defaultimage = defaultimage
        self.crop = crop
        self.editable = editable
        self.format = format
        self.colorspace = colorspace
        self.alias = alias

    def render(self, context):
        #return "dsfds"
        if isinstance(self.content_object, unicode):
            content_object = template.Variable(self.content_object).resolve(context)
        else:
            content_object = self.content_object
        
        if self.editable == True:
            editable = True
        else:
            editable = template.Variable(self.editable).resolve(context)
        
        if self.constraint:
            constraint = template.Variable(self.constraint).resolve(context)
        else:
            constraint = None
        
        if self.defaultimage:
            defaultimage = template.Variable(self.defaultimage).resolve(context)
        else:
            defaultimage = False
        
        if self.format:
            format = template.Variable(self.format).resolve(context)
        else:
            format = 'html'
        
        if self.colorspace:
            colorspace = template.Variable(self.colorspace).resolve(context)
        else:
            colorspace = ''
        
        label = self.label.resolve(context)
        
        
        if not content_object:
            content_object = Page.objects.get_for_url(context['request'].path_info)
            

        image, created = Image.objects.get_or_create(
            label=label,
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.id
        )
        #print image.file
        try:
            crop = template.Variable(self.crop).resolve(context)
        except:
            crop = self.crop
        
        if crop == 'crop':
            crop = 'center'
        
        data = {
            'label': label,
            'request': context.get('request', None),
            'image': image,
            'constraint': constraint,
            'crop': crop,
            'colorspace': colorspace,
            'defaultimage': defaultimage,
            'sitewide': isinstance(content_object, Site),
            'content_object': content_object,
        }
        #print self.editable
        if 'request' in context and context['request'].user.has_perm("cms.change_page") and cms_settings.EDIT_IN_PLACE and editable and is_editing(context['request']):
            data['editable'] = True
        
        
        


        if hasattr(sorl, "NullHandler"):
            # assume up-to-date sorl
            if format == 'url':
                returnval = template.loader.render_to_string("cms/cms/image_url.html", data)
            else:
                returnval = template.loader.render_to_string("cms/cms/image.html", data)
        else:
            # assume older sorl syntax
            if format == 'url':
                returnval = template.loader.render_to_string("cms/cms/image_url_oldsorl.html", data)
            else:
                returnval = template.loader.render_to_string("cms/cms/image_oldsorl.html", data)
        
        
        if self.alias:
            if returnval.strip():
                context[self.alias] = mark_safe(returnval)
            else:
                context[self.alias] = ''
            return ""
        else:
            return returnval


@register.tag
@easy_tag
def cmsimage(_tag, label, constraint=None, crop="", defaultimage=False, editable=True, format=None, colorspace='', _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSImageNode(label, False, constraint, crop, defaultimage, editable, format, colorspace, alias)



@register.tag
@easy_tag
def cmsgenericimage(_tag, label, content_object_variable, constraint=None, crop="", defaultimage=False, editable=True, format=None, colorspace='', _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSImageNode(label, content_object_variable, constraint, crop, defaultimage, editable, format, colorspace, alias)



@register.tag
@easy_tag
def cmssiteimage(_tag, label, constraint=None, crop="", defaultimage=False, editable=True, format=None, colorspace='', _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    content_object = Site.objects.get(pk=settings.SITE_ID)
    return CMSImageNode(label, content_object, constraint, crop, defaultimage, editable, format, colorspace, alias)




class CMSEditorNode(template.Node):
        
    def render(self, context):
        if cms_settings.EDIT_IN_PLACE:
            if context['request'].user.has_module_perms("cms"):
                if is_editing(context['request']):
                    try:
                        page = Page.objects.get(url=context['request'].path_info)
                    except Page.DoesNotExist:
                        page = False

                    return template.loader.render_to_string("cms/cms/editor.html", RequestContext(context['request'], {
                        'page': page,
                        'cms_settings': cms_settings,
                        'editor_form': BlockForm(),
                        'html_editor_form': BlockForm(prefix="html"),
                        'image_form': ImageForm(),
                        'page_form': page and PublicPageForm(instance=page) or None,
                        'new_page_form': PublicPageForm(prefix='new'),
                    }))
                else:
                    return template.loader.render_to_string("cms/cms/logged_in.html", RequestContext(context['request'], {
                        'cms_settings': cms_settings,
                    }))
            elif 'edit' in context['request'].GET:
                return template.loader.render_to_string("cms/cms/login_top.html", RequestContext(context['request'], {
                    'login_form': AuthenticationForm(),
                    'cms_settings': cms_settings,
                }))
            elif 'cms-has_edited_before' in context['request'].COOKIES:
                return "" #template.loader.render_to_string("cms/cms/persistent_link.html")
            else:
                return ""
        else:
            return ''

@register.tag
@easy_tag
def cmseditor(_tag):
    return CMSEditorNode()







class CMSEditingNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = is_editing(context['request'])
        return ''

@register.tag
@easy_tag
def cmsediting(_tag, _as, varname):
    return CMSEditingNode(varname)





