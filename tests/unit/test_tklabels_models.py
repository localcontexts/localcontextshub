import pytest
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from factories.tklabels_factories import TKLabelFactory


class TestTKLabel(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.tklabel = TKLabelFactory()

    def test_tklabel_str_method(self):
        string = str(self.tklabel)
        assert isinstance(string, str)
        assert string == f"{self.tklabel.community} - {self.tklabel.name}"

    def test_tklabel_save_method(self):
        # Mock the external requests.get method to avoid making actual requests
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'English': 'en'}
            self.tklabel.save()
        assert self.tklabel.language_tag is not None
        assert self.tklabel.img_url is not None
        assert self.tklabel.svg_url is not None

    def test_tklabel_audiofile_upload(self):
        audio_file = SimpleUploadedFile("test_audio.mp3",
                                        b"file_content",
                                        content_type="audio/mp3")
        self.tklabel.audiofile = audio_file
        self.tklabel.save()
        assert self.tklabel.audiofile.url is not None
