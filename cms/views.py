import re
import copy
try:
    import json
except ImportError:
    # python 2.5 fallback
    from django.utils import simplejson as json

from django.http import HttpResponse, HttpResponseNotAllowed, Http404
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout as logout_request
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.conf import settings
from django.contrib.auth.views import login as auth_login
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import resolve, Resolver404
from django.core.exceptions import PermissionDenied
from django.utils import translation

from .forms import PageForm, BlockForm, ImageForm
from . import settings as cms_settings
from .models import Block, Page, Image
from .utils import is_editing, public_key, strip_i18n_prefix


def logout(request):
    '''Basic logout & redirect view.'''

    logout_request(request)
    if 'from' in request.GET:
        return redirect(request.GET['from'] or '/')
    else:
        return redirect('/')


def login(request, *args, **kwargs):
    '''Basic login view used by cms login forms.'''

    kwargs['template_name'] = 'cms/cms/login.html'
    return auth_login(request, *args, **kwargs)


def savepage(request, page_pk=None):
    '''Ajax-only view to save cms.page objects from the frontend editor. Used to
       change or add pages - requires change_page or add_page permission.'''

    if not request.POST:
        return HttpResponseNotAllowed(['POST'])
    else:
        if page_pk:
            if not request.user.has_perm('cms.change_page'):
                raise PermissionDenied
            page = get_object_or_404(Page, pk=page_pk)
        else:
            if not request.user.has_perm('cms.add_page'):
                raise PermissionDenied
            page = None

        form = PageForm(request.POST, instance=page,
                        prefix=request.POST.get('prefix', None))

        if form.is_valid():
            saved_page = form.save()
            form.save_sites()
            return HttpResponse(json.dumps({
                'success': True,
                'url': saved_page.get_absolute_url(),
                'message': page and 'Page saved' or
                                    'Page created... redirecting'
            }), content_type='application/json')
        else:
            return HttpResponse(json.dumps({
                'success': False,
                'errors': form.errors,
            }), content_type='application/json')


def get_page_content(base_request, page_url):
    '''Fakes a request to retrieve page content, used for updating content
       by the frontend editor save views. Hacks and reuses the request
       to ensure page access is not denied.'''

    try:
        urlmatch = resolve(page_url)
    except Resolver404:
        # must be an admin-created page, rendered by the middleware
        page_func = lambda r: render_page(r, page_url)
    else:
        # must be a django-created page, rendered by a urlconf
        page_func = lambda r: urlmatch.func(r, *urlmatch.args,
                                            **urlmatch.kwargs)

    # reuse the request to avoid having to fake sessions etc, but it'll have to
    # be hacked a little so it has the right url and doesn't trigger a POST
    request = copy.copy(base_request)
    request.path = request.path_info = page_url
    request.META['REQUEST_METHOD'] = request.method = 'GET'
    request.POST = None

    try:
        response = page_func(request)
    except Http404:
        # this shouldn't ever happen, but just in case
        return ''
    else:
        # handle deferred rendering - see BaseHandler.get_response in
        # django.core.handlers.base
        # Note that we're ignoring any template response middleware modifiers
        if hasattr(response, 'render') and callable(response.render):
            return response.render()
        else:
            return response


BODY_RE = re.compile('<body[^>]*>([\S\s]*)<\/body>')


@permission_required("cms.change_block")
def saveblock(request, block_id):
    '''Ajax-only view to save cms.block objects from the frontend editor'''

    block = get_object_or_404(Block, id=block_id)

    # html has its own form, so it uses a prefix
    if block.format == Block.FORMAT_HTML:
        prefix = 'html'
    else:
        prefix = None

    form = BlockForm(request.POST, instance=block, prefix=prefix)
    block = form.save()

    # render the page to get the updated content
    domain_regex = re.compile('https?://%s' % request.META['HTTP_HOST'])
    page_url = domain_regex.sub('', request.META['HTTP_REFERER']).split('?')[0]
    page_response = get_page_content(request, page_url)

    # extract body content from HttpResponse. The response content is assumed
    # to be sane
    match = BODY_RE.search(page_response.content.decode("utf-8"))
    if match:
        page_content = match.groups()[0]
    else:
        # no <body> tag, so assume an ajax response containing only a page
        # fragment
        page_content = page_response.content

    return HttpResponse(json.dumps({
        'page_content': page_content,
        'content': block.content,
    }), content_type='application/json')


