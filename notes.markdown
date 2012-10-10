BACKWARDS-INCOMPATIBLE CHANGES:
===============================

"CMS" MIGRATION:
----------------

Applies to any descendant of commit b40137c51a4fc8d2b2ac2e6826afd05d77ab7a49,
in which the app name was changed from `djangocms2000` to just `cms`, and moved
into a subfolder.

You should apply all of these steps at once, without running the site until
you're finished.

- Place the cms subfolder on your path, instead of the djangocms2000 project folder
- `djangocms2000` becomes `cms` in `INSTALLED_APPS` and your root urls.py
- `{% load djangocms2000_tags %}` becomes `{% load cms_tags %}` in templates.
- Change `DJANGOCMS2000_` settings prefixes to `CMS_`
- Change `djangocms2000.middleware.Djangocms2000FallbackMiddleware` to `cms.middleware.CMSFallbackMiddleware`
- If you are NOT using staticfiles, rename media/djangocms2000 -> media/cms
- Rename templates/djangocms2000 -> templates/cms
- Rename djangocms2000 db tables
- Replace `cms_page` template names
- Modify djangocms2000 entries in `django_content_type` db table (change app_label to 'cms')
- If you are using [haystack](http://haystacksearch.org/) with the cms, you'll need to rename your search template folder from `djangocms2000` to `cms`

URL/URI MIGRATION:
------------------

In commit 69c99c2b4e8c7adf4643bab7648831d375ae0e7a, all references to `uri` became
`url`. To migrate, change the `cms_page.uri` field to `cms_page.url`

Example SQL for the above migrations:
-------------------------------------

    update django_content_type set app_label='cms' where app_label='djangocms2000';
    alter table djangocms2000_page rename to cms_page;
    alter table djangocms2000_block rename to cms_block;
    alter table djangocms2000_image rename to cms_image;
    alter table djangocms2000_menuitem rename to cms_menuitem;
    update cms_page set template='cms/static.html' where template='djangocms2000/static.html';
    alter table cms_page change `uri` `url` varchar(255)  not null default '';



TODO
====

- Upgrade tinymce and jquery, fix the way we load jquery (load own non-clashing version?)
- give non-standard cms block attrs a data- prefix, and use jquery's .data() to access them
- plain text needs to somehow distinguish between single line stuff and multi line for admin
- incorporate tim's new designs
- Markdown editing weirdness
- The "click to add" text should be added if the only thing present is tags, i.e. the content is <p></p> etc
- It's not really happy about editable blocks when there's no CMSPage
  e.g. when all blocks are 'generic'
- z-indexes e.g. editable fields above panel at top of window.
- editing a plain text block before the page has fully loaded opens up the html editor as well as the plain text editor
- ability to tab through cms blocks on a page, hitting enter to edit the currently highlighted block
- upgrade tinymce
- Bind ESC key to cancel when editing inline
- Handle the readonly template and url for auto-created django url pages better (currently a hidden/readonly input, should just remove from form)
- The test for urlconf-rendered vs middleware-rendered pages fails when the url resolves, but the view returns a 404. Fix this, or perhaps just document? See forms.py, line 62
- With extended syntax, just wrap the block content and not the whole thing in editing bits...? Might need a new RenderedBlock object and to revamp the `renderer` system somewhat.

TODONE
======

- When editing "plain" fields (I think) the field is always populated 
  with what was its content on page load, even if it's been changed 
  since then, e.g.:
  	
      1. Title is "A Title"
      2. Change to "New Title"
      3. Save
      4. Click to edit again
      5. Field is populated with "A Title"

- Create blocks on page creation in admin, rather than having to view the page in 
   the site in order to create the blocks (use template nodelist etc to see what 
   needs to be done - or maybe dummy-render the page... ?)
- js should add the "click to add new ..." text, so that it doesn't show if the 
  editor is turned off
- CSRF token needs to be added to image upload/change form
- refactor template tags to use dynamic number of arguments so "as varname" just has to go at the end
- For CMSBaseModel-based generic objects, render the objects get\_absolute\_url instead
  of requiring BLOCK\_LABELS and IMAGE\_LABELS constants
- New syntax for blocks, with default eg. {% cmsblock "title" %}Default title here{% endcmsblock %}