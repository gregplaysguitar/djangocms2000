from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.utils import simplejson
from models import Block, Page, Image
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout as logout_request
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
import re, os
from django.contrib.contenttypes.models import ContentType
from djangocms2000 import settings as djangocms2000_settings
from djangocms2000.utils import is_editing, page_is_authorised
from forms import PublicPageForm


try:
    from django.views.decorators.csrf import csrf_protect
except ImportError:
    def csrf_protect(func):
        return func
from django.contrib.auth.views import login as auth_login


def logout(request):
    logout_request(request)
    if 'from' in request.GET:
        return HttpResponseRedirect(request.GET['from'] or '/')
    else:
        return HttpResponseRedirect('/')
        

def login(request, *args, **kwargs):
    kwargs['template_name'] = 'djangocms2000/cms/login.html'
    return auth_login(request, *args, **kwargs)
        

    #(r'^login/$', '', {'template_name': 'djangocms2000/cms/login.html',}),




@permission_required("djangocms2000.change_page")
def savepage(request, page_pk=None):
    if not request.POST:
        return HttpResponseNotAllowed('POST required')
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
                'uri': saved_page.get_absolute_url(),
                'message': page and 'Page saved' or 'Page created... redirecting'
            }), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({
                'success': False,
                'errors': form.errors,
            }), mimetype='application/json')

    



@permission_required("djangocms2000.change_page")
def saveblock(request):
    if 'prefix' in request.POST:
        prefix = '%s-' % request.POST['prefix']
    else:
        prefix = ''
        
    block = Block.objects.get(
        pk=request.POST['%sblock_id' % (prefix)]
    )
    #print block.save()
    
    block.raw_content = request.POST['%sraw_content' % (prefix)]
    block.format = request.POST['%sformat' % (prefix)]
    block.save()
    #print block
    return HttpResponse(simplejson.dumps({'compiled_content': block.compiled_content, 'raw_content': block.raw_content,}), mimetype='application/json')

    

    
@permission_required("djangocms2000.change_page")
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
def render_page(request, uri=None):
    if request.user.has_module_perms("djangocms2000") or \
       request.GET.get('djangocms2000_dummy_render', None) == djangocms2000_settings.SECRET_KEY:
        qs = Page.objects
    else:
        qs = Page.live
    
    if not uri:
        uri = request.path_info
    
    page = get_object_or_404(qs, uri=uri)
    
    if not page_is_authorised(request, page):
        return HttpResponseForbidden('Permission denied')
    else:
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
        'djangocms2000/cms/page_admin_init.js',
        {
            'djangocms2000_settings': djangocms2000_settings,
        },
        context_instance=RequestContext(request)
    )
    response['Content-Type'] = 'application/javascript'
    return response

# populate the tinymce link list popup
def linklist(request):
    response = render_to_response(
        'djangocms2000/cms/linklist.js',
        {
            'page_list': Page.objects.all(),
        },
        context_instance=RequestContext(request)
    )
    response['Content-Type'] = 'application/javascript'
    return response