@permission_required("cms.change_image")
def saveimage(request, image_id):
    '''Ajax-only view to save cms.image objects from the frontend editor'''

    image = get_object_or_404(Image, id=image_id)

    if 'delete' in request.POST:
        if image.file:
            image.file.delete()
        image.description = ""
        image.save()
    else:
        form = ImageForm(request.POST, request.FILES, instance=image)
        image = form.save()

    return redirect(request.POST.get('redirect_to') or '/')


@csrf_protect
def render_page(request, url):
    '''Renders a cms.page object.'''

    if settings.USE_I18N and not translation.get_language_from_path(url):
        return redirect('/' + translation.get_language() + url)

    if hasattr(request, 'user') and request.user.has_module_perms("cms") or \
       request.GET.get('cms_dummy_render', None) == public_key():
        qs = Page.objects.all()
    else:
        qs = Page.objects.live()

    # don't try to render pages with no template (e.g. those who hold content
    # for a url resolved elsewhere in the project)
    qs = qs.exclude(template='')

    page = get_object_or_404(qs, url=strip_i18n_prefix(url),
                             sites__site_id=settings.SITE_ID)

    tpl = get_template(page.template)
    content = tpl.render({
        'page': page,
    }, request=request)
    return HttpResponse(content)


def tinymce_config_json():
    '''Return tinymce overrides from settings, as a json string for js.'''
    tinymce_config = cms_settings.TINYMCE_CONFIG
    if callable(tinymce_config):
        tinymce_config = tinymce_config()
    return json.dumps(tinymce_config)


@permission_required("cms.change_block")
def block_admin_init(request):
    '''Dynamic javascript file; used to initialise tinymce controls etc
       in the django admin.'''

    response = render(request, 'cms/cms/block_admin_init.js', {
        'tinymce_config_json': tinymce_config_json(),
        'cms_settings': cms_settings,
    })

    response['Content-Type'] = 'application/javascript'
    return response


@permission_required("cms.change_block")
def linklist(request):
    '''Used to populate the tinymce link list popup.'''

    response = render(request, 'cms/cms/linklist.js', {
        'page_list': Page.objects.all(),
    })
    response['Content-Type'] = 'application/javascript'
    return response


@never_cache
def editor_js(request):
    '''Dynamic js file for frontend editing. Serves up a blank file, the full
       editor js, or the edit-mode switcher button depending on the user's
       cookies and permissions.'''

    if not request.user.has_module_perms('cms'):
        response = HttpResponse('')
    else:
        if is_editing(request):
            response = render(request, 'cms/cms/editor.js', {
                'cms_settings': cms_settings,
                'tinymce_config_json': tinymce_config_json(),
            })
        else:
            response = render(request, 'cms/cms/edit-mode-switcher.js', {
                'cms_settings': cms_settings,
            })

    response['Content-Type'] = 'application/javascript'
    return response


@never_cache
def editor_html(request):
    """Provides html bits for the editor js - downloaded and injected via
       ajax. """

    if not request.user.has_module_perms('cms'):
        response = HttpResponse('')
    else:
        path = request.GET.get('page')
        page = None
        if path:
            try:
                page = Page.objects.get(url=strip_i18n_prefix(path),
                                        sites__site_id=settings.SITE_ID)
            except Page.DoesNotExist:
                pass

        response = render(request, 'cms/cms/editor.html', {
            'page': page,
            'path': path,
            'user': request.user,
            'cms_settings': cms_settings,
            'editor_form': BlockForm(),
            'html_editor_form': BlockForm(prefix='html'),
            'image_form': ImageForm(),
            'page_form': page and PageForm(instance=page) or None,
            'new_page_form': PageForm(prefix='new'),
        })
    return response


@never_cache
def login_js(request):
    '''Dynamic js file to show the login form.'''

    response = render(request, 'cms/cms/login.js', {
        'cms_settings': cms_settings,
    })

    response['Content-Type'] = 'application/javascript'
    return response
