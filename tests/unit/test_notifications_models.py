import pytest
from django.test import TestCase
from factories.notifications_factories import UserNotificationFactory, ActionNotificationFactory


class TestUserNotification(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.user_notification = UserNotificationFactory()

    def test_user_notification_str(self):
        new_user_notification = self.user_notification
        string = str(new_user_notification)
        assert isinstance(string, str)
        assert string == f"{new_user_notification.notification_type}-{new_user_notification.title}"

    def test_user_notification_ordering(self):
        new_user_notification = self.user_notification
        assert new_user_notification._meta.ordering == ('viewed', '-created')


class TestActionNotification(TestCase):

    def setUp(self):
        self.action_notification = ActionNotificationFactory()

    def test_action_notification_str(self):
        new_action_notification = self.action_notification
        string = str(new_action_notification)
        assert isinstance(string, str)
        assert string == f"{new_action_notification.notification_type} - {new_action_notification.title}"

    def test_action_notification_ordering(self):
        new_action_notification = self.action_notification
        assert new_action_notification._meta.ordering == ('viewed', '-created')
