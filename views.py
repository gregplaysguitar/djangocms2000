from django.http import HttpResponse, HttpResponseRedirect
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




def logout(request):
	logout_request(request)
	if 'from' in request.GET:
		return HttpResponseRedirect(request.GET['from'] or '/')
	else:
		return HttpResponseRedirect('/')
		




@permission_required("djangocms2000.change_page")
def saveblock(request):
	block = Block.objects.get(
		pk=request.POST['block_id']
	)
	#print block.save()
	
	block.raw_content = request.POST['raw_content']
	block.format = request.POST['format']
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
	
	


def render_page(request, uri):
    page = get_object_or_404(Page, uri=uri)
    return render_to_response(
        page.template.replace("/%s/" % settings.TEMPLATE_DIRS[0], "", 1),
        {
            'page': page,
        },
        context_instance=RequestContext(request)
    )
	
	
	
# used to initialise django admin tinymce
def page_admin_init(request):
    return render_to_response(
        'djangocms2000/cms/page_admin_init.js',
        {
            'djangocms2000_settings': djangocms2000_settings,
        },
        context_instance=RequestContext(request)
    )

# populate the tinymce link list popup
def linklist(request):
    return render_to_response(
        'djangocms2000/cms/linklist.js',
        {
            'page_list': Page.objects.all(),
        },
        context_instance=RequestContext(request)
    )





