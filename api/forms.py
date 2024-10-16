from django import forms
from .models import AccountAPIKey
from django.core.exceptions import ValidationError

class APIKeyGeneratorForm(forms.ModelForm):

    class Meta:
        model = AccountAPIKey
        fields = ['name']
        widgets ={
            'name': forms.TextInput(attrs={'required': True, "placeholder": "Enter a name for your API key", 'class': 'w-100'})
        }
        
    def clean_name(self):
        key_name = self.cleaned_data.get("name")
        if not key_name:
            raise ValidationError("Please enter an API Key name.")
        return key_name