from views import render_page
from django.http import Http404, HttpResponseRedirect
from django.conf import settings
import re
from models import Page

class Djangocms2000FallbackMiddleware(object):
    def process_response(self, request, response):
        path = request.path_info
        
        # check uri sanity
        if not re.match('^[\w\-\/]+$', path):
            return response
            
        if response.status_code != 404:
            return response # No need to check for a page for non-404 responses.
        else:
            # append slash if required (only if the slash-appended uri is valid)
            if settings.APPEND_SLASH and not re.match(r'/$', path) and Page.objects.filter(uri="%s/" % path).count():
                return HttpResponseRedirect("%s/" % path)
            else:
                try:
                    return render_page(request, request.path_info)
                # Return the original response if any errors happened. Because this
                # is a middleware, we can't assume the errors will be caught elsewhere.
                except Http404:
                    return response
                except:
                    if settings.DEBUG:
                        raise
                    return response
