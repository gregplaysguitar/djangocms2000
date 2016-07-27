import hashlib

from django.conf import settings

# Customisable settings - see reference.markdown

USE_SITES_FRAMEWORK = getattr(settings, 'CMS_USE_SITES_FRAMEWORK', False)
TINYMCE_CONFIG = getattr(settings, 'CMS_TINYMCE_CONFIG', {})
POST_EDIT_CALLBACK = getattr(settings, 'CMS_POST_EDIT_CALLBACK', '""')
MAX_IMAGE_DIMENSIONS = getattr(settings, 'CMS_MAX_IMAGE_DIMENSIONS',
                               (1920, 1200))
BLOCK_REQUIRED_CALLBACK = getattr(settings, 'CMS_BLOCK_REQUIRED_CALLBACK',
                                  None)
IMAGE_REQUIRED_CALLBACK = getattr(settings, 'CMS_IMAGE_REQUIRED_CALLBACK',
                                  None)
DUMMY_IMAGE_SOURCE = getattr(settings, 'CMS_DUMMY_IMAGE_SOURCE', None)
DB_ALIAS = getattr(settings, 'CMS_DB_ALIAS', 'default')
UPLOAD_PATH = getattr(settings, 'CMS_UPLOAD_PATH', 'cms/%Y_%m')

LANGUAGES = getattr(settings, 'CMS_LANGUAGES', getattr(settings, 'LANGUAGES'))

# The following are for internal use and can't be customised

STATIC_URL = settings.STATIC_URL + 'cms/'

# Assume there's a template engine, and that the first one is the one we want
try:
    TEMPLATE_DIRS = settings.TEMPLATES[0].get('DIRS', [])
except AttributeError:
    # pre-1.8 fallback
    TEMPLATE_DIRS = settings.TEMPLATE_DIRS

# let's be *really* careful not to display content from another site using
# the same cache
CACHE_PREFIX = 'cms-%s' % hashlib.sha1(
    settings.SECRET_KEY.encode('utf-8')).hexdigest()[:5]
