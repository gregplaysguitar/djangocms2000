from django.conf.urls.defaults import *
import os


urlpatterns = patterns('djangocms2000.views',
	(r'^actions/saveblock/$', 'saveblock'),
	(r'^actions/saveimage/$', 'saveimage'),
	(r'^login/$', 'login'),
	(r'^logout/$', 'logout'),
	(r'^page_admin_init.js$', 'page_admin_init'),
    (r'^linklist.js$', 'linklist'),
)


urlpatterns += patterns('',
	#(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'djangocms2000/cms/login.html',}),
)


urlpatterns += patterns('',
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
		{'document_root': os.path.join(os.path.dirname(globals()["__file__"]), 'media')}),
)