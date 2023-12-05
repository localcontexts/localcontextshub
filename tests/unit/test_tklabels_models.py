import pytest
import requests
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from factories.tklabels_factories import TKLabelFactory


# Fixture for TKLabel model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_tklabel():
    return TKLabelFactory()

# Test for TKLabel model __str__ method
@pytest.mark.django_db
def test_tklabel_str_method(new_tklabel):
    tklabel = new_tklabel
    result = str(new_tklabel)
    assert isinstance(result, str)

# Test for TKLabel model save method
@pytest.mark.django_db
def test_tklabel_save_method(new_tklabel):
    tklabel = new_tklabel
    # Mock the external requests.get method to avoid making actual requests
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'English': 'en'}
        new_tklabel.save()
    assert tklabel.language_tag is not None
    assert tklabel.img_url is not None
    assert tklabel.svg_url is not None

# Test for TKLabel model audiofile upload
@pytest.mark.django_db
def test_tklabel_audiofile_upload(new_tklabel):
    audio_file = SimpleUploadedFile("test_audio.mp3", b"file_content", content_type="audio/mp3")
    new_tklabel.audiofile = audio_file
    new_tklabel.save()
    assert new_tklabel.audiofile.url is not None