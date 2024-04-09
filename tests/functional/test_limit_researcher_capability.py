from django.urls import reverse
from django.test import Client, TransactionTestCase
from factories.researchers_factories import ResearcherFactory
from factories.accounts_factories import UserFactory
from factories.projects_factories import ProjectFactory

from helpers.exceptions import UnsubscribedAccountException


class TestDownloadOTC(TransactionTestCase):
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


class TestViewProject(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.subscribed_researcher = ResearcherFactory(user=UserFactory(), is_subscribed=True)
        self.subscribed_researcher_project = ProjectFactory(project_creator=self.subscribed_researcher.user)
        self.unsubscribed_researcher = ResearcherFactory(user=UserFactory(), is_subscribed=False)
        self.unsubscribed_researcher_project = ProjectFactory(project_creator=self.unsubscribed_researcher.user)

    def test_view_project_as_unsubscribed(self):
        self.client.force_login(user=self.unsubscribed_researcher.user)
        kwargs = {
            'unique_id': self.unsubscribed_researcher_project.unique_id,
        }
        response = self.client.get(reverse('view-project', kwargs=kwargs))

        expected_download_restricted_message = 'The account that created this Project needs ' \
                                               'to be subscribed before download is available.'
        self.assertEqual(response.context['can_download'], False)
        self.assertEqual(response.context['download_restricted_message'], expected_download_restricted_message)

    def test_view_project_as_subscribed(self):
        self.client.force_login(user=self.subscribed_researcher.user)
        kwargs = {
            'unique_id': self.subscribed_researcher_project.unique_id,
        }
        response = self.client.get(reverse('view-project', kwargs=kwargs))
        self.assertEqual(response.context['can_download'], True)


class TestCreateProject(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.subscribed_researcher = ResearcherFactory(user=UserFactory(), is_subscribed=True)
        self.subscribed_researcher_project = ProjectFactory(project_creator=self.subscribed_researcher.user)
        self.unsubscribed_researcher = ResearcherFactory(user=UserFactory(), is_subscribed=False)
        self.unsubscribed_researcher_project = ProjectFactory(project_creator=self.unsubscribed_researcher.user)

    def test_create_project_as_unsubscribed(self):
        self.client.force_login(user=self.unsubscribed_researcher.user)
        kwargs = {
            'pk': self.unsubscribed_researcher_project.id,
        }
        with self.assertRaises(UnsubscribedAccountException):
            self.client.get(reverse('researcher-create-project', kwargs=kwargs))

    def test_create_project_as_subscribed(self):
        self.client.force_login(user=self.subscribed_researcher.user)
        kwargs = {
            'pk': self.subscribed_researcher_project.id,
        }
        response = self.client.get(reverse('researcher-create-project', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
