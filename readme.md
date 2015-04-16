django-adhoc is a flexible Django CMS with edit-in-place capability. 


GETTING STARTED:
================

Requirements
------------
1. [Django,](https://www.djangoproject.com) version 1.4 or higher
2. [sorl.thumbnail](https://github.com/sorl/sorl-thumbnail) version 10+ (optional, 
   required for automatically resizing cms images)
3. [importlib](https://pypi.python.org/pypi/importlib), for python < 2.7

Installation
------------
1. Run `./setup.py install` to install django-adhoc.
2. Add `'adhoc'` to `INSTALLED_APPS`
3. Add `'adhoc.urls'` to your `ROOT_URLCONF` conf, i.e.
    
        (r'^adhoc/', include('adhoc.urls')),

4. Ensure `'django.core.context_processors.request'` is present in your 
   `TEMPLATE_CONTEXT_PROCESSORS` setting
5. Ensure `'django.template.loaders.app_directories.load_template_source'` is present in 
   your `TEMPLATE_LOADERS` setting
6. Optional: Add `'sorl.thumbnail'` to your `INSTALLED_APPS` if you want to use
   resized images
7. Optional: add `'adhoc.middleware.FallbackMiddleware'` to your middleware
   classes if you want to be able to add new pages via Django's admin.
8. Optional: add `{% adhoc_editor %}` to the bottom of your base template to
   enable sitewide in-place editing (use `{% load adhoc_editor %}` to load)

Usage
-----
1. Use `{% load adhoc_tags %}` to enable the adhoc tags in a template/
2. Use `{% cmsblock LABEL [format=FORMAT] %}` to create an editable text block.
   FORMAT can be 'plain' (default) or 'html'.
3. Use `{% cmsimage LABEL [geometry=GEOMETRY crop=CROP] %}` to create editable images. 
   GEOMETRY and CROP (both optional) correspond to sorl's 
   [geometry](http://thumbnail.sorl.net/template.html#geometry) and
   [crop](http://thumbnail.sorl.net/template.html#crop) options. If not specified, the
   original image will be displayed.

Jinja2/Coffin compatibility
---------------------------
Grab jinja_cms.py from https://gist.github.com/gregplaysguitar/aeac2702562c5b0771a1, and 
place it in a templatetags directory for coffin to find. Basic usage examples:

    {{ cms_block('intro', filters='linebreaks') }}
    {{ cms_block('content', format='html') }}
    {{ cms_image('main-image', '200x200') }}

Committing cms content and media to version control
-----------------------------------------
django-adhoc database content can be kept separate from the rest of the 
database. To enable, set `ADHOC_DB_ALIAS` to point to a secondary database and 
add `'adhoc.db_router.AdhocRouter'` to your `DATABASE_ROUTERS` setting. For 
example, you may want to store CMS content in an sqlite database which can be
easily committed to version control. CMS media, by default, is stored in the 
`adhoc` subfolder of `MEDIA_ROOT`.


See reference.md for more info
