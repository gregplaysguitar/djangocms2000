# Djangocms2000 Reference

... currently a work in progress.

## Template Tags

Use `{% load djangocms2000_tags %}` to enable.

### Text tags

#### `{% cmsblock label format='html' editable=1 alias=None filters='' %}`

Basic cms content block. Place as many of these as you need in your template, 
with unique labels (labels can be repeated if you want the same content in 
more than one place, ie the window title and page title). Example template code:
    
    {# standard plain-text block #}
    <h1>{% cmsblock "title" "plain" %}</h1>
    
    {# non-editable #}
    <title>{% cmsblock "title" "plain" editable=0 %} | Example.com</title>
    
    {# markdown-formatted #}
    {% cmsblock "content" "markdown" %}
    
    {# format defaults to "html" #}
    {% cmsblock "content" %}
    
    {# only show the block and surrounds if it has content or we're in edit mode #}
    {% cmsblock "tagline" "markdown" alias=tagline %}
    {% if tagline %}
    <blockquote class="grid_10">
        {{ tagline }}
    </blockquote>
    {% endif %}
    
    {# apply the built in "typogrify" filter (requires django-typogrify) #}
    {% cmsblock "content" filters='typogrify' %}


#### `{% cmsgenericblock label content_object_variable format='html' editable=1 alias=None filters='' %}`

Like `cmssiteblock`, but attached to a generic object (`Article`, `Post` etc) instead
of a cms page. `content_object_variable` should be the relevant instance. Example usage:

    {% for article in article_list %}
        <article>
            <h1>{% cmsgenericblock 'title' article 'plain' %}</h1>
            {% cmsgenericblock 'text' article %}
        </article>
    {% endfor %}


#### `{% cmssiteblock label format='html' editable=1 alias=None filters='' %}`

Like a `cmsgenericblock` that is attached to the current site instance, so effectively
a site-wide block. Example

    <head>
        <title>{% block title %}{% endblock %} | {% cmssiteblock "base-title" "plain" editable=0 %}</title>
    </head>
 
### Image tags

#### `{% cmsimage label constraint='' crop='' defaultimage='' editable=1 format='' alias=None %}`

Basic image block - use as with `cmsblock`. By default, will fit an image within
the constraint, but won't crop. Format can be "html" (generates an <img> tag)
or "url" (outputs the url to the resized image). Examples:

    {# standard usage #}
    {% cmsimage "portrait" "300x400" %}

    {# Don't resize the uploaded image at all #}
    {% cmsimage "portrait" %}

    {# crop to an exact size #}
    {% cmsimage "banner" "960x120" crop=1 %}
    
    {# show i/default.png if no image added, and don't crop #}
    {% cmsimage "portrait" "300x400" defaultimage='i/default.png' %}
    
    {# only show the image if one has been uploaded #}
    {% cmsimage "portrait" "300x400" defaultimage='i/default.png' format='url' alias=image_url %}
    {% if image_url %}
    <img src="{{ image_url }}" alt="portrait">
    {% endif %}


#### `{% cmsgenericimage label content_object_variable constraint='' crop='' defaultimage='' editable=1 format='' alias=None %}`

See `cmsgenericblock`, above.


#### `{% cmssiteimage label constraint='' crop='' defaultimage='' editable=1 format='' alias=None %}`

See `cmssiteblock`', above.


### Miscellaneous tags

#### `{% cmsgetcrumbtrail as varname %}`

Returns a list of links representing the "crumbtrail" - example template code:

    {% cmsgetcrumbtrail as crumbtrail %}
    <a href="/">Home</a>
    {% for link in crumbtrail %}
    > <a href="{{ link.uri }}">{{ link.name }}</a>
    {% endfor %}


#### `{% cmspage as varname %}`

Returns the current Page object based on request.path_info. This can be used in
conjunction with [django-shorturls](http://github.com/jacobian/django-shorturls)
in django template code, to generate a canonical link ie:
    
    {% load djangocms2000_tags shorturl %}
    {% get_current_page as current_page %}
    {% revcanonical current_page %}
    
produces something like

    <link rev="canonical" href="http://gregbrown.co.nz/s/E">


#### `{% cmssitemap base_uri=None include_base=True depth=None %}`

Generates sitemap as a nested html list, starting with base_uri as the root
(relies on a sane url scheme to work).


#### `{% get_page_menu as varname)`

Returns a list of MenuItem objects for constructing a navigation menu. Example

    <ul>
        {% get_page_menu as menu_item_list %}
        {% for item in menu_item_list %}
        <li>
            <a href="{{ item.page.uri }}">{{ item }}</a>
        </li>
        {% endfor %}
    </ul>
    
    
## Settings


#### `DJANGOCMS2000_ROOT_URL`

Should correspond to whatever url base you've got pointing to djangocms2000.urls
in your root url conf. Defaults to `'/djangocms2000/'`


#### `DJANGOCMS2000_MEDIA_URL`

Where the djangocms2000/media directory can be found. Defaults to

    DJANGOCMS2000_ROOT_URL + 'media/', 

which is (by default) served by django's built in static view. For better performance, set
    
    DJANGOCMS2000_MEDIA_URL = MEDIA_URL + 'djangocms2000/'
    
and symlink to the directory from within your `MEDIA_ROOT`


#### `DJANGOCMS2000_EDIT_IN_PLACE`

Turns the edit-in-place function on and off – default is `True`.


#### `DJANGOCMS2000_CUSTOM_STYLESHEET`

Location of custom styles for the editor, if needed. Defaults to `None`.


#### `DJANGOCMS2000_HIGHLIGHT_START_COLOR`

Used to highlight changes made via the edit-in-place system on save. Default is `'#ff0'`.

#### `DJANGOCMS2000_HIGHLIGHT_END_COLOR`

Should equal (as closely as possible) your site's background colour. Default is `'#fff'`.


#### `DJANGOCMS2000_ADMIN_JS`

A tuple of javascript files to include when using the built in admin. Defaults to

    (
        DJANGOCMS2000_MEDIA_URL + 'tiny_mce/tiny_mce.js',
        DJANGOCMS2000_MEDIA_URL + 'lib/jquery-1.3.2.min.js',
        DJANGOCMS2000_MEDIA_URL + 'js/page_admin.js',
        DJANGOCMS2000_ROOT_URL + 'page_admin_init.js',
    )


#### `DJANGOCMS2000_ADMIN_CSS`

A dict of css files to include when using in the built-in admin. Defaults to

    {
        'all': (MEDIA_URL + 'css/page_admin.css',),
    }


#### `DJANGOCMS2000_ADMIN_CAN_DELETE_BLOCKS`

Whether or not blocks can be deleted when editing in the built-in admin. Defaults to `settings.DEBUG`


#### `DJANGOCMS2000_FILEBROWSER_URL_ADMIN`

Url for filebrowser integration into tinymce - default is blank.


#### `DJANGOCMS2000_USE_SITES_FRAMEWORK`


Turns on integration with django.contrib.sites - default is `False`.


#### `DJANGOCMS2000_TINYMCE_BUTTONS`


Buttons to include in tinymce editor - defaults to

    "formatselect,bold,italic,|,undo,redo,|,link,|,blockquote,bullist,numlist,|,pastetext,code"


#### `DJANGOCMS2000_TINYMCE_CONTENT_CSS`


Path to css file for styling tinymce editor - default is blank.


#### `DJANGOCMS2000_POST_EDIT_CALLBACK`


Javascript code to execute after a front-end edit - default is blank. Example usage:  

    DJANGOCMS2000_POST_EDIT_CALLBACK = 'Cufon.refresh()'
    

#### `DJANGOCMS2000_MAX_IMAGE_DIMENSIONS`


Maximum image dimensions saved by the editor - if a larger file is uploaded, it 
will be resized before save. Default is `(1920, 1200)`

#### `DJANGOCMS2000_FILTERS`


A tuple of filter declarations - each of the form `(module, shortname, default)`. 
`shortname` is used to apply the filter when calling the templatetag, ie 
`{% cmsblock 'text' filters='typogrify' %}`. Default determines whether the filter
will be applied by default or not. Default:

    (
        ('djangocms2000.filters.typogrify_filter', 'typogrify', False),
    )

#### `DJANGOCMS2000_BLOCK_REQUIRED_CALLBACK`

A python function to determine whether a block is required - takes the Block instance 
in question as its sole argument. Default is `None`. Example:

    def required_cb(block):
        return block.label in ('title', 'main',)
    DJANGOCMS2000_BLOCK_REQUIRED_CALLBACK = required_cb


#### `DJANGOCMS2000_IMAGE_REQUIRED_CALLBACK`

Identical to `BLOCK_REQUIRED_CALLBACK` but takes an Image instance as its argument.


#### `DJANGOCMS2000_CACHE_PREFIX`

Cache backend prefix - defaults to `djangocms2000`

