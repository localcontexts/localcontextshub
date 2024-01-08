import json
import sys

from django import forms
from django.forms.utils import ErrorList

from .models import Community, InviteMember, JoinRequest, Boundary
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
        max_coordinates_in_boundary_count = 2000
        max_boundary_count = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supplementary_boundary_data = None
        self.fields['boundaries'].widget = BoundaryWidget(
            attrs={
                'community_id': self.instance.id,
                'boundary_ids': [b.id for b in self.instance.boundaries.all()]
            }
        )
        self.fields['boundaries'].help_text = None

    def parse_boundary_str(self, boundary_str: str) -> dict:
        boundary_str_with_brackets = boundary_str.replace('(', '[').replace(')', ']')
        boundary_data = json.loads(f'[{boundary_str_with_brackets}]')
        boundary_data_length = len(boundary_data)

        if boundary_data_length > self.Meta.max_coordinates_in_boundary_count:
            raise Exception(f'Boundary Has Too Many Coordinates. '
                            f'{boundary_data_length} Coordinates Are Detected')

        return boundary_data

    def read_supplementary_boundary_data(self) -> dict:
        deleted_boundary_ids = []
        new_boundaries = []
        current_boundaries = {}
        errors = ErrorList()

        for key in self.data:
            try:
                if 'deleted-boundary' in key:
                    _, boundary_id = key.split(':')
                    deleted_boundary_ids.append(boundary_id)

                elif 'new-boundary' in key:
                    new_boundary_value = self.parse_boundary_str(self.data[key])
                    new_boundaries.append(new_boundary_value)

                elif 'current-boundary' in key:
                    current_boundary_value = self.data[key]
                    _, boundary_id = key.split(':')
                    current_boundaries[boundary_id] = self.parse_boundary_str(current_boundary_value)

            except Exception as e:
                # send error to FE
                errors.data.append('Error Reading Boundary Data')

                # log detailed error for devs
                print(f'Error Reading Supplemental Boundary Data: {e}', file=sys.stderr)
                break

        # create error when they are too many boundaries
        boundary_count = len(current_boundaries) - len(deleted_boundary_ids) + len(new_boundaries)
        if boundary_count > self.Meta.max_boundary_count:
            errors.data.append('Too Many Boundaries Detected')

        # when errors exist, add those to the form
        if errors:
            self.errors['boundaries'] = errors

        return {
            'deleted_boundary_ids': deleted_boundary_ids,
            'current_boundaries': current_boundaries,
            'new_boundaries': new_boundaries,
        }

    def validate_boundaries(self):
        # remove previous errors
        if 'boundaries' in self.errors:
            del self.errors['boundaries']

        # store supplementary boundary data
        self.supplementary_boundary_data = self.read_supplementary_boundary_data()

    def is_valid(self):
        super().is_valid()
        self.validate_boundaries()
        return self.is_bound and not self.errors

    def save_boundaries(self):

        # delete boundaries that should be deleted
        for boundary_id in self.supplementary_boundary_data['deleted_boundary_ids']:
            self.instance.boundaries.filter(id=boundary_id).delete()

            # del corresponding boundary from current boundaries
            del self.supplementary_boundary_data['current_boundaries'][boundary_id]

        # update current boundaries
        for boundary_id in self.supplementary_boundary_data['current_boundaries']:
            boundary_object = self.instance.boundaries.filter(id=boundary_id).first()
            boundary_object.coordinates = self.supplementary_boundary_data['current_boundaries'][boundary_id]
            boundary_object.save()

        # add new boundaries
        for coordinates in self.supplementary_boundary_data['new_boundaries']:
            boundary = Boundary.objects.create(coordinates=coordinates)
            self.instance.boundaries.add(boundary)

    def save(self, commit=True):
        obj = super().save(commit=False)
        self.save_boundaries()
        if commit:
            obj.save()
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