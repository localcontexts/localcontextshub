import pytest
from django.test import TestCase
from django.contrib.auth.models import User

from helpers.exceptions import UnconfirmedAccountException
from projects.models import ProjectContributors

from factories.accounts_factories import UserFactory
from factories.institutions_factories import InstitutionFactory
from factories.communities_factories import CommunityFactory
from factories.researchers_factories import ResearcherFactory
from factories.projects_factories import ProjectFactory, ProjectPersonFactory, ProjectNoteFactory, ProjectContributorsFactory, ProjectCreatorFactory, ProjectActivityFactory


class TestProject(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.project = ProjectFactory()
        self.user = UserFactory()

    def test_project_has_labels(self):
        assert self.project.has_labels()
        assert self.project.has_bclabels()
        assert self.project.has_tklabels()

    def test_project_can_user_access(self):
        assert isinstance(self.project.can_user_access(self.user), bool)

    def test_get_template_name_public_privacy(self):
        self.project.project_privacy = "Public"
        self.project.save()
        assert self.project.get_template_name(self.user) == "partials/_project-actions.html"

    def test_get_template_name_contributor_privacy(self):
        self.project.project_privacy = "Contributor"
        self.project.save()
        assert self.project.get_template_name(self.user) == "partials/_project-actions.html"

    def test_get_template_name_private_and_unexpected_privacy(self):
        another_user = UserFactory()
        self.project.project_privacy = "Private"
        self.user = self.project.project_creator
        self.project.save()
        assert self.project.get_template_name(self.user) == "partials/_project-actions.html"

        self.project.project_privacy = "SomethingElse"
        self.project.save()
        assert self.project.get_template_name(self.user) is None

    def test_str_method(self):
        string = str(self.project)
        assert isinstance(string, str)
        assert string == self.project.title


class TestProjectPerson(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.project_person = ProjectPersonFactory()

    def test_project_person_str_method(self):
        new_project_person = self.project_person
        string = new_project_person.__str__()
        assert isinstance(new_project_person.__str__(), str)


@pytest.fixture
@pytest.mark.django_db
def new_project_contributor():
    assert isinstance(ProjectContributorsFactory().__str__(), str)
    return ProjectContributorsFactory()


@pytest.mark.django_db
def test_is_user_contributor():
    user = UserFactory()

    project = ProjectFactory()
    institution = InstitutionFactory()
    community = CommunityFactory()
    researcher = ResearcherFactory()

    # Checking if a ProjectContributors instance exists for the project
    existing_contributor = ProjectContributors.objects.filter(project=project).first()

    if not existing_contributor:
        ProjectContributors.objects.create(project=project)

    project_contributors = ProjectContributors.objects.create()
    project_contributors.communities.add(community)
    project_contributors.institutions.add(institution)
    project_contributors.researchers.add(researcher)
    
    assert project_contributors.is_user_contributor(user) is False 
    assert not project_contributors.is_user_contributor(User.objects.create_user(username='another_user', password='another_password'))
    assert not project_contributors.is_user_contributor(User.objects.create_user(username='yet_another_user', password='yet_another_password'))


class TestProjectCreator(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.project_creator = ProjectCreatorFactory()
        self.user = UserFactory()
        self.community = CommunityFactory()
        self.institution = InstitutionFactory()
        self.researcher = ResearcherFactory()

        # Assign creator account to the project creator
        self.project_creator.community_creator = self.community
        self.project_creator.institution_creator = self.institution
        self.project_creator.researcher_creator = self.researcher

        # for unconfirmed account
        self.unconfirmed_account_user = UserFactory()
        self.project_creator_of_unconfirmed_account = ProjectCreatorFactory()
        self.project_creator_of_unconfirmed_account.community.is_approved = False
        self.project_creator_of_unconfirmed_account.community.community_creator = self.unconfirmed_account_user

        # for confirmed account
        self.confirmed_account_user = UserFactory()
        self.project_creator_of_confirmed_account = ProjectCreatorFactory()
        self.project_creator_of_confirmed_account.community.is_approved = True
        self.project_creator_of_confirmed_account.community.community_creator = self.confirmed_account_user

    def test_which_account_type_created_community(self):
        is_created_by = self.project_creator.which_account_type_created()
        assert is_created_by['community'] is True
        is_user_in_account = self.project_creator.is_user_in_creator_account(self.user, is_created_by)
        assert is_user_in_account is False

    def test_which_account_type_created_institution(self):
        # Set expected account type
        is_created_by = self.project_creator.which_account_type_created()
        assert is_created_by['community'] is True
        is_user_in_account = self.project_creator.is_user_in_creator_account(self.user, is_created_by)
        assert is_user_in_account is False

    def test_which_account_type_created_researcher(self):
        # Set expected account type
        is_created_by = self.project_creator.which_account_type_created()
        assert is_created_by['community'] is True
        is_user_in_account = self.project_creator.is_user_in_creator_account(self.user, is_created_by)
        assert is_user_in_account is False
        
    def test_project_creator_str_method(self):
        project_creator = self.project_creator
        assert isinstance(project_creator.__str__(), str)

    def test_user_of_unconfirmed_account_can_see_project(self):
        # confirmed error is not raised
        try:
            user_of_unconfirmed_account = self.unconfirmed_account_user
            self.project_creator_of_unconfirmed_account.validate_user_access(
                user_of_unconfirmed_account
            )
        except UnconfirmedAccountException:
            raise Exception('Error: user of unconfirmed account cannot see own project')

    def test_user_of_confirmed_account_can_see_project(self):
        # confirmed error is not raised
        try:
            user_of_confirmed_account = self.confirmed_account_user
            self.project_creator_of_confirmed_account.validate_user_access(
                user_of_confirmed_account
            )
        except UnconfirmedAccountException:
            raise Exception('Error: user of confirmed account cannot see own project')

    def test_nonuser_of_confirmed_account_can_see_project(self):
        # confirmed error is not raised
        try:
            nonuser_of_confirmed_account = self.user
            self.project_creator_of_confirmed_account.validate_user_access(
                nonuser_of_confirmed_account
            )
        except UnconfirmedAccountException:
            raise Exception('Error: nonuser of confirmed account cannot see confirmed project')

    def test_nonuser_of_unconfirmed_account_cannot_see_project(self):
        # confirm error is raised
        with pytest.raises(UnconfirmedAccountException, match='Account Is Not Confirmed And User Is Not In Account'):
            nonuser_of_unconfirmed_account = self.user
            self.project_creator_of_unconfirmed_account.validate_user_access(
                nonuser_of_unconfirmed_account
            )


class TestProjectNote(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.project_activity = ProjectActivityFactory()

    def test_project_activity_str_method(self):
        new_project_activity = self.project_activity
        assert isinstance(new_project_activity.__str__(), str)
