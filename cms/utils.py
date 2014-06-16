import hashlib

import settings


def is_editing(request, obj_type=None):
    '''Test the request object to see if we're in edit mode'''
    if ('cms-edit_mode' in request.COOKIES):
        if obj_type =='block':
            return request.user.has_perm("cms.change_block")
        elif obj_type =='image':
            return request.user.has_perm("cms.change_image")
        else:
            return request.user.has_module_perms("cms")
    else:
        return False


def generate_cache_key(type, label=None, site_id=None, related_object=None, url=None):
    '''generate a consistent unique cache key based on various arguments'''
    
    if not (site_id or related_object or url):
        raise TypeError(u'Required arguments: one of site_id, related_object or url.')

    key_bits = [settings.CACHE_PREFIX, type, label]
    
    if related_object:
        app_label = related_object._meta.app_label
        
        try:
            model_name = related_object._meta.model_name
        except AttributeError:
            # Django < 1.7 fallback
            model_name = related_object._meta.module_name
            
        if app_label == 'sites' and model_name == 'site':
            # must actually be a site block, being referenced by the sites.Site object
            site_id = related_object.pk
        elif app_label == 'cms' and model_name == 'page':
            # must be a cms.Page, ditto
            url = related_object.url
        
    if site_id:
        key_bits.append('site_id:%s' % site_id)
    elif url:
        # include site id, because there could be two pages with the same url
        # but attached to different sites
        key_bits.append('url:%s,%s' % (url, settings.SITE_ID)) 
    else:
        # must be a related_object present, otherwise we wouldn't have got this far
        key_bits.append('object_pk:%s' % related_object.pk)
                
    return '|'.join(key_bits)


def public_key():
    '''Returns a consistent hash of the secret key which can be used in a
       public context, i.e. as a GET parameter.'''
    
    return hashlib.sha1(settings.SECRET_KEY).hexdigest()[:10]

