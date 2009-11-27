# Djangocms2000 Reference

... a work in progress.

## Template Tags

Use `{% load djangocms2000_tags %}` to enable.

#### {% cmsblock _label_ _format_ [_enable-edit-in-place=True_ _as=""_ _varname=None_] %}

Basic cms content block. Place as many of these as you need in your template, 
with unique labels (labels can be repeated if you want the same content in 
more than one place, ie the window title and page title). Example template code:
    
    <h1>{% cmsblock "title" "plain" %}</h1>
    
    {# non-editable #}
    <title>{% cmsblock "title" "plain" False %} | Example.com</title>

    {% cmsblock "content" "markdown" %}
    
    {# format defaults to "html" #}
    {% cmsblock "content" %}
    
    {# only show the block and surrounds if it has content #}
    {# (will always show in edit mode) #}
    {% cmsblock "tagline" "markdown" True as tagline %}
    {% if tagline %}
    <blockquote class="grid_10">
        {{ tagline }}
    </blockquote>
    {% endif %}
    

#### {% cmsimage _label_ _dimensions_ %}

...

#### {% cmsgetcrumbtrail _as_ _varname_ %}

Returns a list of links representing the "crumbtrail" - example template code:

    {% cmsgetcrumbtrail as crumbtrail %}
    <a href="/">Home</a>
    {% for link in crumbtrail %}
    > <a href="{{ link.uri }}">{{ link.name }}</a>
    {% endfor %}


### Settings

...
