from django import forms
from .models import Community, InviteMember, JoinRequest
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
import os

from .widgets import BoundaryWidget


class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'community_entity', 'state_province_region', 'country', 'description',]
        widgets = {
            'community_name': forms.TextInput(attrs={'class': 'w-100'}),
            'community_entity': forms.TextInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'w-100'}),
        }
        error_messages = {
            'community_name': {
                'unique': _("A community by that name already exists."),
            },
        }

class ConfirmCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['contact_name', 'contact_email', 'support_document']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100', 'id': 'communityContactEmailField'}),
            'support_document': forms.ClearableFileInput(attrs={'class': 'w-100 hide', 'id': 'communitySupportLetterUploadBtn', 'onchange': 'showFile()'}),
        }

    def clean_support_document(self):
        support_document_file = self.cleaned_data.get('support_document')
        if support_document_file:
            allowed_extensions = ['.pdf', '.doc', '.docx']  # Add more extensions if needed
            file_ext = os.path.splitext(support_document_file.name)[1].lower()

            if file_ext not in allowed_extensions:
                raise ValidationError('Invalid document file extension. Only PDF and DOC/DOCX files are allowed.')

            allowed_mime_types = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if support_document_file.content_type not in allowed_mime_types:
                raise ValidationError('Invalid document file type. Only PDF and DOC/DOCX files are allowed.')
        return support_document_file


class CommunityModelForm(forms.ModelForm):
    class Meta:
        model = Community
        exclude = []
        widgets = {
            'boundaries': BoundaryWidget
        }

    def get_boundaries(self):
        # add logic for getting boundaries using supplemental form data
        return []

    def validate_boundaries(self):
        # remove previous errors
        if 'boundaries' in self.errors:
            del self.errors['boundaries']

        self.cleaned_data['boundaries'] = self.get_boundaries()

    def is_valid(self):
        super().is_valid()
        self.validate_boundaries()
        return self.is_bound and not self.errors

    def save(self, commit=True):
        obj = super().save(commit=False)
        # if commit:
        #     obj.save()
        return obj


class UpdateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['contact_name', 'contact_email', 'description', 'community_entity', 'city_town', 'state_province_region', 'country', 'image']
        widgets = {
            'community_entity': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_name': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'city_town': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-100'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-100 hide', 'id': 'communityImgUploadBtn', 'onchange': 'showFile()'}),
        }

class InviteMemberForm(forms.ModelForm):
    class Meta:
        model = InviteMember
        fields = ['role', 'message']
        widgets = {
            'role': forms.Select(attrs={'class': 'w-100'}),
            'message': forms.Textarea(attrs={'rows': 2, 'class':'w-100'}),
        }

class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ['role', 'message']
        widgets = {
            'role': forms.Select(attrs={'class': 'w-100'}),
            'message': forms.Textarea(attrs={'rows': 3, 'class':'w-100'}),
        }