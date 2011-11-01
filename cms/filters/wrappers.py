from django.template import defaultfilters

def safe(content, block):
    return defaultfilters.safe(content)
