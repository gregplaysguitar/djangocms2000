djangocms2000 is a flexible Django CMS with edit-in-place capability.


GETTING STARTED:
================

Requirements
------------
1. [Django,](https://www.djangoproject.com) version 1.4 or higher
2. [sorl.thumbnail](https://github.com/sorl/sorl-thumbnail) version 10+, or
   [easy_thumbnails](https://github.com/SmileyChris/easy-thumbnails) version 2.3+
   (optional, required for automatically resizing cms images)
3. [importlib](https://pypi.python.org/pypi/importlib), for python < 2.7

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
6. Optional: Install [sorl.thumbnail](https://github.com/sorl/sorl-thumbnail) or
   [easy_thumbnails](https://github.com/SmileyChris/easy-thumbnails) as per the
   relevant documentation if you want to use resized cms images
7. Optional: add `'cms.middleware.CMSFallbackMiddleware'` to your middleware classes if
   you want to be able to add new pages via Django's admin.
8. Optional: add `{% cms_editor %}` to the bottom of your base template to enable sitewide
   in-place editing (use `{% load cms_editor %}` to load)

Usage
-----
1. Use `{% load cms_tags %}` to enable the cms tags in a template/
2. Use `{% cmsblock LABEL [format=FORMAT] %}` to create an editable text block.
   FORMAT can be 'plain' (default) or 'html'.
3. Use `{% cmsimage LABEL [geometry=GEOMETRY crop=CROP] %}` to create editable images.
   GEOMETRY and CROP (both optional) correspond to the sorl.thumbnail's
   [geometry](http://thumbnail.sorl.net/template.html#geometry) and
   [crop](http://thumbnail.sorl.net/template.html#crop) options, or
   easy_thumbnails
   [size and crop](http://easy-thumbnails.readthedocs.io/en/2.1/usage/#thumbnail-options)
   options. If not specified, the original image will be displayed.

Jinja2 compatibility
---------------------------

Add the functions in `cms.jinja2_env` to your jinja2 environment. For example:


    from jinja2 import Environment
    import cms.jinja2_env

    env = Environment()
    env.globals.update(cms.jinja2_env.template_globals)

Basic usage examples:

    {{ cms_block('intro', filters='linebreaks') }}
    {{ cms_block('content', format='html') }}
    {{ cms_block('site-intro', site=True) }}
    {{ cms_image('resized-image', '200x200') }}
    {{ cms_image('cropped-image', '200x200', crop=True) }}
    {{ cms_image('raw-image') }}

Custom image rendering can be achieved via the renderer argument, which can be
defined as a jinja2 macro - i.e.

    {% macro image_as_bg(img) %}
      <div class="image" style="background-image: url({{ img.url }})"></div>
    {% endmacro %}
    {{ cms_image('bg-image', '200x200', renderer=image_as_bg) }}


Upgrading from 1.x to 2.x
-------------------------
1. First make sure you are running the latest 1.x series tag (see [here](https://github.com/gregplaysguitar/djangocms2000/tags)).
   Refer to notes.markdown for pre-1.0 migration instructions.
2. If you're using [South](http://south.aeracode.org/), you may need to fake the first
   migration, ie.

       ./manage.py migrate cms 0001_initial --fake

   (If not using South, you'll need to modify your db to match the new schema by hand.)
3. The `{% cmsextra %}` tag becomes `{% cms_editor %}`, and now requires a separate import,
   `{% load cms_editor %}`.
4. The `'markdown'` block format has been removed, and the default is now `'plain'`.
   `format` is also now a keyword argument, e.g. `{% cmsblock 'text' format='html' %}`.
5. The `format` argument has been removed from `{% cmsimage ... %}` and its variants,
   since the new extended syntax renders it obsolete.

Keeping cms content in a separate database
-----------------------------------------
CMS database content can be kept separate from the rest of the database. To
enable, set `CMS_DB_ALIAS` to point to a secondary database and add
`'cms.db_router.CMSRouter'` to your `DATABASE_ROUTERS` setting. For example,
you may want to store CMS content in an sqlite database which can be easily
committed to version control. CMS media, by default, is stored in the `cms`
subfolder of `MEDIA_ROOT`.


See reference.markdown for more info
