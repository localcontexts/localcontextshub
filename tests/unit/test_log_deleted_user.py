from unittest.mock import patch

import pytest
from django.test import TransactionTestCase
from factories.accounts_factories import UserFactory
from factories.researchers_factories import ResearcherFactory
from factories.communities_factories import CommunityFactory
from factories.institutions_factories import InstitutionFactory
from factories.bclabels_factories import BCLabelFactory
from factories.tklabels_factories import TKLabelFactory

from helpers.logging import get_log_data


class TestLogDeletedUser(TransactionTestCase):

    @pytest.mark.django_db
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
        self.bclabels = [
            BCLabelFactory(created_by=self.user),
            BCLabelFactory(created_by=self.user),
            BCLabelFactory(created_by=self.user),
        ]
        self.tklabels = [
            TKLabelFactory(created_by=self.user),
            TKLabelFactory(created_by=self.user),
            TKLabelFactory(created_by=self.user),
        ]

    def test_log_deleted_user(self):
        with patch('helpers.logging.get_current_timestamp') as timestamp_mock:
            timestamp_mock.return_value = 'time-place_holder'

            with patch('pprint.pprint') as pprint_mock:
                expected_log_data = get_log_data(self.user)
                expected_log_data['UTC-TIME'] = 'time-place_holder'
                self.user.delete()
                pprint_mock.assert_called_with(expected_log_data)
