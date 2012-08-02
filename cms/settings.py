from django.conf import settings

STATICFILES = 'django.contrib.staticfiles' in settings.INSTALLED_APPS

ROOT_URL = getattr(settings, 'CMS_ROOT_URL', '/cms/')

if STATICFILES:
    default_static_url = '%scms/' % settings.STATIC_URL
else:
    default_static_url = '%smedia/' % ROOT_URL
	
# This setting should be CMS_STATIC_URL, but check CMS_MEDIA_URL for backwards-compatibility
STATIC_URL = getattr(settings, 'CMS_STATIC_URL', getattr(settings, 'CMS_MEDIA_URL', default_static_url))

EDIT_IN_PLACE = getattr(settings, 'CMS_EDIT_IN_PLACE', True)

CUSTOM_STYLESHEET = getattr(settings, 'CMS_CUSTOM_STYLESHEET', None)

HIGHLIGHT_START_COLOR = getattr(settings, 'CMS_HIGHLIGHT_START_COLOR', "#ff0")
HIGHLIGHT_END_COLOR = getattr(settings, 'CMS_HIGHLIGHT_END_COLOR', "#fff")



ADMIN_JS = getattr(settings, 'CMS_ADMIN_JS', (
    STATIC_URL + 'lib/jquery-1.4.2.min.js',
    STATIC_URL + 'tiny_mce/tiny_mce.js',
    STATIC_URL + 'tiny_mce/jquery.tinymce.js',
    STATIC_URL + 'js/page_admin.js',
    ROOT_URL + 'page_admin_init.js',
))


ADMIN_CSS = getattr(settings, 'CMS_ADMIN_CSS', {
    'all': (STATIC_URL + 'css/page_admin.css',),
})

ADMIN_CAN_DELETE_BLOCKS = getattr(settings, 'CMS_ADMIN_CAN_DELETE_BLOCKS', settings.DEBUG)


FILEBROWSER_URL_ADMIN = getattr(
    settings,
    'CMS_FILEBROWSER_URL_ADMIN',
    getattr(settings, 'FILEBROWSER_URL_ADMIN', '')
)

USE_SITES_FRAMEWORK = getattr(settings, 'CMS_USE_SITES_FRAMEWORK', False)


TINYMCE_BUTTONS = getattr(settings, 'CMS_TINYMCE_BUTTONS', "formatselect,bold,italic,|,undo,redo,|,link,|,blockquote,bullist,numlist,|,pastetext,code")
TINYMCE_CONTENT_CSS = getattr(settings, 'CMS_TINYMCE_CONTENT_CSS', "")

#HIDE_PAGE_URL = getattr(settings, 'CMS_HIDE_PAGE_URL', False)

POST_EDIT_CALLBACK = getattr(settings, 'CMS_POST_EDIT_CALLBACK', '""')

MAX_IMAGE_DIMENSIONS = getattr(settings, 'CMS_MAX_IMAGE_DIMENSIONS', (1920, 1200))

FILTERS = getattr(settings, 'CMS_FILTERS', (
    # tuples of the form (module, shortname, default)
    ('cms.filters.typogrify_filter', 'typogrify', False),
))

BLOCK_REQUIRED_CALLBACK = getattr(settings, 'CMS_BLOCK_REQUIRED_CALLBACK', None)
IMAGE_REQUIRED_CALLBACK = getattr(settings, 'CMS_IMAGE_REQUIRED_CALLBACK', None)

SECRET_KEY = getattr(settings, 'SECRET_KEY', 'just in case?')

CACHE_PREFIX = getattr(settings, 'CMS_CACHE_PREFIX', 'cms')

LOGIN_URL = getattr(settings, 'CMS_LOGIN_URL', getattr(settings, 'LOGIN_URL', '/accounts/login/'))
UPLOAD_PATH = getattr(settings, 'CMS_UPLOAD_PATH', 'uploads/%Y_%m')


