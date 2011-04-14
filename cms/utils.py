


# test the request object to see if we're in edit mode
def is_editing(request):
    return ('djangocms2000-edit_mode' in request.COOKIES) and request.user.has_module_perms("djangocms2000")
