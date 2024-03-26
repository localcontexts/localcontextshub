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
        self.researcher1 = ResearcherFactory(user=UserFactory())
        self.researcher2 = ResearcherFactory(user=UserFactory())
        self.request = RequestFactory()

    def test_researcher_has_access(self):
        """
        Response should be a 200 since researcher1
        does have access to researcher1
        """
        request = self.request.get('/')
        request.user = self.researcher1.user
        resp = view(request, pk=self.researcher1.id)
        self.assertEqual(resp.status_code, 200)

    def test_non_researcher_does_not_have_access(self):
        """
        Response should be a 302 since researcher1
        does not have access to researcher2
        """
        request = self.request.get('/')
        request.user = self.researcher1.user
        resp = view(request, pk=self.researcher2.id)
        self.assertEqual(resp.status_code, 302)
