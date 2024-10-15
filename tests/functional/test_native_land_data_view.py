from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client, TransactionTestCase


class TestFeatures(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        username = 'user'
        pw = 'pw'
        self.user = User.objects.create_user(
            username=username,
            password=pw
        )
        logged_in = self.client.login(
            username=username,
            password=pw
        )
        self.assertTrue(logged_in, 'Login failed')

    def test_error_raised_when_slug_is_not_defined_in_get_request(self):
        """
        When the get request does not contain a slug, it should raise an error.
        """
        expected_message = 'Slug Variable Is Not Defined In Request'
        response = self.client.get(
            reverse('nld-data', {})
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context['exception'], expected_message)

    def test_error_raised_when_slug_is_not_in_nld_data(self):
        """
        When the retrieve_native_land_all_slug_data returns an empty dictionary
        which does not contain the slug, an error should be raised.
        """
        slug = 'placeholder_slug'
        expected_message = f'Unable to Retrieve Specific NLD Slug Data for {slug}'
        get_variables = {
            'slug': slug,
        }
        with patch('helpers.views.retrieve_native_land_all_slug_data') as mock_function:
            mock_function.return_value = {}
            response = self.client.get(
                reverse('nld-data'),
                data=get_variables
            )
            self.assertEqual(response.context['exception'], expected_message)
