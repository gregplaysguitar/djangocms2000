TODO
====

- plain text needs to somehow distinguish between single line stuff and multi line for admin
- The "click to add" text should be added if the only thing present is tags, i.e. the content is <p></p> etc
- The test for urlconf-rendered vs middleware-rendered pages fails when the url resolves, but the view returns a 404. Fix this, or perhaps just document? See forms.py, line 62
