BASIC INSTALLATION:
==================

1. /djangocms2000/ -> djangocms2000.urls
2. (For optional edit-in-place) add cmsextra tag at bottom of base template (with {% load djangocms2000_tags %} at the top)
3. TEMPLATE_LOADERS -> add 'django.template.loaders.app_directories.load_template_source',
4. Add djangocms2000.middleware.Djangocms2000FallbackMiddleware to your middleware classes
5. Use {% cmsblock 'blockname' 'plain|html|markdown' %} to create editable blocks in templates
6. To use images, download [sorl.thumbnail](http://code.google.com/p/sorl-thumbnail/) and add it to your INSTALLED_APPS
7. Use {% cmsimage 'imagename' '400x300' %} to create editable images 
8. Use ala flatpages
9. Created pages can be edited in place if 2) was followed
10. See reference.markdown for more info








BUGS FOUND BY MATT
------------------

- When editing "plain" fields (I think) the field is always populated 
  with what was its content on page load, even if it's been changed 
  since then, e.g.:
  	
      1. Title is "A Title"
      2. Change to "New Title"
      3. Save
      4. Click to edit again
      5. Field is populated with "A Title"


- It's not really happy about editable blocks when there's no CMSPage
  e.g. when all blocks are 'generic'

- z-indexes e.g. editable fields above panel at top of window.

- editing a plain text block before the page has fully loaded opens up the html editor as well as the plain text editor


TODO
----

- plain text needs to somehow distinguish between single line stuff and multi line for admin
- incorporate tim's new designs
- Markdown editing weirdness
- The "click to add" text should be added if the only thing present is tags, i.e. the content is <p></p> etc


TODONE
---------

- Create blocks on page creation in admin, rather than having to view the page in 
   the site in order to create the blocks (use template nodelist etc to see what 
   needs to be done - or maybe dummy-render the page... ?)
- js should add the "click to add new ..." text, so that it doesn't show if the 
  editor is turned off