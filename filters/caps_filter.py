from typogrify.templatetags.typogrify import caps

def filter(content, block):
    return caps(content)