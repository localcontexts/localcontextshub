import pytest
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User
from projects.models import Project, ProjectContributors, ProjectNote
from factories.accounts_factories import UserFactory
from factories.institutions_factories import InstitutionFactory
from factories.communities_factories import CommunityFactory
from factories.researchers_factories import ResearcherFactory
from factories.projects_factories import ProjectFactory, ProjectArchivedFactory, ProjectPersonFactory, ProjectNoteFactory, ProjectContributorsFactory, ProjectCreatorFactory, ProjectActivityFactory


# This fixture for Project model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_project():
    return ProjectFactory()

# This test is for Project model has_labels method
@pytest.mark.django_db
def test_project_has_labels(new_project):
    test_project_one = new_project
    assert test_project_one.has_labels()
    test_project_two = new_project
    assert test_project_two.has_bclabels()
    test_project_three = new_project
    assert test_project_three.has_tklabels()

# This test is for Project model can_user_access method    
@pytest.mark.django_db
def test_project_can_user_access(new_project):
    user = UserFactory()
    user.save()
    assert isinstance(new_project.can_user_access(user), bool)

# This test is for Project model project_privacy method
@pytest.mark.django_db
def test_get_template_name_public_privacy(new_project):
    project = new_project
    user = project.project_creator

    project.project_privacy = "Public"
    project.save()

    assert project.get_template_name(user) == "partials/_project-actions.html"

# This test is for Project model project_privacy method  
@pytest.mark.django_db
def test_get_template_name_contributor_privacy(new_project):
    project = new_project
    user = project.project_creator

    project.project_privacy = "Contributor"
    project.save()
    assert project.get_template_name(user) == "partials/_project-actions.html"

# This test is for Project model project_privacy method    
@pytest.mark.django_db
def test_get_template_name_private_and_unexpected_privacy(new_project):
    project = new_project
    user = project.project_creator
    another_user = UserFactory(username="another_user")

    project.project_privacy = "Private"
    project.save()

    assert project.get_template_name(user) ==  "partials/_project-actions.html"

    project.project_privacy = "SomethingElse"
    project.save()

    assert project.get_template_name(user) is None

# This test is for Project model __str__ method
@pytest.mark.django_db
def new_project_test_str_method(new_project):
    project = new_project
    result = str(project)

    assert isinstance(result, str)


# This fixture for ProjectPerson model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_project_person():
    return ProjectPersonFactory()

# This test is for ProjectPerson model __Str__ method
@pytest.mark.django_db
def test_project_person_str_method(new_project_person):
    project_person = new_project_person
    assert isinstance(project_person.__str__(), str)

# This fixture for ProjectNote model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_project_note():
    return ProjectNoteFactory()

# This test is for ProjectNote model __str__ method
@pytest.mark.django_db
def new_project_note_test_str_method(new_project_note):
    project = new_project_note
    result = str(project)
    assert isinstance(result, str)
    
# This fixture for ProjectContributors model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_project_contributor():
    assert isinstance(ProjectContributorsFactory().__str__(), str)
    return ProjectContributorsFactory()

# This test is for ProjectContributors model is_user_contributor method
@pytest.mark.django_db
def test_is_user_contributor():
    user = UserFactory()

    project = ProjectFactory()
    institution = InstitutionFactory()
    community = CommunityFactory()
    researcher = ResearcherFactory()

    # Checking if a ProjectContributors instance exists for the project
    existing_contributor = ProjectContributors.objects.filter(project=project).first()

    # Reusing the existing instance if found
    if existing_contributor:
        project_contributors = existing_contributor
    else:
        # Creating a new ProjectContributors instance if not found
        project_contributors = ProjectContributors.objects.create(project=project)

    project_contributors = ProjectContributors.objects.create()
    project_contributors.communities.add(community)
    project_contributors.institutions.add(institution)
    project_contributors.researchers.add(researcher)
    
    assert project_contributors.is_user_contributor(user) is False 
    assert not project_contributors.is_user_contributor(User.objects.create_user(username='another_user', password='another_password'))
    assert not project_contributors.is_user_contributor(User.objects.create_user(username='yet_another_user', password='yet_another_password'))

# This fixture for ProjectCreator model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_project_creator():
    return ProjectCreatorFactory()

# This test is for ProjectCreator model account_type method
@pytest.mark.django_db
def test_which_account_type_created_community():
    user = UserFactory()
    community = CommunityFactory()
    project_creator = ProjectCreatorFactory()
    is_created_by = { 'community': False, 'institution': False, 'researcher': False,}

    is_created_by = project_creator.which_account_type_created()
    assert is_created_by['community'] == True
    is_created_by['community'] == True
    is_user_in_account = project_creator.is_user_in_creator_account(user, is_created_by)
    assert is_user_in_account == False

# This test is for ProjectCreator model account_type method
@pytest.mark.django_db
def test_which_account_type_created_institution():
    user = UserFactory()
    institution = InstitutionFactory()
    project_creator = ProjectCreatorFactory()
    is_created_by = { 'community': False, 'institution': False, 'researcher': False,}

    is_created_by = project_creator.which_account_type_created()
    assert is_created_by['institution'] == True
    is_created_by['institution'] == True
    is_user_in_account = project_creator.is_user_in_creator_account(user, is_created_by)
    assert is_user_in_account == False

# This test is for ProjectCreator model account_type method
@pytest.mark.django_db
def test_which_account_type_created_researcher():
    user = UserFactory()
    researcher = ResearcherFactory()
    project_creator = ProjectCreatorFactory()
    is_created_by = { 'community': False, 'institution': False, 'researcher': False,}

    is_created_by = project_creator.which_account_type_created()
    assert is_created_by['researcher'] == True
    is_created_by['researcher'] == True
    is_user_in_account = project_creator.is_user_in_creator_account(user, is_created_by)
    assert is_user_in_account == False

# This test is for ProjectCreator model __str__ method
@pytest.mark.django_db
def test_project_creator_str_method():
    project_creator = ProjectCreatorFactory()
    assert isinstance(project_creator.__str__(), str)

# Fixture for ProjectActivity model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_project_activity():
    return ProjectActivityFactory()

# This test is for ProjectActivity model __str__ method
@pytest.mark.django_db
def test_project_activity_str_method(new_project_activity):
    project_activity = new_project_activity
    assert isinstance(project_activity.__str__(), str)