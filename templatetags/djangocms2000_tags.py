from django import template
from djangocms2000.models import Block, Page, Image, MenuItem, get_child_pages
from djangocms2000.forms import BlockForm, ImageForm, PublicPageForm
from django.contrib.auth.forms import AuthenticationForm
from django import template
from djangocms2000 import settings as djangocms2000_settings
from django.conf import settings
from djangocms2000.decorators import easy_tag
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.functional import allow_lazy
import re, os
from django.utils.encoding import force_unicode
from djangocms2000.utils import is_editing
from django.template import RequestContext
from django.utils.safestring import mark_safe

register = template.Library()


# special implementation for Page.get_or_create - sets the template
# for created pages in an attempt to minimise confusion in the admin
def get_or_create_page(uri):
    try:
        return Page.objects.get(uri=uri)
    except Page.DoesNotExist:
        # attempt to guess template from url
        if os.path.exists(os.path.join(settings.TEMPLATE_DIRS[0], uri.strip('/') + '.html')):
            template = os.path.join(uri.strip('/') + '.html')
        elif os.path.exists(os.path.join(settings.TEMPLATE_DIRS[0], uri.strip('/'), 'index.html')):
            template = os.path.join(uri.strip('/'), 'index.html')
        else:
            template = ''
    
        return Page.objects.create(uri=uri, template=template)
    




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
        
        # note the `label = kwargs['parser'].compile_filter(label)` below
        label = self.label.resolve(context)

        if isinstance(self.format, str):
            format = self.format
        else:
            format = template.Variable(self.format).resolve(context)
        
        
        self.editable = self.editable in [True, 'True'] or (self.editable not in ['False', '0', 0] and template.Variable(self.editable).resolve(context))
        
        
        if not content_object:
            content_object = get_or_create_page(context['request'].path_info)
                
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
                
        if context['request'].user.has_perm("djangocms2000.change_page") and self.editable and djangocms2000_settings.EDIT_IN_PLACE and is_editing(context['request']):
            data['block'] = block

            returnval = template.loader.render_to_string("djangocms2000/cms/block.html", data)
        else:
            returnval = block.compiled_content
        
        if self.alias:
            context[self.alias] = mark_safe(returnval)
            return ""
        else:
            return returnval
        
