import json
import sys

from django import forms
from django.forms.utils import ErrorList

from .models import Community, InviteMember, JoinRequest, Boundary
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import os

from .widgets import BoundaryWidget


class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['community_name', 'community_entity', 'state_province_region', 'country', 'description', 'website', 'contact_name', 'contact_email']
        widgets = {
            'community_name': forms.TextInput(attrs={'class': 'w-100'}),
            'community_entity': forms.TextInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'w-100'}),
            'website': forms.TextInput(attrs={'class': 'w-100'}),
            'contact_name': forms.TextInput(attrs={'class': 'w-100', 'required': True}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-100', 'required': True, 'id': 'communityContactEmailField'}),
        }
        error_messages = {
            'community_name': {
                'unique': _("A community by that name already exists."),
            },
        }


class CommunityModelForm(forms.ModelForm):
    class Meta:
        model = Community
        exclude = []
        max_coordinates_in_boundary_count = 3000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supplementary_boundary_data = None
        self.fields['boundary'].widget = BoundaryWidget(
            attrs={
                'community_id': self.instance.id,
                'boundary_id': self.instance.boundary.id if self.instance.boundary else None
            }
        )
        self.fields['boundary'].help_text = None

    def parse_boundary_str(self, boundary_str: str) -> dict:
        boundary_str_with_brackets = boundary_str.replace('(', '[').replace(')', ']')
        boundary_data = json.loads(f'[{boundary_str_with_brackets}]')

        boundary_data_length = len(boundary_data)
        if boundary_data_length > self.Meta.max_coordinates_in_boundary_count:
            raise Exception(f'Boundary Has Too Many Coordinates. '
                            f'{boundary_data_length} Coordinates Are Detected')

        return boundary_data

    def read_supplementary_boundary_data(self) -> dict:
        current_boundary = None
        new_boundary = None
        errors = ErrorList()

        for key in self.data:
            try:
                if 'current-boundary' in key:
                    current_boundary_value = self.data[key]
                    _, boundary_id = key.split(':')
                    current_boundary = {
                        'id': boundary_id,
                        'value': self.parse_boundary_str(current_boundary_value)
                    }

                if 'new-boundary' in key:
                    new_boundary = self.parse_boundary_str(self.data[key])

            except Exception as e:
                # send error to FE
                errors.data.append('Error Reading Boundary Data')

                # log detailed error for devs
                print(f'Error Reading Supplemental Boundary Data: {e}', file=sys.stderr)
                break

        # when errors exist, add those to the form
        if errors:
            self.errors['boundary'] = errors

        return {
            'current_boundary': current_boundary,
            'new_boundary': new_boundary,
        }

    def validate_boundary(self):
        # remove previous errors
        if 'boundary' in self.errors:
            del self.errors['boundary']

        # store supplementary boundary data
        self.supplementary_boundary_data = self.read_supplementary_boundary_data()

    def is_valid(self):
        super().is_valid()
        self.validate_boundary()
        return self.is_bound and not self.errors

    def save_boundary(self):
        # update current boundary
        updated_boundary = self.supplementary_boundary_data.get('current_boundary')
        if updated_boundary and self.instance.boundary.id == int(updated_boundary['id']):
            self.instance.boundary.coordinates = updated_boundary['value']
            self.instance.boundary.save()
            return

        new_boundary = self.supplementary_boundary_data.get('new_boundary')
        self.instance.create_or_update_boundary(new_boundary)

    def save(self, commit=True):
        obj = super().save(commit=False)
        self.save_boundary()
        if commit:
            obj.save()
        return obj


class UpdateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = [
            'description', 'community_entity', 'city_town',
            'state_province_region', 'country', 'website', 'image'
        ]
        widgets = {
            'community_entity': forms.TextInput(attrs={'class': 'w-100'}),
            'state_province_region': forms.TextInput(attrs={'class': 'w-100'}),
            'city_town': forms.TextInput(attrs={'class': 'w-100'}),
            'website': forms.TextInput(attrs={'class': 'w-100'}),
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
  
    def __init__(self, *args, **kwargs):
        subscription = kwargs.pop('subscription', None)
        service_provider = kwargs.pop('service_provider', None)
        super().__init__(*args, **kwargs)
        if subscription is not None and subscription.users_count == 0:
            modified_choices = [
                ('viewer', 'Viewer'),
            ]
            self.fields['role'].choices = modified_choices

        if service_provider is not None:
            modified_choices = [
                ('editor', 'Editor'),
            ]
            self.fields['role'].choices = modified_choices

class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ['role', 'message']
        widgets = {
            'role': forms.Select(attrs={'class': 'w-100'}),
            'message': forms.Textarea(attrs={'rows': 3, 'class':'w-100', 'style': 'resize: vertical;'}),
        }
