import pytest
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from factories.bclabels_factories import BCLabelFactory


class TestBCLabels(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.new_bclabel = BCLabelFactory()

    def test_bclabel_str_method(self):
        bclabel = self.new_bclabel
        string = str(bclabel)
        assert isinstance(string, str)
        assert string == f"{bclabel.community} - {bclabel.name}"

    def test_bclabel_save_method(self):
        bclabel = self.new_bclabel
        # This code mocks the external requests.get method to avoid making actual requests
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'English': 'en'}
            bclabel.save()
        assert bclabel.language_tag is not None
        assert bclabel.img_url is not None
        assert bclabel.svg_url is not None

    def test_bclabel_audiofile_upload(self):
        audio_file = SimpleUploadedFile("test_audio.mp3",
                                        b"file_content",
                                        content_type="audio/mp3")
        self.new_bclabel.audiofile = audio_file
        self.new_bclabel.save()
        assert self.new_bclabel.audiofile.url is not None