@easy_tag
def cmsblock(_tag, label, format="html", editable=True, _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSBlockNode(label, format, editable, None, alias)

register.tag(cmsblock)

@register.tag
@easy_tag
def cmsgenericblock(_tag, label, content_object_variable, format="html", editable=True, _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSBlockNode(label, format, editable, content_object_variable, alias)



@easy_tag
def cmssiteblock(_tag, label, format="html", editable=True, _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    content_object = Site.objects.get(pk=settings.SITE_ID)
    return CMSBlockNode(label, format, editable, content_object, alias)

register.tag(cmssiteblock)






try:
    from django.template.defaulttags import csrf_token
except ImportError:
    @register.tag
    def csrf_token(parser, token):
        return template.Node()




class CMSImageNode(template.Node):
    def __init__(self, label, content_object=False, constraint=False, crop="", defaultimage=False, editable=True, format='html', alias=None):
        self.label = label
        self.content_object = content_object
        self.constraint = constraint
        self.defaultimage = defaultimage
        self.crop = crop
        self.editable = editable
        self.format = format
        self.alias = alias

    def render(self, context):
        #return "dsfds"
        if isinstance(self.content_object, unicode):
            content_object = template.Variable(self.content_object).resolve(context)
        else:
            content_object = self.content_object
        
        self.editable = self.editable in [True, 'True'] or (self.editable not in ['False', '0', 0] and template.Variable(self.editable).resolve(context))
        
        if self.constraint:
            constraint = template.Variable(self.constraint).resolve(context)
        else:
            constraint = False
        
        if self.defaultimage:
            defaultimage = template.Variable(self.defaultimage).resolve(context)
        else:
            defaultimage = False
        
        if self.format:
            format = template.Variable(self.format).resolve(context)
        else:
            format = 'html'
        
        label = self.label.resolve(context)
        
        
        if not content_object:
            content_object = get_or_create_page(context['request'].path_info)
            

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
            
        data = {
            'label': label,
            'request': context['request'],
            'image': image,
            'constraint': constraint,
            'crop': crop,
            'defaultimage': defaultimage,
            'sitewide': isinstance(content_object, Site),
            'content_object': content_object,
        }
        #print self.editable
        if context['request'].user.has_perm("djangocms2000.change_page") and djangocms2000_settings.EDIT_IN_PLACE and self.editable and is_editing(context['request']):
            data['editable'] = True
        
        try:
            if format == 'url':
                returnval = template.loader.render_to_string("djangocms2000/cms/image_url.html", data)
            else:
                returnval = template.loader.render_to_string("djangocms2000/cms/image.html", data)
        except template.TemplateSyntaxError, e:
            if format == 'url':
                returnval = template.loader.render_to_string("djangocms2000/cms/image_url_oldsorl.html", data)
            else:
                returnval = template.loader.render_to_string("djangocms2000/cms/image_oldsorl.html", data)
        
        
        if self.alias:
            if returnval.strip():
                context[self.alias] = mark_safe(returnval)
            else:
                context[self.alias] = ''
            return ""
        else:
            return returnval


@easy_tag
def cmsimage(_tag, label, constraint, crop="", defaultimage=False, editable=True, format=None, _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSImageNode(label, False, constraint, crop, defaultimage, editable, format, alias)

register.tag(cmsimage)


@easy_tag
def cmsgenericimage(_tag, label, content_object_variable, constraint, crop="", defaultimage=False, editable=True, format=None, _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSImageNode(label, content_object_variable, constraint, crop, defaultimage, editable, format, alias)

register.tag(cmsgenericimage)


@easy_tag
def cmssiteimage(_tag, label, constraint, crop="", defaultimage=False, editable=True, format=None, _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    content_object = Site.objects.get(pk=settings.SITE_ID)
    return CMSImageNode(label, content_object, constraint, crop, defaultimage, editable, format, alias)

register.tag(cmssiteimage)





# gets a list of menu items from models.MenuItem
class CmsPageMenuNode(template.Node):
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        #print MenuItem.objects.all()
        context[self.varname] = MenuItem.objects.all()
        if not context['request'].user.has_module_perms("djangocms2000"):
            context[self.varname] = context[self.varname].filter(page__is_live=True)
        return ''

@register.tag
@easy_tag
def get_page_menu(_tag, _as, varname):
    return CmsPageMenuNode(varname)




# gets a page
class CmsPageNode(template.Node):
    def __init__(self, varname, uri):
        self.varname = varname
        self.uri = uri
        
    def render(self, context):
        if self.uri:
            uri = template.Variable(self.uri).resolve(context)
        else:
            uri = context['request'].path_info
        context[self.varname] = get_or_create_page(uri)
        return ''

# deprecated, use cmspage instead
@register.tag
@easy_tag
def get_current_page(_tag, _as, varname):
    return CmsPageNode(varname, None)

@register.tag
@easy_tag
def cmspage(_tag, uri, _as, varname):
    return CmsPageNode(varname, uri)









# generates a nested html list of the site structure (relies on sane url scheme)
class CmsSiteMapNode(template.Node):
    def __init__(self, base_uri, include_base, depth, alias):
        self.base_uri = base_uri
        self.include_base = include_base
        self.depth = depth
        self.alias = alias
        
    def render(self, context):
        if context['request'].user.has_module_perms("djangocms2000"):
            page_qs = Page.objects
        else:
            page_qs = Page.live

        try:
            base_uri = self.base_uri and template.Variable(self.base_uri).resolve(context) or '/'
            page = page_qs.get(uri=base_uri)
        except Page.DoesNotExist:
            return ''

        include_base = (self.include_base != 'False' and template.Variable(self.include_base).resolve(context))
        depth = int(self.depth or 0)
        
        
        def _render(page, currentdepth = 1):
            html = []
                
            children = page.get_children(page_qs).order_by('uri')
            if len(children):
                html.append('<ul>')
                for childpage in children:
                    html.append('<li>\n<a href="%s">%s</a>' % (childpage.uri, childpage.page_title()))
                    if (not depth) or currentdepth < depth:
                        html.append(_render(childpage, currentdepth + 1))
                    html.append('</li>')
                html.append('</ul>')
            
            return "\n".join(html)
        
    
        if include_base:
            html = "\n".join([
                '<ul>',
                '<li>',
                '<a href="%s">%s</a>' % (page.uri, page.page_title()),
                _render(page),
                '</li>',
                '</ul>',
            ])
        else:
            html = _render(page)
        

        if self.alias:
            context[self.alias] = mark_safe(html)
            return ''
        else:
            return html
        
# this is deprecated, use cmssitemap instead
@register.tag
@easy_tag
def generate_sitemap(_tag, base_uri=None, include_base=True, depth=None):
    return CmsSiteMapNode(base_uri, include_base, depth)


@register.tag
@easy_tag
def cmssitemap(_tag, base_uri=None, include_base=True, depth=None, _as='', alias=None):
    return CmsSiteMapNode(base_uri, include_base, depth, alias)









class CMSCrumbtrailNode(template.Node):
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        #varname = template.Variable(self.varname).resolve(context)
        crumbtrail = []
        
        if context['request'].META['PATH_INFO'].strip('/'):
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
                if is_editing(context['request']):
                    try:
                        page = Page.objects.get(uri=context['request'].path_info)
                    except Page.DoesNotExist:
                        page = False

                    return template.loader.render_to_string("djangocms2000/cms/editor.html", RequestContext(context['request'], {
                        'page': page,
                        'djangocms2000_settings': djangocms2000_settings,
                        'editor_form': BlockForm(),
                        'html_editor_form': BlockForm(prefix="html"),
                        'image_form': ImageForm(),
                        'page_form': page and PublicPageForm(instance=page) or None,
                        'new_page_form': PublicPageForm(prefix='new'),
                    }))
                else:
                    return template.loader.render_to_string("djangocms2000/cms/logged_in.html", RequestContext(context['request'], {
                        'djangocms2000_settings': djangocms2000_settings,
                    }))
            elif 'edit' in context['request'].GET:
                return template.loader.render_to_string("djangocms2000/cms/login_top.html", RequestContext(context['request'], {
                    'login_form': AuthenticationForm(),
                    'djangocms2000_settings': djangocms2000_settings,
                }))
            elif 'djangocms2000-has_edited_before' in context['request'].COOKIES:
                return "" #template.loader.render_to_string("djangocms2000/cms/persistent_link.html")
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




## Tags for working with Pages

class PageNamedBlockNode(template.Node):
    def __init__(self, page, blockname):
        self.page = template.Variable(page)
        self.blockname = template.Variable(blockname)

    def render(self, context):
        page = self.page.resolve(context)
        blockname = self.blockname.resolve(context)
        return page.blocks.get(label=blockname).compiled_content

@register.tag('get_page_block')
@easy_tag
def get_page_block(_tag, page, block):
    return PageNamedBlockNode(page, block)


class PagesForTemplateNode(template.Node):
    def __init__(self, varname, template_name="default.html"):
        self.varname = varname
        self.template_name = template.Variable(template_name)
        super(PagesForTemplateNode, self).__init__()

    def render(self, context):
        context[self.varname] = Page.objects.filter(template__endswith=self.template_name.resolve(context)).order_by('uri')
        return ''

@register.tag('pages_for_template')
@easy_tag
def pages_for_template(_tagname, template, _as, varname):
    return PagesForTemplateNode(varname, template)

