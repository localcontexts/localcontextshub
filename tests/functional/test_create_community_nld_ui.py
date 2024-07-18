import pytest
import requests
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from factories.accounts_factories import UserFactory
from requests.cookies import RequestsCookieJar


@pytest.mark.usefixtures("py")
class TestFeaturesBase(StaticLiveServerTestCase):
    def setUp(self):
        # create user
        self.user = UserFactory()

        # store user login cookies
        self.community_user_login_cookies = self.get_user_login_cookies(
            username=self.user.username,
            password=self.user.password
        )

    def get_user_login_cookies(self, username: str, password: str) -> RequestsCookieJar:
        # Retrieve the CSRF token for login page
        login_url = self.live_server_url + reverse('login')
        login_get_request = requests.get(login_url)
        login_data = dict(
            username=username,
            password=password,
            csrfmiddlewaretoken=login_get_request.cookies['csrftoken']
        )

        # Get login cookies
        login_post_result = requests.post(login_url, data=login_data, cookies=login_get_request.cookies)

        # return cookies
        return login_post_result.cookies

    def test_foobar(self):
        a = 1
        url = self.live_server_url + '/dashboard'
        login_post_result = requests.post(url, cookies=self.community_user_login_cookies)

