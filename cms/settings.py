import hashlib

from django.conf import settings

# Customisable settings - see reference.markdown

USE_SITES_FRAMEWORK = getattr(settings, 'CMS_USE_SITES_FRAMEWORK', False)
TINYMCE_CONFIG = getattr(settings, 'CMS_TINYMCE_CONFIG', {})
POST_EDIT_CALLBACK = getattr(settings, 'CMS_POST_EDIT_CALLBACK', '""')
MAX_IMAGE_DIMENSIONS = getattr(settings, 'CMS_MAX_IMAGE_DIMENSIONS', 
                               (1920, 1200))
BLOCK_REQUIRED_CALLBACK = getattr(settings, 'CMS_BLOCK_REQUIRED_CALLBACK', None)
IMAGE_REQUIRED_CALLBACK = getattr(settings, 'CMS_IMAGE_REQUIRED_CALLBACK', None)
DUMMY_IMAGE_SOURCE = getattr(settings, 'CMS_DUMMY_IMAGE_SOURCE', None)


# The following are for internal use and shouldn't need to be customised

STATIC_URL = getattr(settings, 'CMS_STATIC_URL', settings.STATIC_URL + 'cms/')
SECRET_KEY = getattr(settings, 'SECRET_KEY', 'just in case?')
UPLOAD_PATH = getattr(settings, 'CMS_UPLOAD_PATH', 'uploads/%Y_%m')
SITE_ID = getattr(settings, 'SITE_ID', 1)

# let's be *really* careful not to display content from another site using
# the same cache
CACHE_PREFIX = 'cms-%s' % hashlib.sha1(settings.SECRET_KEY).hexdigest()[:5]

