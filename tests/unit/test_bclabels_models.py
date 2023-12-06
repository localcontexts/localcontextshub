import pytest
import requests
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from factories.bclabels_factories import BCLabelFactory

# Fixture for BCLabel model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_bclabel():
    return BCLabelFactory()

# Test for BCLabel model __str__ method
@pytest.mark.django_db
def test_bclabel_str_method(new_bclabel):
    bclabel = new_bclabel
    string = str(bclabel)
    assert isinstance(string, str)
    assert string ==  f"{bclabel.community} - {bclabel.name}"

# Test for BCLabel model post creation save method
@pytest.mark.django_db
def test_bclabel_save_method(new_bclabel):
    bclabel = new_bclabel
    #This code mocks the external requests.get method to avoid making actual requests
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'English': 'en'}
        bclabel.save()
    assert bclabel.language_tag is not None
    assert bclabel.img_url is not None
    assert bclabel.svg_url is not None

# Test for BCLabel model audiofile upload
@pytest.mark.django_db
def test_bclabel_audiofile_upload(new_bclabel):
    audio_file = SimpleUploadedFile("test_audio.mp3", b"file_content", content_type="audio/mp3")
    new_bclabel.audiofile = audio_file
    new_bclabel.save()
    assert new_bclabel.audiofile.url is not None