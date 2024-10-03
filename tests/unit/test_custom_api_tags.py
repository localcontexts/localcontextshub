import os
from unittest.mock import patch

from django.test import TransactionTestCase
from api.templatetags.custom_api_tags import external_api


class TestCustomApiTags(TransactionTestCase):
    def test_external_api_when_test_live_server_does_not_exist(self):
        external_url = 'scheme://netloc/path;parameters?query#fragment'

        with patch('os.environ.get') as mock_get:
            mock_get.return_value = None
            output_url = external_api(external_url)

        self.assertEqual(external_url, output_url)

    def test_external_api_when_test_live_server_exists(self):
        external_url = 'scheme://netloc/path;parameters?query#fragment'
        os.environ['TEST_LIVE_SERVER_DOMAIN'] = 'https://example.com'
        expected_url = 'https://example.com/path;parameters'

        output_url = external_api(external_url)
        self.assertEqual(expected_url, output_url)

    def test_external_api_when_test_live_server_exists_and_there_is_an_error(self):
        """
        When an error occurs, the external_url is used. And an error will occur b/c
        the test_live_server_domain is not a string value.
        """
        external_url = 'scheme://netloc/path;parameters?query#fragment'

        with patch('os.environ.get') as mock_get:
            mock_get.return_value = -1
            output_url = external_api(external_url)

        self.assertEqual(external_url, output_url)
