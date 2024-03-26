from django.test import TestCase

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from researchers.decorators import is_researcher
from factories.accounts_factories import UserFactory
from factories.researchers_factories import ResearcherFactory


@is_researcher()
def view(request, researcher):
    return HttpResponse(status=200)


class TestIsResearcher(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.researcher_user = UserFactory()
        self.non_researcher_user = UserFactory()
        self.researcher = ResearcherFactory(user=self.researcher_user)
        self.request = RequestFactory()

    def test_researcher_has_access(self):
        request = self.request.get('/')
        request.user = self.researcher_user
        resp = view(request, pk=self.researcher_user.id)
        self.assertEqual(resp.status_code, 200)

    def test_non_researcher_does_not_have_access(self):
        request = self.request.get('/')
        request.user = self.non_researcher_user
        resp = view(request, pk=self.researcher_user.id)
        self.assertEqual(resp.status_code, 302)
