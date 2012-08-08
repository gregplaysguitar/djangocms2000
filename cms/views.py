import re, os

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseForbidden
from django.utils import simplejson
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout as logout_request
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.views import login as auth_login

try:
    from django.views.decorators.csrf import csrf_protect
except ImportError:
    def csrf_protect(func):
        return func

from forms import PublicPageForm
import settings as cms_settings
from utils import is_editing
from models import Block, Page, Image



def logout(request):
    logout_request(request)
    if 'from' in request.GET:
        return HttpResponseRedirect(request.GET['from'] or '/')
    else:
        return HttpResponseRedirect('/')
        

def login(request, *args, **kwargs):
    kwargs['template_name'] = 'cms/cms/login.html'
    return auth_login(request, *args, **kwargs)
        

    #(r'^login/$', '', {'template_name': 'cms/cms/login.html',}),




@permission_required("cms.change_page")
def savepage(request, page_pk=None):
    if not request.POST:
        return HttpResponseNotAllowed(['POST'])
    else:
        if page_pk:
            page = get_object_or_404(Page, pk=page_pk)
        else:
            page = None
        
        form = PublicPageForm(request.POST, instance=page, prefix=request.POST.get('prefix', None))
            
        if form.is_valid():
            saved_page = form.save()
            return HttpResponse(simplejson.dumps({
                'success': True,
                'url': saved_page.get_absolute_url(),
                'message': page and 'Page saved' or 'Page created... redirecting'
            }), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({
                'success': False,
                'errors': form.errors,
            }), mimetype='application/json')

    



@permission_required("cms.change_page")
def saveblock(request):
    if 'prefix' in request.POST:
        prefix = '%s-' % request.POST['prefix']
    else:
        prefix = ''
        
    block = Block.objects.get(
        pk=request.POST['%sblock_id' % (prefix)]
    )
    
    block.content = request.POST['%scontent' % (prefix)]
    block.format = request.POST['%sformat' % (prefix)]
    block.save()

    return HttpResponse(simplejson.dumps({
        'compiled_content': block.get_filtered_content(request.POST.get('filters', None).split(',')),
        'content': block.content,
    }), mimetype='application/json')

    

    
@permission_required("cms.change_page")
def saveimage(request):
    #print request.POST
    image = Image.objects.get(
        pk=request.POST['image_id']
    )
    
    if 'delete' in request.POST:
        if image.file:
            image.file.delete()
        image.description = ""
    else:
        if 'file' in request.FILES:
            if image.file:
                image.file.delete()
            image.file.save(request.FILES['file'].name, request.FILES['file'])
        image.description = request.POST['description']
    
    image.save()

    return HttpResponseRedirect(request.POST['redirect_to'])
    
    

@csrf_protect
def render_page(request, url):
    if request.user.has_module_perms("cms") or \
       request.GET.get('cms_dummy_render', None) == cms_settings.SECRET_KEY:
        qs = Page.objects
    else:
        qs = Page.live
    
    # don't try to render pages with no template (e.g. those who hold content for a
    # url resolved elsewhere in the project)
    qs = qs.exclude(template='')
    
    page = get_object_or_404(qs, url=url)
    return render_to_response(
        page.template.replace("/%s/" % settings.TEMPLATE_DIRS[0], "", 1),
        {
            'page': page,
        },
        context_instance=RequestContext(request)
    )
    
    
    
# used to initialise django admin tinymce
def page_admin_init(request):
    response = render_to_response(
        'cms/cms/page_admin_init.js',
        {
            'cms_settings': cms_settings,
        },
        context_instance=RequestContext(request)
    )
    response['Content-Type'] = 'application/javascript'
    return response

# populate the tinymce link list popup
def linklist(request):
    response = render_to_response(
        'cms/cms/linklist.js',
        {
            'page_list': Page.objects.all(),
        },
        context_instance=RequestContext(request)
    )
    response['Content-Type'] = 'application/javascript'
    return response





