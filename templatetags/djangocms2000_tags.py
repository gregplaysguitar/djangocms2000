from django import template
from djangocms2000.models import Block, Page, Image, MenuItem
from djangocms2000.forms import BlockForm, ImageForm
from django.contrib.auth.forms import AuthenticationForm
from django import template
from djangocms2000 import settings as djangocms2000_settings
from django.conf import settings
from culturethree.util.decorators import easy_tag
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.functional import allow_lazy
import re
from django.utils.encoding import force_unicode



register = template.Library()




class CMSBlockNode(template.Node):
    def __init__(self, label, format, editable, content_object=None, alias=None):
        self.label = label
        self.format = format
        self.editable = editable
        self.content_object = content_object
        self.alias = alias
        
    def render(self, context):
        
        if isinstance(self.content_object, unicode):
            content_object = template.Variable(self.content_object).resolve(context)
        else:
            content_object = self.content_object

        label = template.Variable(self.label).resolve(context)
        if isinstance(self.format, str):
            format = self.format
        else:
            format = template.Variable(self.format).resolve(context)
        
        #print format
        #print context['testimonial']
        #print content_object
        
        
        if not content_object:
            try:
                content_object = Page.objects.get(uri=context['request'].path_info)
            except Page.DoesNotExist:
                # set the template to blank for created pages otherwise it can be misleading in the admin
                content_object = Page.objects.create(uri=context['request'].path_info, template='')

                
        block, created = Block.objects.get_or_create(
            label=label,
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.id
        )
        if created:
            block.format = format
            block.save()
        

        data = {
            'format': format,
            'label': label,
            'request': context['request'],
            'sitewide': isinstance(content_object, Site),
        }
                
        if context['request'].user.has_perm("djangocms2000.change_page") and self.editable != "False" and djangocms2000_settings.EDIT_IN_PLACE and 'djangocms2000-edit_mode' in context['request'].COOKIES:
            data['block'] = block

            returnval = template.loader.render_to_string("djangocms2000/cms/block.html", data)
        else:
            returnval = block.compiled_content
        
        if self.alias:
            context[self.alias] = returnval
            return ""
        else:
            return returnval
        
@easy_tag
def cmsblock(_tag, label, format="html", editable=True, _as='', alias=None):
    return CMSBlockNode(label, format, editable, None, alias)

register.tag(cmsblock)


@easy_tag
def cmsgenericblock(_tag, label, content_object_variable, format="html", editable=True, _as='', alias=None):
    return CMSBlockNode(label, format, editable, content_object_variable, alias)

register.tag(cmsgenericblock)


@easy_tag
def cmssiteblock(_tag, label, format="html", editable=True, _as='', alias=None):
    content_object = Site.objects.get(pk=settings.SITE_ID)
    return CMSBlockNode(label, format, editable, content_object, alias)

register.tag(cmssiteblock)










class CMSImageNode(template.Node):
    def __init__(self, label, content_object=False, constraint=False, crop="", defaultimage=False, editable=True):
        self.label = label
        self.content_object = content_object
        self.constraint = constraint
        self.defaultimage = defaultimage
        self.crop = crop
        self.editable = editable

    def render(self, context):
        #return "dsfds"
        if isinstance(self.content_object, unicode):
            content_object = template.Variable(self.content_object).resolve(context)
        else:
            content_object = self.content_object
        
        if self.constraint:
            constraint = template.Variable(self.constraint).resolve(context)
        else:
            constraint = False
        
        if self.defaultimage:
            defaultimage = template.Variable(self.defaultimage).resolve(context)
        else:
            defaultimage = False
        
        label = template.Variable(self.label).resolve(context)
        
        
        if not content_object:
            content_object, created = Page.objects.get_or_create(uri=context['request'].path_info)
        
        image, created = Image.objects.get_or_create(
            label=label,
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.id
        )
        #print image.file
        data = {
            'label': label,
            'request': context['request'],
            'image': image,
            'constraint': constraint,
            'crop': self.crop,
            'defaultimage': defaultimage,
            'sitewide': isinstance(content_object, Site),
        }
        #print self.editable
        if context['request'].user.has_perm("djangocms2000.change_page") and djangocms2000_settings.EDIT_IN_PLACE and self.editable != "False" and 'djangocms2000-edit_mode' in context['request'].COOKIES:
            data['editable'] = True
            
        return template.loader.render_to_string("djangocms2000/cms/image.html", data)



