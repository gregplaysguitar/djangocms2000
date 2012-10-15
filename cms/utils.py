import settings


def is_editing(request):
    '''test the request object to see if we're in edit mode'''
    return ('cms-edit_mode' in request.COOKIES) and request.user.has_module_perms("cms")



def generate_cache_key(type, label=None, site_id=None, object=None, url=None):
    '''generate a consistent unique cache key based on various arguments'''
    
    if not (site_id or object or url):
        raise TypeError(u'Required arguments: one of site_id, object or url.')

    key_bits = [settings.CACHE_PREFIX, type, label]
    
    if object:
        app_label = object._meta.app_label
        module_name = object._meta.module_name
        if app_label == 'sites' and module_name == 'site':
            # must actually be a site block, being referenced by the sites.Site object
            site_id = object.pk
        elif app_label == 'cms' and module_name == 'page':
            # must be a cms.Page, ditto
            url = object.url
        
    if site_id:
        key_bits.append('site_id:%s' % site_id)
    elif url:
        key_bits.append('url:%s' % url)
    else:
        # must be an object present, otherwise we wouldn't have got this far
        key_bits.append('object_pk:%s' % object.pk)
                
    return '|'.join(key_bits)
