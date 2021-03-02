from django import forms
from .models import *

class AttachLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['default_text', 'modified_text']
        widgets = {
            'default_text': forms.Textarea(attrs={'class':'default-label-textarea'}),
            'modified_text': forms.Textarea(attrs={'class': 'implement-labels-textarea'})
        }

class CustomiseLabelForm(forms.ModelForm):
    class Meta:
        model = BCLabel
        fields = ['name', 'default_text']
        widgets = {
            'name': forms.TextInput(attrs={'size': 40, 'id': 'bclabel-title'}),
            'default_text': forms.Textarea(attrs={'rows': 4, 'cols': 204, 'id': 'bclabel-template'}),
        }