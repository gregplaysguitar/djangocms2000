from typogrify.templatetags.typogrify import typogrify

def filter(content, block):
    return typogrify(content)