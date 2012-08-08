



def is_editing(request):
    '''test the request object to see if we're in edit mode'''
    return ('cms-edit_mode' in request.COOKIES) and request.user.has_module_perms("cms")



def generate_cache_key(label, app_label=None, module_name=None, object_pk=None, object=None):
    '''generate a consistent unique cache key based on various arguments'''
    
    if all([app_label, module_name, object_pk]):
        key_bits = [app_label, module_name, object_pk]
    elif object:
        key_bits = [object._meta.app_label, object._meta.module_name, object.pk]
    else:
        raise TypeError(u'Required arguments: either all of app_label, module_name and object_pk, or object')
    
    key_bits.append(label)
    return '|'.join(key_bits)
