from django import forms
from .models import AccountAPIKey

class APIKeyGeneratorForm(forms.ModelForm):

    class Meta:
        model = AccountAPIKey
        fields = ['name']
        widgets ={
            'name': forms.TextInput(attrs={'required': True, "placeholder": "API Key Application Name"})
        }
        