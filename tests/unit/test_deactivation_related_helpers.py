from django.test import TransactionTestCase
from factories.accounts_factories import UserFactory
from factories.communities_factories import CommunityFactory
from factories.institutions_factories import InstitutionFactory
from factories.researchers_factories import ResearcherFactory
from factories.projects_factories import ProjectCreatorFactory
from factories.projects_factories import ProjectFactory

from accounts.models import UserAffiliation
from accounts.templatetags.custom_acct_tags import (
    user_created_project_in_community,
    user_created_project_in_institution, 
    user_created_project_as_researcher
)
from accounts.utils import remove_user_from_account


class TestDeactivationRelatedHelpers(TransactionTestCase):
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

    def test_user_created_project_in_institution(self):
        # create user and institutions
        user = UserFactory()
        institution_with_project = InstitutionFactory()
        institution_without_project = InstitutionFactory()

        # create project for the institution_with_project
        project = ProjectFactory(
            project_creator=user
        )
        ProjectCreatorFactory(
            institution=institution_with_project,
            project=project
        )

        assert user_created_project_in_institution(
            user_id=user.id,
            institution_id=institution_with_project.id
        ) is True

        assert user_created_project_in_institution(
            user_id=user.id,
            institution_id=institution_without_project.id
        ) is False

    def test_researcher_created_project(self):
        # create user and researcher
        user = UserFactory()
        researcher_with_project = ResearcherFactory()
        researcher_without_project = ResearcherFactory()

        # create project for the researcher_with_project
        project = ProjectFactory(
            project_creator=user
        )
        ProjectCreatorFactory(
            researcher=researcher_with_project,
            project=project
        )

        assert user_created_project_as_researcher(
            user_id=user.id,
            researcher_id=researcher_with_project.id
        ) is True

        assert user_created_project_as_researcher(
            user_id=user.id,
            researcher_id=researcher_without_project.id
        ) is False

    def test_remove_admin_user_from_community(self):
        admin_user = UserFactory()
        community = CommunityFactory()
        community.admins.add(admin_user)
        affiliation = UserAffiliation.objects.prefetch_related(
            'communities'
        ).get(user=admin_user)
        affiliation.communities.add(community)

        # verify admin_user is an admin
        assert community.admins.contains(admin_user) is True
        # verify community is in affiliation.communities
        assert affiliation.communities.contains(community) is True

        remove_user_from_account(
            user=admin_user,
            account=community
        )

        # verify admin_user is no longer an admin
        assert community.admins.contains(admin_user) is False
        # verify community is no longer in affiliation.communities
        assert affiliation.communities.contains(community) is False

    def test_remove_editor_user_from_community(self):
        editor_user = UserFactory()
        community = CommunityFactory()
        community.editors.add(editor_user)
        affiliation = UserAffiliation.objects.prefetch_related(
            'communities'
        ).get(user=editor_user)
        affiliation.communities.add(community)

        # verify editor_user is an editor
        assert community.editors.contains(editor_user) is True
        # verify community is in affiliation.communities
        assert affiliation.communities.contains(community) is True

        remove_user_from_account(
            user=editor_user,
            account=community
        )

        # verify editor_user is no longer an editor
        assert community.editors.contains(editor_user) is False
        # verify community is no longer in affiliation.communities
        assert affiliation.communities.contains(community) is False

    def test_remove_viewer_user_from_community(self):
        viewer_user = UserFactory()
        community = CommunityFactory()
        community.viewers.add(viewer_user)
        affiliation = UserAffiliation.objects.prefetch_related(
            'communities'
        ).get(user=viewer_user)
        affiliation.communities.add(community)

        # verify viewer_user is a viewer
        assert community.viewers.contains(viewer_user) is True
        # verify community is in affiliation.communities
        assert affiliation.communities.contains(community) is True

        remove_user_from_account(
            user=viewer_user,
            account=community
        )

        # verify viewer_user is no longer a viewer
        assert community.viewers.contains(viewer_user) is False
        # verify community is no longer in affiliation.communities
        assert affiliation.communities.contains(community) is False
