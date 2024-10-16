from django.urls import reverse
from django.test import Client, TransactionTestCase
from factories.researchers_factories import ResearcherFactory
from factories.accounts_factories import UserFactory
from factories.projects_factories import ProjectFactory
from helpers.exceptions import UnsubscribedAccountException
from accounts.models import Subscription


class TestFeatures(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.subscribed_researcher = ResearcherFactory(user=UserFactory(), is_subscribed=True)
        self.subscription = Subscription.objects.create(
        researcher=self.subscribed_researcher,
        project_count=1,
        users_count=1,
        notification_count=1,
        api_key_count=1,
        subscription_type='large'
        )
        self.subscribed_researcher_project = ProjectFactory(project_creator=self.subscribed_researcher.user)
        self.unsubscribed_researcher = ResearcherFactory(user=UserFactory(), is_subscribed=False)
        self.unsubscribed_researcher_project = ProjectFactory(project_creator=self.unsubscribed_researcher.user)

    def test_download_otc_as_subscribed(self):
        self.client.force_login(user=self.subscribed_researcher.user)
        kwargs = {
            'perm': 1,
            'researcher_id': self.subscribed_researcher.id
        }
        response = self.client.get(reverse('download-open-to-collaborate-notice-researcher', kwargs=kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertIn('open-to-collaborate-notice', response.url)

    def test_download_otc_as_unsubscribed(self):
        self.client.force_login(user=self.unsubscribed_researcher.user)
        kwargs = {
            'perm': 1,
            'researcher_id': self.unsubscribed_researcher.id
        }
        response = self.client.get(reverse('download-open-to-collaborate-notice-researcher', kwargs=kwargs))
        self.assertEqual(response.status_code, 403)

    def test_create_project_as_unsubscribed(self):
        self.client.force_login(user=self.unsubscribed_researcher.user)
        kwargs = {
            'pk': self.unsubscribed_researcher.id,
        }
        response = self.client.get(reverse('researcher-create-project', kwargs=kwargs))
        self.assertEqual(response.status_code, 302)

    def test_create_project_as_subscribed(self):
        self.client.force_login(user=self.subscribed_researcher.user)
        kwargs = {
            'pk': self.subscribed_researcher.id,
        }
        response = self.client.get(reverse('researcher-create-project', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)

    def test_edit_project_as_unsubscribed(self):
        self.client.force_login(user=self.unsubscribed_researcher.user)
        kwargs = {
            'pk': self.unsubscribed_researcher.id,
        }
        response = self.client.get(reverse('researcher-create-project', kwargs=kwargs))
        self.assertEqual(response.status_code, 302)

    def test_edit_project_as_subscribed(self):
        self.client.force_login(user=self.subscribed_researcher.user)
        kwargs = {
            'pk': self.subscribed_researcher.id,
        }
        response = self.client.get(reverse('researcher-create-project', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
