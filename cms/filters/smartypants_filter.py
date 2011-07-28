from typogrify.templatetags.typogrify import smartypants

def filter(content, block):
    return smartypants(content)