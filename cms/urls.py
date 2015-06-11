import os

from django.conf.urls import url

from . import views


urlpatterns = (
	url(r'^actions/savepage/$', views.savepage, {}, 'cms_savepage'),
	url(r'^actions/savepage/(\d+)/$', views.savepage, {}, 'cms_savepage'),
	url(r'^actions/saveblock/(\d+)$', views.saveblock, {}, 'cms_saveblock'),
	url(r'^actions/saveimage/(\d+)$', views.saveimage, {}, 'cms_saveimage'),
	
	url(r'^login/$', views.login, {}, 'cms_login'),
	url(r'^logout/$', views.logout, {}, 'cms_logout'),
	url(r'^block_admin_init\.js$', views.block_admin_init, {}, 
	    'cms_block_admin_init'),
	url(r'^linklist\.js$', views.linklist, {}, 'cms_linklist'),
	url(r'^editor\.js$', views.editor_js, {}, 'cms_editor_js'),
	url(r'^editor\.html$', views.editor_html, {}, 'cms_editor_html'),
	url(r'^login\.js$', views.login_js, {}, 'cms_login_js'),
)
