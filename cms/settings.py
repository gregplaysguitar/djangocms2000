from django.conf import settings

ROOT_URL = getattr(settings, 'CMS_ROOT_URL', '/cms/')

MEDIA_URL = getattr(settings, 'CMS_MEDIA_URL', ROOT_URL + 'media/')

EDIT_IN_PLACE = getattr(settings, 'CMS_EDIT_IN_PLACE', True)

CUSTOM_STYLESHEET = getattr(settings, 'CMS_CUSTOM_STYLESHEET', None)

HIGHLIGHT_START_COLOR = getattr(settings, 'CMS_HIGHLIGHT_START_COLOR', "#ff0")
HIGHLIGHT_END_COLOR = getattr(settings, 'CMS_HIGHLIGHT_END_COLOR', "#fff")



ADMIN_JS = getattr(settings, 'CMS_ADMIN_JS', (
    MEDIA_URL + 'lib/jquery-1.4.2.min.js',
    MEDIA_URL + 'tiny_mce/tiny_mce.js',
    MEDIA_URL + 'tiny_mce/jquery.tinymce.js',
    MEDIA_URL + 'js/page_admin.js',
    ROOT_URL + 'page_admin_init.js',
))


ADMIN_CSS = getattr(settings, 'CMS_ADMIN_CSS', {
    'all': (MEDIA_URL + 'css/page_admin.css',),
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




