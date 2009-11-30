# Djangocms2000 Reference

... currently a work in progress.

## Template Tags

Use `{% load djangocms2000_tags %}` to enable.

#### {% cmsblock _label format editable=True _as='' alias=None_ %}

Basic cms content block. Place as many of these as you need in your template, 
with unique labels (labels can be repeated if you want the same content in 
more than one place, ie the window title and page title). Example template code:
    
    <h1>{% cmsblock "title" "plain" %}</h1>
    
    {# non-editable #}
    <title>{% cmsblock "title" "plain" False %} | Example.com</title>

    {% cmsblock "content" "markdown" %}
    
    {# format defaults to "html" #}
    {% cmsblock "content" %}
    
    {# only show the block and surrounds if it has content and we're not in edit mode #}
    {% cmsblock "tagline" "markdown" True as tagline %}
    {% if tagline %}
    <blockquote class="grid_10">
        {{ tagline }}
    </blockquote>
    {% endif %}
    

#### {% cmsimage _label constraint crop="" defaultimage=False editable=True format=None _as='' alias=None_ %}

Basic image block - use as with `cmsblock`. By default, will fit an image within the constraint, but won't crop. Format can be "html" (generates an <img> tag) or "url" (outputs the url to the resized image). Examples:

    {% cmsimage "portrait" "300x400" %}

    {# crop to an exact size #}
    {% cmsimage "banner" "960x120" True %}
    
    {# show i/default.png if no image added, and don't crop #}
    {% cmsimage "portrait" "300x400" '' 'i/default.png' %}
    
    {# only show the image if one has been uploaded #}
    {% cmsimage "portrait" "300x400" '' 'i/default.png' 'url' as 'image_url' %}
    {% if image_url %}
    <img src="{{ image_url }}" alt="portrait">
    {% endif %}


#### {% cmsgetcrumbtrail _as varname_ %}

Returns a list of links representing the "crumbtrail" - example template code:

    {% cmsgetcrumbtrail as crumbtrail %}
    <a href="/">Home</a>
    {% for link in crumbtrail %}
    > <a href="{{ link.uri }}">{{ link.name }}</a>
    {% endfor %}


## Settings


#### DJANGOCMS2000\_ROOT\_URL

Should correspond to whatever url base you've got pointing to djangocms2000.urls
in your root url conf. Defaults to `'/djangocms2000/'`


#### DJANGOCMS2000\_MEDIA\_URL

Where the djangocms2000/media directory can be found. Defaults to

    DJANGOCMS2000_ROOT_URL + 'media/', 

which is (by default) served by django's built in static view. For better performance, set
    
    DJANGOCMS2000_MEDIA_URL = MEDIA_URL + 'djangocms2000/'
    
and symlink to the directory from within your `MEDIA_ROOT`


#### DJANGOCMS2000\_EDIT\_IN\_PLACE

Turns the edit-in-place function on and off – default is true.


#### DJANGOCMS2000\_CUSTOM\_STYLESHEET

Location of custom styles for the editor, if needed. Defaults to `None`.


#### DJANGOCMS2000\_HIGHLIGHT\_START\_COLOR

Used to highlight changes made via the edit-in-place system on save. Default is `'#ff0'`.

#### DJANGOCMS2000\_HIGHLIGHT\_END_COLOR

Should equal (as closely as possible) your site's background colour. Default is `'#fff'`.


#### DJANGOCMS2000\_ADMIN\_JS

A tuple of javascript files to include when using the built in admin. Defaults to

    (
        DJANGOCMS2000_MEDIA_URL + 'tiny_mce/tiny_mce.js',
        DJANGOCMS2000_MEDIA_URL + 'lib/jquery-1.3.2.min.js',
        DJANGOCMS2000_MEDIA_URL + 'js/page_admin.js',
        DJANGOCMS2000_ROOT_URL + 'page_admin_init.js',
    )


#### DJANGOCMS2000\_ADMIN\_CSS

A dict of css files to include when using in the built-in admin. Defaults to

    {
        'all': (MEDIA_URL + 'css/page_admin.css',),
    }


#### DJANGOCMS2000\_ADMIN\_CAN\_DELETE\_BLOCKS

Whether or not blocks can be deleted when editing in the built-in admin. Defaults to `settings.DEBUG`



