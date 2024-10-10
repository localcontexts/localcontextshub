import os
import urllib.parse

import pytest

from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.test.utils import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from factories.accounts_factories import UserFactory
from external_api.urls import UrlsWithMockedExternalApi


@override_settings(ROOT_URLCONF=UrlsWithMockedExternalApi)
@pytest.mark.usefixtures("py")
class UiFeatureHelper(StaticLiveServerTestCase):
    def login(self,):
        os.environ['TEST_LIVE_SERVER_DOMAIN'] = self.live_server_url

        # create user
        unhashed_pw = 'pw'
        self.user_password_hashed = make_password(unhashed_pw)
        self.user = UserFactory(password=self.user_password_hashed)

        # visit login page
        login_url = urllib.parse.urljoin(self.live_server_url, reverse('login'))
        self.py.visit(login_url)

        # enter credentials
        self.py.get("[name='username']").type(self.user.username)
        self.py.get("[name='password']").type(unhashed_pw)

        # submit login
        self.py.get("[class~='signin-btn']").click()
