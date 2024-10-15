from unittest.mock import patch
from django.test import TestCase

from helpers.utils import retrieve_native_land_all_slug_data


class TestUtils(TestCase):

    def test_retrieve_native_land_all_slug_data(self):
        with patch('requests.get') as mock_get:
            retrieve_native_land_all_slug_data()
            url = (
                'https://raw.githubusercontent.com/biocodellc/'
                'localcontexts_json/refs/heads/main/data/'
                'nativeland_slug_coordinates_description_dict.json'
            )
            mock_get.assert_called_with(url)
