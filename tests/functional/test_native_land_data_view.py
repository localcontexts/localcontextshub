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

    def test_slug_does_not_exist_returns_404(self):
        kwargs = {}
        expected_message = 'Slug Variable Is Not Defined In Request'
        response = self.client.get(reverse('nld-data', kwargs=kwargs))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context['exception'], expected_message)
