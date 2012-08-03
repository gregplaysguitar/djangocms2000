import os

from django.conf.urls import *

import settings


urlpatterns = patterns('cms.views',
	(r'^actions/savepage/$', 'savepage'),
	(r'^actions/savepage/(\d+)/$', 'savepage'),
	(r'^actions/saveblock/$', 'saveblock'),
	(r'^actions/saveimage/$', 'saveimage'),
	
	(r'^login/$', 'login'),
	(r'^logout/$', 'logout'),
	(r'^page_admin_init.js$', 'page_admin_init'),
    (r'^linklist.js$', 'linklist'),
)

if not settings.STATICFILES:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
			{'document_root': os.path.join(os.path.dirname(globals()["__file__"]), 'media')}),
	)
