from django.test import TestCase
from django.utils import timezone
import pytest
from unittest.mock import patch
from accounts.models import Profile, SignUpInvitation
from django.contrib.auth.models import User
from factories.accounts_factories import ProfileFactory, UserFactory
import faker

fake = faker.Faker()

#This fiXture of Profile model instacne creation
@pytest.fixture
@pytest.mark.django_db
def new_user():
    return ProfileFactory()

#This test is for Profile model validation of User.username
@pytest.mark.django_db
@patch('accounts.models.Profile') 
def test_user_creation_with_default_values(new_user):
    assert new_user.user.username is not None

#This test is for Profile model get_location method
@pytest.mark.django_db
def test_get_location():
    user = Profile.objects.create(
        city_town=None, state_province_region=None, country=None)
    expected_result = 'None specified'
    result = user.get_location()
    assert result == expected_result

#This test is for Profile model country field validation
@pytest.mark.django_db
@patch('accounts.models.Profile') 
def test_profile_validation(new_user):
    new_user.country = "England"
    assert new_user.save() is not None

#This test is for the Profile model string method
@pytest.mark.django_db
@patch('accounts.models.Profile') 
def test_str_method(new_user):
    user = new_user
    string = str(user)

    assert isinstance(string, str)

#This test is for Invitation model instance creation
@pytest.mark.django_db
def test_create_signup_invitation_with_defaults():
    invitation = SignUpInvitation.objects.create(email=fake.email(),message=fake.text(),sender=UserFactory(),date_sent=timezone.now())
    assert invitation.save() is None

#This test is for the Invitation model string method
@pytest.mark.django_db
def test_create_signup_invitation_str():
    invitation = SignUpInvitation.objects.create(email=fake.email(),message=fake.text(),sender=UserFactory(),date_sent=timezone.now())
    invitation.save()
    string = str(invitation)
    assert isinstance(invitation.__str__(),str)
    assert string == invitation.email