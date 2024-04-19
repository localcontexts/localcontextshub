from unittest.mock import patch

from django.test import TransactionTestCase
from factories.accounts_factories import UserFactory
from factories.researchers_factories import ResearcherFactory
from factories.communities_factories import CommunityFactory
from factories.institutions_factories import InstitutionFactory

from accounts.signals import get_log_data


class TestLogDeletedUser(TransactionTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.researcher = ResearcherFactory(user=self.user)
        self.communities = [
            CommunityFactory(community_creator=self.user),
            CommunityFactory(community_creator=self.user),
            CommunityFactory(community_creator=self.user),
        ]
        self.institutions = [
            InstitutionFactory(institution_creator=self.user),
            InstitutionFactory(institution_creator=self.user),
            InstitutionFactory(institution_creator=self.user),
        ]

    def test_log_deleted_user(self):
        with patch('accounts.signals.get_log_data_timestamp') as timestamp_mock:
            timestamp_mock.return_value = 'time-place_holder'

            with patch('pprint.pprint') as pprint_mock:
                expected_log_data = get_log_data(self.user)
                expected_log_data['UTC-TIME'] = 'time-place_holder'
                self.user.delete()
                pprint_mock.assert_called_with(expected_log_data)
