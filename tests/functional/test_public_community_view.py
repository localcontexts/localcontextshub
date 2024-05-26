import urllib.parse

import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from factories.communities_factories import CommunityFactory
from factories.communities_factories import CommunityBoundaryFactory


@pytest.mark.usefixtures("py")
class TestFeatures(StaticLiveServerTestCase):
    def setUp(self):
        self.client = Client()
        self.community_with_boundary = CommunityFactory(
            boundary=CommunityBoundaryFactory(
                coordinates=[
                    [0, 0], [0, 1], [0, 2]
                ]
            ),
        )
        self.community_without_boundary = CommunityFactory()

    def test_non_existent_community_returns_404(self):
        non_existent_community_id = self.community_with_boundary.id + 1000
        kwargs = {
            'pk': non_existent_community_id,
        }
        response = self.client.get(reverse('public-community', kwargs=kwargs))
        self.assertEqual(response.status_code, 404)

    def test_public_community_ui_with_boundaries(self):
        kwargs = {
            'pk': self.community_with_boundary.id,
        }
        page_url = urllib.parse.urljoin(self.live_server_url, reverse('public-community', kwargs=kwargs))
        self.py.visit(page_url)
        # confirm boundary is present
        self.py.find("[data-testid='community-boundary-iframe']").should().not_be_empty()

    def test_public_community_ui_without_boundaries(self):
        kwargs = {
            'pk': self.community_without_boundary.id,
        }
        page_url = urllib.parse.urljoin(self.live_server_url, reverse('public-community', kwargs=kwargs))
        self.py.visit(page_url)
        # confirm boundary is not present
        self.py.find("[data-testid='community-boundary-iframe']").should().be_empty()
