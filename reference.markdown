# djangocms2000 Reference

... currently a work in progress.

## Template Tags

Use `{% load cms_tags %}` to enable.

### Text tags

#### `{% cmsblock label format='plain' editable=1 alias=None filters='' %}`

Basic cms content block. Place as many of these as you need in your template, 
with unique labels (labels can be repeated if you want the same content in 
more than one place, ie the window title and page title). Example template code:
    
    {# standard plain-text block #}
    <h1>{% cmsblock "title" %}</h1>
    
    {# non-editable #}
    <title>{% cmsblock "title" editable=0 %} | Example.com</title>
    
    {# markdown-formatted #}
    {% cmsblock "content" "markdown" %}
    
    {# html format (uses tinymce editor) #}
    {% cmsblock "content" "html" %}
    
    {# only show the block and surrounds if it has content or we're in edit mode #}
    {% cmsblock "tagline" "markdown" alias=tagline %}
    {% if tagline %}
    <blockquote class="grid_10">
        {{ tagline }}
    </blockquote>
    {% endif %}
    
    {# utilise django's built in filters #}
    {% cmsblock "content" filters='linebreaks,urlize' %}
    
    {# apply the built in "typogrify" filter (requires django-typogrify) #}
    {% cmsblock "content" "html" filters='typogrify' %}


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
or "url" (outputs the url to the resized image). 
The 'constraint' argument can be of the format 'XxY', 'X', or 'xY' - the latter 
two are for constraining just width and and just height, respectively.
Examples:

    {# standard usage, fitted within 300x400 box but not cropped #}
    {% cmsimage "portrait" "300x400" %}
    
    {# resize to 200px wide, aspect ratio preserved #}
    {% cmsimage "portrait" '200' %}
    
    {# resize to 200px high, aspect ratio preserved #}
    {% cmsimage "portrait" 'x200' %}

    {# Don't resize the uploaded image at all #}
    {% cmsimage "portrait" %}

    {# crop to an exact size #}
    {% cmsimage "banner" "960x120" crop='center' %}
    
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
    > <a href="{{ link.uri }}">{% firstof link.page.page_title link.name %}</a>
    {% endfor %}


#### `{% cmspage as varname %}`

Returns the current Page object based on request.path_info. This can be used in
conjunction with [django-shorturls](http://github.com/jacobian/django-shorturls)
in django template code, to generate a canonical link ie:
    
    {% load cms_tags shorturl %}
    {% cmspage as current_page %}
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


#### `CMS_ROOT_URL`

Should correspond to whatever url base you've got pointing to cms.urls
in your root url conf. Defaults to `'/cms/'`


#### `CMS_STATIC_URL`

Where the cms/media directory can be found. Defaults to

    CMS_ROOT_URL + 'media/', 

which is (by default) served by django's built in static view. For better performance, set
    
    CMS_STATIC_URL = STATIC_URL + 'cms/'
    
and symlink to the directory from within your `MEDIA_ROOT`


#### `CMS_CUSTOM_STYLESHEET`

Location of custom styles for the editor, if needed. Defaults to `None`.


#### `CMS_HIGHLIGHT_START_COLOR`

Used to highlight changes made via the edit-in-place system on save. Default is `'#ff0'`.

#### `CMS_HIGHLIGHT_END_COLOR`

Should equal (as closely as possible) your site's background colour. Default is `'#fff'`.


#### `CMS_ADMIN_JS`

A tuple of javascript files to include when using the built in admin. Defaults to

    (
        CMS_STATIC_URL + 'tiny_mce/tiny_mce.js',
        CMS_STATIC_URL + 'lib/jquery-1.3.2.min.js',
        CMS_STATIC_URL + 'js/page_admin.js',
        CMS_ROOT_URL + 'page_admin_init.js',
    )


#### `CMS_ADMIN_CSS`

A dict of css files to include when using in the built-in admin. Defaults to

    {
        'all': (STATIC_URL + 'css/page_admin.css',),
    }


#### `CMS_ADMIN_CAN_DELETE_BLOCKS`

Whether or not blocks can be deleted when editing in the built-in admin. Defaults to `settings.DEBUG`


#### `CMS_FILEBROWSER_URL_ADMIN`

Url for filebrowser integration into tinymce - default is blank.


#### `CMS_USE_SITES_FRAMEWORK`


Turns on integration with django.contrib.sites - default is `False`.


#### `CMS_TINYMCE_BUTTONS`


Buttons to include in tinymce editor - defaults to

    "formatselect,bold,italic,|,undo,redo,|,link,|,blockquote,bullist,numlist,|,pastetext,code"


#### `CMS_TINYMCE_CONTENT_CSS`


Path to css file for styling tinymce editor - default is blank.


#### `CMS_POST_EDIT_CALLBACK`


Javascript code to execute after a front-end edit - default is blank. Example usage:  

    CMS_POST_EDIT_CALLBACK = 'Cufon.refresh()'
    

#### `CMS_MAX_IMAGE_DIMENSIONS`


Maximum image dimensions saved by the editor - if a larger file is uploaded, it 
will be resized before save. Default is `(1920, 1200)`

#### `CMS_FILTERS`


A tuple of filter declarations - each of the form `(module, shortname, default)`. 
`shortname` is used to apply the filter when calling the templatetag, ie 
`{% cmsblock 'text' filters='typogrify' %}`. Default determines whether the filter
will be applied by default or not. Default:

    (
        ('cms.filters.typogrify_filter', 'typogrify', False),
    )

#### `CMS_BLOCK_REQUIRED_CALLBACK`

A python function to determine whether a block is required - takes the Block instance 
in question as its sole argument. Default is `None`. Example:

    def required_cb(block):
        return block.label in ('title', 'main',)
    CMS_BLOCK_REQUIRED_CALLBACK = required_cb


#### `CMS_IMAGE_REQUIRED_CALLBACK`

Identical to `BLOCK_REQUIRED_CALLBACK` but takes an Image instance as its argument.


#### `CMS_CACHE_PREFIX`

Cache backend prefix - defaults to `cms`

