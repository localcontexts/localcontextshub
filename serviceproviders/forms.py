from django import forms
from .models import ServiceProvider
from django.utils.translation import gettext_lazy as _


class CreateServiceProviderForm(forms.ModelForm):

    class Meta:
        model = ServiceProvider
        fields = ['name', 'description', 'website', 'contact_name', 'contact_email',]
        error_messages = {
            'name': {'unique': _("This service provider is already on the Hub."), },
        }
        widgets = {
            'name': forms.TextInput(
                attrs={'name': 'name', 'class': 'w-100', 'autocomplete': 'off', 'required': True}
            ),
            'description': forms.Textarea(
                attrs={'class': 'w-100', 'rows': 2, 'required': True}
            ),
            'website': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_name': forms.TextInput(
                attrs={
                    'class': 'w-100', 'id': 'serviceProviderContactNameField', 'required': True
                }
            ),
            'contact_email': forms.EmailInput(
                attrs={
                    'class': 'w-100', 'id': 'serviceProviderContactEmailField', 'required': True
                }
            ),
        }


class UpdateServiceProviderForm(forms.ModelForm):

    class Meta:
        model = ServiceProvider
        fields = ['image', 'description', 'website', 'documentation']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'w-100', 'rows': 3}),
            'image': forms.ClearableFileInput(
                attrs={
                    'class': 'w-100 hide', 'id': 'serviceProviderImgUploadBtn',
                    'onchange': 'showFile()',
                }
            ),
            'website': forms.TextInput(attrs={'class': 'w-100'}),
            'documentation': forms.TextInput(attrs={'class': 'w-100'}),
        }
