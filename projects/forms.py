from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from .models import Project, ProjectNote, ProjectPerson
from django.utils.translation import ugettext_lazy as _


class CreateProjectForm(forms.ModelForm):
    PRIVACY = (
        ('Public',
         'Public: Project contributors and notified communities can interact with the Project. Anyone can access the Project with the Project URL, your page in the registry, or the Projects Board.'
         ),
        ('Contributor',
         'Contributor View: Project contributors and notified communities can interact with the Project. Anyone with the Project URL can view the Project ID and Labels/Notices.'
         ),
        ('Private',
         'Private: Only the Project creator can view the Project. This visibility changes to Contributor View if contributors are added, communities are notified, or Labels applied.'
         ),
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

    project_privacy = forms.ChoiceField(
        label=_('Who can view this project?'),
        choices=PRIVACY,
        initial='Public',
        widget=forms.RadioSelect(
            attrs={'class': 'ul-no-bullets ul-no-padding'}))
    project_type = forms.ChoiceField(label=_('What is your project type? *'),
                                     choices=TYPES,
                                     widget=forms.Select(attrs={
                                         'class': 'w-100',
                                     }))

    class Meta:
        model = Project
        fields = [
            'title', 'project_type', 'other_type', 'project_privacy',
            'description', 'project_contact', 'project_contact_email',
            'providers_id', 'publication_doi', 'project_data_guid'
        ]
        widgets = {
            'title':
            forms.TextInput(attrs={'class': 'w-100'}),
            'other_type':
            forms.TextInput(attrs={
                'class': 'w-100',
                'placeholder': 'Specify other Project type'
            }),
            'description':
            forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-100'
            }),
            'project_contact':
            forms.TextInput(attrs={'class': 'w-100'}),
            'project_contact_email':
            forms.TextInput(attrs={'class': 'w-100'}),
            'publication_doi':
            forms.TextInput(attrs={'class': 'w-100'}),
            'project_data_guid':
            forms.TextInput(attrs={'class': 'w-100'}),
            'providers_id':
            forms.TextInput(attrs={'class': 'w-100'}),
        }


# Create Project Person
ProjectPersonFormset = modelformset_factory(
    ProjectPerson,
    fields=('name', 'email'),
    extra=1,
    widgets={
        'name':
        forms.TextInput(attrs={
            'size': 35,
            'placeholder': 'Contributor name'
        }),
        'email':
        forms.EmailInput(attrs={
            'size': 35,
            'placeholder': 'Contributor email'
        }),
    },
    can_delete=True)

# Edit Project Person
ProjectPersonFormsetInline = inlineformset_factory(
    Project,
    ProjectPerson,
    extra=1,
    fields=('name', 'email'),
    widgets={
        'name':
        forms.TextInput(attrs={
            'size': 35,
            'placeholder': 'Contributor name'
        }),
        'email':
        forms.EmailInput(attrs={
            'size': 35,
            'placeholder': 'Contributor email'
        }),
    },
    can_delete=True,
)


class EditProjectForm(forms.ModelForm):
    PRIVACY = (
        ('Public',
         'Public: Project contributors and notified communities can interact with the Project. Anyone can access the Project with the Project URL, your page in the registry, or the Projects Board.'
         ),
        ('Contributor',
         'Contributor View: Project contributors and notified communities can interact with the Project. Anyone with the Project URL can view the Project ID and Labels/Notices.'
         ),
        ('Private',
         'Private: Only the Project creator can view the Project. This visibility changes to Contributor View if contributors are added, communities are notified, or Labels applied.'
         ),
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
    project_privacy = forms.ChoiceField(
        label=_('Who can view this project?'),
        choices=PRIVACY,
        widget=forms.RadioSelect(
            attrs={'class': 'ul-no-bullets ul-no-padding'}))
    project_type = forms.ChoiceField(label=_('What is your project type? *'),
                                     choices=TYPES,
                                     widget=forms.Select(attrs={
                                         'class': 'w-100',
                                     }))

    class Meta:
        model = Project
        fields = [
            'title', 'project_type', 'other_type', 'project_privacy',
            'description', 'project_contact', 'project_contact_email',
            'publication_doi', 'project_data_guid', 'providers_id'
        ]
        widgets = {
            'title':
            forms.TextInput(attrs={'class': 'w-100'}),
            'other_type':
            forms.TextInput(attrs={
                'class': 'w-100',
                'placeholder': 'Specify other Project type'
            }),
            'description':
            forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-100'
            }),
            'project_contact':
            forms.TextInput(attrs={'class': 'w-100'}),
            'project_contact_email':
            forms.TextInput(attrs={'class': 'w-100'}),
            'publication_doi':
            forms.TextInput(attrs={'class': 'w-100'}),
            'project_data_guid':
            forms.TextInput(attrs={'class': 'w-100'}),
            'providers_id':
            forms.TextInput(attrs={'class': 'w-100'}),
        }


class CreateProjectNoteForm(forms.ModelForm):

    class Meta:
        model = ProjectNote
        fields = ['note']
        widgets = {
            'note':
            forms.Textarea(attrs={
                'rows': 1,
                'class': 'w-100',
                'placeholder': 'Add a note....'
            }),
        }
