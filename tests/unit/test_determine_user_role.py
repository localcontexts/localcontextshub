from django.test import TransactionTestCase
from factories.accounts_factories import UserFactory
from factories.researchers_factories import ResearcherFactory
from factories.communities_factories import CommunityFactory
from factories.institutions_factories import InstitutionFactory

from helpers.views import determine_user_role


class TestDetermineUserRole(TransactionTestCase):
    def test_creator_user(self):
        # create creator users
        researcher_creator_user = UserFactory()
        community_creator_user = UserFactory()
        institution_creator_user = UserFactory()

        # create accounts with creator users
        ResearcherFactory(user=researcher_creator_user)
        CommunityFactory(community_creator=community_creator_user)
        InstitutionFactory(institution_creator=institution_creator_user)

        assert determine_user_role(user=researcher_creator_user) == 'is_creator'
        assert determine_user_role(user=community_creator_user) == 'is_creator'
        assert determine_user_role(user=institution_creator_user) == 'is_creator'

    def test_community_member_user(self):
        # create community member users
        community_admin_member_user = UserFactory()
        community_editor_member_user = UserFactory()
        community_viewer_member_user = UserFactory()

        # create community accounts with member users
        CommunityFactory().admins.add(community_admin_member_user)
        CommunityFactory().editors.add(community_editor_member_user)
        CommunityFactory().viewers.add(community_viewer_member_user)

        assert determine_user_role(user=community_admin_member_user) == 'is_member'
        assert determine_user_role(user=community_editor_member_user) == 'is_member'
        assert determine_user_role(user=community_viewer_member_user) == 'is_member'

    def test_institution_member_user(self):
        # create institution member users
        institution_admin_member_user = UserFactory()
        institution_editor_member_user = UserFactory()
        institution_viewer_member_user = UserFactory()

        # create institution accounts with member users
        InstitutionFactory().admins.add(institution_admin_member_user)
        InstitutionFactory().editors.add(institution_editor_member_user)
        InstitutionFactory().viewers.add(institution_viewer_member_user)

        assert determine_user_role(user=institution_admin_member_user) == 'is_member'
        assert determine_user_role(user=institution_editor_member_user) == 'is_member'
        assert determine_user_role(user=institution_viewer_member_user) == 'is_member'

    def test_non_admin_and_non_member_user(self):
        non_admin_and_non_member_user = UserFactory()
        assert determine_user_role(user=non_admin_and_non_member_user) == 'default'
