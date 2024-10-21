import json
import sys

from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from django.forms.utils import ErrorList

from projects.widgets import BoundaryWidget
from .models import *
from django.utils.translation import gettext_lazy as _


class CreateProjectForm(forms.ModelForm):
    PRIVACY = (
        ('Public', 'Public: Project contributors and notified communities can interact with the Project. Anyone can access the Project with the Project URL, your page in the registry, or the Projects Board.'),
        ('Contributor', 'Contributor View: Project contributors and notified communities can interact with the Project. Anyone with the Project URL can view the Project ID and Labels/Notices.'),
        ('Private', 'Private: Only the Project creator can view the Project. This visibility changes to Contributor View if contributors are added, communities are notified, or Labels applied.'),
    )
    TYPES = (
        ('Item', 'Item'),
        ('Collection', 'Collection'),
        ('Samples', 'Samples'),
        ('Expedition', 'Expedition'),
        ('Publication', 'Publication'),
        ('Exhibition', 'Exhibition'),
        ('Other', 'Other'),
    )

    project_privacy = forms.ChoiceField(label=_('Who can view this project?'), choices=PRIVACY, initial='Public', widget=forms.RadioSelect(attrs={'class': 'ul-no-bullets ul-no-padding'}))
    project_type = forms.ChoiceField(label=_('What is your project type? *'), choices=TYPES, widget=forms.Select(attrs={'class': 'w-100',}))

    class Meta:
        model = Project
        fields = ['title', 'project_type', 'other_type', 'project_privacy', 'description', 'project_contact', 'project_contact_email', 'providers_id', 'publication_doi', 'project_data_guid']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-100'}),
            'other_type': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Specify other Project type'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'project_contact': forms.TextInput(attrs={'class': 'w-100'}),
            'project_contact_email': forms.TextInput(attrs={'class': 'w-100'}),
            'publication_doi': forms.TextInput(attrs={'class': 'w-100'}),
            'project_data_guid': forms.TextInput(attrs={'class': 'w-100'}),
            'providers_id': forms.TextInput(attrs={'class': 'w-100'}),
        }

# Create Project Person
ProjectPersonFormset = modelformset_factory(
    ProjectPerson,
    fields=('name', 'email' ),
    extra=1,
    widgets = {
        'name': forms.TextInput(attrs={'size': 35, 'placeholder': 'Contributor name'}),
        'email': forms.EmailInput(attrs={'size': 35, 'placeholder': 'Contributor email'}),
    },
    can_delete=True
)

# Edit Project Person
ProjectPersonFormsetInline = inlineformset_factory(
    Project, 
    ProjectPerson, 
    extra=1,
    fields=('name', 'email'),
    widgets = {
        'name': forms.TextInput(attrs={'size': 35, 'placeholder': 'Contributor name'}),
        'email': forms.EmailInput(attrs={'size': 35, 'placeholder': 'Contributor email'}),
    },
    can_delete=True,
)

class EditProjectForm(forms.ModelForm):
    PRIVACY = (
        ('Public', 'Public: Project contributors and notified communities can interact with the Project. Anyone can access the Project with the Project URL, your page in the registry, or the Projects Board.'),
        ('Contributor', 'Contributor View: Project contributors and notified communities can interact with the Project. Anyone with the Project URL can view the Project ID and Labels/Notices.'),
        ('Private', 'Private: Only the Project creator can view the Project. This visibility changes to Contributor View if contributors are added, communities are notified, or Labels applied.'),
    )
    TYPES = (
        ('Item', 'Item'),
        ('Collection', 'Collection'),
        ('Samples', 'Samples'),
        ('Expedition', 'Expedition'),
        ('Publication', 'Publication'),
        ('Exhibition', 'Exhibition'),
        ('Other', 'Other'),
    )
    project_privacy = forms.ChoiceField(label=_('Who can view this project?'), choices=PRIVACY, widget=forms.RadioSelect(attrs={'class': 'ul-no-bullets ul-no-padding'}))
    project_type = forms.ChoiceField(label=_('What is your project type? *'), choices=TYPES, widget=forms.Select(attrs={'class': 'w-100',}))

    class Meta:
        model = Project
        fields = ['title', 'project_type', 'other_type', 'project_privacy', 'description', 'project_contact', 'project_contact_email', 'publication_doi', 'project_data_guid', 'providers_id']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-100'}),
            'other_type': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Specify other Project type'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-100'}),
            'project_contact': forms.TextInput(attrs={'class': 'w-100'}),
            'project_contact_email': forms.TextInput(attrs={'class': 'w-100'}),
            'publication_doi': forms.TextInput(attrs={'class': 'w-100'}),
            'project_data_guid': forms.TextInput(attrs={'class': 'w-100'}),
            'providers_id': forms.TextInput(attrs={'class': 'w-100'}),
        }

class CreateProjectNoteForm(forms.ModelForm):
    class Meta:
        model = ProjectNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 1, 'class': 'w-100', 'placeholder': 'Add a note....'}),
        }


class ProjectModelForm(forms.ModelForm):
    class Meta:
        model = Boundary
        exclude = []
        max_coordinates_in_boundary_count = 3000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supplementary_boundary_data = None
        self.fields['boundary'].widget = BoundaryWidget(
            attrs={
                'project_id': self.instance.id,
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
            geometry = {
                'type': GEOJSON_MULTI_POLYGON_TYPE, 'coordinates': [
                    [updated_boundary['value']]
                ],
            }
            self.instance.boundary.geometry = geometry
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
