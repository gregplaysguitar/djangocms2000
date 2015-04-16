import hashlib

from django.conf import settings

# Customisable settings - see reference.md

USE_SITES_FRAMEWORK = getattr(settings, 'ADHOC_USE_SITES_FRAMEWORK', False)
TINYMCE_CONFIG = getattr(settings, 'ADHOC_TINYMCE_CONFIG', {})
POST_EDIT_CALLBACK = getattr(settings, 'ADHOC_POST_EDIT_CALLBACK', '""')
MAX_IMAGE_DIMENSIONS = getattr(settings, 'ADHOC_MAX_IMAGE_DIMENSIONS', 
                               (1920, 1200))
BLOCK_REQUIRED_CALLBACK = getattr(settings, 'ADHOC_BLOCK_REQUIRED_CALLBACK', None)
IMAGE_REQUIRED_CALLBACK = getattr(settings, 'ADHOC_IMAGE_REQUIRED_CALLBACK', None)
DUMMY_IMAGE_SOURCE = getattr(settings, 'ADHOC_DUMMY_IMAGE_SOURCE', None)
TEMPLATE_RENDERER = getattr(settings, 'ADHOC_TEMPLATE_RENDERER', 
                            'django.shortcuts.render_to_response')
DB_ALIAS = getattr(settings, 'ADHOC_DB_ALIAS', 'default')
UPLOAD_PATH = getattr(settings, 'ADHOC_UPLOAD_PATH', 'adhoc/%Y_%m')


# The following are for internal use and can't be customised

STATIC_URL = settings.STATIC_URL + 'adhoc/'
SECRET_KEY = settings.SECRET_KEY
SITE_ID = settings.SITE_ID
EDIT_MODE_COOKIE = 'adhoc-edit_mode'

# Assume there's a template engine, and that the first one is the one we want
TEMPLATE_DIRS = settings.TEMPLATES[0].get('DIRS', [])

# let's be *really* careful not to display content from another site using
# the same cache
CACHE_PREFIX = 'adhoc-%s' % hashlib.sha1(SECRET_KEY).hexdigest()[:5]
