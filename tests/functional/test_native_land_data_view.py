import requests
from unittest.mock import patch

from django.urls import reverse
from django.core.cache import cache
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

        # clear cache since view function modifies the cache
        cache.clear()

    def test_error_raised_when_slug_is_not_defined_in_get_request(self):
        """
        When the get request does not contain a slug, it should raise an error.
        """
        expected_message = 'Slug Variable Is Not Defined In Request'
        response = self.client.get(
            reverse('nld-data')
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context['exception'], expected_message)

    def test_error_raised_when_slug_is_not_in_all_nld_data(self):
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

    def test_error_raised_when_error_occurs_retrieving_all_nld_data(self):
        """
        When the retrieve_native_land_all_slug_data fails
        an error should be raised.
        """
        slug = 'placeholder_slug'
        expected_message = f'Unable to Retrieve All NLD Slug Data'
        get_variables = {
            'slug': slug,
        }
        with patch('helpers.views.retrieve_native_land_all_slug_data') as mock_function:
            mock_function.side_effect = requests.exceptions.HTTPError('Some Error Occurred')
            response = self.client.get(
                reverse('nld-data'),
                data=get_variables
            )
            self.assertEqual(response.context['exception'], expected_message)

    def test_no_error_raised_when_getting_data_for_slug(self):
        """
        No error is raised when getting data for slug
        """
        slug = 'placeholder_slug'
        get_variables = {
            'slug': slug,
        }
        with patch('helpers.views.retrieve_native_land_all_slug_data') as mock_function:
            specific_slug_data = {'foo': 'bar'}
            mock_function.return_value = {
                slug: specific_slug_data
            }
            response = self.client.get(
                reverse('nld-data'),
                data=get_variables
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), specific_slug_data)
