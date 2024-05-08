from django.urls import reverse
from django.test import Client, TransactionTestCase
from factories.communities_factories import CommunityFactory
from factories.communities_factories import CommunityBoundaryFactory


class TestFeatures(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.community_without_boundary = CommunityFactory()
        self.community_with_boundary = CommunityFactory(
            boundary=CommunityBoundaryFactory(
                coordinates=[
                    [0, 0], [0, 1], [0, 2]
                ]
            )
        )

    def test_non_existent_community_returns_404(self):
        non_existent_community_id = self.community_with_boundary.id + 1000
        kwargs = {
            'community_id': non_existent_community_id,
        }
        response = self.client.get(reverse('community-boundary-view', kwargs=kwargs))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context.get('exception'), 'Community Does Not Exist')

    def test_community_with_boundaries(self):
        kwargs = {
            'community_id': self.community_with_boundary.id,
        }
        response = self.client.get(reverse('community-boundary-view', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('boundary'), self.community_with_boundary.boundary.coordinates)
