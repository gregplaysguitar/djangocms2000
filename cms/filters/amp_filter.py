from typogrify.templatetags.typogrify import amp

def filter(content, block):
    return amp(content)