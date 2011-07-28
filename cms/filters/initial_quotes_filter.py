from typogrify.templatetags.typogrify import initial_quotes

def filter(content, block):
    return initial_quotes(content)