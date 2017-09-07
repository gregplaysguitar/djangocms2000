from modeltranslation.translator import register, TranslationOptions

from .models import Page, Block


@register(Block)
class BlockOptions(TranslationOptions):
    fields = ('content', )


@register(Page)
class PageOptions(TranslationOptions):
    fields = []
