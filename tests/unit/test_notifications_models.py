import pytest
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from factories.notifications_factories import UserNotificationFactory, ActionNotificationFactory


#This fixture of UserNotification model instacne creation
@pytest.fixture
@pytest.mark.django_db
def user_notification():
    return UserNotificationFactory()

# This test is for UserNotification model __str__ method
@pytest.mark.django_db
def test_user_notification_str(user_notification):
    result = user_notification.__str__()
    assert isinstance(result, str)

# This test is for UserNotification model ordering method
@pytest.mark.django_db
def test_user_notification_ordering(user_notification):
    assert user_notification._meta.ordering == ('viewed', '-created')

#This fixture of ActionNotification model instacne creation
@pytest.fixture
@pytest.mark.django_db
def action_notification():
    return ActionNotificationFactory()

# This test is for ActionNotification model __str__ method
@pytest.mark.django_db
def test_action_notification_str(action_notification):
    result = action_notification.__str__()
    assert isinstance(result, str)

# This test is for ActionNotification model ordering method
@pytest.mark.django_db
def test_action_notification_ordering(action_notification):
    assert action_notification._meta.ordering == ('viewed', '-created')