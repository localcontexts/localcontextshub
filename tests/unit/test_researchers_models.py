from django.test import TestCase
import pytest
from factories.researchers_factories import ResearcherFactory

# This fixture for Researcher model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_researcher():
    return ResearcherFactory()

# This test is for Researcher model get_project method
@pytest.mark.django_db
def test_get_projects_exists(new_researcher):
    researcher = new_researcher
    result = researcher.get_projects()

    assert isinstance(result, bool)

# This test is for Researcher model __str__ method
@pytest.mark.django_db
def test_str_method(new_researcher):
    researcher = new_researcher
    string = str(researcher)
    
    assert isinstance(string, str)
    assert string == str(researcher)