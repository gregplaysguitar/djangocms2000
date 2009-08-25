from django import forms
#from models import Block, Page, Image
#from tinymce.widgets import TinyMCE


class BlockForm(forms.Form):
	block_id = forms.CharField(widget=forms.HiddenInput)
	format = forms.CharField(widget=forms.HiddenInput)
	
	raw_content = forms.CharField(widget=forms.Textarea)


class ImageForm(forms.Form):
	image_id = forms.CharField(widget=forms.HiddenInput)
	redirect_to = forms.CharField(widget=forms.HiddenInput)
	
	description = forms.CharField(widget=forms.TextInput)
	file = forms.FileField()

