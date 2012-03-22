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


def resolve_bool(var, context):
    return var in [True, 'True'] or (var not in ['False', '0', 0] and template.Variable(var).resolve(context))


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
        
        editable = resolve_bool(self.editable, context)
        
        
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
    def __init__(self, label, content_object=False, constraint=None, crop="", defaultimage=False, editable=True, format='html', alias=None):
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
        
        editable = resolve_bool(self.editable, context)
        
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
def cmsimage(_tag, label, constraint=None, crop="", defaultimage=False, editable=True, format=None, _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSImageNode(label, False, constraint, crop, defaultimage, editable, format, alias)



@register.tag
@easy_tag
def cmsgenericimage(_tag, label, content_object_variable, constraint=None, crop="", defaultimage=False, editable=True, format=None, _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    return CMSImageNode(label, content_object_variable, constraint, crop, defaultimage, editable, format, alias)



@register.tag
@easy_tag
def cmssiteimage(_tag, label, constraint=None, crop="", defaultimage=False, editable=True, format=None, _as='', alias=None, **kwargs):
    label = kwargs['parser'].compile_filter(label)
    content_object = Site.objects.get(pk=settings.SITE_ID)
    return CMSImageNode(label, content_object, constraint, crop, defaultimage, editable, format, alias)






# gets a list of menu items from models.MenuItem
class CmsPageMenuNode(template.Node):
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        #print MenuItem.objects.all()
        context[self.varname] = MenuItem.objects.all()
        if not context['request'].user.has_module_perms("cms"):
            context[self.varname] = context[self.varname].filter(page__is_live=True)
        return ''

@register.tag
@easy_tag
def get_page_menu(_tag, _as, varname):
    return CmsPageMenuNode(varname)




# gets a page
class CmsPageNode(template.Node):
    def __init__(self, varname, url):
        self.varname = varname
        self.url = url
        
    def render(self, context):
        if self.url:
            url = template.Variable(self.url).resolve(context)
        else:
            url = context['request'].path_info
        context[self.varname] = Page.objects.get_for_url(url)
        return ''

@register.tag
@easy_tag
def cmspage(_tag, url, _as, varname):
    return CmsPageNode(varname, url)









# generates a nested html list of the site structure (relies on sane url scheme)
class CmsSiteMapNode(template.Node):
    def __init__(self, base_url, include_base, depth, alias):
        self.base_url = base_url
        self.include_base = include_base
        self.depth = depth
        self.alias = alias
        
    def render(self, context):
        if context['request'].user.has_module_perms("cms"):
            page_qs = Page.objects
        else:
            page_qs = Page.live

        try:
            base_url = self.base_url and template.Variable(self.base_url).resolve(context) or '/'
            page = page_qs.get(url=base_url)
        except Page.DoesNotExist:
            return ''

        include_base = self.include_base == True or (self.include_base != 'False' and template.Variable(self.include_base).resolve(context))
        depth = int(self.depth or 0)
        
        
        def _render(page, currentdepth = 1):
            html = []
                
            children = page.get_children(page_qs).order_by('url')
            if len(children):
                html.append('<ul>')
                for childpage in children:
                    html.append('<li>\n<a href="%s">%s</a>' % (childpage.url, childpage.page_title()))
                    if (not depth) or currentdepth < depth:
                        html.append(_render(childpage, currentdepth + 1))
                    html.append('</li>')
                html.append('</ul>')
            
            return "\n".join(html)
        
    
        if include_base:
            html = "\n".join([
                '<ul>',
                '<li>',
                '<a href="%s">%s</a>' % (page.url, page.page_title()),
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
        

@register.tag
@easy_tag
def cmssitemap(_tag, base_url=None, include_base=True, depth=None, _as='', alias=None):
    return CmsSiteMapNode(base_url, include_base, depth, alias)









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
                try:
                    page = Page.objects.get(url=current_url)
                except Page.DoesNotExist:
                    page = None
                crumbtrail.append({
                    'url': current_url,
                    'name': name,
                    'page': page
                })
            
        context[self.varname] = crumbtrail
        return ''

@register.tag
@easy_tag
def cmsgetcrumbtrail(_tag, _as, varname):
    return CMSCrumbtrailNode(varname)






class CMSExtraNode(template.Node):
        
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
            
@easy_tag
def cmsextra(_tag):
    return CMSExtraNode()

register.tag(cmsextra)






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





## Tags for working with Pages

class PageNamedBlockNode(template.Node):
    def __init__(self, page, blockname):
        self.page = template.Variable(page)
        self.blockname = template.Variable(blockname)

    def render(self, context):
        page = self.page.resolve(context)
        blockname = self.blockname.resolve(context)
        return page.blocks.get(label=blockname).compiled_content

@register.tag
@easy_tag
def get_page_block(_tag, page, block):
    return PageNamedBlockNode(page, block)


class PagesForTemplateNode(template.Node):
    def __init__(self, varname, template_name="default.html"):
        self.varname = varname
        self.template_name = template.Variable(template_name)
        super(PagesForTemplateNode, self).__init__()

    def render(self, context):
        context[self.varname] = Page.objects.filter(template__endswith=self.template_name.resolve(context)).order_by('url')
        return ''

@register.tag
@easy_tag
def pages_for_template(_tagname, template, _as, varname):
    return PagesForTemplateNode(varname, template)

