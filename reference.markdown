# djangocms2000 Reference

## Template Tags

Use `{% load cms_tags %}` to enable.


#### cmsblock

Format: `{% cmsblock label [format='plain' editable=1 as alias] %}`

Basic cms content block. Place as many of these as you need in your template, 
with unique labels (labels can be repeated if you want the same content in 
more than one place, ie the window title and page title). Example template code:
    
    {# standard plain-text block #}
    <h1>{% cmsblock "title" %}</h1>
    
    {# non-editable #}
    <title>{% cmsblock "title" editable=0 %} | Example.com</title>
    
    {# html format (uses tinymce editor) #}
    {% cmsblock "content" format="html" %}
    
    {# extended syntax, demonstrating the use of template filters on the block content #}
    {% cmsblock 'text' as block %}
        {{ block.content|urlize|linebreaks }}
    {% endcmsblock %}

    {# extended syntax, with default content #}
    {% cmsblock 'text' as block %}
        <p>{{ block.content }}</p>
    {% empty %}
        <p>Default content here</p>
    {% endcmsblock %}    
    

#### cmsimage

Format: `{% cmsimage label [geometry='' crop='' editable=1 as alias] %}`

Basic image block - use as with `cmsblock`. The `geometry` and `crop` arguments
correspond to sorl's [geometry](http://thumbnail.sorl.net/template.html#geometry) and 
[crop](http://thumbnail.sorl.net/template.html#crop) options, and can be of the format
'XxY', 'X', or 'xY', for constraining width and height, just width, and just height, 
respectively. Examples:

    {# render image as uploaded, no resizing #}
    {% cmsimage "image" %}
    
    {# fit within a 300x400 box, don't crop #}
    {% cmsimage "image" geometry="300x400" %}
    
    {# resize to 300x400 exactly, cropping if necessary #}
    {% cmsimage "image" geometry="300x400" crop='center' %}
    
    {# resize to 200px wide, don't crop  #}
    {% cmsimage "image" geometry='200' %}
    
    {# resize to 200px high, don't crop #}
    {% cmsimage "image" geometry='x200' %}
    
    {# custom image display, in this case adding a link to download the original image #}
    {% cmsimage "image" geometry="300x400" as img %}
        <a href="{{ img.image.file.url }}">
            <img src="{{ img.url }}" alt="{{ img.image.description }}" 
                 width="{{ img.width }}" height="{{ img.height }}">
        </a>
    {% endcmsimage %}
    
    {# show default image if no image added #}
    {% cmsimage "image" as img %}
        <img src="{{ img.url }}" alt="{{ img.image.description }}" 
             width="{{ img.width }}" height="{{ img.height }}">
    {% empty %}
        <img src="path-to-default-image.jpg">
    {% endcmsimage %}
    

#### Generic blocks and images

Format:

    {% cmsgenericblock label object [format='plain' editable=1 as alias] %}
    {% cmsgenericimage label object [geometry='' crop='' editable=1 as alias] %}

Like `cmsblock` and `cmsimage`, but attached to a generic `django.db.models.Model` 
object instead of a cms page. The additional `object` argument is required and should 
be the relevant instance. Example usage:

    {% for article in articles %}
        <article>
            <h1>{% cmsgenericblock 'title' article %}</h1>
            {% cmsgenericblock 'text' article format='html' %}
            {% cmsgenericimage 'text' article geometry='400x300' %}
        </article>
    {% endfor %}


#### Site blocks and images

Format:

    {% cmssiteblock label [format='plain' editable=1 as alias] %}
    {% cmssiteimage label [geometry='' crop='' editable=1 as alias] %}

Like a `cmsgenericblock` that is automatically attached to the current site instance, 
so effectively a site-wide block. Example

    <title>{% block title %}{% endblock %} | {% cmssiteblock "base-title" editable=0 %}</title>
    
    <footer>{% cmssiteimage "footer-logo" geometry='200x200' %}</footer>


## Settings


#### `CMS_USE_SITES_FRAMEWORK`

Turns on integration with django.contrib.sites - default is `False`.


#### `CMS_TINYMCE_BUTTONS`

Buttons to include in tinymce editor - defaults to

    "formatselect,bold,italic,|,undo,redo,|,link,|,blockquote,bullist,numlist,|,pastetext,code"


#### `CMS_TINYMCE_CONTENT_CSS`

Path, or callable returning a path, to css file for styling tinymce editor. Default is
blank. Use a callable to avoid reversing urls etc at runtime.


#### `CMS_POST_EDIT_CALLBACK`

Javascript function to execute after a front-end edit - default is blank. Example usage:  

    CMS_POST_EDIT_CALLBACK = 'function() { ... }'
    

#### `CMS_MAX_IMAGE_DIMENSIONS`

Maximum image dimensions saved by the editor - if a larger file is uploaded, it 
will be resized before save. Default is `(1920, 1200)`


#### `CMS_BLOCK_REQUIRED_CALLBACK`

A python function to determine whether a block is required - takes the Block instance 
in question as its sole argument. Default is `None`. Example:

    def required_cb(block):
        return block.label in ('title', 'main',)
    CMS_BLOCK_REQUIRED_CALLBACK = required_cb


#### `CMS_IMAGE_REQUIRED_CALLBACK`

Identical to `BLOCK_REQUIRED_CALLBACK` but takes an Image instance as its argument.


#### `CMS_DUMMY_IMAGE_SOURCE`

If set, and DEBUG is True, empty cms images will be filled with a placeholder from 
the given source. Format is borrowed from
[sorl](http://sorl-thumbnail.readthedocs.org/en/latest/reference/settings.html),
and should contain `%(width)s` and `%(height)s` placeholders, i.e.

    'http://placehold.it/%(width)sx%(height)s'
    'http://placekitten.com/%(width)s/%(height)s'

Defaults value is `None`.