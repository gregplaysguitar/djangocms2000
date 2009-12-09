from django.contrib.sitemaps import Sitemap
from models import Page

class PageSitemap(Sitemap):
    def items(self):
        return Page.objects.all()
