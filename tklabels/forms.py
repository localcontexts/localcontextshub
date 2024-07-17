from django import forms
from .models import *
from django.core.exceptions import ValidationError

class CustomizeTKLabelForm(forms.ModelForm):
    class Meta:
        model = TKLabel
        fields = ['name', 'language', 'label_text', 'audiofile']
        widgets = {
            'name': forms.TextInput(attrs={'id': 'label-template-name', 'class': 'w-100', 'autocomplete': 'off'}),
            'language': forms.TextInput(attrs={'class': 'languageListInput w-100', 'placeholder': 'English', 'autocomplete': 'off'}),
            'label_text': forms.Textarea(attrs={'class': 'w-100 mt-1p mb-2p', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
            'audiofile': forms.ClearableFileInput(attrs={'class': 'w-100 hide', 'id': 'originalLabelAudioUploadBtn', 'onchange': 'showAudioFileName()'}),
        }

    def clean(self):
        super(CustomizeTKLabelForm, self).clean()
        label_text =  self.cleaned_data.get('label_text')

        if label_text == '':
            self._errors['label_text'] = self.error_class(['Label text must not be empty.'])

    def clean_audiofile(self):
        audiofile = self.cleaned_data.get('audiofile')
        if audiofile:
            allowed_extensions = ['.mp3', '.wav', '.ogg', '.aac', '.flac', '.wma', '.m4a', '.opus', '.aiff', '.aif']
            file_ext = os.path.splitext(audiofile.name)[1].lower()

            if file_ext not in allowed_extensions:
                raise ValidationError('Invalid audio file extension. Only MP3, WAV, FLAC, WMA, M4A, etc. files are allowed.')
            
            allowed_mime_types = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/aac', 'audio/flac', 'audio/x-ms-wma', 'audio/mp4', 'audio/opus', 'audio/aiff']
            if audiofile.content_type not in allowed_mime_types:
                raise ValidationError('Invalid audio file type. Only MP3, WAV, FLAC, WMA, M4A, etc. files are allowed.')
        return audiofile

class EditTKLabelForm(forms.ModelForm):
    class Meta:
        model = TKLabel
        fields = ['name', 'language', 'label_text', 'audiofile']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-100', 'autocomplete': 'off'}),
            'language': forms.TextInput(attrs={'class': 'languageListInput w-100', 'placeholder': 'Search for language...', 'autocomplete': 'off'}),
            'label_text': forms.Textarea(attrs={'class': 'w-100 mt-1p mb-2p', 'id': 'label-template-text', 'style': 'height: 150px; padding: 10px;'}),
            'audiofile': forms.ClearableFileInput(attrs={'class': 'w-100 hide', 'id': 'originalLabelAudioUploadBtn', 'onchange': 'showAudioFileName()'}),
        }