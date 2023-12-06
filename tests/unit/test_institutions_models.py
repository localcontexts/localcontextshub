from django.test import TestCase
import pytest
from unittest.mock import patch
from institutions.models import Institution
from factories.accounts_factories import UserFactory
from factories.institutions_factories import InstitutionFactory
import faker

fake = faker.Faker()

#This fixture of Institute model instacne creation
@pytest.fixture
@pytest.mark.django_db
def new_institution():
    return InstitutionFactory()

# Test case for Institution get_location method 
@pytest.mark.django_db 
def test_get_location(new_institution):
    institution = new_institution
    institution.city_town = 'Test City'
    institution.state_province_region = 'Test State'
    institution.country = 'Test Country'
    institution.is_approved=True
    institution.save()

    expected_location = 'Test City, Test State, Test Country'
    assert institution.get_location() == expected_location

# Test case for Institution location_none method
@pytest.mark.django_db
def test_get_location_none_specified(new_institution):
    institution = new_institution
    institution.city_town=None
    institution.state_province_region = None
    institution.country = None
    institution.save()
    expected_location = 'None specified'
    assert institution.get_location() == expected_location

# Test case for Institution get_member method
@pytest.mark.django_db 
def test_get_member_count(new_institution):
    institution = new_institution
    institution.admins.add(UserFactory())
    institution.save()
    member_count = institution.get_member_count()
    expected_member_count = 2
    
    assert member_count == expected_member_count

# Test case for Institution get_member_count_no_members
@pytest.mark.django_db
def test_get_member_count_no_members(new_institution):
    institution =new_institution
    member_count = institution.get_member_count()
    expected_member_count = 1
    assert member_count == expected_member_count

# Test case for Institution different get method
@pytest.mark.django_db    
def test_model_methods(new_institution):
        # Test get_admins
        admin = UserFactory()
        institution = new_institution
        institution.admins.add(admin)
        admins = institution.get_admins()
        assert admin, admins

        # Test get_editors
        editor = UserFactory()
        institution.editors.add(editor)
        editors = institution.get_editors()
        assert editor, editors

        # Test get_viewers
        viewer = UserFactory()
        institution.viewers.add(viewer)
        viewers = institution.get_viewers()
        assert viewer, viewers

# Test case for Institution is_user_in_institution method
@pytest.mark.django_db
def test_is_user_in_institution(new_institution):
    institution = new_institution
    user = UserFactory()
    institution.viewers.add(user)
    result = institution.is_user_in_institution(user)

    assert isinstance(result, bool)

# Test case for Institution __str__ method
@pytest.mark.django_db
def test_str_method(new_institution):
    institution = new_institution
    string = str(institution)

    assert isinstance(string, str)
    assert string == institution.institution_name