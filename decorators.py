from django import template
from django.conf import settings
from django.core.cache import cache

def easy_tag(func):
    """deal with the repetitive parts of parsing template tags"""
    def inner(parser, token):
        #print token
        try:
            # try passing parser as a kwarg for tags that support it
            args = token.split_contents()
            kwargs = {'parser': parser}
            return func(*args, **kwargs)
        except TypeError:
            try:
                return func(*args)
            except TypeError:
                raise template.TemplateSyntaxError('Bad arguments for tag "%s"' % args[0])
    inner.__name__ = func.__name__
    inner.__doc__ = inner.__doc__
    return inner




def cached(key, duration=None):
    """Wraps caching around an existing function, using the given key and duration.
    
    Use like:
    
    @cached("work-for-x", 600)
    def work():
        # do work here
        return result
    
    result = work() # result will come from cache if possible
    """
    key = "%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, key)
    if not duration:
        duration = settings.CACHE_MIDDLEWARE_SECONDS
    def decorator(func):
        def inner(*args, **kwargs):
            result = cache.get(key)
            if settings.DEBUG or not result:
                result = func(*args, **kwargs)
                cache.set(key, result, duration)
            return result
        inner.__name__ = "@cached %s" % func.__name__
        inner.__doc__ = "@cached. %s" % func.__doc__
        return inner
    return decorator





