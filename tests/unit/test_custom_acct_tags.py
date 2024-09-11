from django.test import TransactionTestCase
from factories.accounts_factories import UserFactory
from factories.communities_factories import CommunityFactory
from factories.projects_factories import ProjectCreatorFactory
from factories.projects_factories import ProjectFactory

from accounts.templatetags.custom_acct_tags import user_created_project_in_community


class TestCustomAccountTags(TransactionTestCase):
    def test_user_created_project_in_community(self):
        # create user and communities
        user = UserFactory()
        community_with_project = CommunityFactory()
        community_without_project = CommunityFactory()

        # create project for the community_with_project
        project = ProjectFactory(
            project_creator=user
        )
        ProjectCreatorFactory(
            community=community_with_project,
            project=project
        )

        assert user_created_project_in_community(
            user_id=user.id,
            community_id=community_with_project.id
        ) is True

        assert user_created_project_in_community(
            user_id=user.id,
            community_id=community_without_project.id
        ) is False
