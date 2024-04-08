from django.urls import reverse
from django.test import Client, TransactionTestCase
from factories.researchers_factories import ResearcherFactory
from factories.accounts_factories import UserFactory

from helpers.exceptions import UnsubscribedAccountException


class TestCalls(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.subscribed_researcher = ResearcherFactory(user=UserFactory(), is_subscribed=True)
        self.unsubscribed_researcher = ResearcherFactory(user=UserFactory(), is_subscribed=False)

    def test_download_otc_as_unsubscribed(self):
        self.client.force_login(user=self.unsubscribed_researcher.user)
        kwargs = {
            'perm': 1,
            'researcher_id': self.unsubscribed_researcher.id
        }
        with self.assertRaises(UnsubscribedAccountException):
            self.client.get(reverse('download-open-to-collaborate-notice-researcher', kwargs=kwargs))

    def test_download_otc_as_subscribed(self):
        self.client.force_login(user=self.subscribed_researcher.user)
        kwargs = {
            'perm': 1,
            'researcher_id': self.subscribed_researcher.id
        }
        response = self.client.get(reverse('download-open-to-collaborate-notice-researcher', kwargs=kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertIn('open-to-collaborate-notice', response.url)
