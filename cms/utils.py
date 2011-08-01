


# test the request object to see if we're in edit mode
def is_editing(request):
    return ('cms-edit_mode' in request.COOKIES) and request.user.has_module_perms("cms")
