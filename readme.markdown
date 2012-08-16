djangocms2000 is a flexible Django CMS with edit-in-place capability. 


GETTING STARTED:
================

Requirements
------------
1. [Django,](https://www.djangoproject.com) version 1.4 or higher
2. [simplejson](pypi.python.org/pypi/simplejson/)
3. [sorl.thumbnail](https://github.com/sorl/sorl-thumbnail) version 10+ (optional, 
   required for automatically resizing cms images)

Installation
------------
1. Run `./setup.py install` to install the cms. Alternately, you can symlink or move the
   `cms` directory onto your path.
2. Add `'cms'` to `INSTALLED_APPS`
3. Add `'cms.urls'` to your `ROOT_URLCONF` conf, i.e.
    
        (r'^cms/', include('cms.urls')),

4. Ensure `'django.core.context_processors.request'` is present in your 
   `TEMPLATE_CONTEXT_PROCESSORS` setting
5. Ensure `'django.template.loaders.app_directories.load_template_source'` is present in 
   your `TEMPLATE_LOADERS` setting
6. Optional: Add `'sorl.thumbnail'` to your `INSTALLED_APPS` if you want to use resized
   cms images
7. Optional: add `'cms.middleware.CMSFallbackMiddleware'` to your middleware classes if 
   you want to be able to add new pages via Django's admin.
8. Optional: add `{% cmseditor %}` to the bottom of your base template to enable sitewide
   in-place editing (use `{% load cms_editor %}` to load)

Usage
-----
1. Use `{% load cms_tags %}` to enable the cms tags in a template/
2. Use `{% cmsblock LABEL [format=FORMAT] %}` to create an editable text block.
   FORMAT can be 'plain' (default) or 'html'.
3. Use `{% cmsimage LABEL [geometry=GEOMETRY crop=CROP] %}` to create editable images. 
   GEOMETRY and CROP (both optional) correspond to sorl's 
   [geometry](http://thumbnail.sorl.net/template.html#geometry) and
   [crop](http://thumbnail.sorl.net/template.html#crop) options. If not specified, the
   original image will be displayed.

See reference.markdown for more info
