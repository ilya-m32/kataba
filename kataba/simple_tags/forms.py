from django import forms
from django.utils.html import mark_safe

class TagCompleteInput(forms.CharField):

	name = 'simple_tags_input'
	required = False

class TagCompleteWidget(forms.widgets.Widget):

    def render(self, name, value, attrs=None):
    	name = 'id_tagcomplete'
        return mark_safe(u"""<div id='{0}'></div>""".format(name))

class TagCompleteField(forms.fields.Field):

    widget = TagCompleteWidget
