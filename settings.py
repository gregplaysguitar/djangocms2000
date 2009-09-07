from django.conf import settings


EDIT_IN_PLACE = getattr(settings, 'DJANGOCMS2000_EDIT_IN_PLACE', True)

CUSTOM_STYLESHEET = getattr(settings, 'DJANGOCMS2000_CUSTOM_STYLESHEET', None)

HIGHLIGHT_START_COLOR = getattr(settings, 'DJANGOCMS2000_HIGHLIGHT_START_COLOR', "#ff0")
HIGHLIGHT_END_COLOR = getattr(settings, 'DJANGOCMS2000_HIGHLIGHT_END_COLOR', "#fff")


ADMIN_JS = getattr(settings, 'DJANGOCMS2000_ADMIN_JS', (
    '/djangocms2000/media/tiny_mce/tiny_mce.js',
    '/djangocms2000/media/lib/jquery-1.3.2.min.js',
    '/djangocms2000/media/js/page_admin.js',
    '/djangocms2000/page_admin_init.js',
))


ADMIN_CSS = getattr(settings, 'DJANGOCMS2000_ADMIN_CSS', {
    'all': ('/djangocms2000/media/css/page_admin.css',),
})

ADMIN_CAN_DELETE_BLOCKS = getattr(settings, 'DJANGOCMS2000_ADMIN_CAN_DELETE_BLOCKS', settings.DEBUG)


FILEBROWSER_URL_ADMIN = getattr(
    settings,
    'DJANGOCMS2000_FILEBROWSER_URL_ADMIN',
    getattr(settings, 'FILEBROWSER_URL_ADMIN', '')
)