@easy_tag
def cmsimage(_tag, label, constraint, crop="", defaultimage=False, editable=True):
    return CMSImageNode(label, False, constraint, crop, defaultimage, editable)

register.tag(cmsimage)


@easy_tag
def cmsgenericimage(_tag, label, content_object_variable, constraint, crop="", defaultimage=False, editable=True):
    return CMSImageNode(label, content_object_variable, constraint, crop, defaultimage, editable)

register.tag(cmsgenericimage)


@easy_tag
def cmssiteimage(_tag, label, constraint, crop="", defaultimage=False, editable=True):
    content_object = Site.objects.get(pk=settings.SITE_ID)
    return CMSImageNode(label, content_object, constraint, crop, defaultimage, editable)

register.tag(cmssiteimage)




# gets a list of menu items from models.MenuItem
class CmsPageMenuNode(template.Node):
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        #print MenuItem.objects.all()
        context[self.varname] = MenuItem.objects.all()
        return ''

@register.tag
@easy_tag
def get_page_menu(_tag, _as, varname):
    return CmsPageMenuNode(varname)








class CMSCrumbtrailNode(template.Node):
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        #varname = template.Variable(self.varname).resolve(context)
        crumbtrail = []
        
        url_parts = context['request'].META['PATH_INFO'].strip('/').split('/')
        current_url = '/'
        for url_part in url_parts:
            current_url += url_part + '/'
            name = url_part.replace('-', ' ').replace(':', ': ').title()
            crumbtrail.append({'uri': current_url, 'name': name})
        
        context[self.varname] = crumbtrail
        return ''

@register.tag
@easy_tag
def cmsgetcrumbtrail(_tag, _as, varname):
    return CMSCrumbtrailNode(varname)






class CMSExtraNode(template.Node):
        
    def render(self, context):
        if djangocms2000_settings.EDIT_IN_PLACE:
            if context['request'].user.has_module_perms("djangocms2000"):
                if 'djangocms2000-edit_mode' in context['request'].COOKIES:
                    try:
                        page = Page.objects.get(uri=context['request'].path_info)
                    except Page.DoesNotExist:
                        page = False

                    return template.loader.render_to_string("djangocms2000/cms/editor.html", {
                        'request': context['request'],
                        'page': page,
                        'djangocms2000_settings': djangocms2000_settings,
                        'editor_form': BlockForm(),
                        'image_form': ImageForm(),
                    })
                else:
                    return template.loader.render_to_string("djangocms2000/cms/logged_in.html", {
                        'djangocms2000_settings': djangocms2000_settings,
                    })
            elif 'edit' in context['request'].GET:
                return template.loader.render_to_string("djangocms2000/cms/login_top.html", {
                    'login_form': AuthenticationForm(),
                })
            elif 'djangocms2000-has_edited_before' in context['request'].COOKIES:
                return template.loader.render_to_string("djangocms2000/cms/persistent_link.html")
            else:
                return ""
        else:
            return ''
            
@easy_tag
def cmsextra(_tag):
    return CMSExtraNode()

register.tag(cmsextra)







class ZealousSpacelessNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return self.strip_spaces_between_tags(self.nodelist.render(context).strip())
    
    def strip_spaces_between_tags(self, value):
        value = re.sub(r'\s+<', '<', force_unicode(value))
        value = re.sub(r'>\s+', '>', force_unicode(value))
        return value
    strip_spaces_between_tags = allow_lazy(strip_spaces_between_tags, unicode)

@register.tag
def zealousspaceless(parser, token):
    """like spaceless, but removes space between text and tags also"""
    nodelist = parser.parse(('endzealousspaceless',))
    parser.delete_first_token()
    return ZealousSpacelessNode(nodelist)


