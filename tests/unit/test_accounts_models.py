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

class TestProfile(TestCase):
    @patch('accounts.models.Profile') 
    def test_user_creation_with_default_values(self, new_user):
        assert new_user.user.username is not None

    @patch('accounts.models.Profile') 
    def test_profile_validation(self, new_user):
        new_user.country = "England"
        assert new_user.save() is not None

    @patch('accounts.models.Profile') 
    def test_str_method(self, new_user):
        user = new_user
        string = str(user)
        assert isinstance(string, str)

@pytest.mark.django_db
def test_get_location():
    user = Profile.objects.create(
        city_town=None, state_province_region=None, country=None)
    assert user.get_location() == 'None specified'

class TestSignUpInvitation(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.invitation = SignUpInvitation.objects.create(
            email=fake.email(),
            message=fake.text(),
            sender=UserFactory(),
            date_sent=timezone.now()
        )

    def test_create_signup_invitation_with_defaults(self):
        assert self.invitation.pk is not None

    def test_create_signup_invitation_str(self):
        assert isinstance(str(self.invitation), str)
        assert self.invitation.email in str(self.invitation)